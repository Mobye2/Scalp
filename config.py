# config.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # ── 環境 ──────────────────────────────────────────
    stock_ids:  tuple = ("2330",)   # 監控標的清單，可放多檔
    simulation: bool  = True

    # ── 時間窗口 ──────────────────────────────────────
    entry_time_start: tuple = (9, 0, 0)   # 09:00:00
    entry_time_end:   tuple = (10, 0, 0)  # 10:00:00

    # ── 資金門檻 ──────────────────────────────────────
    large_order_amount:  float = 30_000_000   # 條件 C：10 秒內外盤累計金額門檻
    trigger_amount:      float = 30_000_000   # 條件 D / 停損 A：點火水位基準金額
    price_factor_threshold: float = 200.0     # 高價股分界
    price_factor_high:   float = 1.5          # 漲停價 ≥ 200 元時的調整係數
    price_factor_low:    float = 1.0          # 漲停價 < 200 元

    # ── 條件 C ────────────────────────────────────────
    large_window_seconds: int = 10            # 滑動窗口秒數

    # ── 停損參數 ──────────────────────────────────────
    stop_a_multiplier:   float = 3.0          # 停損 A：trigger_lot × 3
    stop_c_shrink_ratio: float = 0.30         # 停損 C：委買縮減比例門檻


CFG = Config()
