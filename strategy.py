# strategy.py
import math
import queue
import threading
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Optional, Union

import shioaji as sj

from config import CFG
from trade_logger import log_trade


# ── 輔助函式 ──────────────────────────────────────────────────────────────────

def get_tick_size(price: float) -> float:
    """台股 tick size 查表"""
    if price < 10:
        return 0.01
    elif price < 50:
        return 0.05
    elif price < 100:
        return 0.1
    elif price < 500:
        return 0.5
    elif price < 1000:
        return 1.0
    else:
        return 5.0


def get_limit_up_price(contract: sj.contracts.Stock) -> float:
    """從商品檔取得漲停價"""
    return float(contract.limit_up)


# ── 狀態 ──────────────────────────────────────────────────────────────────────

@dataclass
class StrategyState:
    # 盤前計算（初始化後不變）
    limit_up_price:     float = 0.0
    trigger_lot:        int   = 0
    large_order_amount: float = 5_000_000

    # 即時行情
    ask_vol_at_limit_up: float = float('inf')  # 初始設大，避免條件 D 誤觸
    bid_vol_at_limit_up: int   = 0
    last_price:          float = 0.0

    # VWAP
    cumulative_pv:  float = 0.0
    cumulative_vol: int   = 0
    vwap:           float = 0.0

    # 條件 C 滑動窗口：list of (datetime, amount)
    recent_large_window: list = field(default_factory=list)

    # 持倉狀態
    bought:        bool               = False
    order_filled:  bool               = False  # 買單已實際成交
    exit_pending:  bool               = False  # 賣單已送出，等待成交回報
    entry_trade:   object             = None   # 買單 trade 物件，用於撤單
    bought_time:   Optional[datetime] = None
    trade_count:   int                = 0   # 當日進出場次數（上限 2）

    # 停損 C 用
    peak_bid_vol:               int = 0
    cumulative_trade_after_buy: int = 0

    # 診斷用計數器
    tick_count:   int                = 0
    bidask_count: int                = 0
    last_tick_dt: Optional[datetime] = None
    last_ba_dt:   Optional[datetime] = None

    # 診斷用：最近 tick 逐筆條件快照 (ring buffer, 最多 50 筆)
    debug_ticks: list = field(default_factory=list)
    DEBUG_TICK_MAX: int = 50

    # 最新五檔（供 monitor 顯示）
    last_bidask: dict = field(default_factory=dict)


# ── 盤前初始化 ────────────────────────────────────────────────────────────────

def init_state(contract: sj.contracts.Stock, large_order_amount: float) -> StrategyState:
    """08:30 執行一次，計算當日固定參數"""
    state = StrategyState()
    state.limit_up_price = get_limit_up_price(contract)

    price_factor = (
        CFG.price_factor_high
        if state.limit_up_price >= CFG.price_factor_threshold
        else CFG.price_factor_low
    )
    state.trigger_lot = math.ceil(
        CFG.trigger_amount * price_factor / (state.limit_up_price * 1_000)
    )
    state.large_order_amount = large_order_amount
    return state


# ── 進場邏輯 ──────────────────────────────────────────────────────────────────

MAX_TRADES_PER_DAY = 2


def _check_entry(state: StrategyState, tick: sj.TickSTKv1) -> bool:
    """四條件同時成立才回傳 True，同時產生診斷快照"""
    now = tick.datetime.time()
    close = float(tick.close)
    tick_size = get_tick_size(state.limit_up_price)

    # 條件 A：時間濾網
    entry_start = time(*CFG.entry_time_start)
    entry_end   = time(*CFG.entry_time_end)
    cond_a = entry_start < now < entry_end

    # 條件 B：價格位置（漲停價或下一檔）
    cond_b = close >= state.limit_up_price - tick_size

    # 條件 C：10 秒內外盤累計金額 ≥ 門檻
    if tick.tick_type == 1:  # 外盤
        amount = close * tick.volume * 1_000
        state.recent_large_window.append((tick.datetime, amount))
    cutoff = tick.datetime - timedelta(seconds=CFG.large_window_seconds)
    state.recent_large_window = [
        (dt, amt) for dt, amt in state.recent_large_window if dt > cutoff
    ]
    window_amount = sum(amt for _, amt in state.recent_large_window)
    cond_c = window_amount >= state.large_order_amount

    # 條件 D：點火水位
    ask_vol = state.ask_vol_at_limit_up if state.ask_vol_at_limit_up != float('inf') else -1
    cond_d = ask_vol < state.trigger_lot and ask_vol >= 0

    # 條件 E：進場價不得低於 VWAP（避免進場後立刻觸發停損 B）
    cond_e = state.vwap <= 0 or close >= state.vwap

    # 停損條件快照（僅持倉時才計算，未持倉顯示 "-"）
    if state.bought:
        stop_a_threshold = state.trigger_lot * CFG.stop_a_multiplier
        # ask_vol 此處是原始 state 值（非轉換後的 -1），直接用 state.ask_vol_at_limit_up
        raw_ask = state.ask_vol_at_limit_up
        stop_a = raw_ask != float('inf') and raw_ask > stop_a_threshold
        stop_b = (state.last_price > 0 and state.last_price < state.vwap) if state.vwap > 0 else False
        if state.peak_bid_vol > 0:
            shrink     = state.peak_bid_vol - state.bid_vol_at_limit_up
            shrink_pct = shrink / state.peak_bid_vol
            stop_c = shrink_pct > CFG.stop_c_shrink_ratio and shrink > state.cumulative_trade_after_buy
        else:
            shrink_pct = 0.0
            stop_c = False
        stop_snap = {
            "stopA": stop_a,  "stopA_v": f"ask={raw_ask} > {stop_a_threshold:.0f}",
            "stopB": stop_b,  "stopB_v": f"price={state.last_price} < vwap={round(state.vwap,2)}",
            "stopC": stop_c,  "stopC_v": f"shrink={shrink_pct:.1%} peak={state.peak_bid_vol} bid={state.bid_vol_at_limit_up}",
        }
    else:
        stop_snap = {
            "stopA": "-", "stopA_v": "-",
            "stopB": "-", "stopB_v": "-",
            "stopC": "-", "stopC_v": "-",
        }

    # 寫入診斷 ring buffer
    snap = {
        "t":       tick.datetime.strftime("%H:%M:%S.%f")[:12],
        "price":   close,
        "vol":     tick.volume,
        "type":    "外" if tick.tick_type == 1 else ("內" if tick.tick_type == 2 else "?"),
        "vwap":    round(state.vwap, 2),
        "A":       cond_a,
        "B":       cond_b,
        "B_val":   f"{close} >= {state.limit_up_price - tick_size}",
        "C":       cond_c,
        "C_val":   f"{window_amount/1e6:.1f}M / {state.large_order_amount/1e6:.1f}M",
        "D":       cond_d,
        "D_val":   f"ask={ask_vol} < trig={state.trigger_lot}",
        "E":       cond_e,
        "E_val":   f"{close} >= vwap={round(state.vwap,2)}",
        "bought":  state.bought,
        **stop_snap,
    }
    state.debug_ticks.append(snap)
    if len(state.debug_ticks) > state.DEBUG_TICK_MAX:
        state.debug_ticks = state.debug_ticks[-state.DEBUG_TICK_MAX:]

    # 次數上限
    if state.trade_count >= MAX_TRADES_PER_DAY:
        return False

    return cond_a and cond_b and cond_c and cond_d and cond_e


def _execute_entry(state: StrategyState, api: sj.Shioaji, tick: sj.TickSTKv1) -> None:
    """送限價買單並初始化持倉狀態"""
    print(f"[Entry] {tick.code} | price={state.limit_up_price} | ask_vol={state.ask_vol_at_limit_up}")
    contract = api.Contracts.Stocks[tick.code]
    # 市價單在漲停板會以漲停價成交，且優先於同價限價單
    order = api.Order(
        price=0,
        quantity=1,
        action=sj.constant.Action.Buy,
        price_type=sj.constant.StockPriceType.MKT,
        order_type=sj.constant.OrderType.ROD,
        order_lot=sj.constant.StockOrderLot.Common,
        account=api.stock_account,
    )
    try:
        trade = api.place_order(contract, order)
        order_status = str(trade.status.status)
        print(f"[Entry] place_order status={order_status}")
    except Exception as e:
        print(f"[Entry] place_order 失敗，不設 bought: {e}")
        return

    state.bought       = True
    state.entry_trade  = trade
    state.bought_time  = tick.datetime
    state.peak_bid_vol = state.bid_vol_at_limit_up

    # 記錄進場
    log_trade({
        "timestamp":      tick.datetime.isoformat(),
        "stock_id":       tick.code,
        "action":         "Entry",
        "reason":         "四條件成立",
        "price":          float(tick.close),
        "limit_up_price": state.limit_up_price,
        "vwap":           round(state.vwap, 2),
        "ask_vol":        state.ask_vol_at_limit_up,
        "bid_vol":        state.bid_vol_at_limit_up,
        "trigger_lot":    state.trigger_lot,
        "trade_count":    state.trade_count + 1,
        "peak_bid_vol":   state.peak_bid_vol,
        "cum_trade_vol":  state.cumulative_trade_after_buy,
        "order_status":   order_status,
    })


# ── 停損邏輯 ──────────────────────────────────────────────────────────────────

def _reset_after_exit(state: StrategyState, count_trade: bool = True) -> None:
    """出場後重置持倉狀態，撤單不計入次數"""
    state.bought                     = False
    state.order_filled               = False
    state.exit_pending               = False
    state.entry_trade                = None
    state.bought_time                = None
    state.peak_bid_vol               = 0
    state.cumulative_trade_after_buy = 0
    if count_trade:
        state.recent_large_window = []  # 真實出場才清窗口，撤單保留條件 C 累積
        state.trade_count += 1


def _execute_exit(state: StrategyState, api: sj.Shioaji, stock_id: str, reason: str, event_dt: Optional[datetime] = None) -> None:
    """送市價賣單，等待成交回報再 reset"""
    if state.exit_pending:
        return  # 賣單已送出，不重複下單

    print(f"[Exit] {stock_id} | {reason} | last_price={state.last_price} | vwap={state.vwap:.2f}")

    contract = api.Contracts.Stocks[stock_id]
    order = api.Order(
        price=0,
        quantity=1,
        action=sj.constant.Action.Sell,
        price_type=sj.constant.StockPriceType.MKT,
        order_type=sj.constant.OrderType.IOC,
        order_lot=sj.constant.StockOrderLot.Common,
        account=api.stock_account,
    )
    try:
        trade = api.place_order(contract, order)
        order_status = str(trade.status.status)
        print(f"[Exit] place_order status={order_status}")
    except Exception as e:
        print(f"[Exit] place_order 失敗: {e}")
        order_status = f"Error: {e}"

    state.exit_pending = True  # 賣單已送出，等待 order_callback 確認再 reset

    # 記錄出場（在 reset 之前，才能取到持倉期間的數據）
    log_trade({
        "timestamp":      (event_dt or datetime.now()).isoformat(),
        "stock_id":       stock_id,
        "action":         "Exit",
        "reason":         reason,
        "price":          state.last_price,
        "limit_up_price": state.limit_up_price,
        "vwap":           round(state.vwap, 2),
        "ask_vol":        state.ask_vol_at_limit_up,
        "bid_vol":        state.bid_vol_at_limit_up,
        "trigger_lot":    state.trigger_lot,
        "trade_count":    state.trade_count + 1,
        "peak_bid_vol":   state.peak_bid_vol,
        "cum_trade_vol":  state.cumulative_trade_after_buy,
        "order_status":   order_status,
    })
    # 不在這裡 reset，由 order_callback 收到賣出成交回報後再 reset


def _check_stop_loss(state: StrategyState, api: sj.Shioaji, stock_id: str, event_dt: Optional[datetime] = None) -> None:
    """三條件任一成立即市價出場"""
    if not state.bought:
        return

    if state.exit_pending:
        return  # 賣單已送出，等待成交回報

    # 狀況1：有委託但未成交 → 停損條件成立時撤買單
    if not state.order_filled:
        if (
            (state.ask_vol_at_limit_up != float('inf') and
             state.ask_vol_at_limit_up > state.trigger_lot * CFG.stop_a_multiplier)
            or (state.last_price > 0 and state.last_price < state.vwap and state.vwap > 0)
            or (
                state.peak_bid_vol > 0
                and (state.peak_bid_vol - state.bid_vol_at_limit_up) / state.peak_bid_vol > CFG.stop_c_shrink_ratio
                and (state.peak_bid_vol - state.bid_vol_at_limit_up) > state.cumulative_trade_after_buy
            )
        ):
            print(f"[Cancel] {stock_id} 停損條件成立但未成交，撤銷買單")
            try:
                # double-check：避免 order_callback 在此間設了 order_filled=True
                if not state.order_filled:
                    api.cancel_order(state.entry_trade)
                    api.update_status(api.stock_account)
                    _reset_after_exit(state, count_trade=False)  # 撤單不消耗次數
                else:
                    # 已成交，改走停損出場流程
                    _execute_exit(state, api, stock_id, reason="停損（撤單時已成交）", event_dt=event_dt)
            except Exception as e:
                print(f"[Cancel] 撤單失敗: {e}")
        return

    # 狀況2：已成交 → 停損條件成立時送賣單
    # 停損 A：委賣壓頂（ask_vol=0 是鎖漲停，不觸發）
    if state.ask_vol_at_limit_up != float('inf') and state.ask_vol_at_limit_up > state.trigger_lot * CFG.stop_a_multiplier:
        _execute_exit(state, api, stock_id, reason="停損A：委賣壓頂", event_dt=event_dt)
        return

    # 停損 B：跌破 VWAP（last_price=0 代表尚未收到 tick，不觸發）
    if state.vwap > 0 and state.last_price > 0 and state.last_price < state.vwap:
        _execute_exit(state, api, stock_id, reason="停損B：跌破VWAP", event_dt=event_dt)
        return

    # 停損 C：委買撤退
    if state.peak_bid_vol > 0:
        shrink     = state.peak_bid_vol - state.bid_vol_at_limit_up
        shrink_pct = shrink / state.peak_bid_vol
        if shrink_pct > CFG.stop_c_shrink_ratio and shrink > state.cumulative_trade_after_buy:
            _execute_exit(state, api, stock_id, reason="停損C：委買撤退", event_dt=event_dt)


# ── 每檔獨立執行緒 ────────────────────────────────────────────────────────────

def _worker(stock_id: str, state: StrategyState, q: queue.Queue, api: sj.Shioaji) -> None:
    """
    每檔一條執行緒，從 Queue 取事件後執行策略邏輯
    事件格式：('tick', tick) 或 ('bidask', bidask)
    收到 None 代表結束信號
    """
    while True:
        try:
            event = q.get(timeout=1)
        except queue.Empty:
            continue

        if event is None:  # 結束信號
            break

        try:
            kind, data = event
            if kind == 'tick':
                tick: sj.TickSTKv1 = data
                state.tick_count   += 1
                state.last_tick_dt  = tick.datetime
                state.last_price    = float(tick.close)
                state.cumulative_pv  += float(tick.close) * tick.volume
                state.cumulative_vol += tick.volume
                if state.cumulative_vol > 0:
                    state.vwap = state.cumulative_pv / state.cumulative_vol
                if state.bought:
                    state.cumulative_trade_after_buy += tick.volume
                if not state.bought and _check_entry(state, tick):
                    _execute_entry(state, api, tick)
                elif state.bought:
                    _check_stop_loss(state, api, stock_id, event_dt=tick.datetime)

            elif kind == 'bidask':
                bidask: sj.BidAskSTKv1 = data
                state.bidask_count += 1
                state.last_ba_dt    = bidask.datetime

                # 掃描五檔，找出價格等於漲停價的委賣/委買量
                # 股價未到漲停時五檔內不會有漲停價，回傳 0
                lup = state.limit_up_price
                ask_vol = 0
                ask_found = False
                for p, v in zip(bidask.ask_price, bidask.ask_volume):
                    if abs(float(p) - lup) < 0.001:
                        ask_vol = v
                        ask_found = True
                        break
                bid_vol = 0
                for p, v in zip(bidask.bid_price, bidask.bid_volume):
                    if abs(float(p) - lup) < 0.001:
                        bid_vol = v
                        break
                if ask_found:
                    state.ask_vol_at_limit_up = ask_vol  # 可能是 0（鎖死）或正整數
                else:
                    state.ask_vol_at_limit_up = float('inf')  # 股價未到漲停
                state.bid_vol_at_limit_up = bid_vol

                # 儲存最新五檔供 monitor 顯示
                state.last_bidask = {
                    "ask_price": [float(p) for p in bidask.ask_price],
                    "ask_vol":   list(bidask.ask_volume),
                    "bid_price": [float(p) for p in bidask.bid_price],
                    "bid_vol":   list(bidask.bid_volume),
                }

                if state.bought and state.bid_vol_at_limit_up > state.peak_bid_vol:
                    state.peak_bid_vol = state.bid_vol_at_limit_up
                _check_stop_loss(state, api, stock_id, event_dt=bidask.datetime)

        except Exception as e:
            print(f"[Worker:{stock_id}] 錯誤: {e}")


# ── Callbacks（只負責分發）────────────────────────────────────────────────────

def make_callbacks(queues: dict[str, queue.Queue]):
    """
    on_tick / on_bidask 只做一件事：把事件丟進對應的 Queue
    不做任何運算，確保 Shioaji callback 執行緒不被阻塞
    """

    def on_tick(exchange: sj.Exchange, tick: sj.TickSTKv1) -> None:
        q = queues.get(tick.code)
        if q is not None:
            q.put(('tick', tick))

    def on_bidask(exchange: sj.Exchange, bidask: sj.BidAskSTKv1) -> None:
        q = queues.get(bidask.code)
        if q is not None:
            q.put(('bidask', bidask))

    return on_tick, on_bidask


# ── 啟動 / 停止所有執行緒 ─────────────────────────────────────────────────────

def start_workers(
    states: dict[str, StrategyState],
    api: sj.Shioaji,
) -> tuple[dict[str, queue.Queue], list[threading.Thread]]:
    """為每檔建立 Queue 和執行緒，回傳供 main.py 管理"""
    queues  = {}
    threads = []
    for stock_id, state in states.items():
        q = queue.Queue()
        t = threading.Thread(
            target=_worker,
            args=(stock_id, state, q, api),
            name=f"worker-{stock_id}",
            daemon=True,
        )
        queues[stock_id] = q
        threads.append(t)
        t.start()
        print(f"[Worker:{stock_id}] 執行緒啟動")
    return queues, threads


def stop_workers(queues: dict[str, queue.Queue], threads: list[threading.Thread]) -> None:
    """送結束信號並等待所有執行緒結束"""
    for q in queues.values():
        q.put(None)
    for t in threads:
        t.join(timeout=3)
        print(f"[{t.name}] 已結束")
