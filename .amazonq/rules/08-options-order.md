## 下單

組合單提供類型包括:**價格價差**、**時間價差**、**跨式**、**勒式**、**轉換**以及**逆轉**。組合規則詳見期交所[文件](https://www.taifex.com.tw/cht/5/margingReqIndexOpt)。

place_comboorder

```
api.place_comboorder?

    Signature:
        api.place_comboorder(
            combo_contract: shioaji.contracts.ComboContract,
            order: shioaji.order.ComboOrder,
            timeout: int = 5000,
            cb: Callable[[shioaji.order.ComboTrade], NoneType] = None,
        )
    Docstring:
        placing combo order

```

下單時必須提供商品資訊`contract`及下單資訊`order`。商品資訊無關前後順序，只需提供認可的組合。

商品資訊

```
contract_1 = api.Contracts.Options.TX4.TX4202111017850C
contract_2 = api.Contracts.Options.TX4.TX4202111017850P
combo_contract = sj.contracts.ComboContract(
    legs=[
        sj.contracts.ComboBase(action="Sell", **contract_1.dict()),
        sj.contracts.ComboBase(action="Sell", **contract_2.dict()),
    ]
)

```

下單資訊

```
order = api.ComboOrder(
    price_type="LMT", 
    price=1, 
    quantity=1, 
    order_type="IOC",
    octype=sj.constant.FuturesOCType.New,
)

```

In

```
trade = api.place_comboorder(combo_contract, order)

```

## 刪單

`trade`為要刪的單，可從[查詢](#_3)取得。

In

```
api.cancel_comboorder(trade)

```

## 查詢狀態

如同 `list_trades` 及 `update_status` 的概念。在取得組合單狀態前，必須利用 `update_combostatus` 更新狀態。

In

```
api.update_combostatus()
api.list_combotrades()

```

Out

```
[
    ComboTrade(
        contract=ComboContract(
            legs=[
                ComboBase(
                    security_type=<SecurityType.Option: 'OPT'>, 
                    exchange=<Exchange.TAIFEX: 'TAIFEX'>, 
                    code='TX516000L1', 
                    symbol='TX5202112016000C', 
                    name='臺指選擇權12W5月 16000C', 
                    category='TX5', 
                    delivery_month='202112', 
                    delivery_date='2021/12/29', 
                    strike_price=16000.0, 
                    option_right=<OptionRight.Call: 'C'>, 
                    underlying_kind='I', 
                    unit=1, 
                    limit_up=3630.0, 
                    limit_down=68.0, 
                    reference=1850.0, 
                    update_date='2021/12/23', 
                    action=<Action.Sell: 'Sell'>), 
                ComboBase(
                    security_type=<SecurityType.Option: 'OPT'>, 
                    exchange=<Exchange.TAIFEX: 'TAIFEX'>, 
                    code='TX516000X1', 
                    symbol='TX5202112016000P', 
                    name='臺指選擇權12W5月 16000P', 
                    category='TX5', 
                    delivery_month='202112',
                    delivery_date='2021/12/29',
                    strike_price=16000.0, 
                    option_right=<OptionRight.Put: 'P'>, 
                    underlying_kind='I', 
                    unit=1, 
                    limit_up=1780.0, 
                    limit_down=0.1, 
                    reference=0.9, 
                    update_date='2021/12/23', 
                    action=<Action.Sell: 'Sell'>)
                ]
            ), 
        order=Order(
            action=<Action.Sell: 'Sell'>, 
            price=1.0,
            quantity=1, 
            id='46989de8', 
            seqno='743595', 
            ordno='000000', 
            account=Account(
                account_type=<AccountType.Future: 'F'>, 
                person_id='YOUR_PERSON_ID', 
                broker_id='F002000', 
                account_id='1234567', 
                signed=True
            ), 
            price_type=<StockPriceType.LMT: 'LMT'>, 
            order_type=<OrderType.IOC: 'IOC'>, 
            octype=<FuturesOCType.New: 'New'>
        ), 
        status=ComboStatus(
            id='46989de8', 
            status=<Status.Failed: 'Failed'>, 
            status_code='99Q9', 
            order_datetime=datetime.datetime(2021, 12, 23, 8, 46, 47), 
            msg='可委託金額不足', 
            modified_price=1.0, 
            deals={}
        )
    )
]

```

提醒

下單前必須先[登入](../../login/)及啟用[憑證](../../prepare/terms/)。

### 期貨委託單

期貨委託單

```
price (float or int): 價格
quantity (int): 委託數量
action (str): {Buy: 買, Sell: 賣}
price_type (str): {LMT: 限價, MKT: 市價, MKP: 範圍市價}
order_type (str): 委託類別 {ROD, IOC, FOK}
octype (str): {Auto: 自動, New: 新倉, Cover: 平倉, DayTrade: 當沖} 
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
contract = api.Contracts.Futures.TXF.TXF202301

```

委託單

```
order = api.Order(
    action=sj.constant.Action.Buy,
    price=14400,
    quantity=3,
    price_type=sj.constant.FuturesPriceType.LMT,
    order_type=sj.constant.OrderType.ROD, 
    octype=sj.constant.FuturesOCType.Auto,
    account=api.futopt_account
)

```

```
order = api.Order(
    action=sj.constant.Action.Buy,
    price=14400,
    quantity=3,
    price_type=sj.constant.FuturesPriceType.LMT,
    order_type=sj.constant.FuturesOrderType.ROD, 
    octype=sj.constant.FuturesOCType.Auto,
    account=api.futopt_account
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
    contract=Future(
        code='TXFA3', 
        symbol='TXF202301', 
        name='臺股期貨01', 
        category='TXF', 
        delivery_month='202301', 
        delivery_date='2023/01/30', 
        underlying_kind='I', 
        unit=1, 
        limit_up=16270.0, 
        limit_down=13312.0, 
        reference=14791.0, 
        update_date='2023/01/12'
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=14400, 
        quantity=3, 
        id='5efffde1', 
        seqno='000004', 
        ordno='000003', 
        account=Account(
            account_type=<AccountType.Future: 'F'>,
            person_id='A123456789', 
            broker_id='F002000', 
            account_id='1234567', 
            signed=True
        ), 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>
    ), 
    status=OrderStatus(
        id='5efffde1', 
        status=<Status.PendingSubmit: 'PendingSubmit'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 14, 56, 13, 995651), 
        deals=[]
    )
)

```

下單完同時也會收到從交易所傳回來的資料，詳情內容可詳見[下單回報](../order_deal_event/stocks/)。

您需要執行`update_status`已更新`trade`物件的狀態。

更新委託狀態

```
api.update_status(api.futopt_account)
trade

```

Out

```
Trade(
    contract=Future(
        code='TXFA3', 
        symbol='TXF202301', 
        name='臺股期貨01', 
        category='TXF', 
        delivery_month='202301', 
        delivery_date='2023/01/30', 
        underlying_kind='I', 
        unit=1, 
        limit_up=16270.0, 
        limit_down=13312.0, 
        reference=14791.0, 
        update_date='2023/01/12'
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=14400, 
        quantity=3, 
        id='5efffde1', 
        seqno='000004', 
        ordno='000003', 
        account=Account(
            account_type=<AccountType.Future: 'F'>,
            person_id='A123456789', 
            broker_id='F002000', 
            account_id='1234567', 
            signed=True
        ), 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>
    ), 
    status=OrderStatus(
        id='5efffde1', 
        status=<Status.Submitted: 'Submitted'>,
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 14, 56, 13, 995651), 
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
api.update_order(trade=trade, price=14450)
api.update_status(api.futopt_account)
trade

```

Out

```
Trade(
    contract=Future(
        code='TXFA3', 
        symbol='TXF202301', 
        name='臺股期貨01', 
        category='TXF', 
        delivery_month='202301', 
        delivery_date='2023/01/30', 
        underlying_kind='I', 
        unit=1, 
        limit_up=16270.0, 
        limit_down=13312.0, 
        reference=14791.0, 
        update_date='2023/01/12'
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=14400, 
        quantity=3, 
        id='5efffde1', 
        seqno='000004', 
        ordno='000003', 
        account=Account(
            account_type=<AccountType.Future: 'F'>,
            person_id='A123456789', 
            broker_id='F002000', 
            account_id='1234567', 
            signed=True
        ), 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>
    ), 
    status=OrderStatus(
        id='5efffde1', 
        status=<Status.Submitted: 'Submitted'>,
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 14, 56, 13, 995651), 
        modified_price=14450,
        order_quantity=3,
        deals=[]
    )
)

```

#### 改量(減量)

`update_order` 只能用來**減少**原委託單的委託數量。    qty 為目標剩餘口數（非取消數量），只能減少不能增加。    例如：原委託 3 口，qty=1 → 剩 1 口（自動取消 2 口）    ⚠️ Shioaji 文件說「減少數量」易誤解，實際為目標剩餘量。
    
改量(減量)

```
api.update_order(trade=trade, qty=1)
api.update_status(api.futopt_account)
trade

```

Out

```
Trade(
    contract=Future(
        code='TXFA3', 
        symbol='TXF202301', 
        name='臺股期貨01', 
        category='TXF', 
        delivery_month='202301', 
        delivery_date='2023/01/30', 
        underlying_kind='I', 
        unit=1, 
        limit_up=16270.0, 
        limit_down=13312.0, 
        reference=14791.0, 
        update_date='2023/01/12'
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=14400, 
        quantity=3, 
        id='5efffde1', 
        seqno='000004', 
        ordno='000003', 
        account=Account(
            account_type=<AccountType.Future: 'F'>,
            person_id='A123456789', 
            broker_id='F002000', 
            account_id='1234567', 
            signed=True
        ), 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>
    ), 
    status=OrderStatus(
        id='5efffde1', 
        status=<Status.Submitted: 'Submitted'>,
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 14, 56, 13, 995651), 
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
api.update_status(api.futopt_account)
trade

```

Out

```
Trade(
    contract=Future(
        code='TXFA3', 
        symbol='TXF202301', 
        name='臺股期貨01', 
        category='TXF', 
        delivery_month='202301', 
        delivery_date='2023/01/30', 
        underlying_kind='I', 
        unit=1, 
        limit_up=16270.0, 
        limit_down=13312.0, 
        reference=14791.0, 
        update_date='2023/01/12'
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=14400, 
        quantity=3, 
        id='5efffde1', 
        seqno='000004', 
        ordno='000003', 
        account=Account(
            account_type=<AccountType.Future: 'F'>,
            person_id='A123456789', 
            broker_id='F002000', 
            account_id='1234567', 
            signed=True
        ), 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>
    ), 
    status=OrderStatus(
        id='5efffde1', 
        status=<Status.Cancelled: 'Cancelled'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 14, 56, 13, 995651), 
        order_quantity=3,
        cancel_quantity=3,
        deals=[]
    )
)

```

### 成交

更新委託狀態(成交後)

```
api.update_status(api.futopt_account)
trade

```

Out

```
Trade(
    contract=Future(
        code='TXFA3', 
        symbol='TXF202301', 
        name='臺股期貨01', 
        category='TXF', 
        delivery_month='202301', 
        delivery_date='2023/01/30', 
        underlying_kind='I', 
        unit=1, 
        limit_up=16270.0, 
        limit_down=13312.0, 
        reference=14791.0, 
        update_date='2023/01/12'
    ), 
    order=Order(
        action=<Action.Buy: 'Buy'>, 
        price=14400, 
        quantity=3, 
        id='5efffde1', 
        seqno='000004', 
        ordno='000003', 
        account=Account(
            account_type=<AccountType.Future: 'F'>,
            person_id='A123456789', 
            broker_id='F002000', 
            account_id='1234567', 
            signed=True
        ), 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>
    ), 
    status=OrderStatus(
        id='5efffde1', 
        status=<Status.Filled: 'Filled'>,
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 14, 56, 13, 995651), 
        order_quantity=3,
        deals=[
            Deal(seq='000001', price=14400, quantity=3, ts=1673501631.62918)
        ]
    )
)

```

