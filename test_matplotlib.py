import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_config.settings')
django.setup()

import pandas as pd
from analytics.analysis.matplotlib_charts import (
    build_category_distribution,
    build_state_heatmap,
    build_profit_by_subcategory,
    build_sales_by_region,
)

# Create sample test data
test_df = pd.DataFrame({
    'Category': ['Furniture', 'Technology', 'Office Supplies'] * 10,
    'Sub-Category': ['Chair', 'Laptop', 'Pen'] * 10,
    'Sales': [100, 200, 50] * 10,
    'Profit': [10, 30, 5] * 10,
    'Quantity': [1, 2, 5] * 10,
    'State': ['Mumbai', 'Delhi', 'Bangalore'] * 10,
    'Region': ['North', 'South', 'East'] * 10,
    'Order ID': range(30),
    'order_date': pd.date_range('2023-01-01', periods=30),
})

# Test matplotlib chart generation
try:
    print("Testing build_category_distribution...")
    result = build_category_distribution(test_df)
    assert '<img src="data:image/png;base64,' in result, "Invalid output format"
    print("✓ build_category_distribution works")
    
    print("Testing build_sales_by_region...")
    result = build_sales_by_region(test_df)
    assert '<img src="data:image/png;base64,' in result, "Invalid output format"
    print("✓ build_sales_by_region works")
    
    print("Testing build_profit_by_subcategory...")
    result = build_profit_by_subcategory(test_df)
    assert '<img src="data:image/png;base64,' in result, "Invalid output format"
    print("✓ build_profit_by_subcategory works")
    
    print("\n✓ All matplotlib chart tests passed!")
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
