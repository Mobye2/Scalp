import os
import shioaji as sj
from shioaji.constant import (
    Action,
    StockPriceType,
    StockOrderLot,
    OrderType,
    FuturesPriceType,
    FuturesOCType,
)


def login(simulation: bool = True) -> sj.Shioaji:
    api = sj.Shioaji(simulation=simulation)
    api.login(
        api_key=os.environ["API_KEY"],
        secret_key=os.environ["SECRET_KEY"],
        contracts_timeout=10000,
    )
    api.activate_ca(
        ca_path=os.environ["CA_CERT_PATH"],
        ca_passwd=os.environ["CA_PASSWORD"],
    )
    return api


# ── 現貨 ──────────────────────────────────────────────

def place_stock_order(api: sj.Shioaji, code: str, action: Action, price: float, quantity: int):
    contract = api.Contracts.Stocks[code]
    order = api.Order(
        price=price,
        quantity=quantity,
        action=action,
        price_type=StockPriceType.LMT,
        order_type=OrderType.ROD,
        order_lot=StockOrderLot.Common,
        account=api.stock_account,
    )
    trade = api.place_order(contract, order)
    print(f"[Stock] place_order: {trade.status.status}")
    return trade


def update_stock_order(api: sj.Shioaji, trade, price: float = None, qty: int = None):
    api.update_order(trade=trade, price=price, qty=qty)
    api.update_status(api.stock_account)
    print(f"[Stock] update_order: {trade.status.status}")


def cancel_stock_order(api: sj.Shioaji, trade):
    api.cancel_order(trade)
    api.update_status(api.stock_account)
    print(f"[Stock] cancel_order: {trade.status.status}")


# ── 期貨 ──────────────────────────────────────────────

def place_futures_order(api: sj.Shioaji, code: str, action: Action, price: float, quantity: int):
    contract = api.Contracts.Futures[code]
    order = api.Order(
        action=action,
        price=price,
        quantity=quantity,
        price_type=FuturesPriceType.LMT,
        order_type=OrderType.ROD,
        octype=FuturesOCType.Auto,
        account=api.futopt_account,
    )
    trade = api.place_order(contract, order)
    print(f"[Futures] place_order: {trade.status.status}")
    return trade


def update_futures_order(api: sj.Shioaji, trade, price: float = None, qty: int = None):
    api.update_order(trade=trade, price=price, qty=qty)
    api.update_status(api.futopt_account)
    print(f"[Futures] update_order: {trade.status.status}")


def cancel_futures_order(api: sj.Shioaji, trade):
    api.cancel_order(trade)
    api.update_status(api.futopt_account)
    print(f"[Futures] cancel_order: {trade.status.status}")


# ── 查詢委託 ──────────────────────────────────────────

def list_trades(api: sj.Shioaji, account=None):
    api.update_status(account)
    return api.list_trades()


# ── 範例 ──────────────────────────────────────────────

if __name__ == "__main__":
    api = login(simulation=True)

    # 現貨買進 2890 永豐金 1張 限價17元
    stock_trade = place_stock_order(api, "2890", Action.Buy, 17.0, 1)

    # 改價
    # update_stock_order(api, stock_trade, price=17.5)

    # 刪單
    # cancel_stock_order(api, stock_trade)

    # 期貨買進 台指期近月 1口 限價
    contract = api.Contracts.Futures.TXF.TXFR1
    futures_trade = place_futures_order(api, "TXFR1", Action.Buy, contract.reference, 1)

    # 查詢所有委託
    trades = list_trades(api)
    for t in trades:
        print(t.status)

    api.logout()
