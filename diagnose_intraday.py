"""
診斷盤中數據問題
"""

import pandas as pd
from calculate_indicators import calculate_intraday_prices

# 讀取 Excel
df = pd.read_excel("量化交易.xlsx", sheet_name="資料庫")

print("="*60)
print("診斷盤中數據問題")
print("="*60)

# 找出有開盤價但沒有「最高價前的最低價」的項目
open_col = '*開盤價格' if '*開盤價格' in df.columns else '開盤價格'
low_before_high_col = '*最高價前的最低價' if '*最高價前的最低價' in df.columns else '最高價前的最低價'

if open_col not in df.columns or low_before_high_col not in df.columns:
    print("✗ 找不到必要欄位")
    exit(1)

# 找出問題項目
problem_rows = []
for idx, row in df.iterrows():
    has_open = not pd.isna(row[open_col]) and str(row[open_col]).strip() not in ['', 'nan']
    has_low_before_high = not pd.isna(row[low_before_high_col]) and str(row[low_before_high_col]).strip() not in ['', 'nan']
    
    if has_open and not has_low_before_high:
        problem_rows.append({
            'index': idx,
            'ticker': row['公司代碼'],
            'date': row['開盤日期'],
            'open_price': row[open_col]
        })

if not problem_rows:
    print("\n✓ 沒有發現問題項目")
    print("  所有有開盤價的項目都有「最高價前的最低價」")
else:
    print(f"\n發現 {len(problem_rows)} 個問題項目:")
    print("-"*60)
    
    for item in problem_rows[:3]:  # 只檢查前 3 個
        print(f"\n項目 {item['index'] + 1}:")
        print(f"  股票: {item['ticker']}")
        print(f"  日期: {item['date']}")
        print(f"  開盤價: ${item['open_price']}")
        
        # 重新獲取盤中數據來診斷
        print(f"\n  重新獲取盤中數據...")
        result = calculate_intraday_prices(item['ticker'], item['date'])
        
        if result:
            print(f"  結果:")
            print(f"    開盤價: ${result['開盤價']}")
            print(f"    10分鐘最低價: ${result['10分鐘最低價']}")
            print(f"    1.5小時最高價: ${result['1.5小時最高價']}")
            print(f"    最高價前的最低價: ${result['最高價前的最低價']}")
            print(f"    數據分鐘數: {result['數據分鐘數']}")
            
            if result['最高價前的最低價'] is None:
                print(f"\n  ⚠ 原因: 可能是最高價出現在開盤 10 分鐘內")
        else:
            print(f"  ✗ 無法獲取盤中數據")

print("\n" + "="*60)
print("可能的原因:")
print("  1. 最高價出現在開盤 10 分鐘內")
print("  2. 數據不足 90 分鐘")
print("  3. 該日期超過 7 天（yfinance 限制）")
print("="*60)
