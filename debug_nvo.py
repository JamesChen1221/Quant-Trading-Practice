"""
詳細檢查 NVO 的盤中數據
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

ticker = "NVO"
trade_date = "2026-02-03"

print("="*60)
print(f"詳細檢查 {ticker} 在 {trade_date} 的盤中數據")
print("="*60)

# 下載分鐘級數據
start = trade_date
end = (pd.to_datetime(trade_date) + timedelta(days=1)).strftime("%Y-%m-%d")

df = yf.download(ticker, start=start, end=end, interval="1m", progress=False)

if df.empty:
    print("✗ 無法獲取數據")
    exit(1)

# 處理多層索引
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

print(f"\n總共有 {len(df)} 根 K 棒")
print(f"時間範圍: {df.index[0]} ~ {df.index[-1]}")

# 顯示前 15 分鐘的數據
print("\n前 15 分鐘的數據:")
print("-"*60)
for i in range(min(15, len(df))):
    row = df.iloc[i]
    print(f"第 {i+1:2d} 分鐘 ({df.index[i].strftime('%H:%M')}): "
          f"開 ${row['Open']:.2f}, "
          f"高 ${row['High']:.2f}, "
          f"低 ${row['Low']:.2f}, "
          f"收 ${row['Close']:.2f}")

# 分析 10 分鐘後到 90 分鐘的數據
after_10min_to_90min = df.iloc[10:90]
print(f"\n開盤 10 分鐘後 ~ 1.5 小時的數據:")
print("-"*60)
print(f"數據範圍: 第 11 根到第 {min(90, len(df))} 根")

if len(after_10min_to_90min) > 0:
    high_90min = after_10min_to_90min['High'].max()
    high_90min_idx = after_10min_to_90min['High'].idxmax()
    high_position = df.index.get_loc(high_90min_idx)
    
    print(f"最高價: ${high_90min:.2f}")
    print(f"最高價時間: {high_90min_idx.strftime('%H:%M')}")
    print(f"最高價位置: 第 {high_position + 1} 根 K 棒")
    
    # 計算最高價前的最低價
    if high_position > 10:
        before_high = df.iloc[10:high_position+1]
        low_before_high = before_high['Low'].min()
        print(f"\n最高價前的範圍: 第 11 根到第 {high_position + 1} 根")
        print(f"最高價前的最低價: ${low_before_high:.2f}")
    elif high_position == 10:
        print(f"\n⚠ 最高價出現在第 11 根 K 棒（開盤後第 11 分鐘）")
        print(f"   這表示開盤 10 分鐘後立即達到高點")
        print(f"   建議設為最高價: ${high_90min:.2f}")
    else:
        print(f"\n⚠ 異常：最高價位置 {high_position} < 10")

print("\n" + "="*60)
