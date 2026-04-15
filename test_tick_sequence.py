# test_tick_sequence.py
"""
用假 tick/bidask 序列驅動 _worker，驗證完整買賣邏輯。
執行：python test_tick_sequence.py
"""
import sys, queue, threading, time, types
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
    tick_type: int          # 1=外盤 2=內盤
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

from strategy import StrategyState, _worker
from config import CFG

# ── 工具函式 ──────────────────────────────────────────────────────────────────
CODE  = "6706"
LUP   = 153.0   # 漲停價
T0    = datetime(2026, 4, 15, 10, 0, 0)

def t(sec: float) -> datetime:
    return T0 + timedelta(seconds=sec)

def tick(sec, price, vol, tick_type) -> FakeTick:
    return FakeTick(
        code=CODE, datetime=t(sec),
        close=Decimal(str(price)), volume=vol, tick_type=tick_type,
    )

def bidask(sec, ask_vol_at_lup, bid_vol_at_lup) -> FakeBidAsk:
    """漲停價掛在第一檔"""
    return FakeBidAsk(
        code=CODE, datetime=t(sec),
        ask_price=[Decimal(str(LUP))]   + [Decimal(str(LUP+0.5))]*4,
        ask_volume=[ask_vol_at_lup]      + [10]*4,
        bid_price=[Decimal(str(LUP))]   + [Decimal(str(LUP-0.5))]*4,
        bid_volume=[bid_vol_at_lup]      + [50]*4,
    )

def make_api():
    api = MagicMock()
    trade = MagicMock()
    trade.status.status = "Submitted"
    api.place_order.return_value = trade
    api.stock_account = MagicMock()
    return api

def make_state(trigger_lot=50) -> StrategyState:
    s = StrategyState()
    s.limit_up_price     = LUP
    s.trigger_lot        = trigger_lot
    s.large_order_amount = 5_000_000
    return s

def run_sequence(state: StrategyState, api, events: list, *, order_filled_after=None):
    """
    把 events 依序丟進 worker queue，等 worker 處理完再回傳。
    order_filled_after: 若指定，在第 N 個事件後模擬買單成交回報。
    """
    q = queue.Queue()
    t_worker = threading.Thread(target=_worker, args=(CODE, state, q, api), daemon=True)
    t_worker.start()

    for i, ev in enumerate(events):
        kind = 'tick' if isinstance(ev, FakeTick) else 'bidask'
        q.put((kind, ev))
        time.sleep(0.005)   # 讓 worker 有時間處理
        if order_filled_after is not None and i == order_filled_after:
            state.order_filled = True   # 模擬成交回報

    q.put(None)             # 結束信號
    t_worker.join(timeout=3)

# ── 測試結果統計 ──────────────────────────────────────────────────────────────
PASS = FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        print(f"  ✅ {name}")
        PASS += 1
    else:
        print(f"  ❌ {name}" + (f"  ({detail})" if detail else ""))
        FAIL += 1

def section(name):
    print(f"\n{'─'*60}\n【{name}】")

# ═════════════════════════════════════════════════════════════════════════════
# 情境 1：正常進場 → 停損 B 出場
# ─────────────────────────────────────────────────────────────────────────────
# 序列說明：
#   0s  bidask: ask=30(>trigger), 不滿足條件D
#   1~5s tick: 外盤 153, vol=10 × 5 → 累積 5M，條件C成立
#   6s  bidask: ask=40(<50=trigger), 條件D成立
#   7s  tick: 外盤 153, vol=10 → 四條件全部成立 → 進場
#   8s  (模擬成交回報 order_filled=True)
#   9s  tick: 內盤 152, vol=5 → price < vwap → 停損B
# ═════════════════════════════════════════════════════════════════════════════
section("情境1：正常進場 → 停損B出場")
log_calls.clear()
s1 = make_state(trigger_lot=50)
api1 = make_api()

events1 = [
    bidask(0,  ask_vol_at_lup=80,  bid_vol_at_lup=200),   # 條件D不成立
    tick(1,  LUP, 10, 1),   # 外盤，累積 153*10*1000 = 1.53M
    tick(2,  LUP, 10, 1),   # 3.06M
    tick(3,  LUP, 10, 1),   # 4.59M
    tick(4,  LUP, 10, 1),   # 6.12M ← 條件C成立(>5M)
    tick(5,  LUP, 10, 1),   # 7.65M
    bidask(6,  ask_vol_at_lup=40,  bid_vol_at_lup=300),   # 條件D成立(40<50)
    tick(7,  LUP, 10, 1),   # 四條件全部成立 → 進場
    # order_filled 在 index=7 後設定（見 order_filled_after=7）
    tick(9,  152.0, 5, 2),  # 內盤，price < vwap → 停損B
]

run_sequence(s1, api1, events1, order_filled_after=7)

check("情境1：有進場",        api1.place_order.call_count >= 1)
check("情境1：進場後有停損B", any(r.get("reason","").startswith("停損B") for r in log_calls))
check("情境1：賣單已送出",    s1.exit_pending == True)
check("情境1：Entry log存在", any(r["action"] == "Entry" for r in log_calls))
check("情境1：Exit log存在",  any(r["action"] == "Exit"  for r in log_calls))

# ═════════════════════════════════════════════════════════════════════════════
# 情境 2：條件 D 不成立（ask_vol 始終 > trigger）→ 不進場
# ═════════════════════════════════════════════════════════════════════════════
section("情境2：條件D不成立 → 不進場")
log_calls.clear()
s2 = make_state(trigger_lot=50)
api2 = make_api()

events2 = [
    bidask(0, ask_vol_at_lup=200, bid_vol_at_lup=300),   # ask=200 > 50
    tick(1, LUP, 10, 1),
    tick(2, LUP, 10, 1),
    tick(3, LUP, 10, 1),
    tick(4, LUP, 10, 1),
    tick(5, LUP, 10, 1),
    tick(6, LUP, 10, 1),
]

run_sequence(s2, api2, events2)

check("情境2：未進場",          not s2.bought)
check("情境2：place_order未呼叫", api2.place_order.call_count == 0)

# ═════════════════════════════════════════════════════════════════════════════
# 情境 3：進場後停損 A（委賣壓頂）
# ═════════════════════════════════════════════════════════════════════════════
section("情境3：進場後停損A（委賣壓頂）")
log_calls.clear()
s3 = make_state(trigger_lot=50)
api3 = make_api()

# stop_a_multiplier=3.0 → 門檻 = 50*3 = 150
events3 = [
    bidask(0, ask_vol_at_lup=40,  bid_vol_at_lup=300),
    tick(1, LUP, 10, 1),
    tick(2, LUP, 10, 1),
    tick(3, LUP, 10, 1),
    tick(4, LUP, 10, 1),
    tick(5, LUP, 10, 1),
    tick(6, LUP, 10, 1),   # 進場
    # order_filled 在 index=6 後
    bidask(8, ask_vol_at_lup=200, bid_vol_at_lup=300),  # ask=200 > 150 → 停損A
]

run_sequence(s3, api3, events3, order_filled_after=6)

check("情境3：有進場",        api3.place_order.call_count >= 1)
check("情境3：停損A觸發",     any(r.get("reason","").startswith("停損A") for r in log_calls))
check("情境3：exit_pending",  s3.exit_pending)

# ═════════════════════════════════════════════════════════════════════════════
# 情境 4：進場前停損條件成立（未成交）→ 撤買單，不計次數
# ═════════════════════════════════════════════════════════════════════════════
section("情境4：買單未成交時停損條件成立 → 撤單")
log_calls.clear()
s4 = make_state(trigger_lot=50)
api4 = make_api()

# 進場後「不」設 order_filled，然後 ask_vol 暴增 → 撤單
events4 = [
    bidask(0, ask_vol_at_lup=40,  bid_vol_at_lup=300),
    tick(1, LUP, 10, 1),
    tick(2, LUP, 10, 1),
    tick(3, LUP, 10, 1),
    tick(4, LUP, 10, 1),
    tick(5, LUP, 10, 1),
    tick(6, LUP, 10, 1),   # 進場（order_filled 仍 False）
    bidask(8, ask_vol_at_lup=200, bid_vol_at_lup=300),  # 停損條件成立 → 撤單
]

run_sequence(s4, api4, events4)   # 不設 order_filled_after

check("情境4：有進場動作",      api4.place_order.call_count >= 1)
check("情境4：撤單被呼叫",      api4.cancel_order.called)
check("情境4：bought=False",    not s4.bought)
check("情境4：trade_count=0",   s4.trade_count == 0)

# ═════════════════════════════════════════════════════════════════════════════
# 情境 5：停損 C（委買撤退）
# ═════════════════════════════════════════════════════════════════════════════
section("情境5：停損C（委買撤退 >30%）")
log_calls.clear()
s5 = make_state(trigger_lot=50)
api5 = make_api()

events5 = [
    bidask(0, ask_vol_at_lup=40,  bid_vol_at_lup=300),
    tick(1, LUP, 10, 1),
    tick(2, LUP, 10, 1),
    tick(3, LUP, 10, 1),
    tick(4, LUP, 10, 1),
    tick(5, LUP, 10, 1),
    tick(6, LUP, 10, 1),   # 進場
    # order_filled 在 index=6 後
    bidask(8, ask_vol_at_lup=40,  bid_vol_at_lup=300),  # peak=300
    bidask(9, ask_vol_at_lup=40,  bid_vol_at_lup=180),  # 縮減 120/300=40% > 30% → 停損C
]

run_sequence(s5, api5, events5, order_filled_after=6)

check("情境5：停損C觸發",    any(r.get("reason","").startswith("停損C") for r in log_calls))
check("情境5：exit_pending", s5.exit_pending)

# ═════════════════════════════════════════════════════════════════════════════
# 情境 6：達每日 2 次上限 → 不再進場
# ═════════════════════════════════════════════════════════════════════════════
section("情境6：達每日2次上限 → 不進場")
log_calls.clear()
s6 = make_state(trigger_lot=50)
s6.trade_count = 2   # 已達上限
api6 = make_api()

events6 = [
    bidask(0, ask_vol_at_lup=40,  bid_vol_at_lup=300),
    tick(1, LUP, 10, 1),
    tick(2, LUP, 10, 1),
    tick(3, LUP, 10, 1),
    tick(4, LUP, 10, 1),
    tick(5, LUP, 10, 1),
    tick(6, LUP, 10, 1),
]

run_sequence(s6, api6, events6)

check("情境6：未進場",            not s6.bought)
check("情境6：place_order未呼叫", api6.place_order.call_count == 0)

# ═════════════════════════════════════════════════════════════════════════════
# 情境 7：條件 E 擋住（price < vwap）
# ═════════════════════════════════════════════════════════════════════════════
section("情境7：條件E擋住（price < vwap）")
log_calls.clear()
s7 = make_state(trigger_lot=50)
# 先灌高價 tick 拉高 vwap，再用漲停價嘗試進場
api7 = make_api()

events7 = [
    # 先用高價 tick 把 vwap 拉到 155
    tick(0, 155.0, 100, 2),   # 內盤，不觸發條件C，但更新 vwap
    tick(0.1, 155.0, 100, 2),
    bidask(1, ask_vol_at_lup=40, bid_vol_at_lup=300),
    # 再用漲停價外盤累積條件C
    tick(2, LUP, 10, 1),
    tick(3, LUP, 10, 1),
    tick(4, LUP, 10, 1),
    tick(5, LUP, 10, 1),
    tick(6, LUP, 10, 1),
    tick(7, LUP, 10, 1),   # 四條件成立，但 price(153) < vwap(~155) → 條件E擋住
]

run_sequence(s7, api7, events7)

check("情境7：條件E擋住，未進場",    not s7.bought)
check("情境7：place_order未呼叫",   api7.place_order.call_count == 0)
check("情境7：vwap > LUP",          s7.vwap > LUP,
      f"vwap={s7.vwap:.2f}")

# ═════════════════════════════════════════════════════════════════════════════
print(f"\n{'═'*60}")
print(f"結果：{PASS} 通過 / {FAIL} 失敗")
sys.exit(0 if FAIL == 0 else 1)
