import io
import base64
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set_style("whitegrid")
sns.set_palette("husl")


def _fig_to_html(fig) -> str:
    """Convert matplotlib figure to base64-encoded HTML image tag."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return f'<img src="data:image/png;base64,{image_base64}" style="width:100%;height:auto;border-radius:8px;"/>'


def build_category_distribution(df: pd.DataFrame) -> str:
    """Pie chart showing category-wise sales distribution."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    category_sales = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)
    colors = ['#E07B4F', '#4F8EE0', '#5DBD72']
    
    wedges, texts, autotexts = ax.pie(
        category_sales.values,
        labels=category_sales.index,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 11, 'weight': 'bold'}
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
    
    ax.set_title('Sales Distribution by Category', fontsize=14, weight='bold', pad=20)
    fig.tight_layout()
    
    return _fig_to_html(fig)


def build_state_heatmap(df: pd.DataFrame) -> str:
    """Heatmap showing monthly sales by state (top 15 states)."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    df_copy = df.copy()
    df_copy['Month'] = pd.to_datetime(df_copy['order_date']).dt.to_period('M').astype(str)
    
    pivot_data = df_copy.pivot_table(
        values='Sales',
        index='State',
        columns='Month',
        aggfunc='sum'
    )
    
    top_states = pivot_data.sum(axis=1).nlargest(15).index
    pivot_data = pivot_data.loc[top_states]
    
    sns.heatmap(
        pivot_data,
        cmap='YlGnBu',
        annot=False,
        fmt='.0f',
        cbar_kws={'label': 'Sales (₹)'},
        ax=ax,
        linewidths=0.5
    )
    
    ax.set_title('Monthly Sales Heatmap by State (Top 15)', fontsize=14, weight='bold', pad=20)
    ax.set_xlabel('Month', fontsize=11, weight='bold')
    ax.set_ylabel('State', fontsize=11, weight='bold')
    fig.tight_layout()
    
    return _fig_to_html(fig)


def build_profit_by_subcategory(df: pd.DataFrame) -> str:
    """Bar chart showing profit by sub-category."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    profit_data = df.groupby('Sub-Category')['Profit'].sum().sort_values()
    
    colors_list = ['#d32f2f' if x < 0 else '#388e3c' for x in profit_data.values]
    
    profit_data.plot(
        kind='barh',
        ax=ax,
        color=colors_list,
        edgecolor='black',
        linewidth=0.5
    )
    
    ax.set_title('Profit by Sub-Category', fontsize=14, weight='bold', pad=20)
    ax.set_xlabel('Profit (₹)', fontsize=11, weight='bold')
    ax.set_ylabel('Sub-Category', fontsize=11, weight='bold')
    
    for i, v in enumerate(profit_data.values):
        ax.text(v + 500, i, f'₹{v:,.0f}', va='center', fontsize=9)
    
    fig.tight_layout()
    
    return _fig_to_html(fig)


def build_sales_by_region(df: pd.DataFrame) -> str:
    """Bar chart showing total sales by region with sub-category breakdown."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    region_data = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
    
    bars = ax.bar(region_data.index, region_data.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
    
    ax.set_title('Total Sales by Region', fontsize=14, weight='bold', pad=20)
    ax.set_xlabel('Region', fontsize=11, weight='bold')
    ax.set_ylabel('Sales (₹)', fontsize=11, weight='bold')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x/1_000_000:.1f}M'))
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'₹{height/1_000_000:.2f}M',
                ha='center', va='bottom', fontsize=10, weight='bold')
    
    fig.tight_layout()
    
    return _fig_to_html(fig)


def build_discount_impact(df: pd.DataFrame) -> str:
    """Scatter plot showing discount vs profit relationship."""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    scatter = ax.scatter(
        df['Discount'] * 100,
        df['Profit'],
        alpha=0.5,
        s=50,
        c=df['Sales'],
        cmap='viridis',
        edgecolors='black',
        linewidth=0.3
    )
    
    ax.set_title('Impact of Discount on Profit', fontsize=14, weight='bold', pad=20)
    ax.set_xlabel('Discount (%)', fontsize=11, weight='bold')
    ax.set_ylabel('Profit (₹)', fontsize=11, weight='bold')
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7, label='Break-even')
    ax.grid(True, alpha=0.3)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Sales (₹)', fontsize=10, weight='bold')
    
    ax.legend()
    fig.tight_layout()
    
    return _fig_to_html(fig)


def build_rfm_segment_heatmap(rfm: pd.DataFrame) -> str:
    """Heatmap showing RFM scores by segment."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    segment_data = rfm.groupby('Segment')[['R_Score', 'F_Score', 'M_Score']].mean()
    
    sns.heatmap(
        segment_data.T,
        annot=True,
        fmt='.1f',
        cmap='RdYlGn',
        cbar_kws={'label': 'Score'},
        ax=ax,
        linewidths=1,
        linecolor='white'
    )
    
    ax.set_title('Average RFM Scores by Segment', fontsize=14, weight='bold', pad=20)
    ax.set_xlabel('Segment', fontsize=11, weight='bold')
    ax.set_ylabel('RFM Score', fontsize=11, weight='bold')
    
    fig.tight_layout()
    
    return _fig_to_html(fig)


def build_monthly_trend(df: pd.DataFrame) -> str:
    """Line chart showing monthly sales and profit trends."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    df_copy = df.copy()
    df_copy['Month'] = pd.to_datetime(df_copy['order_date']).dt.to_period('M').astype(str)
    
    monthly_data = df_copy.groupby('Month').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    })
    
    ax2 = ax.twinx()
    
    line1 = ax.plot(monthly_data.index, monthly_data['Sales'], marker='o', linewidth=2.5, 
                    color='#2196F3', label='Sales', markersize=6)
    line2 = ax2.plot(monthly_data.index, monthly_data['Profit'], marker='s', linewidth=2.5, 
                     color='#FF9800', label='Profit', markersize=6)
    
    ax.set_title('Monthly Sales & Profit Trend', fontsize=14, weight='bold', pad=20)
    ax.set_xlabel('Month', fontsize=11, weight='bold')
    ax.set_ylabel('Sales (₹)', fontsize=11, weight='bold', color='#2196F3')
    ax2.set_ylabel('Profit (₹)', fontsize=11, weight='bold', color='#FF9800')
    
    ax.tick_params(axis='y', labelcolor='#2196F3')
    ax2.tick_params(axis='y', labelcolor='#FF9800')
    
    ax.grid(True, alpha=0.3)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='upper left', fontsize=10)
    
    fig.tight_layout()
    
    return _fig_to_html(fig)


def build_product_performance_matrix(df: pd.DataFrame) -> str:
    """Bubble chart (scatter) showing product performance: revenue vs quantity."""
    fig, ax = plt.subplots(figsize=(11, 7))
    
    product_data = df.groupby('Sub-Category').agg({
        'Sales': 'sum',
        'Quantity': 'sum',
        'Profit': 'sum',
        'Order ID': 'count'
    }).reset_index()
    
    product_data['Profit_Margin'] = (product_data['Profit'] / product_data['Sales'] * 100).round(1)
    
    scatter = ax.scatter(
        product_data['Quantity'],
        product_data['Sales'],
        s=product_data['Order ID'] * 3,
        c=product_data['Profit_Margin'],
        cmap='RdYlGn',
        alpha=0.6,
        edgecolors='black',
        linewidth=1
    )
    
    for idx, row in product_data.iterrows():
        ax.annotate(
            row['Sub-Category'],
            (row['Quantity'], row['Sales']),
            fontsize=8,
            ha='center'
        )
    
    ax.set_title('Product Performance Matrix\n(Size = Orders, Color = Profit Margin %)', 
                 fontsize=14, weight='bold', pad=20)
    ax.set_xlabel('Total Quantity Sold', fontsize=11, weight='bold')
    ax.set_ylabel('Total Sales (₹)', fontsize=11, weight='bold')
    ax.grid(True, alpha=0.3)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Profit Margin (%)', fontsize=10, weight='bold')
    
    fig.tight_layout()
    
    return _fig_to_html(fig)


def build_customer_segment_distribution(rfm: pd.DataFrame) -> str:
    """Bar chart showing customer count by RFM segment."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    segment_counts = rfm['Segment'].value_counts()
    
    colors_map = {
        'Champion': '#4CAF50',
        'Loyal': '#2196F3',
        'Potential Loyalist': '#9C27B0',
        'At Risk': '#FF9800',
        'Need Attention': '#F44336',
        'Lost': '#9E9E9E',
    }
    
    colors = [colors_map.get(seg, '#888888') for seg in segment_counts.index]
    
    bars = ax.barh(segment_counts.index, segment_counts.values, color=colors, edgecolor='black', linewidth=0.5)
    
    ax.set_title('Customer Distribution by RFM Segment', fontsize=14, weight='bold', pad=20)
    ax.set_xlabel('Number of Customers', fontsize=11, weight='bold')
    ax.set_ylabel('Segment', fontsize=11, weight='bold')
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 5, bar.get_y() + bar.get_height()/2., f'{int(width)}',
                ha='left', va='center', fontsize=10, weight='bold')
    
    fig.tight_layout()
    
    return _fig_to_html(fig)
