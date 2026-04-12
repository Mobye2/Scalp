## 範例

[證券下單範例 ( jupyter)](https://nbviewer.jupyter.org/github/Sinotrade/Sinotrade.github.io/blob/master/tutorial/stock.ipynb)

### 買賣別

買

```
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Buy, 
    price_type=sj.constant.StockPriceType.LMT, 
    order_type=sj.constant.OrderType.ROD, 
    order_lot=sj.constant.StockOrderLot.Common, 
    custom_field="test",
    account=api.stock_account
)

```

賣

```
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Sell, 
    price_type=sj.constant.StockPriceType.LMT, 
    order_type=sj.constant.OrderType.ROD, 
    order_lot=sj.constant.StockOrderLot.Common, 
    custom_field="test",
    account=api.stock_account
)

```

Daytrade Short

```
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Sell,
    price_type=sj.constant.StockPriceType.LMT,
    order_type=sj.constant.OrderType.ROD,
    order_lot=sj.constant.StockOrderLot.Common,
    daytrade_short=True,
    custom_field="test",
    account=api.stock_account
)

```

```
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Sell,
    price_type=sj.constant.TFTStockPriceType.LMT, 
    order_type=sj.constant.TFTOrderType.ROD, 
    order_lot=sj.constant.TFTStockOrderLot.Common, 
    first_sell=sj.constant.StockFirstSell.Yes,
    custom_field="test",
    account=api.stock_account
)

```

### ROD + LMT

ROD + LMT

```
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Sell,
    price_type=sj.constant.StockPriceType.LMT,
    order_type=sj.constant.OrderType.ROD,
    order_lot=sj.constant.StockOrderLot.Common,
    custom_field="test",
    account=api.stock_account
)

```

```
order = api.Order(
    price=12, 
    quantity=1, 
    action=sj.constant.Action.Sell,
    price_type=sj.constant.TFTStockPriceType.LMT, 
    order_type=sj.constant.TFTOrderType.ROD, 
    order_lot=sj.constant.TFTStockOrderLot.Common, 
    custom_field="test",
    account=api.stock_account
)

```

提醒

必須先[登入](../../login/)及啟用[憑證](../../prepare/terms/)。

在取得 `Trade` 狀態前，必須先利用`update_status`進行更新。如果無法成功刪單或改單，你可以對特定`trade`物件進行更新，並確認在`trade`中的`OrderStatus`，是否為可刪改狀態。`update_status` 預設查詢為名下所有帳號。若想查詢特定帳號，將帳號帶入`account`。

Update Status

```
api.update_status?

```

Out

```
Signature:
    api.update_status(
        account: shioaji.account.Account = None,
        trade: shioaji.order.Trade = None,
        timeout: int = 5000,
        cb: Callable[[List[shioaji.order.Trade]], NoneType] = None,
    )
Docstring: update status of all trades you have

```

### 取得證券委託狀態

取得證券委託狀態

```
api.update_status(api.stock_account)
api.list_trades()

```

Out

```
[
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
            daytrade_short=True
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
]

```

### 取得期貨委託狀態

取得期貨委託狀態

```
api.update_status(api.futopt_account)
api.list_trades()

```

Out

```
[
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
]

```

### 更新特定交易狀態

更新特定交易狀態

```
# you can get trade from place_order
# trade = api.place_order(contract, order)

# or get from api.list_trades
# trade = api.list_trades()[0]

api.update_status(trade=trade)

```

### 委託及成交狀態屬性

委託狀態屬性

```
id (str): 關聯Order物件編碼
status (:obj:Status): {
            Cancelled: 已刪除, 
            Filled: 完全成交, 
            PartFilled: 部分成交, 
            Failed: 失敗, 
            PendingSubmit: 傳送中, 
            PreSubmitted: 預約單, 
            Submitted: 傳送成功
        }
status_code (str): 狀態碼
order_datetime (datetime): 委託時間
order_quantity (int): 委託數量
modified_price (float): 改價金額
cancel_quantity (int): 取消委託數量
deals (:List:Deal): 成交資訊

```

成交屬性

```
seq (str): 成交序號
price (int or float): 成交價
quantity (int): 成交數量
ts (float): 成交時間戳

```

### 委託回報

當期交所收到委託將會回傳回報。在回報中分為四部分，包括operation、order、status及contract。以下我們會在進行詳細的說明。

委託回報

```
OrderState.FuturesOrder {
    'operation': {
        'op_type': 'New', 
        'op_code': '00', 
        'op_msg': ''
    }, 
    'order': {
        'id': 'fcb42a6e', 
        'seqno': '585886', 
        'ordno': '00', 
        'account': {
            'account_type': 'F', 
            'person_id': '', 
            'broker_id': 'F002000', 
            'account_id': '1234567', 
            'signed': True
        }, 
        'action': 'Buy', 
        'price': 27000.0, 
        'quantity': 1, 
        'order_type': 'ROD', 
        'price_type': 'LMT', 
        'market_type': 'Night', 
        'oc_type': 'New', 
        'subaccount': '', 
        'combo': False
    }, 
    'status': {
        'id': 'fcb42a6e', 
        'exchange_ts': 1764731566.0, 
        'modified_price': 0.0, 
        'cancel_quantity': 0, 
        'order_quantity': 1, 
        'web_id': 'Z'
    }, 
    'contract': {
        'security_type': 'FUT', 
        'code': 'TXF', 
        'full_code': 'TXFL5', 
        'exchange': 'TIM', 
        'delivery_month': '202512', 
        'delivery_date': '', 
        'strike_price': 0.0, 
        'option_right': 'Future'
    }
}

```

```
OrderState.FOrder {
    'operation': {
        'op_type': 'New', 
        'op_code': '00', 
        'op_msg': ''
    }, 
    'order': {
        'id': 'fcb42a6e', 
        'seqno': '585886', 
        'ordno': '00', 
        'account': {
            'account_type': 'F', 
            'person_id': '', 
            'broker_id': 'F002000', 
            'account_id': '1234567', 
            'signed': True
        }, 
        'action': 'Buy', 
        'price': 27000.0, 
        'quantity': 1, 
        'order_type': 'ROD', 
        'price_type': 'LMT', 
        'market_type': 'Night', 
        'oc_type': 'New', 
        'subaccount': '', 
        'combo': False
    }, 
    'status': {
        'id': 'fcb42a6e', 
        'exchange_ts': 1764731566.0, 
        'modified_price': 0.0, 
        'cancel_quantity': 0, 
        'order_quantity': 1, 
        'web_id': 'Z'
    }, 
    'contract': {
        'security_type': 'FUT', 
        'code': 'TXF', 
        'full_code': 'TXFL5', 
        'exchange': 'TIM', 
        'delivery_month': '202301', 
        'delivery_date': '', 
        'strike_price': 0.0, 
        'option_right': 'Future'
    }
}

```

委託回報資訊

**operation**

```
op_type (str): {
        "New": 新單, 
        "Cancel": 刪單, 
        "UpdatePrice": 改價, 
        "UpdateQty": 改量
    }
op_code (str): {"00": 成功, others: 失敗}
op_msg (str): 錯誤訊息

```

**order**

```
id (str): 與成交回報的trade_id相同
seqno (str): 平台單號
ordno (str): 委託單號
account (dict): 帳號資訊
action (str): 買賣別
price (float or int): 委託價
quantity (int): 委託量
order_cond (str): {
            Cash: 現股, 
            MarginTrading: 融資, 
            ShortSelling: 融券
        }
order_type (str): 委託類別 {ROD, IOC, FOK}
price_type (str): {LMT: 限價, MKT: 市價, MKP: 範圍市價}
market_type (str): 市場別 {Day:日盤, Night:夜盤}
oc_type(str): {New: 新倉, Cover: 平倉, Auto: 自動}
subaccount(str): 子帳號
combo (bool): 是否為組合單

```

**status**

```
id (str): 與成交回報的trade_id相同
exchange_ts (int): 交易所時間
modified_price (float or int): 改價
cancel_quantity (int): 取消數量
order_quantity (int): 委託數量
web_id (str): 下單平台代碼

```

**contract**

```
security_type (str): 商品類別
code (str): 商品代碼
full_code (str): 商品代碼(含交割月份)
exchange (str): 交易所
delivery_month (str): 交割月份
delivery_date (str): 交割日期
strike_price (float): 履約價
option_right (str): {Future, OptionCall, OptionPut}

```

### 成交回報

當搓合成功，期交所會傳送成交回報告知。搓合成功包含部分成交以及完全成交，可以從委託回報中的`id`去對應成交回報中的`trade_id`去確認是否為同一筆委託單。

成交回報

```
OrderState.FuturesDeal {
    'trade_id': '4e6df0f6', 
    'seqno': '458545', 
    'ordno': 'tA0deX1O', 
    'exchange_seq': 'j5006396', 
    'broker_id': 'F002000', 
    'account_id': '1234567', 
    'action': 'Sell', 
    'code': 'TX1', 
    'full_code': 'TX127900L5',
    'price': 25.0, 
    'quantity': 1, 
    'subaccount': '', 
    'security_type': 'OPT', 
    'delivery_month': '202512', 
    'strike_price': 27900.0, 
    'option_right': 'OptionCall', 
    'market_type': 'Day', 
    'combo': False, 
    'ts': 1764685425.0
}

```

```
OrderState.FDeal {
    'trade_id': '4e6df0f6', 
    'seqno': '458545', 
    'ordno': 'tA0deX1O', 
    'exchange_seq': 'j5006396', 
    'broker_id': 'F002000', 
    'account_id': '1234567', 
    'action': 'Sell', 
    'code': 'TX1', 
    'full_code': 'TX127900L5',
    'price': 25.0, 
    'quantity': 1, 
    'subaccount': '', 
    'security_type': 'OPT', 
    'delivery_month': '202512', 
    'strike_price': 27900.0, 
    'option_right': 'OptionCall', 
    'market_type': 'Day', 
    'combo': False, 
    'ts': 1764685425.0
}

```

成交回報

```
trade_id (str): 與委託回報id相同
seqno (str): 平台單號
ordno (str): 前五碼為同委託回報委託單號，後三碼為同筆委託成交交易序號。
exchange_seq (str): 回報序號
broker_id (str): 分行代碼
account_id (str): 帳號
action (str): 買賣別
code (str): 商品代碼
full_code (str): 商品代碼(含交割月份)
price (float or int): 成交價
quantity (int): 成交量
subaccount (str): 子帳號
security_type (str): 商品類別
delivery_month (str): 交割月份
strike_price (float): 履約價
option_right (str): {Future, OptionCall, OptionPut}
market_type (str): {Day, Night}
ts (int): 成交時間戳    

```

注意

交易所回傳訊息優先順序成交回報大於委託回報，所以當委託立即成交可能會先收到成交回報。

### 回報處理

欲處理委託、成交回報，詳細可參見[Callback](../../../callback/orderdeal_event/)。

### 委託回報

當證交所收到委託將會回傳回報。在回報中分為四部分，包括operation、order、status及contract。以下我們會在進行詳細的說明。

委託回報

```
OrderState.StockOrder {
    'operation': {
        'op_type': 'New', 
        'op_code': '00', 
        'op_msg': ''
    }, 
    'order': {
        'id': '97b63e2f', 
        'seqno': '267677', 
        'ordno': 'IM394', 
        'account': {
            'account_type': 'S', 
            'person_id': '', 
            'broker_id': '9A95', 
            'account_id': '1234567', 
            'signed': True
        }, 
        'action': 'Buy', 
        'price': 16.0, 
        'quantity': 1, 
        'order_type': 'ROD', 
        'price_type': 'LMT', 
        'order_cond': 'Cash', 
        'order_lot': 'Common', 
        'custom_field': 'test'
    }, 
    'status': {
        'id': '97b63e2f', 
        'exchange_ts': 1673576134.038, 
        'modified_price': 0.0, 
        'cancel_quantity': 0, 
        'order_quantity': 1, 
        'web_id': '137'
    }, 
    'contract': {
        'security_type': 'STK', 
        'exchange': 'TSE', 
        'code': '2890', 
        'symbol': '', 
        'name': '', 
        'currency': 'TWD'
    }
}

```

```
OrderState.TFTOrder {
    'operation': {
        'op_type': 'New', 
        'op_code': '00', 
        'op_msg': ''
    }, 
    'order': {
        'id': '97b63e2f', 
        'seqno': '267677', 
        'ordno': 'IM394', 
        'account': {
            'account_type': 'S', 
            'person_id': '', 
            'broker_id': '9A95', 
            'account_id': '1234567', 
            'signed': True
        }, 
        'action': 'Buy', 
        'price': 16.0, 
        'quantity': 1, 
        'order_type': 'ROD', 
        'price_type': 'LMT', 
        'order_cond': 'Cash', 
        'order_lot': 'Common', 
        'custom_field': 'test'
    }, 
    'status': {
        'id': '97b63e2f', 
        'exchange_ts': 1673576134.038, 
        'modified_price': 0.0, 
        'cancel_quantity': 0, 
        'order_quantity': 1, 
        'web_id': '137'
    }, 
    'contract': {
        'security_type': 'STK', 
        'exchange': 'TSE', 
        'code': '2890', 
        'symbol': '', 
        'name': '', 
        'currency': 'TWD'
    }
}

```

委託回報資訊

**operation**

```
op_type (str): {
            "New": 新單, 
            "Cancel": 刪單, 
            "UpdatePrice": 改價, 
            "UpdateQty": 改量
        }
op_code (str): {"00": 成功, others: 失敗}
op_msg (str): 錯誤訊息

```

**order**

```
id (str): 與成交回報的trade_id相同
seqno (str): 平台單號
ordno (str): 委託單號
account (dict): 帳號資訊
action (str): 買賣別 {Buy, Sell}
price (float or int): 委託價格
quantity (int): 委託數量
order_type (str): 委託類別 {ROD, IOC, FOK}
price_type (str): {LMT: 限價, MKT: 市價, MKP: 範圍市價}
order_cond (str): {
            Cash: 現股, 
            MarginTrading: 融資, 
            ShortSelling: 融券
        }
order_lot (str): {
            Common: 整股, 
            Fixing: 定盤, 
            Odd: 盤後零股, 
            IntradayOdd: 盤中零股
        }
custom_field (str): 自訂欄位

```

**status**

```
id (str): 與成交回報的trade_id相同
exchange_ts (int): 交易所時間
modified_price (float or int): 改價
cancel_quantity (int): 取消數量
order_quantity (int): 委託數量
web_id (str): 下單平台代碼

```

**contract**

```
security_type (str): 商品類別
exchange (str): 交易所
code (str): 商品代碼
symbol (str): 符號
name (str): 商品名稱
currency (str): 幣別

```

### 成交回報

當搓合成功，證交所會傳送成交回報告知。搓合成功包含部分成交以及完全成交，可以從委託回報中的`id`去對應成交回報中的`trade_id`去確認是否為同一筆委託單。

成交回報

```
OrderState.StockDeal {
    'trade_id': '9c6ae2eb', 
    'seqno': '269866', 
    'ordno': 'IN497', 
    'exchange_seq': '669915', 
    'broker_id': '9A95', 
    'account_id': '1234567', 
    'action': 'Buy', 
    'code': '2890', 
    'order_cond': 'Cash', 
    'order_lot': 'IntradayOdd', 
    'price': 267.5, 
    'quantity': 3, 
    'web_id': '137', 
    'custom_field': 'test', 
    'ts': 1673577256.354
}

```

```
OrderState.TFTDeal {
    'trade_id': '9c6ae2eb', 
    'seqno': '269866', 
    'ordno': 'IN497', 
    'exchange_seq': '669915', 
    'broker_id': '9A95', 
    'account_id': '1234567', 
    'action': 'Buy', 
    'code': '2890', 
    'order_cond': 'Cash', 
    'order_lot': 'IntradayOdd', 
    'price': 267.5, 
    'quantity': 3, 
    'web_id': '137', 
    'custom_field': 'test', 
    'ts': 1673577256.354
}

```

成交回報

```
trade_id (str): 與委託回報id相同
seqno (str): 平台單號
ordno (str): 前五碼為同委託回報委託單號，後三碼為同筆委託成交交易序號。
exchange_seq (str): 回報序號
broker_id (str): 分行代碼
account_id (str): 帳號
action (str): 買賣別 {Buy, Sell}
code (str): 商品代碼
order_cond (str): {
            Cash: 現股, 
            MarginTrading: 融資, 
            ShortSelling: 融券
        }
order_lot (str): {
            Common: 整股, 
            Fixing: 定盤, 
            Odd: 盤後零股, 
            IntradayOdd: 盤中零股
        }
price (float or int): 成交價
quantity (int): 成交量
web_id (str): 平台代碼
custom_field (str): 自訂欄位
ts (int): 成交時間戳

```

注意

交易所回傳訊息優先順序成交回報大於委託回報，所以當委託立即成交可能會先收到成交回報。

### 回報處理

欲處理委託、成交回報，詳細可參見[Callback](../../../callback/orderdeal_event/)。

首先，我們延伸前面在環境建立章節使用 `uv` 建立的專案 `sj-trading` 來新增測試流程的部分。

這部分完整專案的程式碼可以參考 [sj-trading https://github.com/Sinotrade/sj-trading-demo](https://github.com/Sinotrade/sj-trading-demo)。

可以使用 `git` 將整個環境複製到本地就可以直接使用

下載專案

```
git clone https://github.com/Sinotrade/sj-trading-demo.git
cd sj-trading-demo

```

下面我們將一步一步的介紹如何新增測試流程。

### Shioaji 版本

獲取 Shioaji 版本資訊

新增版本資訊

在 `src/sj_trading/__init__.py` 新增

```
def show_version() -> str:
    print(f"Shioaji Version: {sj.__version__}")
    return sj.__version__

```

新增版本指令到專案

在 `pyproject.toml` 新增 `version` 的指令

```
[project.scripts]
version = "sj_trading:show_version"

```

執行 `uv run version` 就可以看到 Shioaji 的版本資訊

```
Shioaji Version: 1.2.0

```

### 現貨下單測試

新增下單測試檔案

在 `src/sj_trading` 新增檔案 `testing_flow.py`

新增以下內容

```
import shioaji as sj
from shioaji.constant import Action, StockPriceType, OrderType
import os

def testing_stock_ordering():
    # 測試環境登入
    api = sj.Shioaji(simulation=True)
    accounts = api.login(
        api_key=os.environ["API_KEY"],
        secret_key=os.environ["SECRET_KEY"],
    )
    # 顯示所有可用的帳戶
    print(f"Available accounts: {accounts}")
    api.activate_ca(
        ca_path=os.environ["CA_CERT_PATH"],
        ca_passwd=os.environ["CA_PASSWORD"],
    )

    # 準備下單的 Contract
    # 使用 2890 永豐金為例
    contract = api.Contracts.Stocks["2890"]
    print(f"Contract: {contract}")

    # 建立委託下單的 Order
    order = sj.order.StockOrder(
        action=Action.Buy, # 買進
        price=contract.reference, # 以平盤價買進
        quantity=1, # 下單數量
        price_type=StockPriceType.LMT, # 限價單
        order_type=OrderType.ROD, # 當日有效單
        account=api.stock_account, # 使用預設的帳戶
    )
    print(f"Order: {order}")

    # 送出委託單
    trade = api.place_order(contract=contract, order=order)
    print(f"Trade: {trade}")

    # 更新狀態
    api.update_status()
    print(f"Status: {trade.status}")

```

新增測試下單指令到專案

在 `pyproject.toml` 新增 `stock_testing` 的指令

```
[project.scripts]
stock_testing = "sj_trading.testing_flow:testing_stock_ordering"

```

執行 `uv run stock_testing` 就開始進行測試下單了

### 期貨下單測試

新增期貨下單測試

在 `src/sj_trading/testing_flow.py` 新增以下內容

```
from shioaji.constant import (
    FuturesPriceType,
    FuturesOCType,
)

def testing_futures_ordering():
    # 測試環境登入
    api = sj.Shioaji(simulation=True)
    accounts = api.login(
        api_key=os.environ["API_KEY"],
        secret_key=os.environ["SECRET_KEY"],
    )
    # 顯示所有可用的帳戶
    print(f"Available accounts: {accounts}")
    api.activate_ca(
        ca_path=os.environ["CA_CERT_PATH"],
        ca_passwd=os.environ["CA_PASSWORD"],
    )

    # 取得合約 使用台指期近月為例
    contract = api.Contracts.Futures["TXFR1"]
    print(f"Contract: {contract}")

    # 建立期貨委託下單的 Order
    order = sj.order.FuturesOrder(
        action=Action.Buy,  # 買進
        price=contract.reference,  # 以平盤價買進
        quantity=1,  # 下單數量
        price_type=FuturesPriceType.LMT,  # 限價單
        order_type=OrderType.ROD,  # 當日有效單
        octype=FuturesOCType.Auto,  # 自動選擇新平倉
        account=api.futopt_account,  # 使用預設的帳戶
    )
    print(f"Order: {order}")

    # 送出委託單
    trade = api.place_order(contract=contract, order=order)
    print(f"Trade: {trade}")

    # 更新狀態
    api.update_status()
    print(f"Status: {trade.status}")

```

新增期貨下單指令到專案

在 `pyproject.toml` 新增 `futures_testing` 的指令

```
[project.scripts]
futures_testing = "sj_trading.testing_flow:testing_futures_ordering"

```

執行 `uv run futures_testing` 就開始進行測試下單了

使用Shioaji必須擁有永豐金帳戶。若你還沒有擁永豐金帳戶，請依據下列步驟開戶:

1. 至[開戶](https://www.sinotrade.com.tw/openact?utm_campaign=OP_inchannel&utm_source=newweb&utm_medium=button_top&strProd=0037&strWeb=0035)頁面
1. 若你沒有永豐銀行帳戶，請先開銀行帳戶當你的交割戶
1. 請選取**我要開DAWHO+大戶投**，為開銀行戶以及證券戶
1. 完成銀行及證券開戶

受限於台灣金融法規，新用戶首次使用需簽署相關文件並在測試模式完成測試報告才能進行正式環境的使用。

開戶

在開始之前必須先擁有[永豐金帳戶](https://www.sinotrade.com.tw/openact?utm_campaign=OP_inchannel&utm_source=newweb&utm_medium=button_top&strProd=0037&strWeb=0035)。

