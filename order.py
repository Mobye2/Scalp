import os
from dotenv import load_dotenv
import shioaji as sj
from shioaji.order import Trade
from shioaji.constant import (
    Action,
    StockPriceType,
    StockOrderLot,
    OrderType,
    FuturesPriceType,
    FuturesOCType,
)

# 載入 .env 檔案
load_dotenv()


def login(simulation: bool = True) -> sj.Shioaji:
    api = sj.Shioaji(simulation=simulation)
    print(f"[Login] 環境: {'模擬' if simulation else '正式'}")
    api.login(
        api_key=os.environ["API_KEY"],
        secret_key=os.environ["SECRET_KEY"],
        contracts_timeout=10000,
    )
    # 模擬環境不需要憑證
    if not simulation:
        api.activate_ca(
            ca_path=os.environ["CA_CERT_PATH"],
            ca_passwd=os.environ["CA_PASSWORD"],
        )
    return api


# ── 現貨 ──────────────────────────────────────────────

def place_stock_order(
    api: sj.Shioaji, code: str, action: Action, price: float, quantity: int
) -> Trade:
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


def update_stock_order(
    api: sj.Shioaji, trade: Trade, price: float = None, qty: int = None
) -> None:

    kwargs = {}
    if price is not None:
        kwargs["price"] = price
    if qty is not None:
        kwargs["qty"] = qty
    api.update_order(trade=trade, **kwargs)
    api.update_status(api.stock_account)
    print(f"[Stock] update_order: {trade.status.status}")


def cancel_stock_order(api: sj.Shioaji, trade: Trade) -> None:
    api.cancel_order(trade)
    api.update_status(api.stock_account)
    print(f"[Stock] cancel_order: {trade.status.status}")


# ── 期貨 ──────────────────────────────────────────────

def place_futures_order(
    api: sj.Shioaji, code: str, action: Action, price: float, quantity: int
) -> Trade:
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


def update_futures_order(
    api: sj.Shioaji, trade: Trade, price: float = None, qty: int = None
) -> None:

    kwargs = {}
    if price is not None:
        kwargs["price"] = price
    if qty is not None:
        kwargs["qty"] = qty
    api.update_order(trade=trade, **kwargs)
    api.update_status(api.futopt_account)
    print(f"[Futures] update_order: {trade.status.status}")


def cancel_futures_order(api: sj.Shioaji, trade: Trade) -> None:
    api.cancel_order(trade)
    api.update_status(api.futopt_account)
    print(f"[Futures] cancel_order: {trade.status.status}")


# ── 查詢委託 ──────────────────────────────────────────

def list_trades(api: sj.Shioaji, account=None) -> list:
    api.update_status(account)
    return api.list_trades()


# ── 範例 ──────────────────────────────────────────────

if __name__ == "__main__":
    api = login(simulation=True)

    # 現貨買進 2890 永豐金 1張 以參考價下單
    stock_trade = place_stock_order(api, "2890", Action.Buy, api.Contracts.Stocks["2890"].reference, 1)

    # 改價
    # update_stock_order(api, stock_trade, price=17.5)

    # 刪單
    # cancel_stock_order(api, stock_trade)

    # 期貨買進 台指期近月 1口 限價(以參考價下單)
    futures_trade = place_futures_order(
        api, "TXFR1", Action.Buy, api.Contracts.Futures["TXFR1"].reference, 1
    )

    # 查詢所有委託
    trades = list_trades(api)
    for t in trades:
        print(t.status)

    api.logout()
