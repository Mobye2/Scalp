## 處置股

Disposition Stocks

```
>> api.punish?

Signature:
api.punish(
    timeout: int = 5000,
    cb: Callable[[shioaji.data.Punish], NoneType] = None,
) -> shioaji.data.Punish
Docstring: get punish information

```

### 範例

In

```
punish = api.punish()
punish

```

Out

```
Punish(
    code=['2349', '2408', ...],
    start_date=[datetime.date(2025, 12, 17), datetime.date(2025, 12, 8), ...],
    end_date=[datetime.date(2025, 12, 31), datetime.date(2025, 12, 19), ...],
    updated_at=[datetime.datetime(2025, 12, 16, 18, 18, 20), datetime.datetime(2025, 12, 16, 18, 18, 20), ...],
    interval=['5分鐘', '5分鐘', ...],
    unit_limit=[10.0, 10.0, ...],
    total_limit=[30.0, 30.0, ...],
    description=['...', '...', ...],
    announced_date=[datetime.date(2025, 12, 16), datetime.date(2025, 12, 5), ...]
)

```

轉成DataFrame

In

```
df = pd.DataFrame(punish.__dict__)
df

```

Out

| code | start_date | end_date | updated_at | interval | unit_limit | total_limit | description | announced_date | | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 2349 | 2025-12-17 | 2025-12-31 | 2025-12-16 18:18:20 | 5分鐘 | 10.0 | 30.0 | ... | 2025-12-16 | | 2408 | 2025-12-08 | 2025-12-19 | 2025-12-16 18:18:20 | 5分鐘 | 10.0 | 30.0 | ... | 2025-12-05 |

### 屬性

Punish

```
code (list[str]): 商品代碼
start_date (list[date]): 處置開始日期
end_date (list[date]): 處置結束日期
updated_at (list[datetime]): 更新時間
interval (list[str]): 撮合間隔
unit_limit (list[float]): 單筆委託上限
total_limit (list[float]): 單日委託上限
description (list[str]): 處置內容
announced_date (list[date]): 公告日期

```

______________________________________________________________________

## 注意股

Attention Stocks

```
>> api.notice?

Signature:
api.notice(
    timeout: int = 5000,
    cb: Callable[[shioaji.data.Notice], NoneType] = None,
) -> shioaji.data.Notice
Docstring: get notice information

```

### 範例

In

```
notice = api.notice()
notice

```

Out

```
Notice(
    code=['089508', '2349', ...],
    updated_at=[datetime.datetime(2025, 12, 16, 18, 18, 19), datetime.datetime(2025, 12, 16, 18, 18, 19), ...],
    close=[9.85, 16.2, ...],
    reason=['最近六個營業日累積收盤價漲幅達39.34%﹝第一款﹞。', '最近六個營業日累積收盤價漲幅達41.59%﹝第一款﹞...', ...],
    announced_date=[datetime.date(2025, 12, 16), datetime.date(2025, 12, 16), ...]
)

```

轉成DataFrame

In

```
df = pd.DataFrame(notice.__dict__)
df

```

Out

| code | updated_at | close | reason | announced_date | | --- | --- | --- | --- | --- | | 089508 | 2025-12-16 18:18:19 | 9.85 | 最近六個營業日累積收盤價漲幅達39.34%﹝第一款﹞。 | 2025-12-16 | | 2349 | 2025-12-16 18:18:19 | 16.2 | 最近六個營業日累積收盤價漲幅達41.59%﹝第一款﹞... | 2025-12-16 |

### 屬性

Notice

```
code (list[str]): 商品代碼
updated_at (list[datetime]): 更新時間
close (list[float]): 收盤價
reason (list[str]): 注意交易資訊
announced_date (list[date]): 公告日期

```

## Ticks

取得方式可以以一整天、某時間區段或是某天的最後幾筆。預設為商品最近交易日的Ticks。

Ticks

```
api.ticks?

Signature:
    api.ticks(
        contract: shioaji.contracts.BaseContract,
        date: str = '2022-12-26',
        query_type: shioaji.constant.TicksQueryType = <TicksQueryType.AllDay: 'AllDay'>,
        time_start: Union[str, datetime.time] = None,
        time_end: Union[str, datetime.time] = None,
        last_cnt: int = 0,
        timeout: int = 30000,
        cb: Callable[[shioaji.data.Ticks], NoneType] = None,
    ) -> shioaji.data.Ticks
Docstring:
    get contract tick volumn

```

### 取得特定日期 Ticks

In

```
ticks = api.ticks(
    contract=api.Contracts.Stocks["2330"], 
    date="2023-01-16"
)
ticks

```

Out

```
Ticks(
    ts=[1673859600113699000, 1673859600228800000, 1673859600244294000, 1673859600308595000], 
    close=[506.0, 505.0, 506.0, 506.0],
    volume=[3340, 1, 17, 2],
    bid_price=[505.0, 505.0, 506.0, 506.0],
    bid_volume=[122, 320, 60, 58],
    ask_price=[506.0, 506.0, 507.0, 507.0],
    ask_volume=[13, 22, 702, 702]
    tick_type=[1, 2, 1, 2]
)

```

Ticks

```
ts (int): timestamp
close (float): 成交價
volume (int): 成交量
bid_price (float): 委買價
bid_volume (int): 委買量
ask_price (float): 委賣價
ask_volume (int): 委賣量
tick_type (int): 內外盤別{1: 外盤, 2: 內盤, 0: 無法判定}

```

轉成DataFrame

In

```
import pandas as pd
df = pd.DataFrame({**ticks})
df.ts = pd.to_datetime(df.ts)
df.head()

```

Out

| ts | ask_price | close | bid_volume | volume | ask_volume | tick_type | bid_price | | --- | --- | --- | --- | --- | --- | --- | --- | | 2023-01-16 09:00:00.113699 | 506 | 506 | 122 | 3340 | 13 | 1 | 505 | | 2023-01-16 09:00:00.228800 | 506 | 505 | 320 | 1 | 22 | 2 | 505 | | 2023-01-16 09:00:00.244294 | 507 | 506 | 60 | 17 | 702 | 1 | 506 | | 2023-01-16 09:00:00.308595 | 507 | 506 | 58 | 2 | 702 | 2 | 506 |

### 取得特定時間區段 Ticks

In

```
ticks = api.ticks(
    contract=api.Contracts.Stocks["2330"], 
    date="2023-01-16",
    query_type=sj.constant.TicksQueryType.RangeTime,
    time_start="09:00:00",
    time_end="09:20:01"
)
ticks

```

Out

```
Ticks(
    ts=[1673859600113699000, 1673859600228800000, 1673859600244294000, 1673859600308595000], 
    close=[506.0, 505.0, 506.0, 506.0],
    volume=[3340, 1, 17, 2],
    bid_price=[505.0, 505.0, 506.0, 506.0],
    bid_volume=[122, 320, 60, 58],
    ask_price=[506.0, 506.0, 507.0, 507.0],
    ask_volume=[13, 22, 702, 702]
    tick_type=[1, 2, 1, 2]
)

```

### 取得最後數筆 Ticks

In

```
ticks = api.ticks(
    contract=api.Contracts.Stocks["2330"], 
    date="2023-01-16",
    query_type=sj.constant.TicksQueryType.LastCount,
    last_cnt=4,
)
ticks

```

Out

```
Ticks(
    ts=[1673859600113699000, 1673859600228800000, 1673859600244294000, 1673859600308595000], 
    close=[506.0, 505.0, 506.0, 506.0],
    volume=[3340, 1, 17, 2],
    bid_price=[505.0, 505.0, 506.0, 506.0],
    bid_volume=[122, 320, 60, 58],
    ask_price=[506.0, 506.0, 507.0, 507.0],
    ask_volume=[13, 22, 702, 702]
    tick_type=[1, 2, 1, 2]
)

```

## KBar

Kbars

```
api.kbars?

Signature:
api.kbars(
    contract: shioaji.contracts.BaseContract,
    start: str = '2023-01-15',
    end: str = '2023-01-16',
    timeout: int = 30000,
    cb: Callable[[shioaji.data.Kbars], NoneType] = None,
) -> shioaji.data.Kbars
Docstring:
get Kbar

```

In

```
kbars = api.kbars(
    contract=api.Contracts.Stocks["2330"], 
    start="2023-01-15", 
    end="2023-01-16", 
)
kbars

```

Out

```
Kbars(
    ts=[1673859660000000000, 1673859720000000000, 1673859780000000000, 1673859840000000000],
    Open=[506.0, 505.0, 505.0, 504.0],
    High=[508.0, 506.0, 506.0, 505.0],
    Low=[505.0, 505.0, 504.0, 504.0],
    Close=[505.0, 505.0, 504.0, 504.0],
    Volume=[5308, 1018, 543, 209]
)

```

Kbars

```
ts (int): timestamp
Open (float): open price
High (float): the highest price
Low: (float): the lowest price
Close (float): close price
Volume (int): volume

```

轉成DataFrame

In

```
import pandas as pd
df = pd.DataFrame({**kbars})
df.ts = pd.to_datetime(df.ts)
df.head()

```

Out

| Close | Amount | Low | Volume | ts | Open | High | | --- | --- | --- | --- | --- | --- | --- | | 505 | 2.68731e+09 | 505 | 5308 | 2023-01-16 09:01:00 | 506 | 508 | | 505 | 5.14132e+08 | 505 | 1018 | 2023-01-16 09:02:00 | 505 | 506 | | 504 | 2.74112e+08 | 504 | 543 | 2023-01-16 09:03:00 | 505 | 506 | | 504 | 1.0542e+08 | 504 | 209 | 2023-01-16 09:04:00 | 504 | 505 |

## 資料歷史期間

Historical Periods

| | Start Date | End Date | | --- | --- | --- | | Index | 2020-03-02 | Today | | Stock | 2020-03-02 | Today | | Futures | 2020-03-22 | Today |

## 連續期貨合約

期貨合約一旦到期，合約即不再有效，亦即他將不會出現在您的`api.Contracts`裡。為了取得到期的期貨合約歷史資料，我們提供連續期貨合約。`R1`, `R2`是近月及次月的連續期貨合約，他們會自動在結算日更換新的合約。您可以使用`R1`, `R2`合約來取得歷史資料，例如`api.Contracts.Futures.TXF.TXFR1`。以下顯示如何使用`R1`, `R2`合約取得到期期貨的歷史`Ticks`及`Kbars`。

Ticks

Ticks

```
ticks = api.ticks(
    contract=api.Contracts.Futures.TXF.TXFR1, 
    date="2020-03-22"
)
ticks

```

Out

```
Ticks(
    ts=[1616166000030000000, 1616166000140000000, 1616166000140000000, 1616166000190000000], 
    close=[16011.0, 16013.0, 16014.0, 16011.0],
    volume=[49, 2, 2, 1],
    bid_price=[0.0, 16011.0, 16011.0, 16011.0],
    bid_volume=[0, 1, 1, 1],
    ask_price=[0.0, 16013.0, 16013.0, 16013.0],
    ask_volume=[0, 1, 1, 1]
    tick_type=[1, 1, 1, 2]
)

```

Kbars

Kbars

```
kbars = api.kbars(
    contract=api.Contracts.Futures.TXF.TXFR1,
    start="2023-01-15", 
    end="2023-01-16", 
)
kbars

```

Out

```
Kbars(
    ts=[1616402760000000000, 1616402820000000000, 1616402880000000000, 1616402940000000000],
    Open=[16018.0, 16018.0, 16000.0, 15992.0],
    High=[16022.0, 16020.0, 16005.0, 15999.0],
    Low=[16004.0, 16000.0, 15975.0, 15989.0],
    Close=[16019.0, 16002.0, 15992.0, 15994.0],
    Volume=[1791, 864, 1183, 342]
)

```

包含漲跌幅、漲跌、高低價差、成交量及成交金額排行。`Scanners`利用`scanner_type`去取得不同類型的排行。

Scanners

```
>> api.scanners?

Signature:
api.scanners(
    scanner_type: shioaji.constant.ScannerType, 
    ascending: bool = True,
    date: str = None,
    count: shioaji.shioaji.ConstrainedIntValue = 100, # 0 <= count <= 200
    timeout: int = 30000,
    cb: Callable[[List[shioaji.data.ChangePercentRank]], NoneType] = None,
) -> List[shioaji.data.ChangePercentRank]

```

排名預設為由大到小排序，`ascending`預設值為`True`。若要由小到大排序請將`ascending`設為`False`。`count`為排行數量。

支援的排行類別

```
ChangePercentRank: 依價格漲跌幅排序
ChangePriceRank: 依價格漲跌排序
DayRangeRank: 依高低價差排序
VolumeRank: 依成交量排序
AmountRank: 依成交金額排序

```

## 範例

依價格漲跌幅排序

```
scanners = api.scanners(
    scanner_type=sj.constant.ScannerType.ChangePercentRank,
    count=1
)
scanners

```

Out

```
[
    ChangePercentRank(
        date='2021-04-09', 
        code='5211', 
        name='蒙恬', 
        ts=1617978600000000000, 
        open=16.4, 
        high=17.6, 
        low=16.35, 
        close=17.6, 
        price_range=1.25, 
        tick_type=1, 
        change_price=1.6, 
        change_type=1, 
        average_price=17.45, 
        volume=7, 
        total_volume=1742, 
        amount=123200, 
        total_amount=30397496, 
        yesterday_volume=514, 
        volume_ratio=3.39, 
        buy_price=17.6, 
        buy_volume=723, 
        sell_price=0.0, 
        sell_volume=0, 
        bid_orders=237, 
        bid_volumes=82, 
        ask_orders=33, 
        ask_volumes=64
    )
]

```

轉成 DataFrame

In

```
scanners = api.scanners(
    scanner_type=sj.constant.ScannerType.ChangePercentRank, 
    count=5
)
df = pd.DataFrame(s.__dict__ for s in scanners)
df.ts = pd.to_datetime(df.ts)
df

```

Out

| date | code | name | ts | open | high | low | close | price_range | tick_type | change_price | change_type | average_price | volume | total_volume | amount | total_amount | yesterday_volume | volume_ratio | buy_price | buy_volume | sell_price | sell_volume | bid_orders | bid_volumes | ask_orders | ask_volumes | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 2023-01-17 | 6259 | 百徽 | 2023-01-17 11:11:41.030000 | 22.8 | 23.75 | 22.45 | 23.75 | 1.3 | 1 | 2.15 | 1 | 23.58 | 4 | 137 | 95000 | 3230900 | 26 | 5.27 | 0 | 8 | 0 | 0 | 65 | 211 | 5 | 11 | | 2023-01-17 | 6788 | 華景電 | 2023-01-17 11:19:01.924000 | 107 | 116 | 107 | 116 | 9 | 1 | 10.5 | 1 | 113.61 | 1 | 4292 | 116000 | 487606000 | 682 | 6.29 | 0 | 1053 | 0 | 0 | 1044 | 3786 | 501 | 1579 | | 2023-01-17 | 2540 | 愛山林 | 2023-01-17 11:17:39.435000 | 85.2 | 85.2 | 83 | 85.2 | 2.2 | 1 | 7.7 | 1 | 85.04 | 1 | 1226 | 85200 | 104253800 | 702 | 1.75 | 0 | 142 | 0 | 0 | 362 | 5779 | 121 | 1831 | | 2023-01-17 | 8478 | 東哥遊艇 | 2023-01-17 11:18:33.702000 | 350.5 | 378 | 347 | 378 | 31 | 1 | 34 | 1 | 363.39 | 1 | 12115 | 378000 | 4402427500 | 8639 | 1.4 | 0 | 3307 | 0 | 0 | 3754 | 235724 | 1906 | 29843 | | 2023-01-17 | 6612 | 奈米醫材 | 2023-01-17 11:15:32.752000 | 102 | 109 | 102 | 109 | 7 | 1 | 9.7 | 1 | 106.95 | 1 | 1329 | 109000 | 142134500 | 1022 | 1.3 | 0 | 298 | 0 | 0 | 467 | 22718 | 162 | 1016 |

## 屬性

ChangePercentRank

```
date (str): 交易日 
code (str): 股票代號
name (str): 股票名稱
ts (int): 時間戳記
open (float): 開盤價
high (float): 最高價
low (float): 最低價
close (float): 收盤價
price_range (float): 價格區間(最高價-最低價)
tick_type (int): 內外盤別 {1: 內盤, 2: 外盤, 0: 無法判定}
change_price (float): 價格漲跌
change_type (int): 漲跌
    {LimitUp, Up, Unchanged, Down, LimitDown}
average_price (float): 均價
volume (int): 成交量
total_volume (int): 總成交量
amount (int): 成交金額
total_amount (int): 總成交金額
yesterday_volume (int): 昨日總成交量
volume_ratio (float): 總成交量/昨日總成交量
buy_price (float): 委買價
buy_volume (int): 委買量
sell_price (float): 委賣價
sell_volume (int): 委賣量
bid_orders (int): 內盤總成交單量
bid_volumes (int): 內盤總成交量
ask_orders (int): 外盤總成交單量
ask_volumes (int): 外盤總成交量

```

或有券源

```
>> api.short_stock_sources?

Signature:
api.short_stock_sources(
    contracts: List[shioaji.contracts.Stock],
    timeout: int = 5000,
    cb: Callable[[shioaji.data.ShortStockSource], NoneType] = None,
) -> List[shioaji.data.ShortStockSource]

```

## 範例

In

```
contracts = [
    api.Contracts.Stocks['2330'], 
    api.Contracts.Stocks['2317']
]
short_stock_sources = api.short_stock_sources(contracts)
short_stock_sources

```

Out

```
[
    ShortStockSource(code='2330', short_stock_source=58260, ts=1673943433000000000),
    ShortStockSource(code='2317', short_stock_source=75049, ts=1673943433000000000)
]

```

轉成 DataFrame

In

```
df = pd.DataFrame(s.__dict__ for s in short_stock_sources)
df.ts = pd.to_datetime(df.ts)
df

```

Out

| code | short_stock_source | ts | | --- | --- | --- | | 2330 | 58260 | 2023-01-17 08:17:13 | | 2317 | 75049 | 2023-01-17 08:17:13 |

## 屬性

ShortStockSource

```
code (str): 商品代碼
short_stock_source (float): 或有券源
ts (int): 時間戳記

```

市場快照為證券、期貨及選擇權當下資訊。內容包含開盤價、最高價、最低價、收盤價、變動價、均價、成交量、總成交量、委買價、委買量、委賣價、委賣量和昨量。

提醒

市場快照每次最多500檔商品。

市場快照

```
>> api.snapshots?

Signature:
api.snapshots(
    contracts: List[Union[shioaji.contracts.Option, shioaji.contracts.Future, shioaji.contracts.Stock, shioaji.contracts.Index]],
    timeout: int = 30000,
    cb: Callable[[shioaji.data.Snapshot], NoneType] = None,
) -> List[shioaji.data.Snapshot]
Docstring:
get contract snapshot info

```

## 範例

In

```
contracts = [api.Contracts.Stocks['2330'],api.Contracts.Stocks['2317']]
snapshots = api.snapshots(contracts)
snapshots

```

Out

```
[
    Snapshot(
        ts=1673620200000000000, 
        code='2330', 
        exchange='TSE', 
        open=507.0, 
        high=509.0, 
        low=499.0, 
        close=500.0, 
        tick_type=<TickType.Sell: 'Sell'>, 
        change_price=13.5, 
        change_rate=2.77,
        change_type=<ChangeType.Up: 'Up'>, 
        average_price=502.42, 
        volume=48, 
        total_volume=77606, 
        amount=24000000, 
        total_amount=38990557755, 
        yesterday_volume=20963.0, 
        buy_price=500.0,
        buy_volume=122.0, 
        sell_price=501.0, 
        sell_volume=1067, 
        volume_ratio=3.7
    ),
    Snapshot(
        ts=1673620200000000000, 
        code='2317', 
        exchange='TSE', 
        open=99.0, 
        high=99.5, 
        low=98.6, 
        close=98.6, 
        tick_type=<TickType.Sell: 'Sell'>, 
        change_price=0.0, 
        change_rate=0.0, 
        change_type=<ChangeType.Unchanged: 'Unchanged'>, 
        average_price=98.96, 
        volume=63, 
        total_volume=17809, 
        amount=6211800, 
        total_amount=1762344817, 
        yesterday_volume=18537.0, 
        buy_price=98.6, 
        buy_volume=607.0, 
        sell_price=98.7, 
        sell_volume=4, 
        volume_ratio=0.96
    )
]

```

轉成Dataframe

In

```
df = pd.DataFrame(s.__dict__ for s in snapshots)
df.ts = pd.to_datetime(df.ts)
df

```

Out

| ts | code | exchange | open | high | low | close | tick_type | change_price | change_rate | change_type | average_price | volume | total_volume | amount | total_amount | yesterday_volume | buy_price | buy_volume | sell_price | sell_volume | volume_ratio | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 2023-01-13 14:30:00 | 2330 | TSE | 507 | 509 | 499 | 500 | Sell | 13.5 | 2.77 | Up | 502.42 | 48 | 77606 | 24000000 | 38990557755 | 20963 | 500 | 122 | 501 | 1067 | 3.7 | | 2023-01-13 14:30:00 | 2317 | TSE | 99 | 99.5 | 98.6 | 98.6 | Sell | 0 | 0 | Unchanged | 98.96 | 63 | 17809 | 6211800 | 1762344817 | 18537 | 98.6 | 607 | 98.7 | 4 | 0.96 |

## 屬性

Snapshot

```
ts (int): 取得資訊時間戳記
code (str): 商品代碼
exchange (Exchange): 交易所
open (float): 開盤價
high (float): 最高價
low (float): 最低價
close (float): 收盤價
tick_type (TickType): 收盤買賣別 {None, Buy, Sell}
change_price (float): 漲跌
change_rate (float): 漲跌幅
change_type (ChangeType): 漲跌 {LimitUp, Up, Unchanged, Down, LimitDown}
avgerage_price (float): 均價
volume (int): 單量
total_volume (int): 成交量
amount (int): 單量成交金額
total_amount (int): 成交金額
yestoday_volume (float): 昨量
buy_price (float): 委買價
buy_volume (float): 委買量
sell_price (float): 賣出價
sell_volume (int): 委賣量
volume_ratio (float): 昨量比

```

利用訂閱[商品檔](../../../contract/)的方式去取得即時行情。

Subscribe

```
api.quote.subscribe?

    Signature:
        api.quote.subscribe(
            contract:shioaji.contracts.Contract,
            quote_type:shioaji.constant.QuoteType=<QuoteType.Tick: 'tick'>,
            intraday_odd:bool=False,
            version: shioaji.constant.QuoteVersion=<QuoteVersion.v0: 'v0'>,
        )
    Docstring: <no docstring>
    Type:      method

```

Quote Parameters:

```
quote_type: 訂閱類型 {'tick', 'bidask', 'quote'}
intraday_odd: 盤中零股 {True, False}
version: 行情版本 {'v1', 'v0'}

```

