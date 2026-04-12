## 簽署文件

請參見[簽署中心](https://www.sinotrade.com.tw/newweb/signCenter/signCenterIndex/)並在簽署前**仔細閱讀文件**。

## API測試

確保您完全理解如何使用，需在模擬模式完成測試報告，內容包含以下功能:

- 登入測試 `login`
- 下單測試 `place_order`

Attention

可測試時間:

- 因應公司資訊安全規定，測試報告服務為星期一至五 08:00 ~ 20:00
- 18:00 ~ 20:00: 只允許台灣IP
- 08:00 ~ 18:00: 沒有限制

版本限制:

- 版本 >= 1.2:

  安裝指令: `uv add shioaji` or `pip install -U shioaji`

其他:

- API下單簽署時間須早於API測試的時間，以利審核通過
- 證券、期貨戶須各別測試
- 證券/期貨下單測試，需間隔1秒以上，以利系統留存測試紀錄

### 查詢使用版本

版本

```
import shioaji as sj

print(sj.__version__)
# 1.0.0

```

- 請注意**版本限制**

### 登入測試

登入

```
api = sj.Shioaji(simulation=True) # 模擬模式
api.login(
    api_key="金鑰",     # 請修改此處
    secret_key="密鑰"   # 請修改此處
)

```

```
api = sj.Shioaji(simulation=True) # 模擬模式
api.login(
    person_id="身分證字號", # 請修改此處
    passwd="密碼",          # 請修改此處
)

```

- 版本 >= 1.0: 使用 `API Key` 進行登入，若您尚未申請 API Key，可參考 [Token](../token/)
- 版本 < 1.0: 使用`身分證字號`進行登入

### 證券下單測試

證券

```
# 商品檔 - 請修改此處
contract = api.Contracts.Stocks.TSE["2890"]

# 證券委託單 - 請修改此處
order = api.Order(
    price=18,                                       # 價格
    quantity=1,                                     # 數量
    action=sj.constant.Action.Buy,                  # 買賣別
    price_type=sj.constant.StockPriceType.LMT,      # 委託價格類別
    order_type=sj.constant.OrderType.ROD,           # 委託條件
    account=api.stock_account                       # 下單帳號
)

# 下單
trade = api.place_order(contract, order)
trade

```

```
# 商品檔 - 請修改此處
contract = api.Contracts.Stocks.TSE["2890"]

# 證券委託單 - 請修改此處
order = api.Order(
    price=18,                                       # 價格
    quantity=1,                                     # 數量
    action=sj.constant.Action.Buy,                  # 買賣別
    price_type=sj.constant.TFTStockPriceType.LMT,   # 委託價格類別
    order_type=sj.constant.TFTOrderType.ROD,        # 委託條件
    account=api.stock_account                       # 下單帳號
)

# 下單
trade = api.place_order(contract, order)
trade

```

Out

```
Response Code: 0 | Event Code: 0 | Info: host '218.32.76.102:80', IP 218.32.76.102:80 (host 1 of 1) (host connection attempt 1 of 1) (total connection attempt 1 of 1) | Event: Session up

Trade(
    contract=Stock(...), 
    order=Order(...),
    status=OrderStatus(
        id='531e27af', 
        status=<Status.Submitted: 'Submitted'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 11, 18, 3, 867490), 
        order_quantity=1,
        deals=[]
    )
)

```

- 收到此訊息，`Response Code: 0 | Event Code: 0 | Info: host '218.32.76.102:80' ...`，代表您成功連結上測試伺服器。此訊息只有首次下單會顯示。若您未收到此訊息，請確認一下狀況均符合

  1. 在`可測試時間`進行測試
  1. 版本限制
  1. `signed` 未在您的帳號中顯示

- 委託單狀態不應為`Failed`，若您的委託單狀態`Failed`，請正確的修改委託單然後再次執行`place_order`

- [商品檔](../../contract/)

- [證券委託下單](../../order/Stock/)

### 期貨下單測試

期貨

```
# 商品檔 - 近月台指期貨, 請修改此處
contract = min(
    [
        x for x in api.Contracts.Futures.TXF 
        if x.code[-2:] not in ["R1", "R2"]
    ],
    key=lambda x: x.delivery_date
)

# 期貨委託單 - 請修改此處
order = api.Order(
    action=sj.constant.Action.Buy,                   # 買賣別
    price=15000,                                     # 價格
    quantity=1,                                      # 數量
    price_type=sj.constant.FuturesPriceType.LMT,     # 委託價格類別
    order_type=sj.constant.OrderType.ROD,            # 委託條件
    octype=sj.constant.FuturesOCType.Auto,           # 倉別
    account=api.futopt_account                       # 下單帳號
)

# 下單
trade = api.place_order(contract, order)

```

```
# 商品檔 - 近月台指期貨, 請修改此處
contract = min(
    [
        x for x in api.Contracts.Futures.TXF 
        if x.code[-2:] not in ["R1", "R2"]
    ],
    key=lambda x: x.delivery_date
)

# 期貨委託單 - 請修改此處
order = api.Order(
    action=sj.constant.Action.Buy,                  # 買賣別
    price=15000,                                    # 價格
    quantity=1,                                     # 數量
    price_type=sj.constant.FuturesPriceType.LMT,    # 委託價格類別
    order_type=sj.constant.FuturesOrderType.ROD,    # 委託條件
    octype=sj.constant.FuturesOCType.Auto,          # 倉別
    account=api.futopt_account                      # 下單帳號
)

# 下單
trade = api.place_order(contract, order)

```

Out

```
Response Code: 0 | Event Code: 0 | Info: host '218.32.76.102:80', IP 218.32.76.102:80 (host 1 of 1) (host connection attempt 1 of 1) (total connection attempt 1 of 1) | Event: Session up

Trade(
    contract=Stock(...), 
    order=Order(...),
    status=OrderStatus(
        id='531e27af', 
        status=<Status.Submitted: 'Submitted'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 11, 18, 3, 867490), 
        order_quantity=1,
        deals=[]
    )
)

```

- 收到此訊息，`Response Code: 0 | Event Code: 0 | Info: host '218.32.76.102:80' ...`，代表您成功連結上測試伺服器。此訊息只有首次下單會顯示。若您未收到此訊息，請確認一下狀況均符合

  1. 在`可測試時間`進行測試
  1. 版本限制
  1. `signed` 未在您的帳號中顯示

- 委託單狀態不應為`Failed`，若您的委託單狀態`Failed`，請正確的修改委託單然後再次執行`place_order`

- [商品檔](../../contract/)

- [期貨委託下單](../../order/FutureOption/)

### 查詢是否通過API測試

Attention

在查詢前，請確認以下狀況均符合

- API下單簽署時間須早於API測試的時間，以利審核通過
- 在可測試時間進行測試
- 證券、期貨戶須各別測試
- 等待API測試審核(約5分鐘)

簽署狀態

```
import shioaji as sj

api = sj.Shioaji(simulation=False)   # Production Mode
accounts = api.login(
    api_key="YOUR_API_KEY",         # edit it
    secret_key="YOUR_SECRET_KEY"    # edit it
)
accounts

```

```
import shioaji as sj

api = sj.Shioaji(simulation=False)   # Production Mode
accounts = api.login(
    person_id="YOUR_PERSON_ID",     # edit it
    passwd="YOUR_PASSWORD",         # edit it
)
accounts

```

Out

```
Response Code: 0 | Event Code: 0 | Info: host '203.66.91.161:80', hostname '203.66.91.161:80' IP 203.66.91.161:80 (host 1 of 1) (host connection attempt 1 of 1) (total connection attempt 1 of 1) | Event: Session up

[FutureAccount(person_id='QBCCAIGJBJ', broker_id='F002000', account_id='9100020', signed=True, username='PAPIUSER01'),
StockAccount(person_id='QBCCAIGJBJ', broker_id='9A95', account_id='0504350', username='PAPIUSER01')]

```

- `signed=True`: 恭喜完成測試! Ex: FutureAccount.
- `signed=False` 或 `signed` 未顯示: 此帳號尚未通過API測試或尚未簽署API下單文件. Ex: StockAccount.

## 憑證

下單前必須**申請**並**啟用**憑證

#### 申請憑證

1. 至[理財網](https://www.sinotrade.com.tw/CSCenter/CSCenter_13_3)下載 eleader
1. 登入 eleader
1. 從上方帳戶資料選取(3303)帳號資料設定
1. 點選"步驟說明"
1. 憑證操作步驟說明

#### 啟用憑證

- 若是使用測試帳號無需啟用憑證
- 如果您使用macOS，可能會遇到版本上的問題。我們建議您使用 [docker](https://github.com/Sinotrade/Shioaji) 去運行shioaji。

In

```
result = api.activate_ca(
    ca_path="/c/your/ca/path/Sinopac.pfx",
    ca_passwd="YOUR_CA_PASSWORD",
    person_id="Person ID of this Ca",
)

print(result)
# True

```

憑證路徑

在 Windows 系統中，如果文件路徑使用 \\ 來分隔文件，您需要將它替換為 /。

#### 確認憑證效期

In

```
api.get_ca_expiretime("Person ID")

```

在版本1.0之後，我們將使用Token作為我們的登入方式。請根據下列的步驟進行申請及使用。

## 申請金鑰

1. 至[理財網](https://www.sinotrade.com.tw/newweb/PythonAPIKey/)個人服務中的API管理頁面

1. 點選新增API KEY

1. 利用手機或是信箱做雙因子驗證，驗證成功才能建立API KEY。

1. 進行API KEY的到期時間設定，以及勾選權限與帳戶，並且設定IP限制。

   權限勾選說明

   - 行情 / 資料 : 可否使用行情 / 資料相關 API
   - 帳務 : 可否使用帳務相關 API
   - 交易 : 可否使用交易相關 API
   - 正式環境 : 可否在正式環境中使用

   注意

   IP建議使用限制，能使該KEY安全性提高。

1. 新增成功會得到金鑰(API Key)與密鑰(Secret Key)

   注意

   - 請妥善保存您的鑰匙，勿將其透漏給任何人，以免造成資產損失。
   - Secret Key 僅在建立成功時取得，此後再無任何方法得到，請確保以保存

## 憑證下載

1. 點選下載憑證按鈕
1. 下載完成請前往下載資料夾將憑證放置到 API 要讀取的路徑

## 確認密鑰與憑證

延續前面開好的專案 `sj-trading`，在專案資料夾中新增 `.env` 檔案，並且新增以下內容

`.env` 檔案內容如下

```
API_KEY=<前面申請的API Key>
SECRET_KEY=<前面申請的Secret Key>
CA_CERT_PATH=<前面設定的憑證路徑>
CA_PASSWORD=<憑證密碼>

```

專案資料夾結構如下

```
sj-trading
├── README.md
├── .env
├── pyproject.toml
├── src
│   └── sj_trading
│       └─ __init__.py
└── uv.lock

```

加入 python-dotenv 套件來將 .env 的金鑰與憑證載入環境變數

```
uv add python-dotenv

```

在 `src/sj_trading/__init__.py` 中新增以下內容

```
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    api = sj.Shioaji(simulation=True)
    api.login(
        api_key=os.environ["API_KEY"],
        secret_key=os.environ["SECRET_KEY"],
        fetch_contract=False
    )
    api.activate_ca(
        ca_path=os.environ["CA_CERT_PATH"],
        ca_passwd=os.environ["CA_PASSWORD"],
    )
    print("login and activate ca success")

```

在 `pyproject.toml` 中 `[project.scripts]` 新增 `main` 指令

```
[project.scripts]
main = "sj_trading:main"

```

執行 `main` 指令

```
uv run main

```

如果看到 `login and activate ca success` 代表成功登入模擬環境了

接著如果你還有沒有進行 API 簽署的話，請前往下一章進行簽署與測試審核。
