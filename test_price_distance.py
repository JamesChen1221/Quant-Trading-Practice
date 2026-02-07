"""
測試價格距離計算功能
"""

from calculate_indicators import calculate_rsi_adx_sequences
from datetime import datetime

# 測試參數
test_ticker = "NVDA"
test_date = "2026-02-05"  # 測試 2/5 的情況

print("="*60)
print("測試價格距離計算")
print("="*60)
print(f"\n測試股票: {test_ticker}")
print(f"測試日期: {test_date}\n")

# 計算指標
result = calculate_rsi_adx_sequences(test_ticker, test_date)

if result:
    print("\n" + "="*60)
    print("計算結果")
    print("="*60)
    
    print(f"\n昨日收盤價: ${result['昨日收盤價']}")
    
    print("\n5日價格距離:")
    if result['價格距離_5日']:
        print(f"  5日最高價: ${result['價格距離_5日']['最高價']}")
        print(f"  5日最低價: ${result['價格距離_5日']['最低價']}")
        print(f"  距離最高價: {result['價格距離_5日']['距離最高價(%)']}%")
        print(f"  距離最低價: {result['價格距離_5日']['距離最低價(%)']}%")
    
    print("\n1個月價格距離:")
    if result['價格距離_30日']:
        print(f"  30日最高價: ${result['價格距離_30日']['最高價']}")
        print(f"  30日最低價: ${result['價格距離_30日']['最低價']}")
        print(f"  距離最高價: {result['價格距離_30日']['距離最高價(%)']}%")
        print(f"  距離最低價: {result['價格距離_30日']['距離最低價(%)']}%")
    
    print("\n6個月價格距離:")
    if result['價格距離_180日']:
        print(f"  120日最高價: ${result['價格距離_180日']['最高價']}")
        print(f"  120日最低價: ${result['價格距離_180日']['最低價']}")
        print(f"  距離最高價: {result['價格距離_180日']['距離最高價(%)']}%")
        print(f"  距離最低價: {result['價格距離_180日']['距離最低價(%)']}%")
    
    print("\n解讀:")
    dist_5d_high = result['價格距離_5日']['距離最高價(%)']
    if dist_5d_high > -5:
        print(f"  ✓ 接近 5 日高點 ({dist_5d_high}%)")
    elif dist_5d_high < -15:
        print(f"  ✓ 遠離 5 日高點 ({dist_5d_high}%)，可能有反彈空間")
    else:
        print(f"  ✓ 距離 5 日高點 {dist_5d_high}%")
    
    print("\n" + "="*60)
else:
    print("\n✗ 計算失敗")
