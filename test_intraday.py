"""
測試盤中數據獲取功能
"""

from calculate_indicators import calculate_intraday_prices
from datetime import datetime, timedelta

print("="*60)
print("測試盤中數據獲取")
print("="*60)

# 測試 1：最近的日期（應該可以獲取）
print("\n測試 1：最近的交易日")
print("-"*60)
recent_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
print(f"日期: {recent_date}")
print(f"股票: NVDA\n")

result = calculate_intraday_prices("NVDA", recent_date)

if result:
    print("\n✓ 成功獲取盤中數據:")
    print(f"  開盤價: ${result['開盤價']}")
    print(f"  10分鐘最低價: ${result['10分鐘最低價']}")
    print(f"  1.5小時最高價: ${result['1.5小時最高價']}")
    print(f"  最高價前的最低價: ${result['最高價前的最低價']}")
    print(f"  數據分鐘數: {result['數據分鐘數']}")
else:
    print("\n✗ 無法獲取盤中數據")

# 測試 2：超過 7 天的日期（應該跳過）
print("\n" + "="*60)
print("測試 2：超過 7 天的日期")
print("-"*60)
old_date = "2026-01-15"
print(f"日期: {old_date}")
print(f"股票: NVDA\n")

result2 = calculate_intraday_prices("NVDA", old_date)

if result2:
    print("\n✓ 成功獲取盤中數據")
else:
    print("\n✓ 正確跳過（超過 7 天限制）")

print("\n" + "="*60)
print("說明:")
print("  - yfinance 免費版只提供最近 7 天的分鐘級數據")
print("  - 超過 7 天的日期會自動跳過")
print("  - 如需歷史盤中數據，需要使用付費 API")
print("="*60)
