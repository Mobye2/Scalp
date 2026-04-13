# trade_logger.py
"""
交易紀錄模組：以 CSV 格式保存每筆進場 / 出場明細。
檔案按日期命名，例如 trades_20260413.csv，存放於 logs/ 資料夾。
"""
import csv
import threading
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_lock = threading.Lock()

# CSV 欄位定義
FIELDS = [
    "timestamp",      # 事件時間 (ISO 格式)
    "stock_id",       # 股票代碼
    "action",         # Entry / Exit
    "reason",         # 進場條件 or 停損原因
    "price",          # 當下成交價 / last_price
    "limit_up_price", # 漲停價
    "vwap",           # 當下 VWAP
    "ask_vol",        # 漲停委賣量
    "bid_vol",        # 漲停委買量
    "trigger_lot",    # 點火門檻
    "trade_count",    # 當日第幾次交易
    "peak_bid_vol",   # 持倉期間委買峰值
    "cum_trade_vol",  # 持倉期間累計成交量
    "order_status",   # 委託狀態 (Submitted/Failed/...)
]


def _get_log_path() -> Path:
    """依當日日期取得 CSV 路徑"""
    return LOG_DIR / f"trades_{datetime.now().strftime('%Y%m%d')}.csv"


def _ensure_header(path: Path) -> None:
    """若檔案不存在或為空，寫入表頭"""
    if not path.exists() or path.stat().st_size == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(FIELDS)


def log_trade(row: dict) -> None:
    """
    寫入一筆交易紀錄（thread-safe）。
    row 為 dict，key 對應 FIELDS。
    """
    path = _get_log_path()
    with _lock:
        _ensure_header(path)
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writerow(row)
