# strategy.py
import math
import queue
import threading
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Optional, Union

import shioaji as sj

from config import CFG


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
    limit_up_price: float = 0.0
    trigger_lot:    int   = 0

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
    bought:      bool               = False
    bought_time: Optional[datetime] = None
    trade_count: int                = 0   # 當日進出場次數（上限 2）

    # 停損 C 用
    peak_bid_vol:               int = 0
    cumulative_trade_after_buy: int = 0


# ── 盤前初始化 ────────────────────────────────────────────────────────────────

def init_state(contract: sj.contracts.Stock) -> StrategyState:
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
    return state


# ── 進場邏輯 ──────────────────────────────────────────────────────────────────

MAX_TRADES_PER_DAY = 2


def _check_entry(state: StrategyState, tick: sj.TickSTKv1) -> bool:
    """四條件同時成立才回傳 True"""
    now = tick.datetime.time()

    # 當日進出場次數上限
    if state.trade_count >= MAX_TRADES_PER_DAY:
        return False

    # 條件 A：時間濾網
    entry_start = time(*CFG.entry_time_start)
    entry_end   = time(*CFG.entry_time_end)
    if not (entry_start < now < entry_end):
        return False

    # 條件 B：價格位置（漲停價或下一檔）
    tick_size = get_tick_size(state.limit_up_price)
    if float(tick.close) < state.limit_up_price - tick_size:
        return False

    # 條件 C：10 秒內外盤累計金額 ≥ 門檻
    if tick.tick_type == 1:  # 外盤
        amount = float(tick.close) * tick.volume * 1_000
        state.recent_large_window.append((tick.datetime, amount))

    cutoff = tick.datetime - timedelta(seconds=CFG.large_window_seconds)
    state.recent_large_window = [
        (dt, amt) for dt, amt in state.recent_large_window if dt > cutoff
    ]
    window_amount = sum(amt for _, amt in state.recent_large_window)
    if window_amount < CFG.large_order_amount:
        return False

    # 條件 D：點火水位
    if state.ask_vol_at_limit_up >= state.trigger_lot:
        return False

    return True


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
    api.place_order(contract, order)
    state.bought       = True
    state.bought_time  = tick.datetime
    state.peak_bid_vol = state.bid_vol_at_limit_up


# ── 停損邏輯 ──────────────────────────────────────────────────────────────────

def _reset_after_exit(state: StrategyState) -> None:
    """出場後重置持倉狀態，累計次數 +1"""
    state.bought                     = False
    state.bought_time                = None
    state.peak_bid_vol               = 0
    state.cumulative_trade_after_buy = 0
    state.recent_large_window        = []
    state.trade_count               += 1


def _execute_exit(state: StrategyState, api: sj.Shioaji, stock_id: str, reason: str) -> None:
    """送市價賣單並重置狀態"""
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
    api.place_order(contract, order)
    _reset_after_exit(state)


def _check_stop_loss(state: StrategyState, api: sj.Shioaji, stock_id: str) -> None:
    """三條件任一成立即市價出場"""
    if not state.bought:
        return

    # 停損 A：委賣壓頂
    if state.ask_vol_at_limit_up > state.trigger_lot * CFG.stop_a_multiplier:
        _execute_exit(state, api, stock_id, reason="停損A：委賣壓頂")
        return

    # 停損 B：跌破 VWAP
    if state.last_price < state.vwap:
        _execute_exit(state, api, stock_id, reason="停損B：跌破VWAP")
        return

    # 停損 C：委買撤退
    if state.peak_bid_vol > 0:
        shrink     = state.peak_bid_vol - state.bid_vol_at_limit_up
        shrink_pct = shrink / state.peak_bid_vol
        if shrink_pct > CFG.stop_c_shrink_ratio and shrink > state.cumulative_trade_after_buy:
            _execute_exit(state, api, stock_id, reason="停損C：委買撤退")


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
                state.last_price    = float(tick.close)
                state.cumulative_pv  += float(tick.close) * tick.volume
                state.cumulative_vol += tick.volume
                if state.cumulative_vol > 0:
                    state.vwap = state.cumulative_pv / state.cumulative_vol
                if state.bought:
                    state.cumulative_trade_after_buy += tick.volume
                if not state.bought and _check_entry(state, tick):
                    _execute_entry(state, api, tick)

            elif kind == 'bidask':
                bidask: sj.BidAskSTKv1 = data
                state.ask_vol_at_limit_up = bidask.ask_volume[0]
                state.bid_vol_at_limit_up = bidask.bid_volume[0]
                if state.bought and state.bid_vol_at_limit_up > state.peak_bid_vol:
                    state.peak_bid_vol = state.bid_vol_at_limit_up
                _check_stop_loss(state, api, stock_id)

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
