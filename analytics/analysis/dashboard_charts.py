import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


CAT_COLORS = {
    "Furniture": "#E07B4F",
    "Technology": "#4F8EE0",
    "Office Supplies": "#5DBD72",
}

SEG_COLORS = {
    "Champion": "#4CAF50",
    "Loyal": "#2196F3",
    "Potential Loyalist": "#9C27B0",
    "At Risk": "#FF9800",
    "Need Attention": "#F44336",
    "Lost": "#9E9E9E",
}



def build_sunburst(df: pd.DataFrame) -> go.Figure:
    sunburst_data = df.groupby(["Category", "Sub-Category", "Region"]).agg(
        Revenue=("Sales", "sum"),
    ).reset_index()

    fig = px.sunburst(
        sunburst_data, path=["Category", "Sub-Category", "Region"],
        values="Revenue", color="Revenue",
        color_continuous_scale="RdYlGn",
        title="Revenue Hierarchy: Category → Sub-Category → Region",
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<extra></extra>",
    )
    fig.update_layout(height=560, title_font_size=16)
    return fig


def build_animated_bar(df: pd.DataFrame) -> go.Figure:
    monthly_cat = (
        df.groupby(["Month Label", "Category"])
        .agg(Revenue=("Sales", "sum"))
        .reset_index()
        .sort_values("Month Label")
    )
    monthly_cat["Cumulative"] = (
        monthly_cat
        .sort_values("Month Label")
        .groupby("Category")["Revenue"]
        .cumsum()
    )

    fig = px.bar(
        monthly_cat, x="Category", y="Cumulative",
        animation_frame="Month Label", animation_group="Category",
        color="Category",
        range_y=[0, monthly_cat["Cumulative"].max() * 1.15],
        title="Cumulative Revenue Race by Category",
        color_discrete_map=CAT_COLORS,
        labels={"Cumulative": "Cumulative Revenue (₹)"},
        text="Cumulative",
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(
        height=480, title_font_size=15, showlegend=False,
        yaxis_tickprefix="₹", yaxis_tickformat=",.0f",
    )
    return fig


def build_bubble_chart(df: pd.DataFrame) -> go.Figure:
    bubble_data = df.groupby(["Sub-Category", "Category"]).agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "count"),
        Avg_Discount=("Discount", "mean"),
    ).reset_index()
    bubble_data["Profit Margin %"] = (
        bubble_data["Profit"] / bubble_data["Revenue"] * 100
    ).round(1)

    fig = px.scatter(
        bubble_data, x="Revenue", y="Profit",
        size="Orders", color="Category", text="Sub-Category",
        hover_data={"Profit Margin %": ":.1f", "Avg_Discount": ":.0%"},
        title="Sub-Category Performance (bubble size = orders)",
        color_discrete_map=CAT_COLORS,
        labels={"Revenue": "Revenue (₹)", "Profit": "Profit (₹)"},
        size_max=55,
    )
    fig.update_traces(textposition="top center", textfont_size=9)
    fig.add_hline(y=0, line_dash="dash", line_color="red",
                  opacity=0.5, annotation_text="Break-even")
    fig.update_layout(
        height=520, title_font_size=15,
        xaxis_tickprefix="₹", xaxis_tickformat=",.0f",
        yaxis_tickprefix="₹", yaxis_tickformat=",.0f",
    )
    return fig


def build_rfm_scatter(rfm: pd.DataFrame) -> go.Figure:
    seg_agg = rfm.groupby("Segment").agg(
        Customers=("Customer ID", "count"),
        Avg_Recency=("Recency", "mean"),
        Avg_Frequency=("Frequency", "mean"),
        Avg_Monetary=("Monetary", "mean"),
    ).reset_index()

    fig = px.scatter(
        seg_agg, x="Avg_Recency", y="Avg_Frequency",
        size="Avg_Monetary", color="Segment", text="Segment",
        title="RFM Segments — Recency vs Frequency (size = avg spend)",
        hover_data={"Customers": True, "Avg_Monetary": ":,.0f"},
        color_discrete_map=SEG_COLORS,
        size_max=60,
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        height=480, title_font_size=15,
        xaxis_title="Avg Recency (days)",
        yaxis_title="Avg Frequency (# orders)",
    )
    return fig


def build_state_bar(df: pd.DataFrame) -> go.Figure:
    data = df.groupby("State").agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "count"),
    ).reset_index()
    data["Profit Margin %"] = (data["Profit"] / data["Revenue"] * 100).round(1)
    data = data.sort_values("Revenue", ascending=True)

    max_rev = data["Revenue"].max() or 1
    marker_colors = []
    for rev in data["Revenue"]:
        if rev == 0:
            marker_colors.append("#D1D5DB")
        else:
            ratio = rev / max_rev
            r = int(59 + (30 - 59) * ratio)
            g = int(130 + (64 - 130) * ratio)
            b = int(246 + (95 - 246) * ratio)
            marker_colors.append(f"rgb({r},{g},{b})")

    stem_x = []
    stem_y = []
    for _, row in data.iterrows():
        rev = row["Revenue"]
        stem_x.extend([0, rev, None])
        stem_y.extend([row["State"], row["State"], None])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stem_x, y=stem_y,
        mode="lines",
        line=dict(color="#CBD5E1", width=1.5),
        hoverinfo="skip",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=data["Revenue"],
        y=data["State"],
        mode="markers+text",
        marker=dict(
            color=marker_colors, size=13,
            line=dict(color="white", width=2.5),
            symbol="circle",
        ),
        text=data["Revenue"].apply(lambda v: f"₹{v/1_000_000:.2f}M" if v > 0 else ""),
        textposition="middle right",
        textfont=dict(size=11, color="#4B5563"),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Revenue: ₹%{x:,.0f}<br>"
            "Profit: ₹%{customdata[0]:,.0f}<br>"
            "Orders: %{customdata[1]}<br>"
            "Margin: %{customdata[2]}%"
            "<extra></extra>"
        ),
        customdata=data[["Profit", "Orders", "Profit Margin %"]].values,
        showlegend=False,
    ))

    fig.update_layout(
        title=dict(text="State-wise Revenue", font=dict(size=17, color="#1F2937"), x=0.03),
        height=500,
        margin=dict(l=10, r=140, t=50, b=10),
        xaxis=dict(
            title=dict(text="Revenue (₹)", font=dict(size=11, color="#6B7280")),
            tickprefix="₹", tickformat=",.0f",
            showgrid=True, gridcolor="#F3F4F6", gridwidth=1,
            zeroline=False, tickfont=dict(size=10, color="#9CA3AF"),
            range=[0, max_rev * 1.3],
        ),
        yaxis=dict(
            title=None, autorange="reversed",
            showgrid=False, tickfont=dict(size=11, color="#374151"),
        ),
        plot_bgcolor="#F9FAFB", paper_bgcolor="white",
        hoverlabel=dict(bgcolor="#1F2937", font=dict(color="white", size=12), bordercolor="#374151"),
        dragmode=False,
    )
    return fig


def build_dropdown_bar(df: pd.DataFrame, rfm: pd.DataFrame) -> go.Figure:
    segments = sorted(rfm["Segment"].unique())
    categories = sorted(df["Category"].unique())

    customer_segments = dict(zip(rfm["Customer ID"], rfm["Segment"]))
    df["Segment"] = df["Customer ID"].map(customer_segments)
    df["Segment"] = df["Segment"].fillna("Unknown")

    segment_rev = (
        df.groupby(["Segment", "Category", "Month Label"])
        .agg(Revenue=("Sales", "sum"))
        .reset_index()
        .sort_values("Month Label")
    )

    fig = go.Figure()
    n_traces = len(categories)

    for seg in segments:
        for cat in categories:
            data = segment_rev[
                (segment_rev["Segment"] == seg) & (segment_rev["Category"] == cat)
            ]
            fig.add_trace(go.Bar(
                x=data["Month Label"], y=data["Revenue"],
                name=cat, marker_color=CAT_COLORS.get(cat, "#888"),
                visible=(seg == segments[0]),
                legendgroup=cat,
                showlegend=(seg == segments[0]),
                hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra>" + cat + "</extra>",
            ))

    buttons = []
    for i, seg in enumerate(segments):
        vis = []
        for j in range(len(segments)):
            vis.extend([j == i] * n_traces)
        buttons.append(dict(
            label=seg, method="update",
            args=[{"visible": vis}, {
                "title": f"Monthly Revenue by Category — {seg} Segment"
            }],
        ))

    fig.update_layout(
        updatemenus=[dict(
            buttons=buttons, direction="down", showactive=True,
            x=0.01, xanchor="left", y=1.18, yanchor="top",
            bgcolor="#F0F0F0", borderwidth=1,
        )],
        title=f"Monthly Revenue — {segments[0]} Segment",
        title_font_size=15, barmode="stack", height=480,
        yaxis_tickprefix="₹", yaxis_tickformat=",.0f",
        legend_title="Category",
        xaxis_tickangle=-45,
    )
    return fig
