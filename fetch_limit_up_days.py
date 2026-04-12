"""
fetch_limit_up_days.py — 查詢歷史漲停日（使用 FinMind API）

說明：
  從 watchlist.csv 讀取監控清單，查詢曾觸及漲停的交易日，
  產生 run_backtest.py 所需的 targets 清單。

使用方式：
  python fetch_limit_up_days.py

watchlist.csv 格式：
  stock_id,name,...（只需要 stock_id 欄位，name 欄位選填）
"""

import calendar
import time

import pandas as pd
import requests

from strategy import get_tick_size

FINMIND_URL = "https://api.finmindtrade.com/api/v4/data"


def fetch_monthly_price(stock_id: str, year: int, month: int) -> pd.DataFrame:
    """用 FinMind API 取得指定股票整月每日 OHLC 資料"""
    _, last_day = calendar.monthrange(year, month)
    start = f"{year}-{month:02d}-01"
    end   = f"{year}-{month:02d}-{last_day:02d}"
    resp = requests.get(
        FINMIND_URL,
        params={"dataset": "TaiwanStockPrice", "data_id": stock_id,
                "start_date": start, "end_date": end},
        timeout=15,
    )
    data = resp.json()
    if data.get("status") != 200 or not data.get("data"):
        return pd.DataFrame()
    df = pd.DataFrame(data["data"])[["date", "open", "max", "close"]]
    df = df.rename(columns={"max": "high"})
    return df.sort_values("date").reset_index(drop=True)


def find_limit_up_days(stock_id: str, year: int, month: int) -> list[dict]:
    """
    找出指定月份「曾經觸及漲停」的交易日（最高價 == 漲停價）。
    不要求收盤在漲停，只要盤中曾觸及漲停即列入。
    """
    df = fetch_monthly_price(stock_id, year, month)
    if df.empty:
        return []

    targets = []
    for i in range(1, len(df)):
        prev_close = df.iloc[i - 1]["close"]
        curr       = df.iloc[i]

        raw_limit_up = prev_close * 1.1
        tick_size    = get_tick_size(raw_limit_up)
        limit_up     = round(round(raw_limit_up / tick_size) * tick_size, 2)

        if abs(curr["high"] - limit_up) < tick_size * 0.5:
            targets.append({
                "stock_id":  stock_id,
                "date":      curr["date"],
                "limit_up":  limit_up,
                "reference": float(prev_close),
            })

    return targets


def main():
    # ── 從 watchlist.csv 讀取監控清單 ────────────────────────────────────
    watchlist_path = "watchlist.csv"
    wl = pd.read_csv(watchlist_path, dtype={"stock_id": str})
    watchlist = wl["stock_id"].tolist()
    name_map  = dict(zip(wl["stock_id"].astype(str), wl["name"])) if "name" in wl.columns else {}
    print(f"讀取 {watchlist_path}，共 {len(watchlist)} 檔股票")

    # ── 查詢月份範圍 ──────────────────────────────────────────────────────
    year_months = [
        (2026, 4), (2026, 3), (2026, 2), (2026, 1),
    ]

    all_targets = []
    for stock_id in watchlist:
        for year, month in year_months:
            name = name_map.get(stock_id, "")
            print(f"查詢 {stock_id} {name} {year}/{month:02d}...")
            targets = find_limit_up_days(stock_id, year, month)
            all_targets.extend(targets)
            time.sleep(0.5)

    print(f"\n共找到 {len(all_targets)} 個漲停日\n")
    print("# 貼入 run_backtest.py 的 targets 清單：")
    print("targets = [")
    for t in all_targets:
        name = name_map.get(t["stock_id"], "")
        print(f'    {{"stock_id": "{t["stock_id"]}", "date": "{t["date"]}", "limit_up": {t["limit_up"]}, "reference": {t["reference"]}}},  # {name}')
    print("]")


if __name__ == "__main__":
    main()
