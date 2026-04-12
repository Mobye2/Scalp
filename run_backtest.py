"""
run_backtest.py — 回測執行入口

說明：
  1. 登入 Shioaji（模擬模式，只需行情權限）
  2. 準備回測標的清單（需手動填入當日漲停價與參考價）
  3. 執行回測，輸出結果 CSV

使用方式：
  python run_backtest.py

⚠️ 漲停價與參考價需自行查詢（可從 Goodinfo / CMoney / TWSE 歷史資料取得）
   或在盤前用 api.Contracts.Stocks[stock_id].limit_up 取得當日值後存檔備用
"""

import os
import calendar

import pandas as pd
import requests
import shioaji as sj
from dotenv import load_dotenv

from backtest import run_backtest
from strategy import get_tick_size

load_dotenv()


def resolve_targets(simple_targets: list[dict]) -> list[dict]:
    """
    將只有 stock_id + date 的簡化格式，自動補充 limit_up 與 reference。
    用 FinMind 查詢指定日期的前一交易日收盤價，計算漲停價。
    """
    # 收集所有需要查詢的 (stock_id, 年, 月) 組合，批次拉取減少 API 呼叫
    needed: dict[str, pd.DataFrame] = {}
    for t in simple_targets:
        if "limit_up" in t and "reference" in t:
            continue  # 已有完整資料，跳過
        sid = t["stock_id"]
        if sid not in needed:
            needed[sid] = _fetch_all_prices(sid, simple_targets)

    result = []
    for t in simple_targets:
        if "limit_up" in t and "reference" in t:
            result.append(t)
            continue

        sid  = t["stock_id"]
        date = t["date"]
        df   = needed.get(sid, pd.DataFrame())

        if df.empty:
            print(f"  [{sid}] 無法取得價格資料，跳過 {date}")
            continue

        # 找指定日期的前一交易日收盤價作為 reference
        df_sorted = df.sort_values("date")
        idx = df_sorted[df_sorted["date"] == date].index
        if idx.empty:
            print(f"  [{sid}] FinMind 無 {date} 資料，跳過")
            continue

        pos = df_sorted.index.get_loc(idx[0])
        if pos == 0:
            print(f"  [{sid}] {date} 無前一交易日資料，跳過")
            continue

        prev_close   = float(df_sorted.iloc[pos - 1]["close"])
        raw_limit_up = prev_close * 1.1
        tick_size    = get_tick_size(raw_limit_up)
        limit_up     = round(round(raw_limit_up / tick_size) * tick_size, 2)

        result.append({
            "stock_id":  sid,
            "date":      date,
            "limit_up":  limit_up,
            "reference": prev_close,
        })
        print(f"  [{sid} {date}] 自動補充: limit_up={limit_up}, reference={prev_close}")

    return result


def _fetch_all_prices(stock_id: str, targets: list[dict]) -> pd.DataFrame:
    """一次拉取該股票所有回測日期涵蓋月份的收盤資料"""
    import time
    dates = [t["date"] for t in targets if t["stock_id"] == stock_id]
    if not dates:
        return pd.DataFrame()

    # 取最早日期的前一個月到最晚日期
    min_date = min(dates)
    max_date = max(dates)
    # 往前多拉一個月保證能找到前一交易日
    from datetime import datetime, timedelta
    start = (datetime.strptime(min_date, "%Y-%m-%d") - timedelta(days=35)).strftime("%Y-%m-%d")

    resp = requests.get(
        "https://api.finmindtrade.com/api/v4/data",
        params={"dataset": "TaiwanStockPrice", "data_id": stock_id,
                "start_date": start, "end_date": max_date},
        timeout=15,
    )
    data = resp.json()
    if data.get("status") != 200 or not data.get("data"):
        return pd.DataFrame()
    return pd.DataFrame(data["data"])[["date", "close"]].sort_values("date").reset_index(drop=True)


def main():
    # ── 登入（只需行情，不需憑證）────────────────────────────────────────────
    api = sj.Shioaji(simulation=False)  # 歷史資料需正式環境
    api.login(
        api_key=os.environ["API_KEY"],
        secret_key=os.environ["SECRET_KEY"],
        contracts_timeout=10_000,
        fetch_contract=True,
    )
    print("登入成功")

    # ── 回測標的清單 ──────────────────────────────────────────────────────────
    # 可以只填 stock_id + date，不需要手動查 limit_up 與 reference
    targets = [
    {"stock_id": "1569", "date": "2026-04-10", "limit_up": 56.1, "reference": 51.0},  # 濱川
    {"stock_id": "6291", "date": "2026-04-10", "limit_up": 397.5, "reference": 361.5},  # 沛亨
    {"stock_id": "6291", "date": "2026-03-11", "limit_up": 291.5, "reference": 265.0},  # 沛亨
    {"stock_id": "6291", "date": "2026-03-12", "limit_up": 320.5, "reference": 291.5},  # 沛亨
    {"stock_id": "6291", "date": "2026-02-11", "limit_up": 276.5, "reference": 251.5},  # 沛亨
    {"stock_id": "6291", "date": "2026-02-23", "limit_up": 304.0, "reference": 276.5},  # 沛亨
    {"stock_id": "2413", "date": "2026-04-10", "limit_up": 53.6, "reference": 48.75},  # 環科
    {"stock_id": "2413", "date": "2026-03-05", "limit_up": 51.9, "reference": 47.2},  # 環科
    {"stock_id": "2413", "date": "2026-03-26", "limit_up": 59.7, "reference": 54.3},  # 環科
    {"stock_id": "2413", "date": "2026-02-03", "limit_up": 44.55, "reference": 40.5},  # 環科
    {"stock_id": "2413", "date": "2026-02-10", "limit_up": 43.65, "reference": 39.7},  # 環科
    {"stock_id": "2413", "date": "2026-02-23", "limit_up": 45.65, "reference": 41.5},  # 環科
    {"stock_id": "2413", "date": "2026-02-24", "limit_up": 50.2, "reference": 45.65},  # 環科
    {"stock_id": "2413", "date": "2026-02-25", "limit_up": 55.2, "reference": 50.2},  # 環科
    {"stock_id": "2413", "date": "2026-01-12", "limit_up": 47.3, "reference": 43.0},  # 環科
    {"stock_id": "8147", "date": "2026-04-10", "limit_up": 155.5, "reference": 141.5},  # 正淩
    {"stock_id": "8147", "date": "2026-02-04", "limit_up": 117.5, "reference": 107.0},  # 正淩
    {"stock_id": "8147", "date": "2026-02-09", "limit_up": 132.0, "reference": 120.0},  # 正淩
    {"stock_id": "3645", "date": "2026-04-08", "limit_up": 76.4, "reference": 69.5},  # 達邁
    {"stock_id": "3645", "date": "2026-02-26", "limit_up": 65.3, "reference": 59.4},  # 達邁
    {"stock_id": "3645", "date": "2026-01-26", "limit_up": 73.0, "reference": 66.4},  # 達邁
    {"stock_id": "4973", "date": "2026-04-07", "limit_up": 74.8, "reference": 68.0},  # 廣穎
    {"stock_id": "4973", "date": "2026-04-08", "limit_up": 76.2, "reference": 69.3},  # 廣穎
    {"stock_id": "4973", "date": "2026-04-10", "limit_up": 78.4, "reference": 71.3},  # 廣穎
    {"stock_id": "4973", "date": "2026-03-13", "limit_up": 67.2, "reference": 61.1},  # 廣穎
    {"stock_id": "4973", "date": "2026-03-16", "limit_up": 73.9, "reference": 67.2},  # 廣穎
    {"stock_id": "4973", "date": "2026-03-18", "limit_up": 89.3, "reference": 81.2},  # 廣穎
    {"stock_id": "4973", "date": "2026-03-19", "limit_up": 98.2, "reference": 89.3},  # 廣穎
    {"stock_id": "4973", "date": "2026-03-30", "limit_up": 67.3, "reference": 61.2},  # 廣穎
    {"stock_id": "4973", "date": "2026-02-09", "limit_up": 45.9, "reference": 41.75},  # 廣穎
    {"stock_id": "4973", "date": "2026-01-07", "limit_up": 44.1, "reference": 40.1},  # 廣穎
    {"stock_id": "4973", "date": "2026-01-08", "limit_up": 48.5, "reference": 44.1},  # 廣穎
    {"stock_id": "4973", "date": "2026-01-16", "limit_up": 53.0, "reference": 48.2},  # 廣穎
    {"stock_id": "4973", "date": "2026-01-19", "limit_up": 58.3, "reference": 53.0},  # 廣穎
    {"stock_id": "6658", "date": "2026-04-10", "limit_up": 82.6, "reference": 75.1},  # 聯策
    {"stock_id": "4977", "date": "2026-03-11", "limit_up": 166.0, "reference": 151.0},  # 眾達-KY
    {"stock_id": "4977", "date": "2026-03-13", "limit_up": 187.0, "reference": 170.0},  # 眾達-KY
    {"stock_id": "4977", "date": "2026-03-20", "limit_up": 211.0, "reference": 192.0},  # 眾達-KY
    {"stock_id": "4977", "date": "2026-03-25", "limit_up": 199.5, "reference": 181.5},  # 眾達-KY
    {"stock_id": "4977", "date": "2026-02-24", "limit_up": 143.5, "reference": 130.5},  # 眾達-KY
    {"stock_id": "4977", "date": "2026-02-26", "limit_up": 173.0, "reference": 157.5},  # 眾達-KY
    {"stock_id": "4977", "date": "2026-01-28", "limit_up": 138.0, "reference": 125.5},  # 眾達-KY
    {"stock_id": "3305", "date": "2026-01-12", "limit_up": 121.5, "reference": 110.5},  # 昇貿
    {"stock_id": "3581", "date": "2026-02-25", "limit_up": 71.7, "reference": 65.2},  # 博磊
    {"stock_id": "6532", "date": "2026-03-05", "limit_up": 59.5, "reference": 54.1},  # 瑞耘
    {"stock_id": "6532", "date": "2026-03-13", "limit_up": 72.9, "reference": 66.3},  # 瑞耘
    {"stock_id": "4979", "date": "2026-03-25", "limit_up": 425.5, "reference": 387.0},  # 華星光
    {"stock_id": "4979", "date": "2026-02-23", "limit_up": 357.5, "reference": 325.0},  # 華星光
    {"stock_id": "7744", "date": "2026-02-06", "limit_up": 363.0, "reference": 330.0},  # 崴寶
    {"stock_id": "2329", "date": "2026-04-08", "limit_up": 54.3, "reference": 49.4},  # 華泰
    {"stock_id": "2329", "date": "2026-03-11", "limit_up": 54.7, "reference": 49.75},  # 華泰
    {"stock_id": "2329", "date": "2026-03-20", "limit_up": 66.3, "reference": 60.3},  # 華泰

        # 也可以手動指定，就不會再查 FinMind
        # {"stock_id": "2330", "date": "2024-03-15", "limit_up": 820.0, "reference": 745.5},
    ]

    if not targets:
        print("\n請在 targets 清單中填入回測標的後再執行")
        api.logout()
        return

    # 自動補充缺少的 limit_up / reference
    print("\n查詢漲停價與參考價...")
    targets = resolve_targets(targets)

    # ── 執行回測 ──────────────────────────────────────────────────────────────
    result_df = run_backtest(api, targets)

    # ── 儲存結果 ──────────────────────────────────────────────────────────────
    if not result_df.empty:
        output_path = "backtest_result.csv"
        result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"結果已儲存至 {output_path}")

        # 顯示明細
        print("\n交易明細：")
        display_cols = ["stock_id", "date", "entry_price", "exit_price", "next_open", "exit_reason", "net_pnl"]
        print(result_df[display_cols].to_string(index=False))

    api.logout()


if __name__ == "__main__":
    main()
