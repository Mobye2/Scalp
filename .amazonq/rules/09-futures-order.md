## 範例

[期權下單範例 ( jupyter)](https://nbviewer.jupyter.org/github/Sinotrade/Sinotrade.github.io/blob/master/tutorial/future_and_option.ipynb)

### 買賣別

買

```
order = api.Order(
    action=sj.constant.Action.Buy,
    price=14400,
    quantity=2,
    price_type=sj.constant.FuturesPriceType.LMT,
    order_type=sj.constant.OrderType.ROD, 
    octype=sj.constant.FuturesOCType.Auto,
    account=api.futopt_account
)

```

賣

```
order = api.Order(
    action=sj.constant.Action.Sell,
    price=14400,
    quantity=2,
    price_type=sj.constant.FuturesPriceType.LMT,
    order_type=sj.constant.OrderType.ROD, 
    octype=sj.constant.FuturesOCType.Auto,
    account=api.futopt_account
)

```

### ROD + LMT

ROD + LMT

```
order = api.Order(
    action=sj.constant.Action.Sell,
    price=14400,
    quantity=2,
    price_type=sj.constant.FuturesPriceType.LMT,
    order_type=sj.constant.OrderType.ROD, 
    octype=sj.constant.FuturesOCType.Auto,
    account=api.futopt_account
)

```

[零股下單範例 ( jupyter)](https://nbviewer.jupyter.org/github/Sinotrade/Sinotrade.github.io/blob/master/tutorial/stock_intraday_odd.ipynb)

提醒

下單前必須先[登入](../../login/)及啟用[憑證](../../prepare/terms/)。

### 下單

下單

```
contract = api.Contracts.Stocks.TSE.TSE0050
order = api.Order(
    price=90,
    quantity=10,
    action=sj.constant.Action.Buy,
    price_type=sj.constant.StockPriceType.LMT,
    order_type=sj.constant.OrderType.ROD,     
    order_lot=sj.constant.StockOrderLot.IntradayOdd, 
    account=api.stock_account,
)

trade = api.place_order(contract, order)
trade

```

Out

```
Trade(
    contract=Stock(
        exchange=<Exchange.TSE: 'TSE'>, 
        code='0050', 
        symbol='TSE0050', 
        name='元大台灣50', 
        category='00', 
        limit_up=115.8, 
        limit_down=94.8, 
        eference=105.3, 
        update_date='2020/09/21', 
        margin_trading_balance=15390, 
        short_selling_balance=2, 
        day_trade=<DayTrade.Yes: 'Yes'>
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=90.0, 
        quantity=10, 
        id='38e68afe', 
        seqno='482283', 
        ordno='WA313', 
        account=Account(
            account_type=<AccountType.Stock: 'S'>, 
            person_id='YOUR_PERSON_ID', 
            broker_id='9A95', 
            account_id='0506112', 
            signed=True
        ), 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>, 
        order_lot=<StockOrderLot.IntradayOdd: 'IntradayOdd'>
    ), 
    status=OrderStatus(
        id='38e68afe', 
        status=<Status.Submitted: 'Submitted'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2020, 9, 21, 14, 38, 51), 
        deals=[]
    )
)

```

### 改單

注意

**零股不能進行改價**

`update_order` 只能用來**減少**原委託單的委託數量。

改量(減量)

```
api.update_order(trade=trade, qty=2)
api.update_status(api.stock_account)
trade

```

Out

```
Trade(
    contract=Stock(
        exchange=<Exchange.TSE: 'TSE'>, 
        code='0050', 
        symbol='TSE0050', 
        name='元大台灣50', 
        category='00', 
        limit_up=115.8, 
        limit_down=94.8, 
        reference=105.3, 
        update_date='2020/09/21', 
        margin_trading_balance=15390, 
        short_selling_balance=2, 
        day_trade=<DayTrade.Yes: 'Yes'>
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=90.0, 
        quantity=10, 
        id='9b44c3b2', 
        seqno='482293', 
        ordno='WA328', 
        account=Account(
            account_type=<AccountType.Stock: 'S'>, 
            person_id='YOUR_PERSON_ID', 
            broker_id='9A95', 
            account_id='0506112', 
            signed=True
        ), 
    price_type=<StockPriceType.LMT: 'LMT'>, 
    order_type=<OrderType.ROD: 'ROD'>, 
    order_lot=<StockOrderLot.IntradayOdd: 'IntradayOdd'>), 
    status=OrderStatus(
        id='9b44c3b2', 
        status=<Status.Submitted: 'Submitted'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2020, 9, 21, 14, 54, 36), 
        cancel_quantity=2, 
        deals=[]
    )
)

```

### 刪單

刪單

```
api.cancel_order(trade)
api.update_status(api.stock_account)
trade

```

Out

```
Trade(
    contract=Stock(
        exchange=<Exchange.TSE: 'TSE'>, 
        code='0050', 
        symbol='TSE0050', 
        name='元大台灣50', 
        category='00', 
        limit_up=115.8, 
        limit_down=94.8, 
        reference=105.3, 
        update_date='2020/09/21', 
        margin_trading_balance=15390, 
        short_selling_balance=2, 
        day_trade=<DayTrade.Yes: 'Yes'>
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=90.0, 
        quantity=10, 
        id='9b44c3b2', 
        seqno='482293', 
        ordno='WA328', 
        account=Account(
            account_type=<AccountType.Stock: 'S'>, 
            person_id='YOUR_PERSON_ID', 
            broker_id='9A95', 
            account_id='0506112', 
            signed=True
        ), 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>, 
        order_lot=<StockOrderLot.IntradayOdd: 'IntradayOdd'>
    ), 
    status=OrderStatus(
        id='9b44c3b2', 
        status=<Status.Cancelled: 'Cancelled'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2020, 9, 21, 14, 54, 36), 
        cancel_quantity=10,
        deals=[]
    )
)

```

當現貨觸發一些交易異常條件，需先預收券款。異常條件包括: 注意股票、警示股票、處置股票及管理股票。

提醒

- 必須先[登入](../../login/)及啟用[憑證](../../prepare/terms/)。
- 服務時間為交易日8:00~14:30。

### 查詢圈券狀態

In

```
reserve_summary_resp = api.stock_reserve_summary(account)

```

Out

```
ReserveStocksSummaryResponse(
    response=ReserveStocksSummary(
        stocks=[
            ReserveStockSummary(
                contract=Contract(
                    security_type=<SecurityType.Stock: 'STK'>, 
                    exchange=<Exchange.TSE: 'TSE'>, 
                    code='2890', 
                    name='永豐金'
                ),
                available_share=5000, 
                reserved_share=0
            )
        ], 
        account=StockAccount(
            person_id='X123456789', 
            broker_id='9A95', 
            account_id='12345678', 
            signed=True
            )
        )
    )

```

### 借券圈券申請

In

```
contract = api.Contracts.Stocks["2890"]
resp = api.reserve_stock(account, contract, 1000)

```

Out

```
ReserveStockResponse(
    response=ReserveOrderResp(
        contract=Stock(
            exchange=<Exchange.TSE: 'TSE'>, 
            code='2890', 
            symbol='TSE2890', 
            name='永豐金'
        ), 
        account=StockAccount(
            person_id='X123456789', 
            broker_id='9A95', 
            account_id='12345678', 
            signed=True), 
        share=1000, 
        status=True, 
        info=''
    )
)

```

### 查詢圈券明細

In

```
resp = api.stock_reserve_detail(account)

```

Out

```
ReserveStocksDetailResponse(
    response=ReserveStocksDetail(stocks=[
            ReserveStockDetail(
                contract=Contract(
                    security_type=<SecurityType.Stock: 'STK'>, 
                    exchange=<Exchange.TSE: 'TSE'>, 
                    code='6153', 
                    name='嘉聯益'
                ), 
                share=1000, 
                order_ts=1638253253, 
                status=True, 
                info='已完成'
            )
        ], 
        account=StockAccount(
            person_id='X123456789', 
            broker_id='9A95', 
            account_id='12345678', 
            signed=True)
        )
)

```

### 預收款項申請

In

```
contract = api.Contracts.Stocks["2890"]
resp = api.reserve_earmarking(account, contract, 1000, 15.15)

```

Out

```
ReserveEarmarkingResponse(
    response=EarmarkingOrderResp(
        contract=Stock(
            exchange=<Exchange.TSE: 'TSE'>, 
            code='2890', 
            symbol='TSE2890', 
            name='永豐金', 
        ), 
        account=StockAccount(
            person_id='X123456789', 
            broker_id='9A95', 
            account_id='12345678', 
            signed=True)
        ), 
        share=1000, 
        price=15.15, 
        status=True, 
        info='OK')
)

```

### 查詢預收款項

In

```
api.earmarking_detail(account)

```

Out

```
EarmarkStocksDetailResponse(
    response=EarmarkStocksDetail(
        stocks=[
            EarmarkStockDetail(
                contract=Contract(
                    security_type=<SecurityType.Stock: 'STK'>, 
                    exchange=<Exchange.TSE: 'TSE'>, 
                    code='2890', 
                    name='永豐金'
                ), 
                share=1000, 
                price=15.15, 
                amount=15171, 
                order_ts=1638416488, 
                status=False, 
                info='扣款失敗'), 
            EarmarkStockDetail(
                contract=Contract(
                    security_type=<SecurityType.Stock: 'STK'>, 
                    exchange=<Exchange.TSE: 'TSE'>, 
                    code='2890', 
                    name='永豐金'
                ), 
                share=1000, 
                price=15.15, 
                amount=15171, 
                order_ts=1638415662, status=True, 
                info='')
            ], 
            account=StockAccount(
                person_id='X123456789', 
                broker_id='9A95', 
                account_id='12345678', 
                signed=True)
            )
        )
    )

```

### 範例

查詢所有名下帳號的圈券狀態

In

```
import shioaji as sj

api = sj.Shioaji()
accounts = api.login("YOUR_PERSON_ID", "YOUR_PASSWORD", contracts_timeout=10000)
api.activate_ca(
    ca_path="/c/your/ca/path/Sinopac.pfx",
    ca_passwd="YOUR_CA_PASSWORD",
    person_id="Person of this Ca",
)
for account in accounts:
    if account.account_type == AccountType.Stock:
        reserve_summary_resp = api.stock_reserve_summary(account)
        for reserve_stock_summary in reserve_summary_resp.response.stocks:
                if reserve_stock_summary.available_share:
                    resp = api.reserve_stock(
                        account, 
                        reserve_stock_summary.contract,
                        reserve_stock_summary.available_share
                    )

```

提醒

下單前必須先[登入](../../login/)及啟用[憑證](../../prepare/terms/)。

### 證券委託單

證券委託單

```
price (float or int): 價格
quantity (int): 委託數量
action (str): {Buy: 買, Sell: 賣}
price_type (str): {LMT: 限價, MKT: 市價, MKP: 範圍市價}
order_type (str): 委託類別 {ROD, IOC, FOK}
order_cond (str): {Cash:現股, MarginTrading:融資, ShortSelling:融券}
order_lot (str): {
        Common:整股, 
        Fixing:定盤, 
        Odd:盤後零股, 
        IntradayOdd:盤中零股
    }
daytrade_short (bool): 先賣後買
custom_field (str): 備註，只允許輸入大小寫英文字母及數字，且長度最長為 6
account (:obj:Account): 下單帳號
ca (binary): 憑證

```

```
price (float or int): 價格
quantity (int): 委託數量
action (str): {Buy: 買, Sell: 賣}
price_type (str): {LMT: 限價, MKT: 市價, MKP: 範圍市價}
order_type (str): 委託類別 {ROD, IOC, FOK}
order_cond (str): {Cash:現股, MarginTrading:融資, ShortSelling:融券}
order_lot (str): {
        Common:整股, 
        Fixing:定盤, 
        Odd:盤後零股, 
        IntradayOdd:盤中零股
    }
first_sell (str): 先賣後買 {true, false}
custom_field (str): 備註，只允許輸入大小寫英文字母及數字，且長度最長為 6
account (:obj:Account): 下單帳號
ca (binary): 憑證

```

### 下單

下單時必須提供商品資訊`contract`及下單資訊`order`。

下單

```
api.place_order?

    Signature:
        api.place_order(
            contract: shioaji.contracts.Contract,
            order: shioaji.order.Order,
            timeout: int = 5000,
            cb: Callable[[shioaji.order.Trade], NoneType] = None,
        ) -> shioaji.order.Trade
    Docstring:
    placing order

```

商品檔

```
contract = api.Contracts.Stocks.TSE.TSE2890

```

委託單

```
order = api.Order(
    price=17, 
    quantity=3, 
    action=sj.constant.Action.Buy, 
    price_type=sj.constant.StockPriceType.LMT, 
    order_type=sj.constant.OrderType.ROD, 
    order_lot=sj.constant.StockOrderLot.Common, 
    # daytrade_short=False,
    custom_field="test",
    account=api.stock_account
)

```

```
order = api.Order(
    price=17, 
    quantity=3, 
    action=sj.constant.Action.Buy, 
    price_type=sj.constant.TFTStockPriceType.LMT, 
    order_type=sj.constant.TFTOrderType.ROD, 
    order_lot=sj.constant.TFTStockOrderLot.Common, 
    # first_sell=sj.constant.StockFirstSell.No,
    custom_field="test",
    account=api.stock_account
)

```

下單

```
trade = api.place_order(contract, order)
trade

```

Out

```
Trade(
    contract=Stock(
        exchange=<Exchange.TSE: 'TSE'>, 
        code='2890', 
        symbol='TSE2890', 
        name='永豐金', 
        category='17', 
        unit=1000, 
        limit_up=19.05, 
        limit_down=15.65, 
        reference=17.35, 
        update_date='2023/01/12',
        day_trade=<DayTrade.Yes: 'Yes'>
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=17, 
        quantity=3, 
        id='531e27af', 
        seqno='000002', 
        ordno='000001', 
        account=Account(
            account_type=<AccountType.Stock: 'S'>,
            person_id='A123456789', 
            broker_id='9A95', 
            account_id='1234567', 
            signed=True
        ), 
        custom_field='test', 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>, 
        daytrade_short=False
    ), 
    status=OrderStatus(
        id='531e27af', 
        status=<Status.PendingSubmit: 'PendingSubmit'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 11, 18, 3, 867490), 
        deals=[]
    )
)

```

下單完同時也會收到從交易所傳回來的資料，詳情內容可詳見[下單回報](../order_deal_event/stocks/)。

您需要執行`update_status`已更新`trade`物件的狀態。

更新委託狀態(成交後)

```
api.update_status(api.stock_account)
trade

```

Out

```
Trade(
    contract=Stock(
        exchange=<Exchange.TSE: 'TSE'>, 
        code='2890', 
        symbol='TSE2890', 
        name='永豐金', 
        category='17', 
        unit=1000, 
        limit_up=19.05, 
        limit_down=15.65, 
        reference=17.35, 
        update_date='2023/01/12',
        day_trade=<DayTrade.Yes: 'Yes'>
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=17, 
        quantity=3, 
        id='531e27af', 
        seqno='000002', 
        ordno='000001', 
        account=Account(
            account_type=<AccountType.Stock: 'S'>,
            person_id='A123456789', 
            broker_id='9A95', 
            account_id='1234567', 
            signed=True
        ), 
        custom_field='test', 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>, 
        daytrade_short=False
    ), 
    status=OrderStatus(
        id='531e27af', 
        status=<Status.Submitted: 'Submitted'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 11, 18, 3, 867490), 
        order_quantity=3,
        deals=[]
    )
)

```

委託單狀態

- `PendingSubmit`: 傳送中
- `PreSubmitted`: 預約單
- `Submitted`: 傳送成功
- `Failed`: 失敗
- `Cancelled`: 已刪除
- `Filled`: 完全成交
- `PartFilled`: 部分成交

### 改單

改單

```
api.update_order?

    Signature:
        api.update_order(
            trade: shioaji.order.Trade,
            price: Union[pydantic.types.StrictInt, float] = None,
            qty: int = None,
            timeout: int = 5000,
            cb: Ca  lable[[shioaji.order.Trade], NoneType] = None,
        ) -> shioaji.order.Trade
    Docstring: update the order price or qty

```

#### 改價

改價

```
api.update_order(trade=trade, price=17.5)
api.update_status(api.stock_account)
trade

```

Out

```
Trade(
    contract=Stock(
        exchange=<Exchange.TSE: 'TSE'>, 
        code='2890', 
        symbol='TSE2890', 
        name='永豐金', 
        category='17', 
        unit=1000, 
        limit_up=19.05, 
        limit_down=15.65, 
        reference=17.35, 
        update_date='2023/01/12',
        day_trade=<DayTrade.Yes: 'Yes'>
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=17, 
        quantity=3, 
        id='531e27af', 
        seqno='000002', 
        ordno='000001', 
        account=Account(
            account_type=<AccountType.Stock: 'S'>,
            person_id='A123456789', 
            broker_id='9A95', 
            account_id='1234567', 
            signed=True
        ), 
        custom_field='test', 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>, 
        daytrade_short=False
    ), 
    status=OrderStatus(
        id='531e27af', 
        status=<Status.Submitted: 'Submitted'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 11, 18, 3, 867490), 
        modified_price=17.5,
        order_quantity=3,
        deals=[]
    )
)

```

#### 改量(減量)

`update_order` 只能用來**減少**原委託單的委託數量。

改量(減量)

```
api.update_order(trade=trade, qty=1)
api.update_status(api.stock_account)
trade

```

Out

```
Trade(
    contract=Stock(
        exchange=<Exchange.TSE: 'TSE'>, 
        code='2890', 
        symbol='TSE2890', 
        name='永豐金', 
        category='17', 
        unit=1000, 
        limit_up=19.05, 
        limit_down=15.65, 
        reference=17.35, 
        update_date='2023/01/12',
        day_trade=<DayTrade.Yes: 'Yes'>
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=17, 
        quantity=3, 
        id='531e27af', 
        seqno='000002', 
        ordno='000001', 
        account=Account(
            account_type=<AccountType.Stock: 'S'>,
            person_id='A123456789', 
            broker_id='9A95', 
            account_id='1234567', 
            signed=True
        ), 
        custom_field='test', 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>, 
        daytrade_short=False
    ), 
    status=OrderStatus(
        id='531e27af', 
        status=<Status.Submitted: 'Submitted'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 11, 18, 3, 867490), 
        order_quantity=3,
        cancel_quantity=1,
        deals=[]
    )
)

```

### 刪單

刪單

```
api.cancel_order(trade)
api.update_status(api.stock_account)
trade

```

Out

```
Trade(
    contract=Stock(
        exchange=<Exchange.TSE: 'TSE'>, 
        code='2890', 
        symbol='TSE2890', 
        name='永豐金', 
        category='17', 
        unit=1000, 
        limit_up=19.05, 
        limit_down=15.65, 
        reference=17.35, 
        update_date='2023/01/12',
        day_trade=<DayTrade.Yes: 'Yes'>
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=17, 
        quantity=3, 
        id='531e27af', 
        seqno='000002', 
        ordno='000001', 
        account=Account(
            account_type=<AccountType.Stock: 'S'>,
            person_id='A123456789', 
            broker_id='9A95', 
            account_id='1234567', 
            signed=True
        ), 
        custom_field='test', 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>, 
        daytrade_short=False
    ), 
    status=OrderStatus(
        id='531e27af', 
        status=<Status.Cancelled: 'Cancelled'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 11, 18, 3, 867490), 
        order_quantity=3,
        cancel_quantity=3,
        deals=[]
    )
)

```

### 成交

更新委託狀態

```
api.update_status(api.stock_account)
trade

```

Out

```
Trade(
    contract=Stock(
        exchange=<Exchange.TSE: 'TSE'>, 
        code='2890', 
        symbol='TSE2890', 
        name='永豐金', 
        category='17', 
        unit=1000, 
        limit_up=19.05, 
        limit_down=15.65, 
        reference=17.35, 
        update_date='2023/01/12',
        day_trade=<DayTrade.Yes: 'Yes'>
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=17, 
        quantity=3, 
        id='531e27af', 
        seqno='000002', 
        ordno='000001', 
        account=Account(
            account_type=<AccountType.Stock: 'S'>,
            person_id='A123456789', 
            broker_id='9A95', 
            account_id='1234567', 
            signed=True
        ), 
        custom_field='test', 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>, 
        daytrade_short=False
    ), 
    status=OrderStatus(
        id='531e27af', 
        status=<Status.Filled: 'Filled'>,
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 11, 18, 3, 867490), 
        order_quantity=3,
        deals=[
            Deal(seq='000001', price=17, quantity=3, ts=1673501631.62918)
        ]
    )
)

```

