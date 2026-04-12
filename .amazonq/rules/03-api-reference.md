## 可使用的APIs

行情資料

```
1. quote.subscribe
2. quote.unsubscribe
3. ticks
4. kbars
5. snapshots
6. short_stock_sources
7. credit_enquires
8. scanners

```

下單

```
1. place_order
2. update_order
3. cancel_order
4. update_status
5. list_trades

```

帳務

```
1. list_positions
2. list_profit_loss

```

用於查詢現貨交割帳戶餘額，需要先[登入](../../login)。

In

```
api.account_balance?

```

Out

```
Signature:
    api.account_balance(
        account: shioaji.account.Account = None,
        timeout: int = 5000,
        cb: Callable[[shioaji.position.AccountBalance], NoneType] = None,
    )
Docstring: query stock account balance

```

In

```
api.account_balance()

```

Out

```
AccountBalance(
    status=<FetchStatus.Fetched: 'Fetched'>,
    acc_balance=100000.0,
    date='2023-01-06 13:30:00.000000',
    errmsg=''
)

```

In - 帶 account 參數

```
api.account_balance(account=api.stock_account)

```

Out

```
AccountBalance(
    status=<FetchStatus.Fetched: 'Fetched'>,
    acc_balance=100000.0,
    date='2023-01-06 13:30:00.000000',
    errmsg=''
)

```

AccountBalance

```
status (FetchStatus): 資料回傳狀態
acc_balance (float): 餘額
date (str): 查詢日期
errmsg (str): 錯誤訊息

```

**Warning**: The features of this page will be removed in the future.

### Account Margin

In

```
api.get_account_margin?

```

Out

```
Signature: api.get_account_margin(currency='NTD', margin_type='1', account={})
Docstring:
query margin    currency: {NTX, USX, NTD, USD, HKD, EUR, JPY, GBP}
the margin calculate in which currency
    - NTX: 約當台幣
    - USX: 約當美金
    - NTD: 新台幣
    - USD: 美元
    - HKD: 港幣
    - EUR: 歐元
    - JPY: 日幣
    - GBP: 英鎊
margin_type: {'1', '2'}
    query margin type
    - 1 : 即時
    - 2 : 風險

```

In

```
account_margin = api.get_account_margin()
account_margin

```

Out

```
AccountMargin(person_id='PERSON_ID' broker_id='BROKER_ID' account_id='ACC_ID' signed=SIGNED username='USERNAME')

```

directly pass our AccountMargin object to pandas to using your model

In

```
df_margin = pd.DataFrame(account_margin.data())
df_margin

```

| | OrderPSecurity | ProfitAccCount | FProfit | FMissConProfit | OMissConProfit | ... | Bapamt | Sapamt | Adps | Adamt | Ybaln | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 0 | 50000.0 | 50000.0 | 0.0 | 0.0 | 0.0 | ... | 0.0 | 0.0 | 0.0 | 0.0 | 50000.0 |

### Get Open Position

In

```
api.get_account_openposition?

```

Out

```
Signature: api.get_account_openposition(product_type='0', query_type='0', account={})
Docstring:
query open position
product_type: {0, 1, 2, 3}
    filter product type of open position
    - 0: all
    - 1: future
    - 2: option
    - 3: usd base
query_type: {0, 1}
    query return with detail or summary
    - 0: detail
    - 1: summary

```

In

```
positions = api.get_account_openposition(query_type='1', account=api.futopt_account)
positions

```

Out

```
AccountOpenPosition(person_id='PERSON_ID' broker_id='BROKER_ID' account_id='ACC_ID' signed=SIGNED username='USERNAME')

```

### AccountOpenPosition

In

```
df_positions = pd.DataFrame(positions.data())
df_positions

```

| | Account | Code | CodeName | ContractAverPrice | Currency | Date | FlowProfitLoss | MTAMT | OTAMT | OrderBS | OrderNum | OrderType | RealPrice | SettlePrice | SettleProfitLoss | StartSecurity | UpKeepSecurity | Volume | paddingByte | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 0 | FF0020009104000 | TXFA9 | 台指期貨 01 | 9508.4137 | NTD | 00000000 | 4795201.620000 | 6438000.000000 | 8352000.000000 | B | | | 9784.0 | 9784.00 | 4795201.620000 | 8352000.000000 | 6438000.000000 | 87.000000 | |

### Get Settle ProfitLoss

In

```
api.get_account_settle_profitloss?

```

Out

```
Signature: api.get_account_settle_profitloss(product_type='0', summary='Y', start_date='', end_date='', currency='', account={})
Docstring:
query settlement profit loss
product_type: {0, 1, 2}
    filter product type of open position
    - 0: all
    - 1: future
    - 2: option
summary: {Y, N}
    query return with detail or summary
    - Y: summary
    - N: detail
start_date: str
    the start date of query range format with %Y%m%d
    ex: 20180101
end_date: str
    the end date of query range format with %Y%m%d
    ex: 20180201
currency: {NTD, USD, HKD, EUR, CAD, BAS}
    the profit loss calculate in which currency
    - NTD: 新台幣
    - USD: 美元
    - HKD: 港幣
    - EUR: 歐元
    - CAD: 加幣 
    - BAS: 基幣

```

### AccountSettleProfitLoss

In

```
st_date = (date.today() - timedelta(days=60)).strftime('%Y%m%d')
settle_profitloss = api.get_account_settle_profitloss(summary='Y', start_date=st_date)
settle_profitloss

```

```
df_profitloss = pd.DataFrame(settle_profitloss.data())
df_profitloss

```

| | account | averagePrice | code | codeName | currency | floatProfitLoss | handCharge | ord_bs | ord_type | ordno | ordno_b | settleAvgPrc | settleDate | settleVolume | tFlag | tdate | tradeProfitLoss | tradeTax | unVolume | volume | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | 0 | F0020009104000 | 9900.0 | TXFK8 | 台指期貨 11 | NTD | 460.000000 | 60.000000 | S | 00 | kY002 | kY003 | 9897.0 | 20181022 | 1.000000 | 1 | 20181022 | 600.000000 | 80.000000 | 0.000000 | 1.000000 |

用於查詢期貨帳戶的保證金，需先[登入](../../login)。

In

```
api.margin?

```

Out

```
Signature:
api.margin(
    account: shioaji.account.Account = None,
    timeout: int = 5000,
    cb: Callable[[shioaji.position.Margin], NoneType] = None,
) -> shioaji.position.Margin
Docstring: query future account of margin

```

In

```
api.margin(api.futopt_account)

```

Out

```
Margin(
    status=<FetchStatus.Fetched: 'Fetched'>, 
    yesterday_balance=6000.0, 
    today_balance=6000.0, 
    deposit_withdrawal=0.0, 
    fee=0.0, 
    tax=0.0, 
    initial_margin=0.0, 
    maintenance_margin=0.0, 
    margin_call=0.0, 
    risk_indicator=999.0, 
    royalty_revenue_expenditure=0.0, 
    equity=6000.0, 
    equity_amount=6000.0, 
    option_openbuy_market_value=0.0, 
    option_opensell_market_value=0.0, 
    option_open_position=0.0, 
    option_settle_profitloss=0.0, 
    future_open_position=0.0, 
    today_future_open_position=0.0, 
    future_settle_profitloss=0.0, 
    available_margin=6000.0, 
    plus_margin=0.0, 
    plus_margin_indicator=0.0, 
    security_collateral_amount=0.0, 
    order_margin_premium=0.0, 
    collateral_amount=0.0
)

```

Margin

```
status (FetchStatus): 資料回傳狀態
yesterday_balance (float): 前日餘額
today_balance (float): 今日餘額
deposit_withdrawal (float): 存提
fee (float): 手續費
tax (float): 期交稅
initial_margin (float): 原始保證金
maintenance_margin (float): 維持保證金
margin_call (float): 追繳保證金
risk_indicator (float): 風險指標
royalty_revenue_expenditure (float): 權利金收入與支出
equity (float): 權益數
equity_amount (float): 權益總值
option_openbuy_market_value (float): 未沖銷買方選擇權市值
option_opensell_market_value (float): 未沖銷賣方選擇權市值
option_open_position (float): 參考未平倉選擇權損益
option_settle_profitloss (float): 參考選擇權平倉損益
future_open_position (float): 未沖銷期貨浮動損益
today_future_open_position (float): 參考當日未沖銷期貨浮動損益
future_settle_profitloss (float): 期貨平倉損益
available_margin (float): 可動用(出金)保證金
plus_margin (float): 依「加收保證金指標」所加收之保證金
plus_margin_indicator (float): 加收保證金指標
security_collateral_amount (float): 有價證券抵繳總額
order_margin_premium (float): 委託保證金及委託權利金
collateral_amount (float): 有價品額

```

用於查詢帳戶未實現損益，需要先[登入](../../login)。

