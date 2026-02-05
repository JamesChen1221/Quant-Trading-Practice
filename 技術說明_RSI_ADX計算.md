# RSI 和 ADX 計算技術說明

## 📊 重要更新：計算過去資料

**序列定義已更新：**
- **5 天序列**：開盤日期**之前**最近的 5 個交易日
- **30 天序列**：開盤日期**之前**最近的 30 個交易日
- **排序方式**：從最近到最遠（最新的資料在前）

這樣可以分析開盤前的技術指標趨勢，用於預測開盤後的走勢。

---

## 資料來源

### 使用 yfinance 套件抓取股價資訊

程式使用 `yfinance` 套件從 **Yahoo Finance** 下載美股歷史股價資料。

```python
import yfinance as yf

# 下載股票資料
df = yf.download("NVDA", start="2025-11-01", end="2026-02-05", progress=False)
```

下載的資料包含：
- **Open**（開盤價）
- **High**（最高價）
- **Low**（最低價）
- **Close**（收盤價）
- **Volume**（成交量）
- **日期索引**（交易日期）

---

## RSI (Relative Strength Index) 計算

### 公式說明

RSI 是衡量價格變動速度和幅度的動量指標，數值範圍 0-100。

**計算步驟：**

1. **計算價格變動（Delta）**
   ```
   Delta = Close(今日) - Close(昨日)
   ```

2. **分離漲跌**
   ```
   Gain = Delta（當 Delta > 0）
   Loss = -Delta（當 Delta < 0）
   ```

3. **計算平均漲跌（使用 n 天移動平均）**
   ```
   Average Gain = Gain 的 n 天移動平均
   Average Loss = Loss 的 n 天移動平均
   ```

4. **計算相對強度（RS）**
   ```
   RS = Average Gain / Average Loss
   ```

5. **計算 RSI**
   ```
   RSI = 100 - (100 / (1 + RS))
   ```

### 程式實作

```python
def calculate_rsi(close_prices, period=14):
    """計算 RSI 指標"""
    # 1. 計算價格變動
    delta = close_prices.diff()
    
    # 2. 分離漲跌
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    # 3. 計算 RS
    rs = gain / loss
    
    # 4. 計算 RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi
```

### 參數設定

- **n = 14**（預設值，業界標準）
- 可調整為其他值（如 9、21、28）

### 解讀

- **RSI > 70**：超買區，可能回調
- **RSI < 30**：超賣區，可能反彈
- **RSI = 50**：中性區

---

## ADX (Average Directional Index) 計算

### 公式說明

ADX 是衡量趨勢強度的指標，數值範圍 0-100，不顯示趨勢方向。

**計算步驟：**

1. **計算真實波幅（True Range, TR）**
   ```
   TR = max(
       High - Low,
       |High - Close(前一日)|,
       |Low - Close(前一日)|
   )
   ```

2. **計算方向移動（Directional Movement）**
   ```
   +DM = High(今日) - High(昨日)（當上漲且 +DM > -DM 時）
   -DM = Low(昨日) - Low(今日)（當下跌且 -DM > +DM 時）
   ```

3. **計算平滑化的 ATR 和 DM（使用 n 天移動平均）**
   ```
   ATR = TR 的 n 天移動平均
   +DI = 100 × (+DM 的 n 天移動平均 / ATR)
   -DI = 100 × (-DM 的 n 天移動平均 / ATR)
   ```

4. **計算方向指標差（DX）**
   ```
   DX = 100 × |+DI - -DI| / (+DI + -DI)
   ```

5. **計算 ADX（DX 的移動平均）**
   ```
   ADX = DX 的 n 天移動平均
   ```

### 程式實作

```python
def calculate_adx(high, low, close, period=14):
    """計算 ADX 指標"""
    # 1. 計算 True Range
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # 2. 計算方向移動
    up_move = high - high.shift()
    down_move = low.shift() - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    plus_dm = pd.Series(plus_dm, index=close.index)
    minus_dm = pd.Series(minus_dm, index=close.index)
    
    # 3. 平滑化
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    
    # 4. 計算 DX
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    
    # 5. 計算 ADX
    adx = dx.rolling(window=period).mean()
    
    return adx
```

### 參數設定

- **n = 14**（預設值，業界標準）
- 可調整為其他值（如 7、21、28）

### 解讀

- **ADX > 25**：強趨勢（適合趨勢跟隨策略）
- **ADX < 20**：弱趨勢或盤整（適合區間交易策略）
- **ADX > 50**：非常強的趨勢
- **ADX 上升**：趨勢增強
- **ADX 下降**：趨勢減弱

---

## 資料抓取邏輯

### 時間範圍計算

為了計算開盤日期**之前**的 RSI/ADX，需要抓取足夠的歷史資料：

```python
# 開盤日期
start_date = "2026-02-03"

# 需要抓取的時間範圍
fetch_start = start_date - 90 天  # 約 3 個月前
fetch_end = start_date + 1 天     # 到開盤日期當天（包含）

# 下載資料
df = yf.download(ticker, start=fetch_start, end=fetch_end)
```

### 為什麼需要提前 90 天？

1. **RSI 計算需要**：
   - 14 天的價格變動資料
   - 額外的資料來計算移動平均（約 14 天）
   - 總計約需要 28 個交易日

2. **ADX 計算需要**：
   - 14 天的 TR 和 DM 資料
   - 14 天的 DI 資料
   - 14 天的 DX 資料來計算 ADX
   - 總計約需要 42 個交易日

3. **30 天序列需要**：
   - 需要開盤日期之前至少 30 個交易日的 RSI/ADX 資料
   - 加上計算指標所需的額外資料
   - 總計約需要 72 個交易日

4. **考慮非交易日**：
   - 週末、假日不是交易日
   - 90 個日曆日約包含 60-65 個交易日
   - 確保有足夠的資料計算 30 天序列

### 序列提取（更新）

```python
# 找到開盤日期當天或之前的資料（包含開盤日期）
df_before_start = df[df.index <= start_date]

# 取得 RSI 和 ADX 序列（移除 NaN 值）
rsi_series = df_before_start["RSI"].dropna()
adx_series = df_before_start["ADX"].dropna()

# 取得最近的 5 天和 30 天序列（從最近到最遠）
rsi_5 = rsi_series.tail(5).tolist()[::-1]   # 取最後5筆並反轉
rsi_30 = rsi_series.tail(30).tolist()[::-1] # 取最後30筆並反轉

# 結果：[最近, 第2近, 第3近, 第4近, 第5近]
```

---

## 完整流程圖

```
1. 讀取 Excel「資料庫」工作表
   ↓
2. 逐行讀取股票代碼和開盤日期
   ↓
3. 檢查是否已有計算結果
   - 如果已有完整資料 → 跳過
   - 如果沒有或不完整 → 繼續計算
   ↓
4. 使用 yfinance 下載股價資料
   - 時間範圍：開盤日期前 90 天 ~ 開盤日期當天
   - 資料來源：Yahoo Finance
   ↓
5. 計算技術指標
   - RSI (n=14)
   - ADX (n=14)
   ↓
6. 提取序列（過去的資料）
   - 從開盤日期往前推
   - 取得最近 5 天和 30 天的序列
   - 排序：從最近到最遠
   ↓
7. 寫回 Excel
   - 5天 RSI 序列
   - 1個月 RSI 序列
   - 5天 ADX 序列
   - 1個月 ADX 序列
   ↓
8. 顯示統計資訊
   - 新計算筆數
   - 跳過筆數
   - 失敗筆數
```

---

## 範例計算

假設股票代碼：**TER**，開盤日期：**2026-02-03**

### 步驟 1：下載資料
```python
# 抓取 2025-11-05 到 2026-02-04 的資料
df = yf.download("TER", start="2025-11-05", end="2026-02-04")
```

### 步驟 2：計算指標
```python
# 計算 RSI (14)
df["RSI"] = calculate_rsi(df["Close"], period=14)

# 計算 ADX (14)
df["ADX"] = calculate_adx(df["High"], df["Low"], df["Close"], period=14)
```

### 步驟 3：提取序列（過去的資料）
```python
# 從 2026-02-03 及之前的資料
df_before = df[df.index <= "2026-02-03"]

# 取得最近 5 天 RSI 序列（從最近到最遠）
rsi_5 = df_before["RSI"].dropna().tail(5).tolist()[::-1]
# 結果：[78.52, 69.18, 68.51, 82.70, 73.66]
# 解讀：最近一天 RSI=78.52（超買），前一天 69.18，再前一天 68.51...

# 取得最近 5 天 ADX 序列
adx_5 = df_before["ADX"].dropna().tail(5).tolist()[::-1]
# 結果：[28.39, 27.57, 28.36, 28.37, 27.95]
# 解讀：最近一天 ADX=28.39（中等趨勢強度）
```

---

## 參數總結

| 參數 | 預設值 | 說明 |
|------|--------|------|
| **RSI 週期 (n)** | 14 | 計算移動平均的天數 |
| **ADX 週期 (n)** | 14 | 計算移動平均的天數 |
| **5 天序列** | 5 | 短期趨勢分析 |
| **30 天序列** | 30 | 長期趨勢分析（約 1 個月） |
| **資料提前天數** | 60 | 確保有足夠的歷史資料 |
| **資料延後天數** | 45 | 確保有足夠的未來資料 |

---

## 注意事項

1. **交易日 vs 日曆日**：
   - 序列中的「5 天」指 5 個交易日，不包含週末和假日
   - 「30 天」指 30 個交易日，約等於 1.5 個月的日曆日

2. **資料方向**：
   - ✅ 計算開盤日期**之前**的資料（過去）
   - ❌ 不需要開盤日期之後的資料（未來）
   - 序列從最近到最遠排列

3. **NaN 值處理**：
   - RSI 和 ADX 的前 14 天會是 NaN（因為需要 14 天的資料來計算）
   - 程式會自動移除 NaN 值

4. **計算精度**：
   - 使用 pandas 的浮點數計算
   - 結果保留完整精度（可根據需求四捨五入）

5. **增量計算**：
   - ✅ 程式會自動跳過已有完整資料的項目
   - ✅ 只計算新增或不完整的項目
   - ✅ 節省時間和 API 請求次數

---

## 參考資料

- **RSI**：由 J. Welles Wilder 於 1978 年提出
- **ADX**：由 J. Welles Wilder 於 1978 年提出
- **資料來源**：Yahoo Finance (透過 yfinance 套件)
- **標準週期**：業界普遍使用 14 天作為預設週期
