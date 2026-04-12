### 非阻塞模式下單

將`place_order` 函數中設置 `timeout = 0`。

In

```
contract = api.Contracts.Futures.TXF['TXF202301']
order = api.Order(
    action=sj.constant.Action.Sell,
    price=14000,
    quantity=1,
    price_type=sj.constant.FuturesPriceType.LMT,
    order_type=sj.constant.OrderType.ROD,
    octype=sj.constant.FuturesOCType.Auto,
    account=api.futopt_account
)
trade = api.place_order(contract, order, timeout=0)
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
        limit_up=16241.0, 
        limit_down=13289.0, 
        reference=14765.0, 
        update_date='2023/01/10'
    ), 
    order=Order(
        action=<Action.Sell: 'Sell'>, 
        price=14000, 
        quantity=1, 
        account=FutureAccount(
            person_id='F123456789', 
            broker_id='F002000', 
            account_id='1234567', 
            signed=True, 
            username='PAPIUSER'
        ), 
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>
    ), 
    status=OrderStatus(status=<Status.Inactive: 'Inactive'>)
)

```

在非阻塞模式中取得的`Trade`物件，因為委託單仍在傳輸中還未送至交易所，所以會缺少一些資訊。在`Order`物件中沒有`id`和`seqno`，`OrderStatus`物件中沒有 `id`、`status_code`、`order_datetime` 和 `deals`，`status`顯示為`Inactive`。在非阻塞模式中要取得上述提到的資訊可利用`委託回報`和`非阻塞模式下單回調`兩種方式。

#### 委託回報

Out

```
OrderState.FuturesOrder {
    'operation': {
        'op_type': 'New', 
        'op_code': '00', 
        'op_msg': ''
    }, 
    'order': {
        'id': 'de616839', 
        'seqno': '500009', 
        'ordno': '000009', 
        'action': 'Sell', 
        'price': 14000, 
        'quantity': 1, 
        'order_type': 'ROD', 
        'price_type': 'LMT', 
        'oc_type': 'Auto', 
        'custom_field': ''
    }, 
    'status': {
        'id': 'de616839', 
        'exchange_ts': 1673334371.492948, 
        'order_quantity': 1, 
        'modified_price': 0, 
        'cancel_quantity': 0, 
        'web_id': 'Z'
    }, 
    'contract': {
        'security_type': 'FUT', 
        'exchange': 'TAIFEX', 
        'code': 'TXFA3'
    }
}

```

#### 非阻塞模式下單回調

In

```
from shioaji.order import Trade

def non_blocking_cb(trade:Trade):
    print('__my_callback__')
    print(trade)

trade = api.place_order(
    contract, 
    order, 
    timeout=0, 
    cb=non_blocking_cb # only work in non-blocking mode
)

```

Out: place order callback

```
__my_callback__
contract=Future(
    code='TXFA3', 
    symbol='TXF202301', 
    name='臺股期貨01', 
    category='TXF', 
    delivery_month='202301', 
    delivery_date='2023/01/30', 
    underlying_kind='I', 
    unit=1, 
    limit_up=16241.0, 
    limit_down=13289.0, 
    reference=14765.0, 
    update_date='2023/01/10'
), 
order=Order(
    action=<Action.Sell: 'Sell'>, 
    price=14000, 
    quantity=1, 
    id='40fd85d6', 
    seqno='958433', 
    ordno='kY01g', 
    account=FutureAccount(
        person_id='F123456789', 
        broker_id='F002000', 
        account_id='1234567', 
        signed=True, 
        username='PAPIUSER'
    ), 
    price_type=<StockPriceType.LMT: 'LMT'>, 
    order_type=<OrderType.ROD: 'ROD'>
), 
status=OrderStatus(
    id='40fd85d6', 
    status=<Status.Submitted: 'Submitted'>, 
    status_code='    ', 
    order_datetime=datetime.datetime(2023, 01, 10, 15, 14, 32), 
    deals=[]
)

```

### 比較兩者模式

在非阻塞模式下，執行 `place_order` 大約需要 0.01 秒，這比阻塞模式下的執行時間快 12 倍。雖然非阻塞模式下單效率更高，需等待交易所收到委託後，委託單才會生效。

contract and order

```
contract = api.Contracts.Futures.TXF['TXF202301']
order = api.Order(
    action='Sell',
    price=14000,
    quantity=1,
    price_type='LMT',
    order_type='ROD', 
    octype=sj.constant.FuturesOCType.Auto,
    account=api.futopt_account
)

```

Blocking

```
start_time = time.time()
api.place_order(contract, order) # block and wait for the order response
print(time.time() - start_time)
# 0.136578369140625 <- may be different

```

Non-Blocking

```
start_time = time.time()
api.place_order(contract, order, timeout=0) # non-block, the order is in transmition (inactive).
print(time.time() - start_time)
# 0.011670351028442383 <- may be different

```

支援非等待模式的函數

```
- place_order
- update_order
- cancel_order
- update_status
- list_positions
- list_position_detail
- list_profit_loss
- list_profit_loss_detail
- list_profit_loss_summary
- settlements
- margin
- ticks
- kbars

```

Shioaji 提供綁訂報價模式，可以用來將報價儲存於訊息佇列，將報價推送至Redis Stream，或者實現觸價委託單。我們提供以下範例，讓您可以更了解綁訂報價模式如何運作。

## 範例

### 綁訂報價至訊息佇列

In: pythonic way by using decorator

```
from collections import defaultdict, deque
from shioaji import TickFOPv1, Exchange

# set context
msg_queue = defaultdict(deque)
api.set_context(msg_queue)

# In order to use context, set bind=True
@api.on_tick_fop_v1(bind=True)
def quote_callback(self, exchange:Exchange, tick:TickFOPv1):
    # append quote to message queue
    self[tick.code].append(tick)

# subscribe
api.quote.subscribe(
    api.Contracts.Futures.TXF['TXF202107'],
    quote_type = sj.constant.QuoteType.Tick, 
    version = sj.constant.QuoteVersion.v1
)

```

In: traditional way

```
def quote_callback(self, exchange:Exchange, tick:TickFOPv1):
    # append tick to context
    self[tick.code].append(tick)

# In order to use context, set bind=True
api.quote.set_on_tick_fop_v1_callback(quote_callback, bind=True)

```

Out

```
# after subscribe and wait for a few seconds ...
# print(msg_queue)
defaultdict(collections.deque, 
    {
        'TXFG1': [
            Tick(code='TXFG1', datetime=datetime.datetime(2021, 7, 5, 10, 0, 21, 220000), open=Decimal('17755'), underlying_price=Decimal('17851.88'), bid_side_total_vol=34824, ask_side_total_vol=36212, avg_price=Decimal('17837.053112'), close=Decimal('17833'), high=Decimal('17900'), low=Decimal('17742'), amount=Decimal('17833'), total_amount=Decimal('981323314'), volume=1, total_volume=55016, tick_type=1, chg_type=2, price_chg=Decimal('184'), pct_chg=Decimal('1.042552'), simtrade=0),
            Tick(code='TXFG1', datetime=datetime.datetime(2021, 7, 5, 10, 0, 21, 781000), open=Decimal('17755'), underlying_price=Decimal('17851.88'), bid_side_total_vol=34825, ask_side_total_vol=36213, avg_price=Decimal('17837.053056'), close=Decimal('17834'), high=Decimal('17900'), low=Decimal('17742'), amount=Decimal('17834'), total_amount=Decimal('981341148'), volume=1, total_volume=55017, tick_type=1, chg_type=2, price_chg=Decimal('185'), pct_chg=Decimal('1.048218'), simtrade=0)
        ]
    }
)

```

### 將報價推送至Redis Stream

在開始之前，請先安裝[redis](https://github.com/andymccurdy/redis-py)。

In

```
import redis
import json
from shioaji import TickFOPv1, Exchange

# redis setting
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# set up context
api.set_context(r)

# In order to use context, set bind=True
@api.on_tick_fop_v1(bind=True)
def quote_callback(self, exchange:Exchange, tick:TickFOPv1):
    # push them to redis stream
    channel = 'Q:' + tick.code # ='Q:TXFG1' in this example
    self.xadd(channel, {'tick':json.dumps(tick.to_dict(raw=True))})

```

Out

```
# after subscribe and wait for a few seconds ...
# r.xread({'Q:TXFG1':'0-0'})
[
    ['Q:TXFG1',
        [
            ('1625454940107-0',
                {'tick': 
                    '{"code": "TXFG1", "datetime": "2021-07-05T11:15:49.066000", "open": "17755", "underlying_price": "17904.03", "bid_side_total_vol": 49698, "ask_side_total_vol": 51490, "avg_price": "17851.312322", "close": "17889", "high": "17918", "low": "17742", "amount": "268335", "total_amount": "1399310819", "volume": 15, "total_volume": 78387, "tick_type": 2, "chg_type": 2, "price_chg": "240", "pct_chg": "1.35985", "simtrade": 0}'
                }
            ),
            ('1625454941854-0',
                {'tick': 
                    '{"code": "TXFG1", "datetime": "2021-07-05T11:15:50.815000", "open": "17755", "underlying_price": "17902.58", "bid_side_total_vol": 49702, "ask_side_total_vol": 51478, "avg_price": "17851.313258", "close": "17888", "high": "17918", "low": "17742", "amount": "35776", "total_amount": "1399346595", "volume": 2, "total_volume": 78389, "tick_type": 2, "chg_type": 2, "price_chg": "239", "pct_chg": "1.354184", "simtrade": 0}'
                }
            )
        ]
    ]
]


# parse redis stream
# [json.loads(x[-1]['tick']) for x in r.xread({'Q:TXFG1':'0-0'})[0][-1]]
[
    {
        'code': 'TXFG1',
        'datetime': '2021-07-05T11:15:49.066000',
        'open': '17755',
        'underlying_price': '17904.03',
        'bid_side_total_vol': 49698,
        'ask_side_total_vol': 51490,
        'avg_price': '17851.312322',
        'close': '17889',
        'high': '17918',
        'low': '17742',
        'amount': '268335',
        'total_amount': '1399310819',
        'volume': 15,
        'total_volume': 78387,
        'tick_type': 2,
        'chg_type': 2,
        'price_chg': '240',
        'pct_chg': '1.35985',
        'simtrade': 0
    },
    {
        'code': 'TXFG1',
        'datetime': '2021-07-05T11:15:50.815000',
        'open': '17755',
        'underlying_price': '17902.58',
        'bid_side_total_vol': 49702,
        'ask_side_total_vol': 51478,
        'avg_price': '17851.313258',
        'close': '17888',
        'high': '17918',
        'low': '17742',
        'amount': '35776',
        'total_amount': '1399346595',
        'volume': 2,
        'total_volume': 78389,
        'tick_type': 2,
        'chg_type': 2,
        'price_chg': '239',
        'pct_chg': '1.354184',
        'simtrade': 0
    },
]

```

### 觸價委託單

[觸價委託單](https://www.investopedia.com/terms/s/stoporder.asp)，在市場價格觸及委託單上所設定之價位時，委託單立刻轉為限價單或市價單。

**以下僅為範例，請小心使用並自行承擔風險**

Example: stop order

```
import time
from typing import Union

import shioaji as sj

class StopOrderExcecutor:
    def __init__(self, api: sj.Shioaji) -> None:
        self.api = api
        self._stop_orders = {}

    def on_quote(
        self, quote: Union[sj.BidAskFOPv1, sj.BidAskSTKv1, sj.TickFOPv1, sj.TickSTKv1]
    ) -> None:
        code = quote.code
        if code in self._stop_orders:
            for stop_order in self._stop_orders[code]:
                if stop_order['executed']:
                    continue
                if hasattr(quote, "ask_price"):
                    price = 0.5 * float(
                        quote.bid_price[0] + quote.ask_price[0]
                    )  # mid price
                else:
                    price = float(quote.close)  # Tick

                is_execute = False
                if stop_order["stop_price"] >= stop_order["ref_price"]:
                    if price >= stop_order["stop_price"]:
                        is_execute = True

                elif stop_order["stop_price"] < stop_order["ref_price"]:
                    if price <= stop_order["stop_price"]:
                        is_execute = True

                if is_execute:
                    self.api.place_order(stop_order["contract"], stop_order["pending_order"])
                    stop_order['executed'] = True
                    stop_order['ts_executed'] = time.time()
                    print(f"execute stop order: {stop_order}")
                else:
                    self._stop_orders[code]

    def add_stop_order(
        self,
        contract: sj.contracts.Contract,
        stop_price: float,
        order: sj.order.Order,
    ) -> None:
        code = contract.code
        snap = self.api.snapshots([contract])[0]
        # use mid price as current price to avoid illiquidity
        ref_price = 0.5 * (snap.buy_price + snap.sell_price)
        stop_order = {
            "code": contract.code,
            "stop_price": stop_price,
            "ref_price": ref_price,
            "contract": contract,
            "pending_order": order,
            "ts_create": time.time(),
            "executed": False,
            "ts_executed": 0.0
        }

        if code not in self._stop_orders:
            self._stop_orders[code] = []
        self._stop_orders[code].append(stop_order)
        print(f"add stop order: {stop_order}")

    def get_stop_orders(self) -> dict:
        return self._stop_orders

    def cancel_stop_order_by_code(self, code: str) -> None:
        if code in self._stop_orders:
            _ = self._stop_orders.pop(code)

    def cancel_stop_order(self, stop_order: dict) -> None:
        code = stop_order["code"]
        if code in self._stop_orders:
            self._stop_orders[code].remove(stop_order)
            if len(self._stop_orders[code]) == 0:
                self._stop_orders.pop(code)

    def cancel_all_stop_orders(self) -> None:
        self._stop_orders.clear()

```

- 使用snapshots的中價作為參考價格，以區分觸價委託單的方向。

基本上，委託單會在您的電腦上待命，只有在商品價格觸擊所設定價格時，觸價委託單才會被送出，以下範例顯示如何提交限價觸價委託單(Stop-Limit Order)。

Set up a stop order

```
# shioaji order
contract = api.Contracts.Futures.TXF['TXF202301']
order = api.Order(
    action='Buy',
    price=14800,
    quantity=1,
    price_type='LMT',
    order_type='ROD', 
    octype=sj.constant.FuturesOCType.Auto,
    account=api.futopt_account
)

# Stop Order Excecutor
soe = StopOrderExcecutor(api)
soe.add_stop_order(contract=contract, stop_price=14805, order=order)

```

Out

```
add stop order: {
    'code': 'TXFA3', 
    'stop_price': 14805, 
    'ref_price': 14790,
    'contract': Future(
        code='TXFA3', 
        symbol='TXF202301', 
        name='臺股期貨01', 
        category='TXF', 
        delivery_month='202301', 
        delivery_date='2023/01/30', 
        underlying_kind='I', 
        unit=1, 
        limit_up=16241.0, 
        limit_down=13289.0, 
        reference=14765.0, 
        update_date='2023/01/10'
    ), 
    'pending_order': Order(
        action=<Action.Buy: 'Buy'>, 
        price=14800, 
        quantity=1, 
        account=FutureAccount(person_id='A123456789', broker_id='F002000', account_id='1234567', signed=True, username='PAIUSER'),
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>
    ), 
    'ts_create': 1673329115.1056178, 
    'executed': False, 
    'ts_executed': 0.0
}

```

- 市價觸價委託單(Stop-Market Order): `price_type = 'MKT'`

最後，我們將`StopOrderExcecutor`綁訂在報價上。請注意，您必須訂略商品報價，觸價委託單才會執行。

Set up context and callback function

```
from shioaji import TickFOPv1, Exchange

# set up context
api.set_context(soe)

# In order to use context, set bind=True
@api.on_tick_fop_v1(bind=True)
def quote_callback(self, exchange:Exchange, tick:TickFOPv1):
    # pass tick object to Stop Order Excecutor
    self.on_quote(tick)

# subscribe
api.quote.subscribe(
    contract,
    quote_type = sj.constant.QuoteType.Tick, 
    version = sj.constant.QuoteVersion.v1
)

```

Out: Once close/mid price hit stop price

```
execute stop order: {
    'code': 'TXFA3', 
    'stop_price': 14805, 
    'ref_price': 14790, 
    'contract': Future(
        code='TXFA3', 
        symbol='TXF202301', 
        name='臺股期貨01', 
        category='TXF', 
        delivery_month='202301', 
        delivery_date='2023/01/30', 
        underlying_kind='I', 
        unit=1, 
        limit_up=16241.0, 
        limit_down=13289.0, 
        reference=14765.0, 
        update_date='2023/01/10'
    ), 
    'pending_order': Order(
        action=<Action.Buy: 'Buy'>, 
        price=14800, 
        quantity=1, 
        account=FutureAccount(person_id='A123456789', broker_id='F002000', account_id='1234567', signed=True, username='PAIUSER'),
        price_type=<StockPriceType.LMT: 'LMT'>, 
        order_type=<OrderType.ROD: 'ROD'>
    ), 
    'ts_create': 1673329115.1056178, 
    'executed': True, 
    'ts_executed': 1673329161.3224185
}

```

本篇教學完整專案的程式碼可以參考 [sj-trading](https://github.com/Sinotrade/sj-trading-demo)， 完整使用範例 jupyter notebook 可以參考 [quote_manager_usage](https://github.com/Sinotrade/sj-trading-demo/blob/main/quote_manager_usage.ipynb)。

本專案是使用 `uv` 建立的，如果還不熟悉如何使用 `uv` 建立專案並使用 `uv` 管理依賴，建議回到 [環境設定](../../../env_setup/) 章節從頭學習起。

在開始進行行情管理器的編寫前，我們會使用 Polars 這個套件來處理行情資料，所以需要將它加入專案的依賴中，同時本篇教學中會有如何用 Polars 快速對多商品計算技術指標的範例，所以也需要將 polars_talib 這個套件加入專案的依這個。

新增 Polars 依賴

```
uv add polars polars_talib

```

如果你對 Polars 不熟悉，可以參考 [Polars 官方文件](https://docs.pola.rs/user-guide/getting-started/) 來了解該如何使用他。

polars_talib 是一個 Polars 的擴充套件，它提供了 polars expression 版本的 ta-lib 完整功能，讓我們可以很方便的用 Polars 進行技術指標的計算，他是由 shioaji 作者開發的，詳細使用可以參考 [polars_ta_extension](https://github.com/Yvictor/polars_ta_extension)。

Polars 是一個高效的 DataFrame 套件，適合用來處理大量資料，並且不需要任何額外的設定，就可以使用多核心來加速資料處理。這篇範例中我們可以看到如何使用 Shioaji 的行情管理器來取得行情資料，並且使用 Polars 來做並行化運算，同時將商品的 ticks 進行分 K 轉換，並且做平行化的多商品技術指標計算。

新增 quote.py

在 `src/sj_trading/` 新增 `quote.py` 檔案，並且新增以下程式碼

```
import shioaji as sj
from typing import List

class QuoteManager:
    def __init__(self, api: sj.Shioaji):
        self.api = api
        self.api.quote.set_on_tick_stk_v1_callback(self.on_stk_v1_tick_handler)
        self.api.quote.set_on_tick_fop_v1_callback(self.on_fop_v1_tick_handler)
        self.ticks_stk_v1: List[sj.TickSTKv1] = []
        self.ticks_fop_v1: List[sj.TickFOPv1] = []

    def on_stk_v1_tick_handler(self, _exchange: sj.Exchange, tick: sj.TickSTKv1):
        self.ticks_stk_v1.append(tick)

    def on_fop_v1_tick_handler(self, _exchange: sj.Exchange, tick: sj.TickFOPv1):
        self.ticks_fop_v1.append(tick)

```

這個部分比較單純，讓收到行情的 handle func 盡可能地做最少的事，我們定義了一個 `QuoteManager` 類別，並且在初始化時設定了註冊兩個回調函數，分別是 `on_stk_v1_tick_handler` 和 `on_fop_v1_tick_handler`，這兩個函數會在接收到行情資料時被呼叫，並且將行情資料存入 `ticks_stk_v1` 和 `ticks_fop_v1` 中。

增加 `QuoteManager` 訂閱與取消訂閱的方法

```
def __init__(self, api: sj.Shioaji):
    # skip
    self.subscribed_stk_tick: Set[str] = set()

def subscribe_stk_tick(self, codes: List[str], recover: bool = False):
    for code in codes:
        contract = self.api.Contracts.Stocks[code]
        if contract is not None and code not in self.subscribed_stk_tick:
            self.api.quote.subscribe(contract, "tick")
            self.subscribed_stk_tick.add(code)

def unsubscribe_stk_tick(self, codes: List[str]):
    for code in codes:
        contract = self.api.Contracts.Stocks[code]
        if contract is not None and code in self.subscribed_stk_tick:
            self.api.quote.unsubscribe(contract, "tick")
            self.subscribed_stk_tick.remove(code)

def unsubscribe_all_stk_tick(self):
    for code in self.subscribed_stk_tick:
        contract = self.api.Contracts.Stocks[code]
        if contract is not None:
            self.api.quote.unsubscribe(contract, "tick")
    self.subscribed_stk_tick.clear()

```

上面我們增加了 `subscribe_stk_tick` 方法，這個方法會將傳入的商品代碼列表中的商品代碼加入到 `subscribed_stk_tick` 中，並且呼叫 Shioaji 的 `subscribe` 方法來訂閱行情，`subscribed_stk_tick` 是一個 `Set`，用來存放已經訂閱的商品代碼，避免重複訂閱以及方便後續將所有訂閱商品取消訂閱。

增加 `QuoteManager` 拿出訂閱的 ticks 的方法

```
def __init__(self, api: sj.Shioaji):
    # skip
    self.df_stk: pl.DataFrame = pl.DataFrame(
        [],
        schema=[
            ("datetime", pl.Datetime),
            ("code", pl.Utf8),
            ("price", pl.Float64),
            ("volume", pl.Int64),
            ("tick_type", pl.Int8),
        ],
    )

def get_df_stk(self) -> pl.DataFrame:
    poped_ticks, self.ticks_stk_v1 = self.ticks_stk_v1, []
    if poped_ticks:
        df = pl.DataFrame([tick.to_dict() for tick in poped_ticks]).select(
            pl.col("datetime", "code"),
            pl.col("close").cast(pl.Float64).alias("price"),
            pl.col("volume").cast(pl.Int64),
            pl.col("tick_type").cast(pl.Int8),
        )
        self.df_stk = self.df_stk.vstack(df)
    return self.df_stk

```

`__init__` 中我們定義了一個 `df_stk` 的 Polars DataFrame，用來存放所有訂閱的台股 tick 資料，`get_df_stk` 方法會將 `ticks_stk_v1` 中的資料轉換成 Polars DataFrame，並且回傳，到這邊我們就已經可以初步看到可以拿出來的 DataFrame 了。

增加 `QuoteManager` 將 ticks 轉換成 K 線的方法

```
def get_df_stk_kbar(
    self, unit: str = "1m", exprs: List[pl.Expr] = []
) -> pl.DataFrame:
    df = self.get_df_stk()
    df = df.group_by(
        pl.col("datetime").dt.truncate(unit),
        pl.col("code"),
        maintain_order=True,
    ).agg(
        pl.col("price").first().alias("open"),
        pl.col("price").max().alias("high"),
        pl.col("price").min().alias("low"),
        pl.col("price").last().alias("close"),
        pl.col("volume").sum().alias("volume"),
    )
    if exprs:
        df = df.with_columns(exprs)
    return df

```

在 `get_df_stk_kbar` 方法中，我們將 `get_df_stk` 拿到 Ticks 的 DataFrame 根據 code 和 truncate 後的 datetime 進行分組，並且對每個分組進行聚合開高低收量，最後回傳一個新的 DataFrame，這個 DataFrame 就是我們所需要的 K 線資料了，並且這邊保留了 `exprs` 參數，讓使用者可以傳入一些額外的運算式，來進行更多的運算。 在這邊 truncate 的單位我們使用 `1m` 來表示 1 分鐘，如果想要拿到 5 分鐘的 K 線，可以將單位改成 `5m`， 1 小時 K 可以將單位改成 `1h`，如果想要更多不同的單位可以參考 [truncate](https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.dt.truncate.html) 的 API 文件。

自定義技術指標計算

```
import polars as pl
import polars_talib as plta

quote_manager.get_df_stk_kbar("5m", [
    pl.col("close").ta.ema(5).over("code").fill_nan(None).alias("ema5"),
    plta.macd(pl.col("close"), 12, 26, 9).over("code").struct.field("macd").fill_nan(None),
])

```

在這邊使用 polars_ta 的 expression 來計算技術指標，並且將計算出來的指標加入到 K 線資料中，這邊我們計算了 `ema` 和 `macd` 兩種指標，更多指標可以參考 [polars_ta_extension 支援指標列表](https://github.com/Yvictor/polars_ta_extension?tab=readme-ov-file#supported-indicators-and-functions)。

在這個 polars_ta 的 expression 中，使用 `over("code")` 來將指標計算結果根據商品代碼進行分組做每個商品獨立的運算 ，所以即使所有的商品都在同一個 DataFrame 中，計算出來的結果還是每個商品獨立的，並且這個 `over` 的 partition 是會自動平行運算的，所以即使有大量的商品，也可以很快的計算出來，使用 `alias` 來將計算結果的欄位名稱設置為 `ema5`，在 `macd` 指標中回傳的是多個欄位的 struct ，這邊取出 struct 中的 macd 欄位。

因為這邊傳入的只是表達式非常輕量，可以根據你需要的任何表達式進行新增就可以看到你需要的各種技術指標了，當然如果你要使用 polars expression 做出自己的指標，也是可以的，這邊只是提供一個可以做運算的接口以及簡單的使用範例。

回補錯過的行情

```
def fetch_ticks(self, contract: BaseContract) -> pl.DataFrame:
    code = contract.code
    ticks = self.api.ticks(contract)
    df = pl.DataFrame(ticks.dict()).select(
        pl.from_epoch("ts", time_unit="ns").dt.cast_time_unit("us").alias("datetime"),
        pl.lit(code).alias("code"),
        pl.col("close").alias("price"),
        pl.col("volume").cast(pl.Int64),
        pl.col("tick_type").cast(pl.Int8),
    )
    return df

def subscribe_stk_tick(self, codes: List[str], recover: bool = False):
    for code in codes:
        # skop
        if recover:
            df = self.fetch_ticks(contract)
            if not df.is_empty():
                code_ticks = [t for t in self.ticks_stk_v1 if t.code == code]
                if code_ticks:
                    t_first = code_ticks[0].datetime
                    df = df.filter(pl.col("datetime") < t_first)
                    self.df_stk = self.df_stk.vstack(df)
                else:
                    self.df_stk = self.df_stk.vstack(df)

```

在訂閱的時候我們可能會超過當天開盤的時間，這時候訂閱即時資料將會缺乏錯過的資料，所以這邊我們實作使用 api 回補歷史 tick 的資料，這邊我們使用 `fetch_ticks` 方法來取得歷史 tick 的資料，並且將取得資料加入到 `df_stk` 中。

以上我們已經完成了一個可以訂閱行情、回補錯過行情、計算技術指標的行情管理器了，這邊我們將所有程式碼整合起來，並且在 jupyter lab 中使用。

完整的 QuoteManager 可以參考 [quote.py](https://github.com/Sinotrade/sj-trading-demo/blob/main/src/sj_trading/quote.py)。

完整使用範例 jupyter notebook 可以參考 [quote_manager_usage](https://github.com/Sinotrade/sj-trading-demo/blob/main/quote_manager_usage.ipynb)。

## 觸價委託範例

這是一個簡單的範例，說明如何實作價格監控以及觸價委託。

```
from pydantic import BaseModel

class TouchOrderCond(BaseModel):
    contract: Contract
    order: Order
    order: Order
    touch_price: float

class TouchOrder:
   def __init__(self, api: sj.Shioaji, condition: TouchOrderCond
    ):
       self.flag = False
       self.api = api
       self.order = condition.order
       self.contract = condition.contract
       self.touch_price = condition.touch_price
       self.api.quote.subscribe(self.contract)
       self.api.quote.set_quote_callback(self.touch)

   def touch(self, topic, quote):
       price = quote["Close"][0]
       if price == self.touch_price and not self.flag:
           self.flag = True
           self.api.place_order(self.contract, self.order)
           self.api.quote.unsubscribe(self.contract)

```

完整程式碼詳見 [TouchPrice Order Extention](https://github.com/SsallyLin/touchprice)

我們使用solace作為mesh broker。事件可視為你與solace的連接狀態。如果你沒有相關網路經驗，可以略過此部分。不用擔心在不用任何的設定下，我們將重連預設為50次。只需要請你確保你的網絡連接狀態正常。

In

```
@api.quote.on_event
def event_callback(resp_code: int, event_code: int, info: str, event: str):
    print(f'Event code: {event_code} | Event: {event}')

```

Out

```
Event code: 16 | Event: Subscribe or Unsubscribe ok

```

如同報價callback，你可以利用兩種方式設定事件callback。

In

```
api.quote.set_event_callback?

```

Out

```
Signature: 
    api.quote.set_event_callback(func:Callable[[int, int, str, str], NoneType]) -> None
Docstring:  <no docstring>
Type:  method

```

### 事件代碼

| Event Code | Event Code Enumerator | Description | | --- | --- | --- | | 0 | SOLCLIENT_SESSION_EVENT_UP_NOTICE | The Session is established. | | 1 | SOLCLIENT_SESSION_EVENT_DOWN_ERROR | The Session was established and then went down. | | 2 | SOLCLIENT_SESSION_EVENT_CONNECT_FAILED_ERROR | The Session attempted to connect but was unsuccessful. | | 3 | SOLCLIENT_SESSION_EVENT_REJECTED_MSG_ERROR | The appliance rejected a published message. | | 4 | SOLCLIENT_SESSION_EVENT_SUBSCRIPTION_ERROR | The appliance rejected a subscription (add or remove). | | 5 | SOLCLIENT_SESSION_EVENT_RX_MSG_TOO_BIG_ERROR | The API discarded a received message that exceeded the Session buffer size. | | 6 | SOLCLIENT_SESSION_EVENT_ACKNOWLEDGEMENT | The oldest transmitted Persistent/Non-Persistent message that has been acknowledged. | | 7 | SOLCLIENT_SESSION_EVENT_ASSURED_PUBLISHING_UP | Deprecated -- see notes in solClient_session_startAssuredPublishing.The AD Handshake (that is, Guaranteed Delivery handshake) has completed for the publisher and Guaranteed messages can be sent. | | 8 | SOLCLIENT_SESSION_EVENT_ASSURED_CONNECT_FAILED | Deprecated -- see notes in solClient_session_startAssuredPublishing.The appliance rejected the AD Handshake to start Guaranteed publishing. Use SOLCLIENT_SESSION_EVENT_ASSURED_DELIVERY_DOWN instead. | | 8 | SOLCLIENT_SESSION_EVENT_ASSURED_DELIVERY_DOWN | Guaranteed Delivery publishing is not available.The guaranteed delivery capability on the session has been disabled by some action on the appliance. | | 9 | SOLCLIENT_SESSION_EVENT_TE_UNSUBSCRIBE_ERROR | The Topic Endpoint unsubscribe command failed. | | 9 | SOLCLIENT_SESSION_EVENT_DTE_UNSUBSCRIBE_ERROR | Deprecated name; SOLCLIENT_SESSION_EVENT_TE_UNSUBSCRIBE_ERROR is preferred. | | 10 | SOLCLIENT_SESSION_EVENT_TE_UNSUBSCRIBE_OK | The Topic Endpoint unsubscribe completed. | | 10 | SOLCLIENT_SESSION_EVENT_DTE_UNSUBSCRIBE_OK | Deprecated name; SOLCLIENT_SESSION_EVENT_TE_UNSUBSCRIBE_OK is preferred. | | 11 | SOLCLIENT_SESSION_EVENT_CAN_SEND | The send is no longer blocked. | | 12 | SOLCLIENT_SESSION_EVENT_RECONNECTING_NOTICE | The Session has gone down, and an automatic reconnect attempt is in progress. | | 13 | SOLCLIENT_SESSION_EVENT_RECONNECTED_NOTICE | The automatic reconnect of the Session was successful, and the Session was established again. | | 14 | SOLCLIENT_SESSION_EVENT_PROVISION_ERROR | The endpoint create/delete command failed. | | 15 | SOLCLIENT_SESSION_EVENT_PROVISION_OK | The endpoint create/delete command completed. | | 16 | SOLCLIENT_SESSION_EVENT_SUBSCRIPTION_OK | The subscribe or unsubscribe operation has succeeded. | | 17 | SOLCLIENT_SESSION_EVENT_VIRTUAL_ROUTER_NAME_CHANGED | The appliance's Virtual Router Name changed during a reconnect operation.This could render existing queues or temporary topics invalid. | | 18 | SOLCLIENT_SESSION_EVENT_MODIFYPROP_OK | The session property modification completed. | | 19 | SOLCLIENT_SESSION_EVENT_MODIFYPROP_FAIL | The session property modification failed. | | 20 | SOLCLIENT_SESSION_EVENT_REPUBLISH_UNACKED_MESSAGES | After successfully reconnecting a disconnected session, the SDK received an unknown publisher flow name response when reconnecting the GD publisher flow. |

每次您使用 `place_order`、`update_order` 或者 `cancel_order` 時，預設皆會收到來自交易所的委託或成交回報。如果您不想收到任何回報通知，您可以參考[訂閱委託回報](../../login/#subscribe-trade)將其關閉。我們亦提供了處理委託及成交回報的介面。如果您正在建立自己的交易系統，這會非常有幫助。

## 處理委託及成交回報

您可以使用 `set_order_callback` 來處理委託及成交回報。以下範例顯示，自製的委託回報函數(`order_cb`)將先 print `my_order_callback` 然後才 print 委託及成交回報。

設定委託回報函式

```
def order_cb(stat, msg):
    print('my_order_callback')
    print(stat, msg)

api.set_order_callback(order_cb)

```

下單

```
contract = api.Contracts.Stocks.TSE.TSE2890
order = api.Order(
    price=16, 
    quantity=1, 
    action=sj.constant.Action.Buy, 
    price_type=sj.constant.StockPriceType.LMT, 
    order_type=sj.constant.OrderType.ROD, 
    order_lot=sj.constant.StockOrderLot.Common, 
    custom_field="test",
    account=api.stock_account
)
trade = api.place_order(contract, order)

```

```
contract = api.Contracts.Stocks.TSE.TSE2890
order = api.Order(
    price=16, 
    quantity=1, 
    action=sj.constant.Action.Buy, 
    price_type=sj.constant.TFTStockPriceType.LMT, 
    order_type=sj.constant.TFTOrderType.ROD, 
    order_lot=sj.constant.TFTStockOrderLot.Common, 
    custom_field="test",
    account=api.stock_account
)
trade = api.place_order(contract, order)

```

### 委託回報

委託回報

```
my_order_callback
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
my_order_callback
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

### 成交回報

成交回報

```
my_order_callback
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
my_order_callback
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

Credit Enquires

```
>> api.credit_enquires?

Signature:
api.credit_enquires(
    contracts: List[shioaji.contracts.Stock],
    timeout: int = 30000,
    cb: Callable[[shioaji.data.CreditEnquire], NoneType] = None,
) -> List[shioaji.data.CreditEnquire]

```

## 範例

In

```
contracts = [
    api.Contracts.Stocks['2330'],
    api.Contracts.Stocks['2890']
]
credit_enquires = api.credit_enquires(contracts)
credit_enquires

```

Out

```
[
    CreditEnquire(update_time='2020-12-11 13:30:13', system='HE', stock_id='2330', margin_unit=1381), 
    CreditEnquire(update_time='2020-12-11 13:30:02', system='HC', stock_id='2330', margin_unit=1371), 
    CreditEnquire(update_time='2020-12-11 13:30:05', system='HN', stock_id='2330', margin_unit=1357), 
    CreditEnquire(update_time='2020-12-11 13:30:03', system='HF', stock_id='2330', margin_unit=1314), 
    CreditEnquire(update_time='2020-12-09 10:56:05', system='HE', stock_id='2890'), 
    CreditEnquire(update_time='2020-12-11 09:33:04', system='HN', stock_id='2890'), 
    CreditEnquire(update_time='2020-12-02 09:01:03', system='HF', stock_id='2890')
]

```

轉成DataFrame

In

```
df = pd.DataFrame(c.__dict__ for c in credit_enquires)
df.update_time = pd.to_datetime(df.update_time)
df

```

Out

| | margin_unit | short_unit | stock_id | system | update_time | | --- | --- | --- | --- | --- | --- | | 0 | 1381 | 0 | 2330 | HE | 2020-12-11 13:30:13 | | 1 | 1371 | 0 | 2330 | HC | 2020-12-11 13:30:02 | | 2 | 1357 | 0 | 2330 | HN | 2020-12-11 14:31:19 | | 3 | 1314 | 0 | 2330 | HF | 2020-12-11 14:31:19 | | 4 | 0 | 0 | 2890 | HE | 2020-12-09 10:56:05 | | 5 | 0 | 0 | 2890 | HN | 2020-12-11 09:33:04 | | 6 | 0 | 0 | 2890 | HF | 2020-12-02 09:01:03 |

## 屬性

CreditEnquire

```
update_time (str): 更新時間
system (str): 類別
stock_id (str): 商品代碼
margin_unit (int): 資餘額
short_unit (int): 券餘額

```

