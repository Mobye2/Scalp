# test_strategy.py
"""
模擬測試：用 tick/bidask 序列餵進 worker queue，測試策略實際反應。
執行：python test_strategy.py
"""
import queue
import sys
import threading
import time
import types
import unittest.mock
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List
from unittest.mock import MagicMock

# ── Mock shioaji ──────────────────────────────────────────────────────────────

@dataclass
class FakeTick:
    code: str
    datetime: datetime
    close: Decimal
    volume: int
    tick_type: int
    open: Decimal = Decimal('0')
    avg_price: Decimal = Decimal('0')
    high: Decimal = Decimal('0')
    low: Decimal = Decimal('0')
    amount: Decimal = Decimal('0')
    total_amount: Decimal = Decimal('0')
    total_volume: int = 0
    chg_type: int = 2
    price_chg: Decimal = Decimal('0')
    pct_chg: Decimal = Decimal('0')
    bid_side_total_vol: int = 0
    ask_side_total_vol: int = 0
    bid_side_total_cnt: int = 0
    ask_side_total_cnt: int = 0
    simtrade: int = 0
    intraday_odd: int = 0
    closing_oddlot_shares: int = 0
    fixed_trade_vol: int = 0
    suspend: int = 0

@dataclass
class FakeBidAsk:
    code: str
    datetime: datetime
    bid_price: List[Decimal]
    bid_volume: List[int]
    ask_price: List[Decimal]
    ask_volume: List[int]
    diff_bid_vol: List[int] = field(default_factory=lambda: [0]*5)
    diff_ask_vol: List[int] = field(default_factory=lambda: [0]*5)
    suspend: int = 0
    simtrade: int = 0
    intraday_odd: int = 0

mock_sj = MagicMock()
mock_sj.TickSTKv1   = FakeTick
mock_sj.BidAskSTKv1 = FakeBidAsk
mock_sj.Exchange     = MagicMock()
sys.modules['shioaji']           = mock_sj
sys.modules['shioaji.constant']  = MagicMock()
sys.modules['shioaji.contracts'] = MagicMock()

log_calls = []
fake_logger = types.ModuleType('trade_logger')
fake_logger.log_trade = lambda row: log_calls.append(dict(row))
sys.modules['trade_logger'] = fake_logger

from strategy import StrategyState, _worker, _reset_after_exit
from config import CFG

# ── 輔助 ──────────────────────────────────────────────────────────────────────

LUP = 153.0   # 漲停價
CODE = "6706"

def make_api():
    api = MagicMock()
    trade = MagicMock()
    trade.status.status = "Status.Submitted"
    api.place_order.return_value = trade
    api.stock_account = MagicMock()
    return api

def make_state() -> StrategyState:
    s = StrategyState()
    s.limit_up_price     = LUP
    s.trigger_lot        = 197
    s.large_order_amount = 5_000_000
    return s

def tick(dt, price, volume, tick_type) -> tuple:
    return ('tick', FakeTick(
        code=CODE, datetime=dt,
        close=Decimal(str(price)), volume=volume, tick_type=tick_type,
    ))

def bidask(dt, ask_at_lup, bid_at_lup) -> tuple:
    return ('bidask', FakeBidAsk(
        code=CODE, datetime=dt,
        ask_price=[Decimal(str(LUP))] + [Decimal(str(LUP+0.5))]*4,
        ask_volume=[ask_at_lup, 10, 10, 10, 10],
        bid_price=[Decimal(str(LUP))] + [Decimal(str(LUP-0.5))]*4,
        bid_volume=[bid_at_lup, 50, 50, 50, 50],
    ))

def run_events(events: list, state: StrategyState, api) -> None:
    """把事件序列餵進 queue，等 worker 處理完"""
    q = queue.Queue()
    t = threading.Thread(target=_worker, args=(CODE, state, q, api), daemon=True)
    t.start()
    for e in events:
        q.put(e)
    q.put(None)  # 結束信號
    t.join(timeout=5)

# ── 測試框架 ──────────────────────────────────────────────────────────────────

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  ✅ PASS  {name}")
        PASS += 1
    else:
        print(f"  ❌ FAIL  {name}" + (f"  →  {detail}" if detail else ""))
        FAIL += 1

def run(name, fn):
    global log_calls
    log_calls = []
    print(f"\n{'─'*60}")
    print(f"【{name}】")
    fn()

# ── 測試案例 ──────────────────────────────────────────────────────────────────

def test_normal_entry_and_stop_b():
    """
    情境：正常進場後價格跌破 VWAP → 停損 B
    Tick 序列：
      t=0~9  外盤 153.0 × 10張 × 10筆  → 條件C累積金額 = 153*10*1000*10 = 15.3M ≥ 5M
      bidask ask=50 < 197              → 條件D成立
      t=10   外盤 153.0 × 1張          → 條件E: price=153 >= vwap≈153 ✅ 進場
      t=11   內盤 151.0 × 1張          → last_price=151 < vwap≈153 → 停損B
    """
    state = make_state()
    api   = make_api()
    base  = datetime(2026, 4, 15, 11, 0, 0)

    events = []
    # 先灌外盤讓條件C成立，同時讓 vwap 穩定在 153
    for i in range(10):
        events.append(tick(base + timedelta(seconds=i), 153.0, 10, 1))  # 外盤
    # bidask：ask_vol=50 < trigger_lot=197
    events.append(bidask(base + timedelta(seconds=9, milliseconds=500), 50, 300))
    # 進場 tick
    events.append(tick(base + timedelta(seconds=10), 153.0, 1, 1))
    # 模擬 order_callback 買進確認
    # （直接在事件後設 order_filled，因為 worker 是單執行緒循序處理）
    # 用一個 callable event 注入
    def set_filled(s=state): s.order_filled = True
    events.append(('_inject', set_filled))
    # 停損 tick：price 跌破 vwap
    events.append(tick(base + timedelta(seconds=11), 151.0, 1, 2))  # 內盤

    # 支援 _inject 事件的 worker wrapper
    orig_worker_events = list(events)
    q = queue.Queue()

    def patched_worker():
        while True:
            try:
                event = q.get(timeout=1)
            except queue.Empty:
                continue
            if event is None:
                break
            kind, data = event
            if kind == '_inject':
                data()  # 執行注入函式
            else:
                import queue as _q
                inner_q = _q.Queue()
                inner_q.put(event)
                inner_q.put(None)
                from strategy import _worker as _w
                # 直接呼叫內部邏輯，不開新執行緒
                try:
                    e2 = inner_q.get_nowait()
                    if e2 is None:
                        continue
                    k2, d2 = e2
                    if k2 == 'tick':
                        from strategy import _check_entry, _execute_entry, _check_stop_loss
                        import shioaji as sj
                        t2 = d2
                        state.tick_count   += 1
                        state.last_tick_dt  = t2.datetime
                        state.last_price    = float(t2.close)
                        state.cumulative_pv  += float(t2.close) * t2.volume
                        state.cumulative_vol += t2.volume
                        if state.cumulative_vol > 0:
                            state.vwap = state.cumulative_pv / state.cumulative_vol
                        if state.bought:
                            state.cumulative_trade_after_buy += t2.volume
                        if not state.bought and _check_entry(state, t2):
                            _execute_entry(state, api, t2)
                        elif state.bought:
                            _check_stop_loss(state, api, CODE)
                    elif k2 == 'bidask':
                        from strategy import _check_stop_loss
                        b2 = d2
                        lup = state.limit_up_price
                        ask_vol, ask_found = 0, False
                        for p, v in zip(b2.ask_price, b2.ask_volume):
                            if abs(float(p) - lup) < 0.001:
                                ask_vol, ask_found = v, True
                                break
                        bid_vol = 0
                        for p, v in zip(b2.bid_price, b2.bid_volume):
                            if abs(float(p) - lup) < 0.001:
                                bid_vol = v
                                break
                        state.ask_vol_at_limit_up = ask_vol if ask_found else float('inf')
                        state.bid_vol_at_limit_up = bid_vol
                        if state.bought and bid_vol > state.peak_bid_vol:
                            state.peak_bid_vol = bid_vol
                        _check_stop_loss(state, api, CODE)
                except Exception as ex:
                    print(f"  [patched_worker error] {ex}")

    # 直接用簡單循序方式跑，不開執行緒
    for event in orig_worker_events:
        kind, data = event
        if kind == '_inject':
            data()
        elif kind == 'tick':
            from strategy import _check_entry, _execute_entry, _check_stop_loss
            t2 = data
            state.tick_count   += 1
            state.last_tick_dt  = t2.datetime
            state.last_price    = float(t2.close)
            state.cumulative_pv  += float(t2.close) * t2.volume
            state.cumulative_vol += t2.volume
            if state.cumulative_vol > 0:
                state.vwap = state.cumulative_pv / state.cumulative_vol
            if state.bought:
                state.cumulative_trade_after_buy += t2.volume
            if not state.bought and _check_entry(state, t2):
                _execute_entry(state, api, t2)
            elif state.bought:
                _check_stop_loss(state, api, CODE)
        elif kind == 'bidask':
            from strategy import _check_stop_loss
            b2 = data
            lup = state.limit_up_price
            ask_vol, ask_found = 0, False
            for p, v in zip(b2.ask_price, b2.ask_volume):
                if abs(float(p) - lup) < 0.001:
                    ask_vol, ask_found = v, True
                    break
            bid_vol = 0
            for p, v in zip(b2.bid_price, b2.bid_volume):
                if abs(float(p) - lup) < 0.001:
                    bid_vol = v
                    break
            state.ask_vol_at_limit_up = ask_vol if ask_found else float('inf')
            state.bid_vol_at_limit_up = bid_vol
            if state.bought and bid_vol > state.peak_bid_vol:
                state.peak_bid_vol = bid_vol
            _check_stop_loss(state, api, CODE)

    entries = [r for r in log_calls if r['action'] == 'Entry']
    exits   = [r for r in log_calls if r['action'] == 'Exit']

    check("有進場", len(entries) == 1, f"entries={len(entries)}")
    check("進場價=153", entries and float(entries[0]['price']) == 153.0)
    check("有停損出場", len(exits) == 1, f"exits={len(exits)}")
    check("停損原因是VWAP", exits and 'VWAP' in exits[0]['reason'], exits[0]['reason'] if exits else '')
    check("exit_pending=True（等成交回報）", state.exit_pending)
    check("bought仍True（未收到賣出成交）", state.bought)


def test_condition_e_no_entry_when_price_below_vwap():
    """
    情境：price < vwap 時條件E擋住，不應進場
    先灌高價 tick 讓 vwap 拉高到 155，再用 153 的 tick 嘗試進場
    """
    state = make_state()
    api   = make_api()
    base  = datetime(2026, 4, 15, 11, 0, 0)

    events = []
    # 先灌高價讓 vwap = 155（高於漲停價153）
    for i in range(5):
        events.append(tick(base + timedelta(seconds=i), 155.0, 100, 1))
    # bidask 條件D成立
    events.append(bidask(base + timedelta(seconds=4, milliseconds=500), 50, 300))
    # 嘗試進場：price=153 < vwap≈155 → 條件E不成立
    for i in range(5, 10):
        events.append(tick(base + timedelta(seconds=i), 153.0, 10, 1))

    for event in events:
        kind, data = event
        if kind == 'tick':
            from strategy import _check_entry, _execute_entry
            t2 = data
            state.cumulative_pv  += float(t2.close) * t2.volume
            state.cumulative_vol += t2.volume
            state.vwap = state.cumulative_pv / state.cumulative_vol
            state.last_price = float(t2.close)
            if not state.bought and _check_entry(state, t2):
                _execute_entry(state, api, t2)
        elif kind == 'bidask':
            b2 = data
            lup = state.limit_up_price
            for p, v in zip(b2.ask_price, b2.ask_volume):
                if abs(float(p) - lup) < 0.001:
                    state.ask_vol_at_limit_up = v
                    break

    check("price<vwap 時不進場", not state.bought, f"vwap={state.vwap:.2f}")
    check("無 Entry log", not any(r['action'] == 'Entry' for r in log_calls))


def test_no_duplicate_sell_order():
    """
    情境：停損條件連續觸發多次，賣單只送一次
    """
    state = make_state()
    api   = make_api()
    state.bought              = True
    state.order_filled        = True
    state.exit_pending        = False
    state.last_price          = 150.0
    state.vwap                = 153.0
    state.ask_vol_at_limit_up = 10

    from strategy import _check_stop_loss
    # 連續觸發 5 次停損檢查
    for _ in range(5):
        _check_stop_loss(state, api, CODE)

    check("賣單只送一次", api.place_order.call_count == 1,
          f"place_order 被呼叫 {api.place_order.call_count} 次")


def test_cancel_then_reentry():
    """
    情境：買單未成交被撤，之後條件再次成立可以再進場
    """
    state = make_state()
    api   = make_api()
    base  = datetime(2026, 4, 15, 11, 0, 0)

    from strategy import _check_entry, _execute_entry, _check_stop_loss

    # 第一次進場
    state.ask_vol_at_limit_up = 50
    for i in range(10):
        t2 = FakeTick(code=CODE, datetime=base+timedelta(seconds=i),
                      close=Decimal('153'), volume=10, tick_type=1)
        state.cumulative_pv  += 153 * 10
        state.cumulative_vol += 10
        state.vwap = state.cumulative_pv / state.cumulative_vol
        state.last_price = 153.0
        if not state.bought and _check_entry(state, t2):
            _execute_entry(state, api, t2)

    check("第一次進場成功", state.bought)

    # 停損條件成立但未成交 → 撤單
    state.last_price = 151.0  # < vwap
    _check_stop_loss(state, api, CODE)
    check("撤單後 bought=False", not state.bought)
    check("撤單不消耗次數", state.trade_count == 0)

    # 第二次進場：條件再次成立
    state.ask_vol_at_limit_up = 50
    state.last_price = 153.0
    for i in range(10, 20):
        t2 = FakeTick(code=CODE, datetime=base+timedelta(seconds=i),
                      close=Decimal('153'), volume=10, tick_type=1)
        state.cumulative_pv  += 153 * 10
        state.cumulative_vol += 10
        state.vwap = state.cumulative_pv / state.cumulative_vol
        state.last_price = 153.0
        if not state.bought and _check_entry(state, t2):
            _execute_entry(state, api, t2)

    check("撤單後可再次進場", state.bought)
    check("trade_count 仍為 0", state.trade_count == 0)


def test_max_2_trades():
    """
    情境：完成 2 次完整進出場後，不再進場
    """
    state = make_state()
    api   = make_api()
    base  = datetime(2026, 4, 15, 11, 0, 0)

    from strategy import _check_entry, _execute_entry

    def do_one_trade(offset_sec):
        state.ask_vol_at_limit_up = 50
        for i in range(10):
            t2 = FakeTick(code=CODE,
                          datetime=base + timedelta(seconds=offset_sec+i),
                          close=Decimal('153'), volume=10, tick_type=1)
            state.cumulative_pv  += 153 * 10
            state.cumulative_vol += 10
            state.vwap = state.cumulative_pv / state.cumulative_vol
            state.last_price = 153.0
            if not state.bought and _check_entry(state, t2):
                _execute_entry(state, api, t2)
        # 模擬賣出成交 reset
        state.order_filled = True
        state.exit_pending = True
        _reset_after_exit(state, count_trade=True)

    do_one_trade(0)
    check("第1次交易完成", state.trade_count == 1)
    do_one_trade(20)
    check("第2次交易完成", state.trade_count == 2)

    # 第3次嘗試進場
    state.ask_vol_at_limit_up = 50
    entered = False
    for i in range(40, 50):
        t2 = FakeTick(code=CODE,
                      datetime=base + timedelta(seconds=i),
                      close=Decimal('153'), volume=10, tick_type=1)
        state.cumulative_pv  += 153 * 10
        state.cumulative_vol += 10
        state.vwap = state.cumulative_pv / state.cumulative_vol
        state.last_price = 153.0
        if not state.bought and _check_entry(state, t2):
            _execute_entry(state, api, t2)
            entered = True

    check("達2次上限不再進場", not entered and not state.bought)


# ── 執行 ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run("正常進場後停損B",              test_normal_entry_and_stop_b)
    run("條件E擋住price<vwap進場",      test_condition_e_no_entry_when_price_below_vwap)
    run("停損條件重複觸發只送一次賣單",  test_no_duplicate_sell_order)
    run("撤單後可再次進場",             test_cancel_then_reentry)
    run("達2次上限不再進場",            test_max_2_trades)

    print(f"\n{'═'*60}")
    print(f"結果：{PASS} 通過 / {FAIL} 失敗")
    sys.exit(0 if FAIL == 0 else 1)
