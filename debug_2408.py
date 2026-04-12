import os, math, datetime, requests
import pandas as pd
import shioaji as sj
from dotenv import load_dotenv
from strategy import StrategyState, get_tick_size, _check_entry
from backtest import _simulate_bidask
from config import CFG

load_dotenv()
api = sj.Shioaji(simulation=False)
api.login(api_key=os.environ['API_KEY'], secret_key=os.environ['SECRET_KEY'], contracts_timeout=10000)

# 查 3/25 收盤算漲停
resp = requests.get('https://api.finmindtrade.com/api/v4/data',
    params={'dataset':'TaiwanStockPrice','data_id':'2408',
            'start_date':'2026-03-20','end_date':'2026-03-26'}, timeout=15)
df_price = pd.DataFrame(resp.json()['data'])[['date','close']]
print(df_price.to_string())

prev_close = float(df_price[df_price['date'] == '2026-03-25']['close'].values[0])
raw = prev_close * 1.1
tick_size = get_tick_size(raw)
limit_up = round(round(raw / tick_size) * tick_size, 2)
print(f"\n3/25 收盤={prev_close}, 3/26 漲停={limit_up}, trigger_lot={math.ceil(CFG.trigger_amount / (limit_up * 1000))}")

# 拉 tick
ticks = api.ticks(contract=api.Contracts.Stocks['2408'], date='2026-03-26')
df = pd.DataFrame({**ticks})
df['dt'] = pd.to_datetime(df['ts'])

state = StrategyState()
state.limit_up_price = limit_up
state.trigger_lot = math.ceil(CFG.trigger_amount / (limit_up * 1000))

entry_time_start = datetime.time(*CFG.entry_time_start)
entry_time_end   = datetime.time(*CFG.entry_time_end)

class MockTick:
    def __init__(self, r):
        self.code = '2408'
        self.datetime = r.dt.to_pydatetime()
        self.close = r.close
        self.volume = r.volume
        self.tick_type = r.tick_type

print(f"\n{'時間':<12} {'價格':<8} {'量':<6} {'型':<3} {'ask':<8} {'bid':<8} {'A':<3} {'B':<3} {'C金額':>14} {'D':<3}")
print("-" * 75)

for row in df.itertuples():
    tick = MockTick(row)
    state.last_price = float(tick.close)
    state.cumulative_pv  += float(tick.close) * tick.volume
    state.cumulative_vol += tick.volume
    if state.cumulative_vol > 0:
        state.vwap = state.cumulative_pv / state.cumulative_vol
    _simulate_bidask(state, tick)

    t = tick.datetime.time()
    if t < entry_time_start or t > entry_time_end:
        continue

    ts = get_tick_size(state.limit_up_price)
    cond_a = entry_time_start < t < entry_time_end
    cond_b = float(tick.close) >= state.limit_up_price - ts
    if tick.tick_type == 1:
        amt = float(tick.close) * tick.volume * 1000
        state.recent_large_window.append((tick.datetime, amt))
    cutoff = tick.datetime - datetime.timedelta(seconds=CFG.large_window_seconds)
    state.recent_large_window = [(dt, a) for dt, a in state.recent_large_window if dt > cutoff]
    window_amt = sum(a for _, a in state.recent_large_window)
    cond_c = window_amt >= CFG.large_order_amount
    cond_d = state.ask_vol_at_limit_up < state.trigger_lot

    # 只印出接近漲停或條件有變化的 tick
    if cond_b or cond_c or cond_d:
        ask_disp = f"{state.ask_vol_at_limit_up:.0f}" if state.ask_vol_at_limit_up != float('inf') else "inf"
        print(f"{t.strftime('%H:%M:%S.%f')[:12]} {float(tick.close):<8} {tick.volume:<6} {tick.tick_type:<3} "
              f"{ask_disp:<8} {state.bid_vol_at_limit_up:<8} "
              f"{'Y' if cond_a else 'N':<3} {'Y' if cond_b else 'N':<3} "
              f"{window_amt:>14,.0f} {'Y' if cond_d else 'N':<3}"
              f"{'  <<< ALL PASS' if (cond_a and cond_b and cond_c and cond_d) else ''}")

api.logout()
