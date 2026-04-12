import math, pandas as pd, datetime, os
import shioaji as sj
from dotenv import load_dotenv
from strategy import StrategyState, get_tick_size
from backtest import _simulate_bidask
from config import CFG

load_dotenv()
api = sj.Shioaji(simulation=False)
api.login(api_key=os.environ['API_KEY'], secret_key=os.environ['SECRET_KEY'], contracts_timeout=10000)

ticks = api.ticks(contract=api.Contracts.Stocks['3532'], date='2026-04-10')
df = pd.DataFrame({**ticks})
df['dt'] = pd.to_datetime(df['ts'])

state = StrategyState()
state.limit_up_price = 165.5
state.trigger_lot = math.ceil(CFG.trigger_amount * CFG.price_factor_low / (165.5 * 1000))
print(f'trigger_lot={state.trigger_lot}')

class MockTick:
    def __init__(self, r):
        self.code = '3532'
        self.datetime = r.dt.to_pydatetime()
        self.close = r.close
        self.volume = r.volume
        self.tick_type = r.tick_type

for row in df.itertuples():
    tick = MockTick(row)
    state.last_price = float(tick.close)
    state.cumulative_pv += float(tick.close) * tick.volume
    state.cumulative_vol += tick.volume
    if state.cumulative_vol > 0:
        state.vwap = state.cumulative_pv / state.cumulative_vol
    _simulate_bidask(state, tick)

    t = tick.datetime.time()
    if datetime.time(9, 17, 55) <= t <= datetime.time(9, 18, 10):
        cond_b = float(tick.close) >= state.limit_up_price - get_tick_size(state.limit_up_price)
        cond_d = state.ask_vol_at_limit_up < state.trigger_lot
        print(f'{t} close={tick.close} vol={tick.volume} type={tick.tick_type} '
              f'ask={state.ask_vol_at_limit_up:.0f} bid={state.bid_vol_at_limit_up} '
              f'B={cond_b} D={cond_d}')

api.logout()
