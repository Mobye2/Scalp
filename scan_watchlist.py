"""
scan_watchlist.py
盤後執行（14:30 後），維護本地 K 棒快取並篩選隔日追蹤清單。

流程：
  1. 對每檔股票檢查 SQLite 內最新 K 棒日期
     - 資料足夠且已是最新 → 跳過
     - 只差一個交易日     → 只抓一根補上
     - 資料不足或差超過一天 → 重抓 30 日
  2. 從 SQLite 讀取最近 30 根 K 棒做篩選
  3. 通過條件的股票輸出至 watchlist.csv

用法：
  python scan_watchlist.py          # 全市場
  python scan_watchlist.py --debug  # 只跑前 10 檔
"""

import os
import re
import sys
import time
import sqlite3
import logging
from datetime import date, timedelta

import pandas as pd
import shioaji as sj
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── 常數 ──────────────────────────────────────────────────────────────────────
KBAR_DAYS      = 35
MIN_BARS       = 20
DB_PATH        = os.path.join(os.path.dirname(__file__), "kbar_cache.db")
CSV_PATH       = os.path.join(os.path.dirname(__file__), "watchlist.csv")
FOUR_DIGIT_RE  = re.compile(r"^\d{4}$")
DEBUG_LIMIT    = 500

# ── 篩選參數 ──────────────────────────────────────────────────────────────────
PRICE_LOW      = 50.0
PRICE_HIGH     = 500.0
MIN_AMOUNT     = 1e8
MIN_VOLUME     = 5000
MIN_CHANGE_PCT = 3.0
VOL_RATIO      = 1.3
MA5_BIAS_MAX   = 10.0
CLOSE_STRENGTH = 0.7


# ── 日期工具 ──────────────────────────────────────────────────────────────────

def last_trading_day() -> date:
    """最近一個交易日（未處理國定假日）"""
    today = date.today()
    wd = today.weekday()
    if wd == 5:
        return today - timedelta(days=1)
    if wd == 6:
        return today - timedelta(days=2)
    return today


def prev_trading_day(d: date) -> date:
    """前一個交易日（跳過週末，未處理國定假日）"""
    d -= timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


# ── SQLite ────────────────────────────────────────────────────────────────────

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kbars (
            stock_id  TEXT NOT NULL,
            ts        TEXT NOT NULL,
            open      REAL,
            high      REAL,
            low       REAL,
            close     REAL,
            volume    INTEGER,
            PRIMARY KEY (stock_id, ts)
        )
    """)
    conn.commit()
    return conn


def get_latest_date(conn: sqlite3.Connection, stock_id: str) -> date | None:
    """回傳該股在 DB 內最新一根 K 棒的日期，無資料回傳 None"""
    row = conn.execute(
        "SELECT MAX(ts) FROM kbars WHERE stock_id = ?", (stock_id,)
    ).fetchone()
    if row and row[0]:
        return date.fromisoformat(row[0][:10])
    return None


def get_bar_count(conn: sqlite3.Connection, stock_id: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) FROM kbars WHERE stock_id = ?", (stock_id,)
    ).fetchone()
    return row[0] if row else 0


def upsert_kbars(conn: sqlite3.Connection, stock_id: str, df: pd.DataFrame) -> None:
    """將 DataFrame 寫入 DB，重複的 (stock_id, ts) 會覆蓋"""
    rows = [
        (stock_id, r["ts"].strftime("%Y-%m-%d"),
         r["Open"], r["High"], r["Low"], r["Close"], int(r["Volume"]))
        for _, r in df.iterrows()
    ]
    conn.executemany("""
        INSERT OR REPLACE INTO kbars (stock_id, ts, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()


def load_kbars(conn: sqlite3.Connection, stock_id: str, n: int = 30) -> pd.DataFrame:
    """從 DB 讀取最近 n 根 K 棒"""
    rows = conn.execute("""
        SELECT ts, open, high, low, close, volume
        FROM kbars WHERE stock_id = ?
        ORDER BY ts DESC LIMIT ?
    """, (stock_id, n)).fetchall()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=["ts", "Open", "High", "Low", "Close", "Volume"])
    df["ts"] = pd.to_datetime(df["ts"])
    return df.sort_values("ts").reset_index(drop=True)


# ── Shioaji ───────────────────────────────────────────────────────────────────

def login() -> sj.Shioaji:
    api = sj.Shioaji(simulation=False)
    api.login(
        api_key=os.environ["API_KEY"],
        secret_key=os.environ["SECRET_KEY"],
        fetch_contract=True,
        contracts_timeout=30_000,
    )
    return api


def get_four_digit_stocks(api: sj.Shioaji) -> list:
    stocks = []
    for exchange in (api.Contracts.Stocks.TSE, api.Contracts.Stocks.OTC):
        for contract in exchange:
            if FOUR_DIGIT_RE.match(contract.code):
                stocks.append(contract)
    log.info("四位數股票總數：%d", len(stocks))
    return stocks


def fetch_kbars(api: sj.Shioaji, contract, start: str, end: str) -> pd.DataFrame:
    """抓分鐘K並用 groupby date 彙總成日K"""
    try:
        kbars = api.kbars(contract=contract, start=start, end=end)
        if not kbars.ts:
            return pd.DataFrame()
        df = pd.DataFrame({**kbars})
        df["ts"] = pd.to_datetime(df["ts"])
        df["date"] = df["ts"].dt.date

        # 用實際有資料的日期 groupby，自然跳過假日，不依賴日曆
        daily = df.groupby("date").agg(
            Open=("Open", "first"),
            High=("High", "max"),
            Low=("Low", "min"),
            Close=("Close", "last"),
            Volume=("Volume", "sum"),
        ).reset_index()
        daily.rename(columns={"date": "ts"}, inplace=True)
        daily["ts"] = pd.to_datetime(daily["ts"])
        return daily.sort_values("ts").reset_index(drop=True)
    except Exception as e:
        log.debug("kbars 失敗 %s: %s", contract.code, e)
        return pd.DataFrame()


# ── 快取更新邏輯 ──────────────────────────────────────────────────────────────

def update_cache(api: sj.Shioaji, conn: sqlite3.Connection,
                 contract, today: date) -> str:
    """
    檢查並更新單一股票的 K 棒快取。
    回傳操作類型：'skip' | 'append' | 'full' | 'empty'
    """
    stock_id   = contract.code
    latest     = get_latest_date(conn, stock_id)
    bar_count  = get_bar_count(conn, stock_id)

    # 已是最新且資料足夠 → 跳過
    if latest == today and bar_count >= MIN_BARS:
        return "skip"

    # 只差一個交易日且資料足夠 → 只補一根
    if latest == prev_trading_day(today) and bar_count >= MIN_BARS:
        df = fetch_kbars(api, contract,
                         today.strftime("%Y-%m-%d"),
                         today.strftime("%Y-%m-%d"))
        if not df.empty:
            upsert_kbars(conn, stock_id, df)
        return "append"

    # 其他情況（首次、資料不足、差超過一天）→ 重抓 30 日
    start = (today - timedelta(days=KBAR_DAYS)).strftime("%Y-%m-%d")
    end   = today.strftime("%Y-%m-%d")
    df = fetch_kbars(api, contract, start, end)
    if df.empty:
        return "empty"
    upsert_kbars(conn, stock_id, df)
    return "full"


# ── 篩選 ──────────────────────────────────────────────────────────────────────

def calc_close_strength(row: pd.Series) -> float:
    rng = row["High"] - row["Low"]
    return 1.0 if rng == 0 else (row["Close"] - row["Low"]) / rng


def screen(df: pd.DataFrame, contract, verbose: bool = False) -> dict | None:
    code = contract.code

    def reject(reason: str):
        if verbose:
            log.info("  ✗ %s  %s", code, reason)
        return None

    if len(df) < MIN_BARS:
        return reject(f"K棒不足 {len(df)}<{MIN_BARS}")

    last  = df.iloc[-1]
    prev  = df.iloc[-2]

    close  = last["Close"]
    volume = last["Volume"]

    if not (PRICE_LOW < close < PRICE_HIGH):
        return reject(f"股價 {close} 不在 {PRICE_LOW}~{PRICE_HIGH}")

    amount = close * volume * 1000
    if amount < MIN_AMOUNT and volume < MIN_VOLUME:
        return reject(f"流動性不足 amount={amount/1e6:.1f}M vol={volume}")

    change_pct = (close - prev["Close"]) / prev["Close"] * 100
    if change_pct < MIN_CHANGE_PCT:
        return reject(f"漲幅 {change_pct:.2f}% < {MIN_CHANGE_PCT}%")

    closes     = df["Close"]
    ma5        = closes.rolling(5).mean()
    ma20       = closes.rolling(20).mean()
    ma5_today  = ma5.iloc[-1]
    ma5_prev   = ma5.iloc[-2]
    ma20_today = ma20.iloc[-1]

    if pd.isna(ma5_today) or pd.isna(ma5_prev) or pd.isna(ma20_today):
        return reject("MA 計算失敗")

    if close <= ma5_today:
        return reject(f"收盤 {close} <= 5MA {ma5_today:.2f}")
    if ma5_today <= ma5_prev:
        return reject(f"5MA 未向上 {ma5_today:.2f} <= {ma5_prev:.2f}")
    if close <= ma20_today:
        return reject(f"收盤 {close} <= 20MA {ma20_today:.2f}")

    vol_ma5 = df["Volume"].rolling(5).mean().iloc[-2]
    if pd.isna(vol_ma5) or volume < VOL_RATIO * vol_ma5:
        return reject(f"量比不足 {volume}/{vol_ma5:.0f}={volume/(vol_ma5 or 1):.2f}x")

    bias = (close - ma5_today) / ma5_today * 100
    if bias >= MA5_BIAS_MAX:
        return reject(f"5MA乖離 {bias:.2f}% >= {MA5_BIAS_MAX}%")

    strength = calc_close_strength(last)
    if strength < CLOSE_STRENGTH:
        return reject(f"收盤強度 {strength:.3f} < {CLOSE_STRENGTH}")

    # 條件 C 動態門檻：過去 5 日均日成交金額 × 1.5%，保底 500 萬
    daily_amounts = df["Close"] * df["Volume"] * 1000
    avg_5d_amount = daily_amounts.iloc[-6:-1].mean()  # 不含今日，取前5日
    large_order_amount = max(avg_5d_amount * 0.015, 5_000_000)

    return {
        "stock_id":           contract.code,
        "name":               contract.name,
        "close":              round(close, 2),
        "change_pct":         round(change_pct, 2),
        "volume":             int(volume),
        "amount_m":           round(amount / 1e6, 1),
        "ma5":                round(ma5_today, 2),
        "ma20":               round(ma20_today, 2),
        "strength":           round(strength, 3),
        "large_order_amount": round(large_order_amount, 0),
    }


# ── 主流程 ────────────────────────────────────────────────────────────────────

def run(debug: bool = False):
    today = last_trading_day()
    log.info("掃描日期：%s", today)

    api  = login()
    conn = get_conn()

    contracts = get_four_digit_stocks(api)
    if debug:
        contracts = contracts[:DEBUG_LIMIT]
        log.info("[DEBUG] 只跑前 %d 檔：%s", DEBUG_LIMIT, [c.code for c in contracts])

    stats   = {"skip": 0, "append": 0, "full": 0, "empty": 0}
    results = []
    total   = len(contracts)

    for i, contract in enumerate(contracts, 1):
        op = update_cache(api, conn, contract, today)
        stats[op] += 1

        if op != "empty":
            df  = load_kbars(conn, contract.code)
            row = screen(df, contract, verbose=debug)
            if row:
                results.append(row)
                log.info("✓ %s %s  漲幅%.1f%%  量比%.1fx",
                         contract.code, contract.name,
                         row["change_pct"],
                         row["volume"] / (df["Volume"].rolling(5).mean().iloc[-2] or 1))

        if debug and op != "skip":
            latest = get_latest_date(conn, contract.code)
            log.info("[DEBUG] %s  op=%-6s  DB最新=%s  筆數=%d",
                     contract.code, op, latest,
                     get_bar_count(conn, contract.code))

        # API 速率控制
        if op in ("append", "full"):
            time.sleep(0.12)
        if i % 50 == 0:
            log.info("進度 %d / %d  (skip=%d append=%d full=%d empty=%d)",
                     i, total, stats["skip"], stats["append"], stats["full"], stats["empty"])

    api.logout()
    conn.close()

    log.info("快取更新完成：skip=%d append=%d full=%d empty=%d",
             stats["skip"], stats["append"], stats["full"], stats["empty"])

    if not results:
        log.warning("篩選結果為空（%s）", today)
        return

    out = pd.DataFrame(results).sort_values("change_pct", ascending=False)
    out.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    log.info("完成！共 %d 檔，已存至 %s", len(out), CSV_PATH)
    print(out.to_string(index=False))


if __name__ == "__main__":
    run(debug="--debug" in sys.argv)
