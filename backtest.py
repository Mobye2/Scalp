"""
backtest.py — 漲停板掃板策略回測引擎

說明：
  使用 Shioaji api.ticks() 拉取歷史 Tick 資料，模擬 on_tick / on_bidask 事件流，
  重用 strategy.py 的進場/停損邏輯，統計每筆交易損益。

歷史資料限制：
  - Shioaji 歷史 Ticks 無 BidAsk 資料，改用以下規則模擬：
    * ask_vol_at_limit_up：若 tick_type==2（內盤）且 close==limit_up，視為有賣壓，
      設為 tick.volume；否則設為 0（門關上）
    * bid_vol_at_limit_up：若 tick_type==1（外盤）且 close==limit_up，
      設為 tick.volume * 5（估算排隊量）；否則設為 0

⚠️ 注意：
  - 歷史 BidAsk 為估算值，與實際盤中委買委賣量有差異，停損 A/C 準確度受限
  - 成交假設：進場以 limit_up_price 成交（限價單），出場以下一筆 tick.close 成交（市價模擬）
  - 手續費：買賣各 0.1425%；交易稅：賣出 0.3%
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Optional

import pandas as pd
import shioaji as sj

from config import CFG
from strategy import (
    StrategyState,
    _check_entry,
    _check_stop_loss,
    _reset_after_exit,
    get_limit_up_price,
    get_tick_size,
    init_state,
)


# ── 費用計算 ──────────────────────────────────────────────────────────────────

BROKERAGE_RATE = 0.001425  # 手續費（買賣各）
TAX_RATE       = 0.003     # 證券交易稅（賣出）
LOT_SIZE       = 1_000     # 1 張 = 1000 股


def calc_net_pnl(buy_price: float, sell_price: float, quantity: int = 1) -> float:
    """計算扣除手續費與交易稅後的淨損益（元）"""
    buy_cost  = buy_price  * quantity * LOT_SIZE
    sell_cost = sell_price * quantity * LOT_SIZE
    fee_buy   = buy_cost  * BROKERAGE_RATE
    fee_sell  = sell_cost * BROKERAGE_RATE
    tax_sell  = sell_cost * TAX_RATE
    return sell_cost - buy_cost - fee_buy - fee_sell - tax_sell


# ── 回測結果 ──────────────────────────────────────────────────────────────────

@dataclass
class TradeRecord:
    stock_id:    str
    date:        str
    entry_time:  datetime
    exit_time:   Optional[datetime]
    entry_price: float
    exit_price:  float
    exit_reason: str
    gross_pnl:   float           # 未扣費
    net_pnl:     float           # 扣費後
    next_open:   Optional[float] = None  # 隔日開盤價（收盤出場時補充）


# ── 模擬 BidAsk（歷史資料無法取得真實委買委賣）────────────────────────────────

def _simulate_bidask(state: StrategyState, tick) -> None:
    """
    用 tick 資料估算 ask_vol / bid_vol at limit_up。

    設計原則：
      歷史 tick 無真實委買委賣量，只能用成交方向推斷趨勢。
      重點是讓條件 D（點火水位）和停損 A（委賣壓頂）能合理觸發，
      停損 C（委買撤退）在鎖板期間不應誤觸。

    規則：
      - 外盤在漲停：ask 被消耗，累計遞減；bid 累計遞增（排隊買）
      - 內盤在漲停：有人賣出，ask 增加；bid 不變（撤退由連續內盤判斷）
      - 離漲停：重置為初始值
    """
    close = float(tick.close)
    tick_size = get_tick_size(state.limit_up_price)

    if close >= state.limit_up_price - tick_size:
        if tick.tick_type == 1:  # 外盤：主動買，ask 被消耗，bid 排隊累積
            if state.ask_vol_at_limit_up == float('inf'):
                # 第一次接近漲停：用此筆外盤成交量估算初始委賣量
                # 這筆大量外盤通常就是在掴委賣，成交量即為被吃掉的委賣量
                state.ask_vol_at_limit_up = tick.volume
            else:
                state.ask_vol_at_limit_up = max(0, state.ask_vol_at_limit_up - tick.volume)
            state.bid_vol_at_limit_up += tick.volume
        elif tick.tick_type == 2:  # 內盤：有人賣，ask 增加
            if state.ask_vol_at_limit_up == float('inf'):
                state.ask_vol_at_limit_up = tick.volume
            else:
                state.ask_vol_at_limit_up += tick.volume
    else:
        # 離漲停：尚未進場時才重置，持倉期間保留最後狀態
        if not state.bought:
            state.ask_vol_at_limit_up = float('inf')
            state.bid_vol_at_limit_up = 0

    # 更新持倉後的委買峰值
    if state.bought and state.bid_vol_at_limit_up > state.peak_bid_vol:
        state.peak_bid_vol = state.bid_vol_at_limit_up


# ── 單日單檔回測 ──────────────────────────────────────────────────────────────

def backtest_one_day(
    api: sj.Shioaji,
    stock_id: str,
    date: str,
    limit_up_price: float,
    reference_price: float,
) -> Optional[TradeRecord]:
    """
    對單一股票單一交易日執行回測。
    回傳 TradeRecord（有交易）或 None（未觸發進場）。
    """
    # 取得當日全部 ticks
    contract = api.Contracts.Stocks[stock_id]
    ticks = api.ticks(contract=contract, date=date)
    if not ticks or not ticks.ts:
        print(f"  [{stock_id} {date}] 無 tick 資料，跳過")
        return None

    df = pd.DataFrame({**ticks})
    df["dt"] = pd.to_datetime(df["ts"])

    # 初始化狀態（用傳入的漲停價，不依賴 contract.limit_up 當日值）
    state = StrategyState()
    state.limit_up_price = limit_up_price
    price_factor = (
        CFG.price_factor_high
        if limit_up_price >= CFG.price_factor_threshold
        else CFG.price_factor_low
    )
    state.trigger_lot = math.ceil(
        CFG.trigger_amount * price_factor / (limit_up_price * 1_000)
    )

    entry_price: Optional[float] = None
    entry_time:  Optional[datetime] = None
    entry_idx:   int = -1
    exit_price:  Optional[float] = None
    exit_time:   Optional[datetime] = None
    exit_reason: str = ""

    ticks_list = list(df.itertuples())

    for i, row in enumerate(ticks_list):
        # 建立 mock tick 物件（只用到 strategy.py 需要的欄位）
        class MockTick:
            def __init__(self, r):
                self.code      = stock_id
                self.datetime  = r.dt.to_pydatetime()
                self.close     = r.close
                self.volume    = r.volume
                self.tick_type = r.tick_type

        tick = MockTick(row)

        # 更新 VWAP
        state.last_price     = float(tick.close)
        state.cumulative_pv  += float(tick.close) * tick.volume
        state.cumulative_vol += tick.volume
        if state.cumulative_vol > 0:
            state.vwap = state.cumulative_pv / state.cumulative_vol

        # 模擬 BidAsk（歷史無真實委買委賣）
        _simulate_bidask(state, tick)

        if state.bought:
            state.cumulative_trade_after_buy += tick.volume

            # 進場當筆不做停損，從下一筆開始
            if i == entry_idx:
                continue

            stop_reason = _check_stop_loss_backtest(state, stock_id)
            if stop_reason:
                tick_size = get_tick_size(state.limit_up_price)
                exit_price = None
                for j in range(i + 1, min(i + 50, len(ticks_list))):
                    candidate = float(ticks_list[j].close)
                    if candidate < state.limit_up_price - tick_size * 0.5:
                        exit_price = candidate
                        break
                if exit_price is None:
                    next_idx = i + 1
                    exit_price = float(ticks_list[next_idx].close) if next_idx < len(ticks_list) else float(tick.close)
                exit_time   = tick.datetime
                exit_reason = stop_reason

                # 出場參數明細
                shrink     = state.peak_bid_vol - state.bid_vol_at_limit_up
                shrink_pct = shrink / state.peak_bid_vol * 100 if state.peak_bid_vol > 0 else 0
                print(
                    f"  [{stock_id} {date}] 出場 @ {exit_price} | {exit_time.strftime('%H:%M:%S')} | {stop_reason}\n"
                    f"    停損A ask_vol: {state.ask_vol_at_limit_up} vs 門檻 {state.trigger_lot * CFG.stop_a_multiplier:.0f} (trigger_lot {state.trigger_lot} x {CFG.stop_a_multiplier})\n"
                    f"    停損B last_price: {state.last_price} vs VWAP {state.vwap:.2f}\n"
                    f"    停損C bid縮減: {shrink_pct:.1f}% (peak {state.peak_bid_vol} → {state.bid_vol_at_limit_up}) vs 門檻 {CFG.stop_c_shrink_ratio*100:.0f}% | 縮減量 {shrink} vs 買後成交 {state.cumulative_trade_after_buy}"
                )
                _reset_after_exit(state)
                break

        elif _check_entry(state, tick):
            entry_price    = state.limit_up_price
            entry_time     = tick.datetime
            entry_idx      = i
            state.bought      = True
            state.bought_time = tick.datetime
            state.peak_bid_vol = state.bid_vol_at_limit_up

            # 計算條件 C 當下窗口金額
            window_amount = sum(amt for _, amt in state.recent_large_window)
            tick_size = get_tick_size(state.limit_up_price)
            print(
                f"  [{stock_id} {date}] 進場 @ {entry_price} | {entry_time.strftime('%H:%M:%S')}\n"
                f"    條件A 時間: {entry_time.strftime('%H:%M:%S')} in ({CFG.entry_time_start}~{CFG.entry_time_end})\n"
                f"    條件B 價格: {float(tick.close)} >= 漲停-1檔 {state.limit_up_price - tick_size:.2f}\n"
                f"    條件C 10秒外盤金額: {window_amount:,.0f} >= 門檻 {CFG.large_order_amount:,.0f}\n"
                f"    條件D ask_vol: {state.ask_vol_at_limit_up} < trigger_lot {state.trigger_lot}"
            )

    # 若持倉到收盤未停損，以最後一筆 tick 收盤價出場
    next_open: Optional[float] = None
    if state.bought and entry_price is not None and exit_price is None:
        exit_price  = float(ticks_list[-1].close)
        exit_time   = ticks_list[-1].dt.to_pydatetime()
        exit_reason = "收盤出場"

        # 查隔日開盤價，作為更真實的出場參考
        next_open = _fetch_next_open(api, stock_id, date)
        if next_open:
            # 改用隔日開盤價作為實際出場價（隔日開盤市價賣出）
            exit_price = next_open
            exit_reason = "隔日開盤出場"
            print(f"  [{stock_id} {date}] 收盤鎖板 → 隔日開盤出場 @ {next_open}")
        else:
            print(f"  [{stock_id} {date}] 收盤出場 @ {exit_price}（無隔日資料）")

    if entry_price is None or exit_price is None:
        return None

    gross_pnl = (exit_price - entry_price) * LOT_SIZE
    net_pnl   = calc_net_pnl(entry_price, exit_price)

    return TradeRecord(
        stock_id=stock_id,
        date=date,
        entry_time=entry_time,
        exit_time=exit_time,
        entry_price=entry_price,
        exit_price=exit_price,
        exit_reason=exit_reason,
        gross_pnl=gross_pnl,
        net_pnl=net_pnl,
        next_open=next_open,
    )


def _fetch_next_open(api: sj.Shioaji, stock_id: str, date: str) -> Optional[float]:
    """
    查詢指定日期的下一個交易日開盤價。
    用 api.kbars 取隔日第一根 1 分 K 的 Open。
    """
    from datetime import date as date_type, timedelta
    import time as time_module

    # 往後找最多 5 個日曆日，跳過非交易日
    base = datetime.strptime(date, "%Y-%m-%d").date()
    for delta in range(1, 6):
        next_date = base + timedelta(days=delta)
        next_str  = next_date.strftime("%Y-%m-%d")
        try:
            contract = api.Contracts.Stocks[stock_id]
            kbars = api.kbars(contract=contract, start=next_str, end=next_str)
            if kbars and kbars.ts:
                df = pd.DataFrame({**kbars})
                df["dt"] = pd.to_datetime(df["ts"])
                # 取當日第一根 K 棒的開盤價
                first_open = float(df.sort_values("dt").iloc[0]["Open"])
                return first_open
        except Exception:
            pass
        time_module.sleep(0.3)
    return None


def _check_stop_loss_backtest(state: StrategyState, stock_id: str) -> Optional[str]:
    """
    回測版停損檢查。
    停損 A 改用「進場後內盤累積量占買後成交量比例」判斷：
      歷史 tick 無真實委賣量，用連續內盤大量來估算委賣壓頂。
    """
    # 停損 A：進場後內盤累積量 > 買後成交量 * stop_a_multiplier
    # 代表有大量主動賣出，委賣壓頂
    if state.ask_vol_at_limit_up > state.trigger_lot * CFG.stop_a_multiplier:
        return "停損A：委賣壓頂"

    # 停損 B：跌破 VWAP
    if state.last_price < state.vwap:
        return "停損B：跌破VWAP"

    # 停損 C：委買撤退
    if state.peak_bid_vol > 0:
        shrink     = state.peak_bid_vol - state.bid_vol_at_limit_up
        shrink_pct = shrink / state.peak_bid_vol
        if shrink_pct > CFG.stop_c_shrink_ratio and shrink > state.cumulative_trade_after_buy:
            return "停損C：委買撤退"

    return None


# ── 批次回測 ──────────────────────────────────────────────────────────────────

def run_backtest(
    api: sj.Shioaji,
    targets: list[dict],  # [{"stock_id": "2330", "date": "2024-01-15", "limit_up": 595.0, "reference": 541.0}]
) -> pd.DataFrame:
    """
    批次執行多檔多日回測。

    targets 格式：
      [
        {"stock_id": "2330", "date": "2024-01-15", "limit_up": 595.0, "reference": 541.0},
        ...
      ]

    回傳 DataFrame，每列一筆交易紀錄。
    """
    records = []
    for t in targets:
        print(f"\n[回測] {t['stock_id']} {t['date']} | 漲停={t['limit_up']}")
        rec = backtest_one_day(
            api=api,
            stock_id=t["stock_id"],
            date=t["date"],
            limit_up_price=t["limit_up"],
            reference_price=t["reference"],
        )
        if rec:
            records.append(rec.__dict__)

    if not records:
        print("\n無任何交易紀錄")
        return pd.DataFrame()

    df = pd.DataFrame(records)
    _print_summary(df)
    return df


def _print_summary(df: pd.DataFrame) -> None:
    """印出回測統計摘要"""
    total     = len(df)
    wins      = (df["net_pnl"] > 0).sum()
    losses    = (df["net_pnl"] <= 0).sum()
    win_rate  = wins / total * 100 if total > 0 else 0
    total_pnl = df["net_pnl"].sum()
    avg_pnl   = df["net_pnl"].mean()
    max_win   = df["net_pnl"].max()
    max_loss  = df["net_pnl"].min()

    print("\n" + "=" * 50)
    print(f"  回測結果摘要（共 {total} 筆交易）")
    print("=" * 50)
    print(f"  勝率：{wins}W / {losses}L = {win_rate:.1f}%")
    print(f"  總損益（淨）：{total_pnl:,.0f} 元")
    print(f"  平均損益（淨）：{avg_pnl:,.0f} 元")
    print(f"  最大獲利：{max_win:,.0f} 元")
    print(f"  最大虧損：{max_loss:,.0f} 元")
    print("=" * 50)

    # 出場原因分布
    reason_counts = df["exit_reason"].value_counts()
    print("\n  出場原因分布：")
    for reason, cnt in reason_counts.items():
        avg = df[df["exit_reason"] == reason]["net_pnl"].mean()
        print(f"    {reason}: {cnt} 筆 | 平均淨損益 {avg:,.0f} 元")

    # 隔日開盤出場詳細
    next_open_df = df[df["exit_reason"] == "隔日開盤出場"]
    if not next_open_df.empty:
        gap_up = next_open_df[next_open_df["next_open"] > next_open_df["entry_price"]]
        gap_dn = next_open_df[next_open_df["next_open"] <= next_open_df["entry_price"]]
        print(f"\n  隔日開盤跨空高開: {len(gap_up)} 筆 | 跨空低開/平開: {len(gap_dn)} 筆")
    print()
