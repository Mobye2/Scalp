# main.py
import csv
import json
import time
from pathlib import Path

import shioaji as sj

from config import CFG
from order import login
from strategy import init_state, make_callbacks, start_workers, stop_workers

WATCHLIST_PATH = Path(__file__).parent / "watchlist.csv"


def load_watchlist() -> list[dict]:
    """從 watchlist.csv 讀取 stock_id 和 large_order_amount"""
    with open(WATCHLIST_PATH, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    result = []
    for row in rows:
        stock_id = row.get("stock_id", "").strip()
        if not stock_id:
            continue
        try:
            loa = float(row.get("large_order_amount", 5_000_000))
        except (ValueError, TypeError):
            loa = 5_000_000
        result.append({"stock_id": stock_id, "large_order_amount": loa})
    return result


def main() -> None:
    # ── 登入 ──────────────────────────────────────────
    api = login(simulation=CFG.simulation)

    # ── 從 watchlist.csv 讀取監控標的 ────────────────
    watchlist = load_watchlist()
    stock_ids = [w["stock_id"] for w in watchlist]
    print(f"[Main] 從 watchlist.csv 載入 {len(stock_ids)} 檔：{stock_ids}")

    # ── 盤前初始化（每檔各自建立 state）─────────────
    states    = {}
    contracts = []
    for w in watchlist:
        stock_id           = w["stock_id"]
        large_order_amount = w["large_order_amount"]
        contract = api.Contracts.Stocks[stock_id]
        state    = init_state(contract, large_order_amount)
        states[stock_id] = state
        contracts.append(contract)
        print(
            f"[Init] {stock_id} | 漲停價={state.limit_up_price} "
            f"| trigger_lot={state.trigger_lot} "
            f"| large_order={large_order_amount/1e6:.1f}M"
        )

    # 用 snapshot 補初始現價，避免 tick 還沒來時顯示 0
    try:
        snaps = api.snapshots(contracts)
        for snap in snaps:
            if snap.code in states and snap.close > 0:
                states[snap.code].last_price = snap.close
    except Exception:
        pass

    # ── 啟動每檔獨立執行緒 ────────────────────────────
    queues, threads = start_workers(states, api)

    # ── 註冊 Callback（只分發，不運算）───────────────
    on_tick, on_bidask = make_callbacks(queues)
    api.quote.set_on_tick_stk_v1_callback(on_tick)
    api.quote.set_on_bidask_stk_v1_callback(on_bidask)

    # ── 註冊成交回報，買進成交才允許停損出場 ──────────
    def order_callback(stat, msg):
        from config import CFG
        stat_str = str(stat)
        # 正式環境：等 StockDeal（真實成交）
        # 模擬環境：StockDeal 不會來，改用 StockOrder op_code=00 當成交確認
        if CFG.simulation:
            if "StockOrder" not in stat_str:
                return
            if msg.get("operation", {}).get("op_code") != "00":
                return
        else:
            if "StockDeal" not in stat_str:
                return
        action = msg.get("order", {}).get("action", "") or msg.get("action", "")
        code   = msg.get("contract", {}).get("code", "") or msg.get("code", "")
        if action == "Buy" and code in states:
            states[code].order_filled = True
            print(f"[OrderCB] {code} 買進成交，允許停損出場")

    api.set_order_callback(order_callback)

    # ── 訂閱行情（所有檔）────────────────────────────
    for contract in contracts:
        api.quote.subscribe(
            contract,
            quote_type=sj.constant.QuoteType.Tick,
            version=sj.constant.QuoteVersion.v1,
        )
        api.quote.subscribe(
            contract,
            quote_type=sj.constant.QuoteType.BidAsk,
            version=sj.constant.QuoteVersion.v1,
        )

    # ── 盤中等待（每 5 秒寫一次第一檔診斷快照）─────────
    monitor_path = Path(__file__).parent / "logs" / "monitor.json"
    monitor_path.parent.mkdir(exist_ok=True)
    debug_id = stock_ids[0]  # 只寫第一檔
    print(f"[Main] 監控 {stock_ids}，Ctrl+C 可手動中止")
    print(f"[Main] 診斷對象: {debug_id}  快照: {monitor_path}")
    print(f"[Main] 另開 console 執行: python monitor.py")
    try:
        while True:
            st = states[debug_id]
            snapshot = {
                "stock_id":     debug_id,
                "tick_count":   st.tick_count,
                "bidask_count": st.bidask_count,
                "last_price":   st.last_price,
                "limit_up":     st.limit_up_price,
                "trigger_lot":  st.trigger_lot,
                "large_order":  round(st.large_order_amount / 1e6, 1),
                "vwap":         round(st.vwap, 2),
                "ask_vol":      float(st.ask_vol_at_limit_up) if st.ask_vol_at_limit_up != float('inf') else -1,
                "bid_vol":      st.bid_vol_at_limit_up,
                "bought":       st.bought,
                "trade_count":  st.trade_count,
                "peak_bid_vol": st.peak_bid_vol,
                "cum_trade":    st.cumulative_trade_after_buy,
                "last_tick_dt": st.last_tick_dt.strftime("%H:%M:%S") if st.last_tick_dt else None,
                "last_ba_dt":   st.last_ba_dt.strftime("%H:%M:%S") if st.last_ba_dt else None,
                "q_size":       queues[debug_id].qsize(),
                "ticks":        list(st.debug_ticks),
                "bidask":       st.last_bidask,
            }
            try:
                monitor_path.write_text(
                    json.dumps(snapshot, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except Exception:
                pass
            time.sleep(5)
    except KeyboardInterrupt:
        print("[Main] 手動中止")
    finally:
        # ── 停止執行緒 ────────────────────────────────
        stop_workers(queues, threads)
        # ── 登出（確保任何中斷都會執行）────────────────
        try:
            for contract in contracts:
                api.quote.unsubscribe(contract, quote_type=sj.constant.QuoteType.Tick)
                api.quote.unsubscribe(contract, quote_type=sj.constant.QuoteType.BidAsk)
            api.logout()
            print("[Main] 已登出")
        except Exception as e:
            print(f"[Main] 登出時發生錯誤: {e}")


if __name__ == "__main__":
    main()
