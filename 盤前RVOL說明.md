# 盤前 RVOL 計算說明

## ⚠️ 重要說明

對於**盤前預測模型**，RVOL 應該使用**盤前成交量**計算，而不是全日成交量。

### 正確的計算方式

```
盤前 RVOL = 今日盤前成交量 / 過去 5 日平均盤前成交量
```

### 目前的限制

**yfinance 無法獲取盤前交易量資料**

- yfinance 只提供全日成交量（Regular Trading Hours）
- 盤前交易量（Pre-market Volume）需要其他資料源

---

## 🔧 解決方案

### 方案 1：手動輸入盤前成交量（推薦）

#### 步驟 1：在 Excel 中新增欄位

在「資料庫」工作表中新增「盤前成交量」欄位：

| 開盤日期 | 公司代碼 | **盤前成交量** | 相對成交量 (RVOL) |
|---------|---------|---------------|------------------|
| 2026-02-03 | NVDA | 1500000 | (自動計算) |
| 2026-02-03 | AAPL | 2000000 | (自動計算) |

#### 步驟 2：填入盤前成交量

從你的資料源（券商平台、財經網站等）獲取盤前成交量並填入。

#### 步驟 3：執行程式

```bash
python calculate_indicators.py
```

程式會：
1. 偵測到「盤前成交量」欄位
2. 使用盤前成交量計算 RVOL
3. 自動填入結果

---

### 方案 2：使用付費 API

如果需要自動獲取盤前成交量，可以使用以下 API：

#### 2.1 Alpha Vantage

```python
import requests

API_KEY = "your_api_key"
symbol = "NVDA"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol={symbol}&interval=1min&slice=year1month1&apikey={API_KEY}"

# 需要篩選盤前時段（美東時間 4:00 AM - 9:30 AM）
```

**限制**：
- 免費版每分鐘 5 次請求
- 需要付費才能獲取更多資料

#### 2.2 Polygon.io

```python
import requests

API_KEY = "your_api_key"
symbol = "NVDA"
date = "2026-02-03"

# 獲取盤前資料
url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}?adjusted=true&sort=asc&apiKey={API_KEY}"

# 篩選盤前時段
```

**限制**：
- 免費版有限制
- 需要付費訂閱

#### 2.3 Interactive Brokers (IBKR) API

```python
from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# 獲取盤前資料
contract = Stock('NVDA', 'SMART', 'USD')
bars = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='1 D',
    barSizeSetting='1 min',
    whatToShow='TRADES',
    useRTH=False  # 包含盤前盤後
)
```

**優點**：
- 資料完整
- 可以獲取盤前盤後資料

**限制**：
- 需要 IBKR 帳戶
- 需要安裝 TWS 或 IB Gateway

---

### 方案 3：使用網頁爬蟲

從財經網站爬取盤前成交量：

#### 3.1 Yahoo Finance（網頁版）

```python
import requests
from bs4 import BeautifulSoup

def get_premarket_volume(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 需要找到盤前成交量的 HTML 元素
    # 注意：網頁結構可能隨時改變
    
    return premarket_volume
```

**限制**：
- 網頁結構可能改變
- 可能違反服務條款
- 不穩定

#### 3.2 MarketWatch

```python
def get_premarket_volume_marketwatch(symbol):
    url = f"https://www.marketwatch.com/investing/stock/{symbol}"
    # 類似的爬蟲邏輯
```

---

## 📊 盤前 RVOL 的重要性

### 為什麼盤前 RVOL 很重要？

1. **預測開盤走勢**
   ```
   高盤前 RVOL + 盤前上漲 → 開盤可能繼續上漲
   高盤前 RVOL + 盤前下跌 → 開盤可能繼續下跌
   低盤前 RVOL → 開盤可能平淡
   ```

2. **識別重大事件**
   ```
   盤前 RVOL > 3.0 → 可能有重大消息（財報、新聞）
   盤前 RVOL > 5.0 → 極重大事件
   ```

3. **評估市場情緒**
   ```
   高盤前 RVOL → 市場關注度高
   低盤前 RVOL → 市場興趣不高
   ```

### 盤前 vs 全日 RVOL 的差異

| 指標 | 盤前 RVOL | 全日 RVOL |
|------|----------|----------|
| **計算時間** | 盤前（4:00-9:30 AM ET） | 全日（9:30 AM - 4:00 PM ET） |
| **用途** | 預測開盤走勢 | 評估全日交易活躍度 |
| **數值範圍** | 通常較高（0.5-10+） | 較穩定（0.5-3.0） |
| **重要性** | 對盤前預測模型極重要 | 對日內交易重要 |

---

## 🎯 實際應用範例

### 範例 1：財報日

```
股票：NVDA
日期：2026-02-03（財報日）
盤前成交量：15,000,000
過去 5 日平均盤前成交量：2,000,000

盤前 RVOL = 15,000,000 / 2,000,000 = 7.5

解讀：
- 盤前 RVOL 7.5 倍（極高）
- 財報引發高度關注
- 開盤可能有大波動
- 需要密切關注盤前價格走勢
```

### 範例 2：正常交易日

```
股票：AAPL
日期：2026-02-04
盤前成交量：3,000,000
過去 5 日平均盤前成交量：2,500,000

盤前 RVOL = 3,000,000 / 2,500,000 = 1.2

解讀：
- 盤前 RVOL 1.2 倍（正常偏高）
- 沒有特別消息
- 開盤可能平穩
- 可以觀望
```

### 範例 3：低成交量

```
股票：XYZ
日期：2026-02-05
盤前成交量：500,000
過去 5 日平均盤前成交量：1,000,000

盤前 RVOL = 500,000 / 1,000,000 = 0.5

解讀：
- 盤前 RVOL 0.5 倍（低）
- 市場興趣不高
- 開盤可能平淡
- 不適合當沖
```

---

## 💡 建議的工作流程

### 流程 1：手動輸入（適合小規模）

```
1. 每天早上從券商平台查看盤前成交量
2. 手動填入 Excel「盤前成交量」欄位
3. 執行 python calculate_indicators.py
4. 查看計算結果
5. 根據 RVOL 和其他指標做決策
```

### 流程 2：半自動（適合中規模）

```
1. 使用爬蟲或 API 獲取盤前成交量
2. 自動填入 Excel
3. 執行計算程式
4. 查看結果並決策
```

### 流程 3：全自動（適合大規模）

```
1. 訂閱專業資料服務（如 Polygon.io）
2. 建立自動化腳本
3. 定時獲取資料並計算
4. 自動生成交易信號
```

---

## 📝 Excel 欄位設定

### 建議的欄位結構

| 欄位名稱 | 資料類型 | 說明 | 範例 |
|---------|---------|------|------|
| 開盤日期(台灣時間) | 日期 | 交易日期 | 2026-02-03 |
| 公司代碼 | 文字 | 股票代號 | NVDA |
| **盤前成交量** | 數字 | **手動填入** | 15000000 |
| 相對成交量 (RVOL) | 數字 | **自動計算** | 7.5 |

### 如何新增欄位

1. 開啟「量化交易.xlsx」
2. 在「資料庫」工作表中找到「盤前漲幅 (%)」欄位
3. 在其後新增「盤前成交量」欄位
4. 填入數據
5. 執行程式

---

## 🔍 資料來源建議

### 免費資源

1. **Yahoo Finance 網頁版**
   - 查看盤前成交量
   - 手動記錄

2. **券商平台**
   - TD Ameritrade
   - Interactive Brokers
   - Webull

3. **財經網站**
   - MarketWatch
   - Investing.com
   - TradingView

### 付費資源

1. **Alpha Vantage**
   - $49.99/月起
   - API 訪問

2. **Polygon.io**
   - $29/月起
   - 完整盤前盤後資料

3. **IEX Cloud**
   - $9/月起
   - 有限資料

---

## ⚠️ 注意事項

### 1. 資料品質

- 確保盤前成交量資料準確
- 注意時區轉換（美東時間 vs 台灣時間）
- 驗證資料來源的可靠性

### 2. 計算時機

- 盤前 RVOL 應在盤前結束後計算（美東時間 9:30 AM）
- 台灣時間約為晚上 10:30 PM（冬令時）或 9:30 PM（夏令時）

### 3. 歷史資料

- 需要至少 5 天的歷史盤前成交量
- 新股或停牌後復牌的股票可能資料不足

### 4. 異常值

- 財報日盤前 RVOL 可能極高（> 10）
- 需要結合其他指標判斷

---

## 🎉 總結

### 目前狀況

- ✅ 程式支援從 Excel 讀取「盤前成交量」欄位
- ✅ 如果有盤前成交量，會優先使用
- ⚠️ 如果沒有，會使用全日成交量（僅供參考）

### 建議做法

1. **短期**：手動填入盤前成交量
2. **中期**：使用爬蟲或免費 API
3. **長期**：訂閱專業資料服務

### 重要提醒

對於**盤前預測模型**：
- 必須使用盤前成交量計算 RVOL
- 全日成交量的 RVOL 參考價值有限
- 建議投資專業資料服務以獲取準確資料

---

**相關文件**：
- [RVOL計算說明.md](RVOL計算說明.md) - 一般 RVOL 說明
- [範例資料說明.md](範例資料說明.md) - Excel 欄位結構
