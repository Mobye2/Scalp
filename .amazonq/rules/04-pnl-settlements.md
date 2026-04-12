## 未實現損益

In

```
api.list_positions?

```

Out

```
Signature:
api.list_positions(
    account: shioaji.account.Account = None,
    unit: shioaji.constant.Unit = <Unit.Common: 'Common'>,
    timeout: int = 5000,
    cb: Callable[[List[Union[shioaji.position.StockPosition, shioaji.position.FuturePosition]]], NoneType] = None,
) -> List[Union[shioaji.position.StockPosition, shioaji.position.FuturePosition]]
Docstring:
query account of unrealized gain or loss
Args:
    account (:obj:Account):
        choice the account from listing account (Default: stock account)

```

### 證券

#### 整股部位

In

```
api.list_positions(api.stock_account)

```

Out

```
[
    StockPosition(
        id=0, 
        code='2890', 
        direction=<Action.Buy: 'Buy'>, 
        quantity=12, 
        price=2.79, 
        last_price=16.95, 
        pnl=169171.0, 
        yd_quantity=12, 
        margin_purchase_amount=0, 
        collateral=0, 
        short_sale_margin=0, 
        interest=0
    )
]

```

轉成DataFrame

In

```
positions = api.list_positions(api.stock_account)
df = pd.DataFrame(s.__dict__ for s in positions)
df

```

Out

| id | code | direction | quantity | price | last_price | pnl | yd_quantity | cond | margin_purchase_amount | collateral | short_sale_margin | interest | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 0 | 0 | 2890 | Buy | 12 | 2.79 | 16.95 | 169172 | 12 | Cash | 0 | 0 | 0 |

StockPosition

```
id (int): 部位代碼
code (str): 商品代碼
direction (Action): {Buy: 買, Sell: 賣}
quantity (int): 數量
price (float): 平均價格
last_price (float): 目前股價
pnl (float): 損益
yd_quantity (int): 昨日庫存數量
cond (StockOrderCond): {
    Cash: 現股(預設值), 
    Netting: 餘額交割,
    MarginTrading: 融資, 
    ShortSelling: 融券, 
    Emerging: 興櫃
    }
margin_purchase_amount (int): 融資金額 
collateral (int): 擔保品 
short_sale_margin (int): 保證金
interest (int): 利息

```

#### 零股部位

單位為股數

In

```
api.list_positions(
    api.stock_account, 
    unit=sj.constant.Unit.Share
)

```

Out

```
[
    StockPosition(
        id=0, 
        code='2890', 
        direction=<Action.Buy: 'Buy'>, 
        quantity=10000, 
        price=10.1, 
        last_price=12.0, 
        pnl=1234.0, 
        yd_quantity=10000, 
        margin_purchase_amount=0, 
        collateral=0, 
        short_sale_margin=0, 
        interest=0
    )
]

```

### 期貨選擇權

`account`預設為證券帳號，若欲查詢期權內容需帶入期權帳號。

In

```
api.list_positions(api.futopt_account)

```

Out

```
[
    FuturePosition(
        id=0,
        code='TX201370J2', 
        direction=<Action.Buy: 'Buy'>, 
        quantity=3, 
        price=131.0000, 
        last_price=126.0, 
        pnl=-750.00
    )
]

```

轉成DataFrame

In

```
positions = api.list_positions(api.futopt_account)
df = pd.DataFrame(p.__dict__ for p in positions)
df

```

Out

| id | code | direction | quantity | price | last_price | pnl | | --- | --- | --- | --- | --- | --- | --- | | 0 | TXFA3 | Buy | 4 | 14181 | 14375 | 155200 |

FuturePosition

```
id (int): 部位代碼
code (str): 商品代碼
direction (Action): {Buy: 買, Sell: 賣}
quantity (int): 數量
price (float): 平均價格
last_price (float): 目前價格
pnl (float): 損益

```

## 未實現損益 - 明細

可從針對`list_positions`得到的結果，將`id`帶入`detail_id`查詢該筆明細。

### 證券

In

```
api.list_position_detail?

```

Out

```
Signature:
    api.list_position_detail(
    account: shioaji.account.Account = None,
    detail_id: int = 0,
    timeout: int = 5000,
    cb: Callable[[List[Union[shioaji.position.StockPositionDetail, shioaji.position.    FuturePositionDetail]]], NoneType] = None,
) -> List[Union[shioaji.position.StockPositionDetail, shioaji.position.FuturePositionDetail]]
Docstring:
query account of position detail

Args:
    account (:obj:Account):
        choice the account from listing account (Default: stock account)
    detail_id (int): the id is from Position object, Position is from list_positions

```

In

```
position_detail = api.list_position_detail(api.stock_account, 1)
position_detail

```

Out

```
[
    StockPositionDetail(
        date='2023-02-22', 
        code='3558', 
        quantity=0, 
        price=1461.0, 
        last_price=1470.0, 
        dseq='WA371', 
        direction=<Action.Buy: 'Buy'>, 
        pnl=9.0, 
        currency=<Currency.TWD: 'TWD'>, 
        fee=1.0
    )
]

```

轉成DataFrame

In

```
df = pd.DataFrame(pnl.__dict__ for pnl in position_detail)
df

```

Out

| date | code | quantity | price | last_price | direction | pnl | currency | fee | cond | ex_dividends | interest | margintrading_amt | collateral | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 2023-02-22 | 3558 | 0 | 1461.0 | WA371 | Action.Buy | 11.0 | Currency.TWD | 1.0 | StockOrderCond.Cash | 0 | 0 | 0 | 0 |

屬性

```
date (str): 交易日期
code (str): 商品代碼    
quantity (int): 數量
price (float): 付出成本
last_price (float): 現值
dseq (str): 委託書號
direction (Action): {Buy: 買, Sell: 賣}
pnl (decimal): 損益
currency (string): 幣別 {NTD, USD, HKD, EUR, CAD, BAS}
fee (decimal): 交易手續費
cond (StockOrderCond): {
    Cash: 現股(預設值), 
    Netting: 餘額交割,
    MarginTrading: 融資, 
    ShortSelling: 融券, 
    Emerging: 興櫃
    }
ex_dividends(int): 除息金額
interest (int): 除息
margintrading_amt(int): 融資金額
collateral (int): 擔保品 

```

### 期貨選擇權

In

```
position_detail = api.list_position_detail(api.futopt_account, 0)
position_detail

```

Out

```
[
    FuturePositionDetail(
        date='2023-02-14', 
        code='MXFC3', 
        quantity=1, 
        price=15611.0, 
        last_price=15541.0, 
        dseq='tA0n8', 
        direction=<Action.Buy: 'Buy'>, 
        pnl=-3500.0, 
        currency=<Currency.TWD: 'TWD'>, 
        entry_quantity=1
    )
]

```

轉成DataFrame

In

```
df = pd.DataFrame(pnl.__dict__ for pnl in position_detail)
df

```

Out

| date | code | quantity | price | last_price | dseq | direction | pnl | currency | entry_quantity | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 2023-02-14 | MXFC3 | 1 | 15611.0 | 15541.0 | tA0n8 | Action.Buy | -3500.0 | Currency.TWD | 1 |

屬性

```
code (str): 商品代碼
date (str): 交易日期
quantity (int): 數量
price (float): 價格
last_price (float): 目前股價    
dseq (str): 委託書號
direction (Action): {Buy: 買, Sell: 賣}
pnl (float): 損益
currency (str): 幣別 {NTD, USD, HKD, EUR, CAD, BAS}
fee (float or int): 交易手續費
entry_quantity(int): 新倉數量

```

需要先[登錄](../../login)。

## 已實現損益

In

```
api.list_profit_loss?

```

Out

```
Signature:
    api.list_profit_loss(
        account: shioaji.account.Account = None,
        begin_date: str = '',
        end_date: str = '',
        unit: shioaji.constant.Unit = <Unit.Common: 'Common'>,
        timeout: int = 5000,
        cb: Callable[[List[shioaji.position.ProfitLoss]], NoneType] = None,
    ) -> List[shioaji.position.ProfitLoss]
Docstring:
    query account of profit loss

    Args:
        account (:obj:Account): 
            choice the account from listing account (Default: stock account)
        begin_date (str): the start date of query profit loss (Default: today)
        end_date (str): the end date of query profit loss (Default: today)

```

帶入想查詢的時間區間。`begin_date`為起始時間，`end_date`為結束時間。`unit`為數量單位，`Common`為整股，`Share`為零股。

In

```
profitloss = api.list_profit_loss(api.stock_account,'2020-05-05','2020-05-30')
profitloss

```

Out

```
[
    StockProfitLoss(
        id=0, 
        code='2890', 
        seqno='14816', 
        dseq='ID111', 
        quantity=1, 
        price=10.1, 
        pnl=1234.0, 
        pr_ratio=0.1237, 
        cond='Cash', 
        date='2020-05-22'
    )
]

```

轉成DataFrame

In

```
df = pd.DataFrame(pnl.__dict__ for pnl in profitloss)
df

```

Out

| id | code | cond | date | pnl | pr_ratio | price | quantity | seqno | dseq | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 0 | 2890 | StockOrderCond.Cash | 2020-05-22 | 1000.0 | 0.1237 | 10.1 | 1 | 14816 | ID111 |

StockProfitLoss

```
id (int): 可利用此id查詢明細
code (str): 商品代碼
seqno (str): seqno no.
dseq (str): seqno no.
quantity (int): 數量
price (float): 價格
pnl (float): 損益
pr_ratio (float): 損益比
cond (StockOrderCond): {
                Cash: 現股(預設值), 
                Netting: 餘額交割,
                MarginTrading: 融資, 
                ShortSelling: 融券, 
                Emerging: 興櫃
            }
date (str): 交易日期

```

FutureProfitLoss

```
id (int): 可利用此id查詢明細
code (str): 商品代碼
quantity (int): 數量
pnl (float): 損益
date (str): 交易日期
direction (Action): 買賣別 {Buy, Sell}
entry_price (int): 進倉價格
cover_price (int): 平倉價格
tax (int): 交易稅
fee (int): 交易手續費

```

## 已實現損益 - 明細

可從針對`list_profit_loss`得到的結果，將`id`帶入`detail_id`查詢該筆明細。`unit`為數量單位，`Common`為整股，`Share`為零股。

In

```
api.list_profit_loss_detail?

```

Out

```
Signature:
api.list_profit_loss_detail(
    account: shioaji.account.Account = None,
    detail_id: int = 0,
    unit: shioaji.constant.Unit = <Unit.Common: 'Common'>,
    timeout: int = 5000,
    cb: Callable[[List[Union[shioaji.position.StockProfitDetail, shioaji.position.FutureProfitDetail]]], NoneType] = None,
) -> List[Union[shioaji.position.StockProfitDetail, shioaji.position.FutureProfitDetail]]
Docstring:
query account of profit loss detail

Args:
    account (:obj:Account):
        choice the account from listing account (Default: stock account)
    detail_id (int): the id is from ProfitLoss object, ProfitLoss is from list_profit_loss

```

In

```
profitloss_detail = api.list_profit_loss_detail(api.stock_account, 2)
profitloss_detail

```

Out

```
[
    StockProfitDetail(
        date='2020-01-01', 
        code='2890', 
        quantity=1, 
        dseq='IX000', 
        fee=20, 
        tax=0, 
        currency='TWD', 
        price=10.8, 
        cost=10820, 
        rep_margintrading_amt=0, 
        rep_collateral=0, 
        rep_margin=0, 
        shortselling_fee=0, 
        ex_dividend_amt=0, 
        interest=0
    )
]

```

轉成DataFrame

In

```
df = pd.DataFrame(pnl.__dict__ for pnl in profitloss_detail)
df

```

Out

| date | code | quantity | dseq | fee | tax | currency | price | cost | rep_margintrading_amt | rep_collateral | rep_margin | shortselling_fee | ex_dividend_amt | interest | trade_type | cond | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 2020-01-01 | 2890 | 1 | IX000 | 20 | 0 | TWD | 10.8 | 10820 | 0 | 0 | 0 | 0 | 0 | 0 | Common | Cash |

StockProfitDetail

```
date (str): 交易日期
code (str): 商品代碼
quantity (int): 數量
dseq (str): 委託書號
fee (int): 交易手續費
tax (int): 交易稅
currency (str): 幣別 {NTD, USD, HKD, EUR, CAD, BAS}
price (float): 成交單價
cost (int): 付出成本
rep_margintrading_amt (int): 償還融資金額
rep_collateral (int): 償還擔保品
rep_margin (int): 償還保證金
shortselling_fee (int): 融券手續費
ex_dividend_amt: 除息金額
interest (int): 利息
trade_type (TradeType): {Common, DayTrade}
cond (StockOrderCond): {
                Cash: 現股(預設值), 
                Netting: 餘額交割,
                MarginTrading: 融資, 
                ShortSelling: 融券, 
                Emerging: 興櫃
            }

```

FutureProfitDetail

```
date (str): 交易日期
code (str): 商品代碼
quantity (int): 數量
dseq (str): 委託書號
fee (int): 交易手續費
tax (int): 交易稅
currency (str): 幣別 {NTD, USD, HKD, EUR, CAD, BAS}
direction (Action): 買賣別 {Buy, Sell}
entry_date (str): 進倉日期
entry_price (int): 進倉價格
cover_price (int): 平倉價格
pnl (int): 損益

```

## 已實現損益 - 彙總

用於查詢一段時間內的損益彙總。

In

```
api.list_profit_loss_summary?

```

Out

```
Signature:
api.list_profit_loss_summary(
    account: shioaji.account.Account = None,
    begin_date: str = '',
    end_date: str = '',
    timeout: int = 5000,
    cb: Callable[[ProfitLossSummaryTotal], NoneType] = None,
) -> ProfitLossSummaryTotal
Docstring:
query summary profit loss of a period time

Args:
    account (:obj:Account):
        choice the account from listing account (Default: stock account)
    begin_date (str): the start date of query profit loss (Default: today)
    end_date (str): the end date of query profit loss (Default: today)

```

帶入想查詢的時間區間。`begin_date`為起始時間，`end_date`為結束時間。

In

```
profitloss_summary = api.list_profit_loss_summary(api.stock_account,'2020-05-05','2020-05-30')
profitloss_summary

```

Out

```
ProfitLossSummaryTotal(
    status=<FetchStatus.Fetched: 'Fetched'>, 
    profitloss_summary=[
        StockProfitLossSummary(
            code='2890', 
            quantity=2000, 
            entry_price=17, 
            cover_price=10, 
            pnl=-11585.0, 
            currency='NTD', 
            entry_cost=34550, 
            cover_cost=21600, 
            buy_cost=33112, 
            sell_cost=21527, 
            pr_ratio=-34.99
        )
    ], 
    total=ProfitLossTotal(
        quantity=2000, 
        buy_cost=33112, 
        sell_cost=21527, 
        pnl=-11585.0, 
        pr_ratio=-34.99
    )
)

```

轉成DataFrame

In

```
df = pd.DataFrame(pnl.__dict__ for pnl in profitloss_summary.profitloss_summary) 
df

```

Out

| code | quantity | entry_price | cover_price | pnl | currency | entry_cost | cover_cost | buy_cost | sell_cost | pr_ratio | cond | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 2890 | 2000 | 17 | 10 | -11585 | NTD | 34550 | 21600 | 33112 | 21527 | -34.99 | Cash |

StockProfitLossSummary

```
code (str): 商品代碼
quantity (int): 數量
entry_price (int): 進倉價格
cover_price (int): 平倉價格
pnl (float): 損益
currency (str): 幣別
entry_cost (int): 進倉金額(不含手續費及交易稅)
cover_cost (int): 平倉金額(不含手續費及交易稅)
buy_cost (int): 付出成本
sell_cost (int): 賣出收入
pr_ratio (float): 損益比
cond (StockOrderCond): {
                Cash: 現股(預設值), 
                Netting: 餘額交割,
                MarginTrading: 融資, 
                ShortSelling: 融券, 
                Emerging: 興櫃
            }

```

FutureProfitLossSummary

```
code (str): 商品代碼
quantity (int): 數量
entry_price (int): 進倉價格
cover_price (int): 平倉價格
pnl (float): 損益
currency (str): 幣別
direction (Action): 買賣別 {Buy, Sell}
tax (int): 交易稅
fee (int): 交易手續費

```

用於查詢交割款，需要先[登錄](../../login)。

## Settlements

In

```
api.settlements?

```

Out

```
Signature:
api.settlements(
    account: shioaji.account.Account = None,
    timeout: int = 5000,
    cb: Callable[[List[shioaji.position.SettlementV1]], NoneType] = None,
) -> List[shioaji.position.SettlementV1]
Docstring: query stock account of settlements

```

In

```
settlements = api.settlements(api.stock_account)   
settlements

```

Out

```
[
    SettlementV1(date=datetime.date(2022, 10, 13), amount=0.0, T=0),
    SettlementV1(date=datetime.date(2022, 10, 14), amount=0.0, T=1),
    SettlementV1(date=datetime.date(2022, 10, 17), amount=0.0, T=2)
]

```

轉成DataFrame

In

```
df = pd.DataFrame([s.__dict__ for s in settlements]).set_index("T")
df

```

out

| T | date | amount | | --- | --- | --- | | 0 | 2022-10-13 | 0 | | 1 | 2022-10-14 | 0 | | 2 | 2022-10-17 | 0 |

SettlementV1

```
date (datetime.date): 交割日期
amount (float): 交割金額
T (int): Tday

```

提醒

查詢時間為交易日 8:30~15:00。

用於查詢證券帳戶交易額度，需要先[登入](../../login)。

In

```
api.trading_limits?

```

Out

```
Signature:
api.trading_limits(
    account: shioaji.account.Account = None,
    timeout: int = 5000,
    cb: Callable[[shioaji.position.TradingLimits], NoneType] = None,
) -> shioaji.position.TradingLimits
Docstring: query stock account trading limits

```

In

```
api.trading_limits(api.stock_account)

```

Out

```
TradingLimits(
    status=<FetchStatus.Fetched: 'Fetched'>,
    trading_limit=1000000,
    trading_used=0,
    trading_available=1000000,
    margin_limit=0,
    margin_used=0,
    margin_available=0,
    short_limit=0,
    short_used=0,
    short_available=0
)

```

TradingLimits

```
status (FetchStatus): 資料回傳狀態
trading_limit (int): 電子交易總額度
trading_used (int): 電子交易已用額度
trading_available (int): 電子交易可用額度
margin_limit (int): 融資額度上限
margin_used (int): 融資已用額度
margin_available (int): 融資可用額度
short_limit (int): 融券額度上限
short_used (int): 融券已用額度
short_available (int): 融券可用額度

```

阻塞(Blocking)模式為函數必須等待某事完成。每個函數都是等待的，不管是在做 I/O 還是在做 CPU 任務。舉例來說，如果函數試圖從資料庫中獲取數據，那麼它需要停下來等待回傳結果，收到回傳結果後，才會繼續處理接下來的任務。相反地，非阻塞(non-blocking)模式，不會等待操作完成。如果您嘗試在短時間內發送批量操作，則非阻塞模式非常有用。我們提供以下範例讓您更了解之間的區別。

切換阻塞/非阻塞模式為利用參數`timeout`。將API參數`timeout`設置為`0`為非阻塞模式。`timeout`預設值為 5000（毫秒），表示該函數最多等待 5 秒。

