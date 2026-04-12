# Shioaji - Taiwan's Leading Cross Platform Trading API

> Shioaji is Taiwan's most popular trading API with highest market share. Cross-platform support for Windows, Linux, and Mac. Trade stocks, futures, options with Python. First Taiwan trading API with AI coding agent skills.

# Usage documentation

商品檔將在很多地方被使用，例如下單、訂閱行情...等。

### 取得商品檔

下方提供兩種方法取得商品檔:

- 方法1: [登入](../../tutor/login)成功後，將開始下載商品檔。但這個下載過程將不會影響其他的操作。若您想了解是否下載完成，可利用`Contracts.status`去得到下載狀態。`contracts_timeout` 設定為10000，它將等待10秒下載商品檔。

In

```
import shioaji as sj
api = sj.Shioaji()
api.login(
    api_key="YOUR_API_KEY", 
    secret_key="YOUR_SECRET_KEY",
    contracts_timeout=10000,
)

```

```
import shioaji as sj
api = sj.Shioaji()
api.login(
    person_id="YOUR_PERSON_ID", 
    passwd="YOUR_PASSWORD",
    contracts_timeout=10000,
)

```

- 方法2: 若不想在登入時下載商品檔，將`fetch_contract` 設定為`False`。利用 `fetch_contracts` 下載商品檔

In

```
import shioaji as sj
api = sj.Shioaji()
api.login(
    api_key="YOUR_API_KEY", 
    secret_key="YOUR_SECRET_KEY",
    fetch_contract=False,
)
api.fetch_contracts(contract_download=True)

```

```
import shioaji as sj
api = sj.Shioaji()
api.login(
    person_id="YOUR_PERSON_ID", 
    passwd="YOUR_PASSWORD",
    fetch_contract=False,
)
api.fetch_contracts(contract_download=True)

```

### 商品檔資訊

目前我們所提供的商品包含:證券、期貨、選擇權以及指數。可從下列方法更詳細得到我們所提供的商品。

In

```
api.Contracts

```

Out

```
Contracts(Indexs=(OTC, TSE), Stocks=(OES, OTC, TSE), Futures=(BRF, CAF, CBF, CCF, CDF, CEF, CFF, CGF, CHF, CJF, CK1, CKF, CLF, CM1, CMF, CNF, CQF, CRF, CSF, CU1, CUF, CWF, CXF, CYF, CZ1, CZF, DCF, DD1, DDF, DEF, DFF, DGF, DHF, DIF, DJF, DKF, DLF, DNF, DOF, DPF, DQF, DSF, DUF, DVF, DWF, DXF, DYF, DZF, EEF, EGF, EHF, EMF, EPF, ERF, EXF, EY1, EYF, FEF, FFF, FGF, FKF, FQF, FRF, FTF, FVF, FWF, FXF, FYF, FZF, G2F, GAF, GCF, GDF, GHF, GIF, GJF, GLF, GMF, GNF, GOF, GRF, GTF, GUF, GWF, GXF, GZF, HAF, HBF, HCF, HHF, HIF, HLF, HOF, HS1, HSF, HY1, HYF, IA1, IAF, IHF, IIF, IJF, IMF, IOF, IPF, IQF, IRF, ITF, IXF, IYF, IZF, JBF, JFF, JNF, JPF, JSF, JWF, JZF, KAF, KB1, KBF, KCF, KDF, KFF, KGF, KIF, KKF, KLF, KOF, KPF, KSF, KWF, LBF, LCF, LE1, LEF, LIF, LMF, LOF, LQF, LRF, LTF, LUF, LVF, LWF, LXF, LYF, MAF, MBF, MCF, MJF, MKF, MPF, MQF, MVF, MX1, MXF, MYF, NAF, NBF, NCF, NDF, NEF, NGF, NHF, NIF, NJF, NLF, NMF, NNF, NOF, NQF, NSF, NUF, NVF, NWF, NXF, NYF, NZF, OAF, OBF, OCF, ODF, OEF, OGF, OHF, OJF, OKF, OLF, OMF, OOF, OPF, OQF, ORF, OS1, OSF, OTF, OUF, OVF, OWF, OXF, OYF, OZF, PAF, PBF, PCF, PDF, PEF, PFF, PGF, PHF, PIF, PJF, PKF, PLF, PMF, PNF, POF, PPF, PQF, RHF, RTF, SPF, T5F, TGF, TJF, TXF, UDF, UNF, XAF, XBF, XEF, XIF, XJF), Options=(CAO, CBO, CCO, CDO, CEO, CFO, CGO, CHO, CJO, CKO, CLO, CMO, CNO, CQO, CRO, CSO, CXO, CZO, DCO, DEO, DFO, DGO, DHO, DJO, DKO, DLO, DNO, DOO, DPO, DQO, DSO, DUO, DVO, DWO, DXO, GIO, GXO, HCO, IJO, LOO, NYA, NYO, NZO, OAO, OBO, OCO, OJO, OKO, OOO, OZO, RHO, RTO, TEO, TFO, TGO, TX1, TXO))

```

#### 證券

In

```
api.Contracts.Stocks["2890"]
# or api.Contracts.Stocks.TSE.TSE2890

```

Out

```
Stock(
    exchange=<Exchange.TSE: 'TSE'>, 
    code='2890', 
    symbol='TSE2890', 
    name='永豐金', 
    category='17', 
    unit=1000, 
    limit_up=19.1, 
    limit_down=15.7, 
    reference=17.4, 
    update_date='2023/01/17', 
    day_trade=<DayTrade.Yes: 'Yes'>
)

```

Stock

```
exchange (Exchange): 交易所 {OES, OTC, TSE ...等}
code (str): 商品代碼
symbol (str): 符號
name (str): 商品名稱
category (str): 類別
unit (int): 單位
limit_up (float): 漲停價
limit_down (float): 跌停價
reference (float): 參考價
update_date (str): 更新日期
margin_trading_balance (int): 融資餘額
short_selling_balance (int): 融券餘額
day_trade (DayTrade): 可否當沖 {Yes, No, OnlyBuy}

```

#### 期貨

In

```
api.Contracts.Futures["TXFA3"]
# or api.Contracts.Futures.TXF.TXF202301

```

Out

```
Future(
    code='TXFA3', 
    symbol='TXF202301', 
    name='臺股期貨01', 
    category='TXF', 
    delivery_month='202301', 
    delivery_date='2023/01/30', 
    underlying_kind='I', 
    unit=1, 
    limit_up=16417.0, 
    limit_down=13433.0, 
    reference=14925.0, 
    update_date='2023/01/18'
)

```

Future

```
code (str): 商品代碼
symbol (str): 符號
name (str): 商品名稱
category (str): 類別
delivery_month (str): 交割月份
delivery_date (str): 結算日
underlying_kind (str): 標的類型
unit (int): 單位
limit_up (float): 漲停價
limit_down (float): 跌停價
reference (float): 參考價
update_date (str): 更新時間

```

#### 選擇權

In

```
api.Contracts.Options["TXO18000R3"]
# or api.Contracts.Options.TXO.TXO20230618000P

```

Out

```
Option(
    code='TXO18000R3', 
    symbol='TXO20230618000P', 
    name='臺指選擇權06月 18000P', 
    category='TXO', 
    delivery_month='202306', 
    delivery_date='2023/06/21', 
    strike_price=18000, 
    option_right=<OptionRight.Put: 'P'>, 
    underlying_kind='I', 
    unit=1, 
    limit_up=4720.0, 
    limit_down=1740.0, 
    reference=3230.0, 
    update_date='2023/01/18'
)

```

Option

```
code (str): 商品代碼
symbol (str): 符號
name (str): 商品名稱
category (str): 類型
delivery_month (str): 交割月份
delivery_date (str): 交割日期
strike_price (int or float): 屢約價
option_right (OptionRight): 買賣權別
underlying_kind (str): 標的類型
limit_up (float): 漲停價
limit_down (float): 跌停價
reference (float): 參考價
update_date (str): 更新時間

```

#### 指數

`Indexs`物件顯示所有可以支援的指數商品，其他類別亦然。指數類的商品不支援下單，但允許訂閱行情。

In

```
api.Contracts.Indexs.TSE

```

Out

```
TSE(TSE001, TSE015, TSE016, TSE017, TSE018, TSE019, TSE020, TSE022, TSE023, TSE024, TSE025, TSE026, TSE028, TSE029, TSE030, TSE031, TSE032, TSE033, TSE035, TSE036, TSE037, TSE038, TSE039, TSE040, TSE041, TSE042, TSE043, TSE004, TSE005)

```

In

```
api.Contracts.Indexs.TSE["001"]
# or api.Contracts.Indexs.TSE.TSE001

```

Out

```
Index(
    exchange=<Exchange.TSE: 'TSE'>, 
    code='001', 
    symbol='TSE001', 
    name='加權指數'
)

```

Index

````python
exchange (Exchange): 交易所{OES, OTC, TSE ...等}
code (str): 商品代碼
symbol (str): 符號
name (str): 商品名稱

商品檔更新資訊

- 07:50 期貨商品檔更新
- 08:00 全市場商品檔更新
- 14:45 期貨夜盤商品檔更新
- 17:15 期貨夜盤商品檔更新```
````

為避免影響其他使用者連線，請遵守以下使用規範

流量

- 現貨 :

  | 近 30 日使用 API 成交金額 | 每日流量限制 | | --- | --- | | 0 | 500MB | | 1 - 1億 | 2GB | | > 1億 | 10GB |

- 期貨 :

  | 近 30 日使用 API 成交金額 | 每日流量限制 | | --- | --- | | 0 | 500MB | | 1 - 大台1000口 / 小台4000口 | 2GB | | > 大台1000口 / 小台4000口 | 10G |

流量及連線數查詢

```
api.usage()

```

Out

```
UsageStatus(connections=1, bytes=41343260, limit_bytes=2147483648, remaining_bytes=2106140388)

```

```
connection: 連線數量
bytes: 已使用流量
limit_bytes: 每日流量限制
remaining_bytes: 剩餘可使用流量

```

次數

- 行情 :

  `credit_enquire`, `short_stock_sources`, `snapshots`, `ticks`, `kbars`

  - 以上查詢總次數 5 秒上限 50 次
  - 盤中查詢 `ticks` 次數不得超過 10 次
  - 盤中查詢 `kbars` 次數不得超過 270 次

- 帳務 :

  `list_profit_loss_detail`,`account_balance`, `list_settlements`, `list_profit_loss`, `list_positions`, `margin`

  以上查詢總次數 5 秒上限 25 次

- 委託 :

  `place_order`, `update_status`, `update_qty`, `update_price`, `cancel_order`

  以上查詢總次數 10 秒上限 250 次

- 訂閱數 :

  `api.subscribe()`數量為200個

- 連線 :

  同一永豐金證券`person_id`，僅可使用最多5個連線。 注意: `api.login()`即建立一個連線

- 登入 :

  `api.login()`一天上限1000次

Warn

- 若流量超過限制，行情(ticks、snapshots、kbars)類查詢將回傳空值，其他功能不受影響
- 若使用量超過限制，將暫停服務一分鐘
- 若當日連續多次超過限制，本公司將暫停該 IP 及 ID 使用權
- 若 ID 被暫停使用，請洽 Shioaji 管理人員

登入必須擁有永豐金帳戶。若你還沒有擁永豐金帳戶，可詳見[開戶](../prepare/open_account/)。

