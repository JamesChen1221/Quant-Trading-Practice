import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import openpyxl
import numpy as np

def calculate_rsi(close_prices, period=14):
    """計算 RSI 指標"""
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_adx(high, low, close, period=14):
    """計算 ADX 指標"""
    # 計算 True Range
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # 計算方向移動
    up_move = high - high.shift()
    down_move = low.shift() - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    plus_dm = pd.Series(plus_dm, index=close.index)
    minus_dm = pd.Series(minus_dm, index=close.index)
    
    # 平滑化
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    
    # 計算 DX 和 ADX
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    
    return adx

def calculate_rvol(volume_series, period=5):
    """
    計算相對成交量 (RVOL)
    
    RVOL = 當日成交量 / 過去 N 天平均成交量
    
    注意：此函數計算的是全日成交量的 RVOL
    對於盤前預測，應使用盤前成交量計算
    
    參數:
        volume_series: 成交量序列
        period: 計算平均的天數（預設 5 天）
    
    返回:
        RVOL 序列
    """
    avg_volume = volume_series.rolling(window=period).mean()
    rvol = volume_series / avg_volume
    return rvol

def calculate_premarket_rvol_from_excel(df, current_idx, premarket_col, date_col, period=5):
    """
    從 Excel 資料中計算盤前 RVOL
    
    需要當日及過去 N 天的盤前成交量資料
    
    參數:
        df: DataFrame
        current_idx: 當前行索引
        premarket_col: 盤前成交量欄位名稱
        date_col: 日期欄位名稱
        period: 計算平均的天數（預設 5 天）
    
    返回:
        盤前 RVOL 或 None
    """
    try:
        # 獲取當日盤前成交量
        current_volume = df.loc[current_idx, premarket_col]
        
        if pd.isna(current_volume) or current_volume <= 0:
            return None
        
        # 獲取當日日期
        current_date = pd.to_datetime(df.loc[current_idx, date_col])
        
        # 獲取同一股票的歷史資料
        ticker = df.loc[current_idx, '公司代碼']
        same_ticker = df[df['公司代碼'] == ticker]
        
        # 找出當日之前的資料
        historical = same_ticker[pd.to_datetime(same_ticker[date_col]) < current_date]
        
        # 按日期排序，取最近的 N 天
        historical = historical.sort_values(by=date_col, ascending=False).head(period)
        
        # 獲取歷史盤前成交量
        historical_volumes = historical[premarket_col].dropna()
        
        # 過濾掉 <= 0 的值
        historical_volumes = historical_volumes[historical_volumes > 0]
        
        if len(historical_volumes) == 0:
            print(f"    ⚠ 警告: 找不到過去 {period} 天的盤前成交量資料")
            return None
        
        if len(historical_volumes) < period:
            print(f"    ⚠ 警告: 只有 {len(historical_volumes)} 天的歷史盤前成交量（建議至少 {period} 天）")
        
        # 計算平均
        avg_volume = historical_volumes.mean()
        
        # 計算 RVOL
        rvol = current_volume / avg_volume
        
        return rvol
        
    except Exception as e:
        print(f"    ✗ 計算盤前 RVOL 時發生錯誤: {str(e)}")
        return None

def calculate_rsi_adx_sequences(ticker, start_date, days_5=5, days_30=30):
    """
    計算指定股票在開盤日期之前的 RSI、ADX 和 RVOL（過去的資料）
    
    參數:
        ticker: 股票代碼 (例如: "NVDA")
        start_date: 開盤日期 (字串或 datetime)
        days_5: 5天序列長度
        days_30: 30天序列長度
    
    返回:
        dict: 包含 RSI、ADX、RVOL 的序列和開盤日當天的 RVOL
    """
    try:
        # 確保日期格式正確
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        
        # 計算需要抓取的日期範圍
        # 需要抓取開盤日期之前的資料，多抓一些以確保有足夠的資料計算指標
        # RSI 和 ADX 預設使用 14 天週期，所以需要額外的資料
        fetch_start = start_date - timedelta(days=90)  # 約 3 個月前，確保有足夠交易日
        fetch_end = start_date + timedelta(days=1)     # 到開盤日期當天
        
        # 下載股票資料
        print(f"  正在下載 {ticker} 的資料...")
        df = yf.download(ticker, start=fetch_start, end=fetch_end, progress=False)
        
        if df.empty:
            print(f"  警告: {ticker} 沒有資料")
            return None
        
        # 處理多層索引的情況（yfinance 新版本可能返回多層索引）
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # 確保資料是一維的
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns and df[col].ndim > 1:
                df[col] = df[col].iloc[:, 0]
        
        # 計算 RSI (14)
        df["RSI"] = calculate_rsi(df["Close"], period=14)
        
        # 計算 ADX (14)
        df["ADX"] = calculate_adx(df["High"], df["Low"], df["Close"], period=14)
        
        # 計算 RVOL (5 天平均)
        df["RVOL"] = calculate_rvol(df["Volume"], period=5)
        
        # 找到開盤日期當天或之前的資料（包含開盤日期當天）
        df_before_start = df[df.index <= start_date]
        
        if len(df_before_start) < days_30:
            print(f"  警告: {ticker} 在 {start_date.date()} 之前的資料不足 {days_30} 天")
        
        # 取得序列（移除 NaN 值）
        rsi_series = df_before_start["RSI"].dropna()
        adx_series = df_before_start["ADX"].dropna()
        rvol_series = df_before_start["RVOL"].dropna()
        
        # 取得最近的 5 天和 30 天序列（從最遠到最近）
        # tail() 取最後 N 筆，保持原始順序（從舊到新）
        rsi_5 = rsi_series.tail(days_5).tolist()
        rsi_30 = rsi_series.tail(days_30).tolist()
        adx_5 = adx_series.tail(days_5).tolist()
        adx_30 = adx_series.tail(days_30).tolist()
        
        # 取得開盤日當天的 RVOL（最新的一筆）
        rvol_current = rvol_series.iloc[-1] if len(rvol_series) > 0 else None
        
        return {
            "RSI_5天": rsi_5,
            "RSI_30天": rsi_30,
            "ADX_5天": adx_5,
            "ADX_30天": adx_30,
            "RVOL": rvol_current,  # 開盤日當天的相對成交量
            "實際資料天數": len(rsi_series)
        }
    
    except Exception as e:
        print(f"  處理 {ticker} 時發生錯誤: {str(e)}")
        return None

if __name__ == "__main__":
    # 執行主程式
    input_file = "量化交易.xlsx"
    sheet_name = "資料庫"  # 指定工作表名稱
    
    # 使用 openpyxl 直接讀取 Excel，保留格式
    print(f"正在讀取 {input_file} 的 '{sheet_name}' 工作表...")
    
    # 先用 pandas 讀取資料
    df = pd.read_excel(input_file, sheet_name=sheet_name)
    
    # 顯示欄位名稱，方便確認
    print(f"Excel 欄位: {df.columns.tolist()}")
    print(f"共有 {len(df)} 筆資料\n")
    
    # 使用正確的欄位名稱
    ticker_col = '公司代碼'
    date_col = '開盤日期(台灣時間)'
    
    # 檢查欄位是否存在
    if ticker_col not in df.columns or date_col not in df.columns:
        print(f"錯誤: 找不到必要欄位")
        print(f"需要的欄位: '{ticker_col}' 和 '{date_col}'")
        print(f"現有欄位: {df.columns.tolist()}")
        exit(1)
    
    print(f"使用欄位: 股票代碼='{ticker_col}', 日期='{date_col}'\n")
    
    # 檢查是否有盤前成交量欄位
    premarket_volume_col = '盤前成交量'
    has_premarket_volume = premarket_volume_col in df.columns
    
    if has_premarket_volume:
        print(f"✓ 偵測到「{premarket_volume_col}」欄位，將使用盤前成交量計算 RVOL")
    else:
        print(f"⚠ 未偵測到「{premarket_volume_col}」欄位，將使用全日成交量計算 RVOL")
        print(f"  提示：對於盤前預測，建議新增「{premarket_volume_col}」欄位\n")
    
    # 更新對應的欄位
    rsi_5_col = '5天 RSI 序列'
    rsi_30_col = '1個月 RSI 序列'
    adx_5_col = '5天 ADX 序列'
    adx_30_col = '1個月 ADX 序列'
    rvol_col = '相對成交量 (RVOL)'
    
    # 找到欄位索引
    col_indices = {}
    for col_name in [rsi_5_col, rsi_30_col, adx_5_col, adx_30_col, rvol_col]:
        if col_name in df.columns:
            col_indices[col_name] = df.columns.get_loc(col_name) + 1  # Excel 列從 1 開始
    
    # 統計變數
    processed_count = 0
    skipped_count = 0
    failed_count = 0
    
    # 儲存需要更新的資料
    updates = {}
    
    # 逐行處理
    for idx, row in df.iterrows():
        ticker = row[ticker_col]
        date = row[date_col]
        
        # 跳過空值
        if pd.isna(ticker) or pd.isna(date):
            print(f"跳過第 {idx + 1} 筆: 資料不完整")
            skipped_count += 1
            continue
        
        # 檢查是否已經計算過（所有欄位都有資料且不是空序列）
        has_rsi_5 = not pd.isna(row[rsi_5_col]) and str(row[rsi_5_col]).strip() not in ['', '[]', 'nan']
        has_rsi_30 = not pd.isna(row[rsi_30_col]) and str(row[rsi_30_col]).strip() not in ['', '[]', 'nan']
        has_adx_5 = not pd.isna(row[adx_5_col]) and str(row[adx_5_col]).strip() not in ['', '[]', 'nan']
        has_adx_30 = not pd.isna(row[adx_30_col]) and str(row[adx_30_col]).strip() not in ['', '[]', 'nan']
        has_rvol = not pd.isna(row[rvol_col]) and str(row[rvol_col]).strip() not in ['', 'nan']
        
        if has_rsi_5 and has_rsi_30 and has_adx_5 and has_adx_30 and has_rvol:
            print(f"跳過第 {idx + 1} 筆: {ticker} (日期: {date}) - 已有計算結果")
            skipped_count += 1
            continue
        
        print(f"處理第 {idx + 1} 筆: {ticker} (日期: {date})")
        
        # 計算指標
        result = calculate_rsi_adx_sequences(ticker, date)
        
        # 計算 RVOL（如果有盤前成交量資料）
        rvol_value = None
        if has_premarket_volume and premarket_volume_col in df.columns:
            # 嘗試從 Excel 計算盤前 RVOL
            rvol_value = calculate_premarket_rvol_from_excel(
                df, idx, premarket_volume_col, date_col, period=5
            )
            
            if rvol_value is None:
                # 如果無法計算盤前 RVOL，使用全日成交量作為替代
                print(f"  ⚠ 無法計算盤前 RVOL，使用全日成交量替代")
                rvol_value = result.get("RVOL") if result else None
        else:
            # 使用全日成交量
            rvol_value = result.get("RVOL") if result else None
        
        if result and len(result["RSI_5天"]) > 0:
            # 儲存更新資料（Excel 行號從 2 開始，因為第 1 行是標題）
            excel_row = idx + 2
            updates[excel_row] = {
                rsi_5_col: str(result["RSI_5天"]),
                rsi_30_col: str(result["RSI_30天"]),
                adx_5_col: str(result["ADX_5天"]),
                adx_30_col: str(result["ADX_30天"]),
                rvol_col: rvol_value if rvol_value is not None else ""
            }
            
            print(f"  ✓ 完成 (實際資料: {result['實際資料天數']} 天)")
            if len(result['RSI_5天']) >= 3:
                print(f"  RSI 5天前3筆: {[round(x, 2) for x in result['RSI_5天'][:3]]}")
            if rvol_value is not None:
                print(f"  RVOL: {round(rvol_value, 2)} {'(全日成交量)' if not has_premarket_volume else '(盤前成交量)'}")
            processed_count += 1
        else:
            print(f"  ✗ 失敗或無資料")
            failed_count += 1
        
        print()
    
    # 顯示統計資訊
    print(f"\n{'='*60}")
    print(f"處理完成統計:")
    print(f"  新計算: {processed_count} 筆")
    print(f"  已跳過: {skipped_count} 筆（已有資料或資料不完整）")
    print(f"  失敗: {failed_count} 筆")
    print(f"  總計: {len(df)} 筆")
    print(f"{'='*60}\n")
    
    # 如果有需要更新的資料，使用 openpyxl 直接寫入以保留格式
    if updates:
        print(f"正在更新 {input_file} 的 '{sheet_name}' 工作表（保留原有格式）...")
        
        # 使用 openpyxl 載入工作簿
        from openpyxl import load_workbook
        wb = load_workbook(input_file)
        ws = wb[sheet_name]
        
        # 更新儲存格
        for excel_row, data in updates.items():
            for col_name, value in data.items():
                if col_name in col_indices:
                    col_idx = col_indices[col_name]
                    cell = ws.cell(row=excel_row, column=col_idx)
                    cell.value = value
        
        # 儲存工作簿
        wb.save(input_file)
        wb.close()
        
        print("完成！格式已保留。")
    else:
        print("沒有需要更新的資料。")
    
    print("\n提示：序列排序為從最遠到最近 [第5天前, 第4天前, 第3天前, 第2天前, 第1天前]")
