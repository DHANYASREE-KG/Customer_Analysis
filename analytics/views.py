import logging
import traceback

import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from .models import Order, Customer, RfmSegment
from .analysis.dashboard_charts import (
    build_state_bar,
    build_sunburst,
    build_animated_bar,
    build_bubble_chart,
    build_rfm_scatter,
    build_dropdown_bar,
)
from .analysis.matplotlib_charts import (
    build_category_distribution,
    build_state_heatmap,
    build_profit_by_subcategory,
    build_sales_by_region,
    build_discount_impact,
    build_rfm_segment_heatmap,
    build_monthly_trend,
    build_product_performance_matrix,
    build_customer_segment_distribution,
)

logger = logging.getLogger(__name__)


def _matplotlib_chart_or_none(builder, *args, **kwargs):
    try:
        html = builder(*args, **kwargs)
        return html
    except Exception as e:
        logger.error("Matplotlib chart error in %s: %s", builder.__name__, e)
        logger.error(traceback.format_exc())
        return ""


def _chart_or_none(builder, *args, **kwargs):
    try:
        fig = builder(*args, **kwargs)
        return fig.to_html(full_html=False, include_plotlyjs=False)
    except Exception as e:
        logger.error("Chart error in %s: %s", builder.__name__, e)
        logger.error(traceback.format_exc())
        return ""



def _prepare_data(state_name=None):
    filter_kwargs = {}
    if state_name:
        filter_kwargs["state"] = state_name

    orders = Order.objects.select_related("customer").filter(**filter_kwargs).values(
        "order_id", "order_date", "ship_date", "category", "sub_category",
        "state", "region", "sales", "profit", "discount", "quantity",
        "customer__customer_id",
    )
    df = pd.DataFrame(list(orders))

    rfm_qs = RfmSegment.objects.all().values(
        "customer__customer_id", "recency", "frequency",
        "monetary", "r_score", "f_score", "m_score",
        "rfm_score", "segment",
    )
    rfm = pd.DataFrame(list(rfm_qs))

    if df.empty:
        return df, rfm

    df["Order Date"] = pd.to_datetime(df["order_date"])
    df["Ship Date"] = pd.to_datetime(df["ship_date"])
    df.rename(columns={
        "category": "Category", "sub_category": "Sub-Category",
        "state": "State", "region": "Region", "sales": "Sales",
        "profit": "Profit", "discount": "Discount", "quantity": "Quantity",
        "order_id": "Order ID",
        "customer__customer_id": "Customer ID",
    }, inplace=True)

    df["Month Label"] = df["Order Date"].dt.to_period("M").astype(str)

    if not rfm.empty:
        rfm.rename(columns={
            "customer__customer_id": "Customer ID",
            "segment": "Segment",
            "recency": "Recency",
            "frequency": "Frequency",
            "monetary": "Monetary",
            "r_score": "R_Score",
            "f_score": "F_Score",
            "m_score": "M_Score",
            "rfm_score": "RFM_Score",
        }, inplace=True)

    return df, rfm


def dashboard(request):
    df, rfm = _prepare_data()

    if df.empty:
        return render(request, "analytics/dashboard.html", {
            "error": "No data found. Run `python manage.py import_data` first.",
        })

    context = {
        "fig_bar": _chart_or_none(build_state_bar, df),
        "fig_sun": _chart_or_none(build_sunburst, df),
        "fig_anim": _chart_or_none(build_animated_bar, df),
        "fig_bubble": _chart_or_none(build_bubble_chart, df),
        "fig_rfm": _chart_or_none(build_rfm_scatter, rfm) if not rfm.empty else "",
        "fig_dd": _chart_or_none(build_dropdown_bar, df, rfm) if not rfm.empty else "",
        # Matplotlib/Seaborn charts
        "fig_category": _matplotlib_chart_or_none(build_category_distribution, df),
        "fig_heatmap": _matplotlib_chart_or_none(build_state_heatmap, df),
        "fig_profit": _matplotlib_chart_or_none(build_profit_by_subcategory, df),
        "fig_region": _matplotlib_chart_or_none(build_sales_by_region, df),
        "fig_discount": _matplotlib_chart_or_none(build_discount_impact, df),
        "fig_rfm_heat": _matplotlib_chart_or_none(build_rfm_segment_heatmap, rfm) if not rfm.empty else "",
        "fig_trend": _matplotlib_chart_or_none(build_monthly_trend, df),
        "fig_product": _matplotlib_chart_or_none(build_product_performance_matrix, df),
        "fig_customer_dist": _matplotlib_chart_or_none(build_customer_segment_distribution, rfm) if not rfm.empty else "",
        "kpi_revenue": f"₹{df['Sales'].sum() / 1_000_000:.2f}M",
        "kpi_profit": f"₹{df['Profit'].sum() / 1_000:.0f}K",
        "kpi_orders": f"{df['Order ID'].nunique():,}",
        "kpi_customers": f"{Customer.objects.count():,}",
        "kpi_margin": f"{(df['Profit'].sum() / df['Sales'].sum() * 100):.1f}%",
        "selected_state": "",
    }
    return render(request, "analytics/dashboard.html", context)


def state_dashboard(request, state_name):
    df, rfm = _prepare_data(state_name)

    if df.empty:
        return JsonResponse({"error": f"No data for {state_name}"}, status=404)

    return JsonResponse({
        "fig_sun": _chart_or_none(build_sunburst, df),
        "fig_anim": _chart_or_none(build_animated_bar, df),
        "fig_bubble": _chart_or_none(build_bubble_chart, df),
        "fig_dd": _chart_or_none(build_dropdown_bar, df, rfm) if not rfm.empty else "",
        # Matplotlib/Seaborn charts for state view
        "fig_category": _matplotlib_chart_or_none(build_category_distribution, df),
        "fig_heatmap": _matplotlib_chart_or_none(build_state_heatmap, df),
        "fig_profit": _matplotlib_chart_or_none(build_profit_by_subcategory, df),
        "fig_region": _matplotlib_chart_or_none(build_sales_by_region, df),
        "fig_discount": _matplotlib_chart_or_none(build_discount_impact, df),
        "fig_rfm_heat": _matplotlib_chart_or_none(build_rfm_segment_heatmap, rfm) if not rfm.empty else "",
        "fig_trend": _matplotlib_chart_or_none(build_monthly_trend, df),
        "fig_product": _matplotlib_chart_or_none(build_product_performance_matrix, df),
        "fig_customer_dist": _matplotlib_chart_or_none(build_customer_segment_distribution, rfm) if not rfm.empty else "",
        "kpi_revenue": f"₹{df['Sales'].sum() / 1_000_000:.2f}M",
        "kpi_profit": f"₹{df['Profit'].sum() / 1_000:.0f}K",
        "kpi_orders": f"{df['Order ID'].nunique():,}",
        "kpi_margin": f"{(df['Profit'].sum() / df['Sales'].sum() * 100):.1f}%",
                "state": state_name,
    })
