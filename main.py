# main.py
import csv
import time
from pathlib import Path

import shioaji as sj

from config import CFG
from order import login
from strategy import init_state, make_callbacks, start_workers, stop_workers

WATCHLIST_PATH = Path(__file__).parent / "watchlist.csv"


def load_watchlist() -> list[str]:
    """從 watchlist.csv 讀取 stock_id 清單"""
    with open(WATCHLIST_PATH, newline="", encoding="utf-8-sig") as f:
        return [row["stock_id"] for row in csv.DictReader(f)]


def main() -> None:
    # ── 登入 ──────────────────────────────────────────
    api = login(simulation=CFG.simulation)

    # ── 從 watchlist.csv 讀取監控標的 ────────────────
    stock_ids = load_watchlist()
    print(f"[Main] 從 watchlist.csv 載入 {len(stock_ids)} 檔：{stock_ids}")

    # ── 盤前初始化（每檔各自建立 state）─────────────
    states    = {}
    contracts = []
    for stock_id in stock_ids:
        contract = api.Contracts.Stocks[stock_id]
        state    = init_state(contract)
        states[stock_id] = state
        contracts.append(contract)
        print(
            f"[Init] {stock_id} | 漲停價={state.limit_up_price} "
            f"| trigger_lot={state.trigger_lot}"
        )

    # ── 啟動每檔獨立執行緒 ────────────────────────────
    queues, threads = start_workers(states, api)

    # ── 註冊 Callback（只分發，不運算）───────────────
    on_tick, on_bidask = make_callbacks(queues)
    api.quote.set_on_tick_stk_v1_callback(on_tick)
    api.quote.set_on_bidask_stk_v1_callback(on_bidask)

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

    # ── 盤中等待 ──────────────────────────────────────
    print(f"[Main] 監控 {stock_ids}，Ctrl+C 可手動中止")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[Main] 手動中止")

    # ── 停止執行緒 ────────────────────────────────────
    stop_workers(queues, threads)

    # ── 登出 ──────────────────────────────────────────
    for contract in contracts:
        api.quote.unsubscribe(contract, quote_type=sj.constant.QuoteType.Tick)
        api.quote.unsubscribe(contract, quote_type=sj.constant.QuoteType.BidAsk)
    api.logout()
    print("[Main] 已登出")


if __name__ == "__main__":
    main()
