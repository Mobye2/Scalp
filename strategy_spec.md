# 漲停板掃板策略規格文件

## 盤前初始化（08:30 執行一次）

```
limit_up_price = get_limit_up_price(stock_id)

# 高價股門檻調整係數
price_factor = 1.5 if limit_up_price >= 200 else 1.0

# 點火水位（條件 D、停損 A 用）
trigger_lot = math.ceil(30_000_000 * price_factor / (limit_up_price * 1_000))

# 條件 C 累計金額門檻（動態，依個股流動性調整）
# 取過去 10 個日曆日的 1 分 K，加總每日成交金額，取最近 5 個交易日平均
avg_5d_daily_amount = 過去5交易日均日成交金額  # 元
large_order_amount = max(avg_5d_daily_amount * 0.015, 5_000_000)

# 狀態變數
ask_vol_at_limit_up        = float('inf')  # 漲停委賣量（初始設大，避免條件 D 誤觸）
bid_vol_at_limit_up        = 0             # 漲停委買量
last_price                 = 0.0          # 最新成交價
bought                     = False        # 是否已持倉
bought_time                = None         # 買進時間
peak_bid_vol               = 0            # 買進後委買峰值（停損 C 用）
cumulative_trade_after_buy = 0            # 買進後累積成交量（停損 C 用）
cumulative_pv              = 0.0          # 累積成交金額（VWAP 用）
cumulative_vol             = 0            # 累積成交量（VWAP 用）
vwap                       = 0.0          # 當日即時 VWAP
recent_large_window        = []           # 滑動 10 秒外盤大單佇列 [(datetime, amount)]
```

---

## 輔助函式

### get_tick_size(price) — 台股 tick size 查表

| 股價區間 | tick size |
|----------|-----------|
| < 10 | 0.01 |
| 10 – 50 | 0.05 |
| 50 – 100 | 0.1 |
| 100 – 500 | 0.5 |
| 500 – 1000 | 1 |
| ≥ 1000 | 5 |

---

## 進場條件（四條件同時成立）

### 條件 A｜時間濾網
- 範圍：`09:00:00 < now < 13:25:00`
- 早盤動能最強，13:25 後收盤前試搓性質不同不適用

### 條件 B｜價格位置
- 條件：`tick.close >= limit_up_price - get_tick_size(limit_up_price)`
- 最新成交價等於漲停價，或漲停價下一檔
- 確認主力正在攻擊漲停，而非隨機跳動

### 條件 C｜動能確認
- 條件：過去 10 秒內，外盤（`tick_type == 1`）成交累計金額 ≥ `large_order_amount`
- `large_order_amount = max(avg_5d_daily_amount × 1.5%, 500 萬)`
  - `avg_5d_daily_amount`：程式啟動時取過去 5 交易日平均日成交金額（元）
  - 保底 500 萬：避免冷門股門檻過低
- 金額計算：`float(tick.close) × tick.volume × 1000`（元 × 張 × 1000股/張）
- 滑動窗口：每筆 tick 加入佇列，清除 10 秒前的紀錄，加總剩餘金額
- 確認是主力連續大力敲進，過濾假大單（小量多筆）
- `tick_type == 1` = 外盤（主動買）

### 條件 D｜點火水位
- 條件：`ask_vol_at_limit_up < trigger_lot`
- 點火水位：`trigger_lot = ceil(30_000_000 × price_factor / (limit_up_price × 1000))` 張
- 漲停委賣量低於門檻，代表門即將關上

### 執行
- 送**限價單**，價格 = `limit_up_price`，數量 = 1 張
- 買進後初始化：`peak_bid_vol = bid_vol_at_limit_up`、`bought = True`、`bought_time = tick.datetime`

---

## 停損條件（三條件任一成立即出場）

### 停損 A｜委賣壓頂
- 條件：`ask_vol_at_limit_up > trigger_lot * 3`
- 漲停委賣量超過點火水位 3 倍
- 代表主力反手持續掛出大量賣單，板子被壓住

### 停損 B｜跌破 VWAP
- 條件：`last_price < vwap`
- 最新成交價跌破當日成交量加權平均價
- 多方已失守重心

### 停損 C｜委買撤退
- 條件：以下**兩者同時成立**
  1. `(peak_bid_vol - bid_vol_at_limit_up) / peak_bid_vol > 0.30`（委買從峰值縮減 > 30%）
  2. `(peak_bid_vol - bid_vol_at_limit_up) > cumulative_trade_after_buy`（縮減量無法被同期成交量解釋）
- 代表排隊的人主動離場，而非正常撮合消耗

### 執行
- 送**市價賣單**
- 出場後重置：`bought = False`、`peak_bid_vol = 0`、`cumulative_trade_after_buy = 0`、`recent_large_window = []`、`bought_time = None`

---

## VWAP 計算

```
# 每筆 tick 無條件累加（09:00 前也算）
cumulative_pv  += float(tick.close) * tick.volume
cumulative_vol += tick.volume
vwap = cumulative_pv / cumulative_vol if cumulative_vol > 0 else 0.0
```

- `tick.close` 單位：元（Decimal，轉 float）
- `tick.volume` 單位：張
- `vwap` 單位：元

---

## 回呼更新順序

### on_tick
1. 更新 `last_price = float(tick.close)`
2. 累加 VWAP（`cumulative_pv`、`cumulative_vol`）
3. 若已持倉：累加 `cumulative_trade_after_buy += tick.volume`
4. 條件 A：時間濾網
5. 條件 B：價格位置
6. 條件 C：更新 `recent_large_window`，清除 10 秒前紀錄，加總金額
7. 條件 D：點火水位
8. 四條件全過且未持倉 → 送限價買單

### on_bidask
1. 更新 `ask_vol_at_limit_up = bidask.ask_volume[0]`
2. 更新 `bid_vol_at_limit_up = bidask.bid_volume[0]`
3. 若已持倉且 `bid_vol_at_limit_up > peak_bid_vol` → 更新峰值
4. 呼叫 `check_stop_loss()`

---

## 參數總覽

| 參數 | 數值 |
|------|------|
| 時間窗口 | 09:00:00 – 13:25:00 |
| 條件 C 累計金額門檻 | 動態：5日均日成交金額 × 1.5%，保底 500 萬 |
| 條件 C 滑動窗口 | 10 秒 |
| 點火水位 | 3,000 萬元換算張數 |
| price_factor（< 200 元） | 1.0 |
| price_factor（≥ 200 元） | 1.5 |
| 停損 A 倍數 | 3x（點火水位） |
| 停損 C 縮減比例 | 30% |
