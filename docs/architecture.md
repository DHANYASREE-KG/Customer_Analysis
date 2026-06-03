# Architecture

## Overview

A single-page Django dashboard that visualises e-commerce sales data using interactive Plotly charts. The backend aggregates data from an SQLite database; the frontend renders 6 Plotly charts with cross-filtering by state.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.x (Python) |
| Database | SQLite via Django ORM |
| Data processing | Pandas, NumPy |
| Charting | Plotly.js (self-hosted, no CDN) |
| Frontend | Vanilla JavaScript, Plotly |
| Template | Django template engine |

## Data Flow

```
                     ┌──────────────────┐
                     │  ecommerce.csv    │
                     │  (raw data file)  │
                     └────────┬─────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  import_data     │
                    │  management cmd  │◄─── python manage.py import_data
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    SQLite DB     │
                    │   (db.sqlite3)   │
                    │                  │
                    │  ┌─ Order        │
                    │  ├─ Customer     │
                    │  └─ RfmSegment   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────────┐ ┌─────────┐ ┌──────────────┐
    │  dashboard_view │ │ state_  │ │ admin views  │
    │  (GET /)        │ │ dashboard│ │ (GET /admin/)│
    └────────┬────────┘ │ (AJAX)  │ └──────────────┘
             │          └────┬─────┘
             ▼               │
    ┌─────────────────┐      │
    │ _prepare_data() │      │
    │ returns df, rfm │      │
    └────────┬────────┘      │
             │               │
             ▼               ▼
    ┌─────────────────────────────────────┐
    │        Chart Builders              │
    │  (analytics/analysis/)             │
    │                                    │
    │  build_state_bar      → Lollipop   │
    │  build_sunburst       → Sunburst   │
    │  build_animated_bar   → Animated   │
    │  build_bubble_chart   → Bubble     │
    │  build_rfm_scatter    → RFM Scatter│
    │  build_dropdown_bar   → Dropdown   │
    └──────────────┬──────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────┐
    │       Django Template              │
    │  analytics/templates/analytics/    │
    │        dashboard.html              │
    │                                    │
    │  ┌──────────────────────────────┐  │
    │  │ Plotly.js renders 6 charts  │  │
    │  │ on page load                │  │
    │  └──────────────────────────────┘  │
    │                                    │
    │  State filter: clicks trigger      │
    │  AJAX call → replace 4 cards       │
    └────────────────────────────────────┘
```

## Request Lifecycle

### Full Page Load (`GET /`)

1. Browser requests `/`
2. `dashboard_config.urls` routes to `analytics.urls`
3. `dashboard_view` in `views.py` calls `_prepare_data()` with no filter
4. `_prepare_data()` queries all `Order` + `Customer` + `RfmSegment` records, returns two Pandas DataFrames (`df`, `rfm`)
5. Six chart builder functions transform the DataFrames into Plotly `go.Figure` objects
6. Each figure is serialised with `.to_html(full_html=False, include_plotlyjs=False)` — this generates a `<div>` + inline `<script>` tag
7. Template renders all charts inside `<div class="card">` containers
8. On page load, Plotly.js renders each chart from its inline data

### State Filter (`GET /state/<state_name>/`)

1. User clicks a bar in the lollipop chart (or a sunburst segment)
2. JavaScript `plotly_click` event fires `filterByState(stateName)`
3. `filterByState()` shows a loading state on 4 chart cards, then calls `GET /state/Maharashtra/` (example)
4. `state_dashboard_view` calls `_prepare_data(state_name="Maharashtra")`, which filters the ORM query with `.filter(state=state_name)`
5. Returns JSON with 4 chart HTML strings + updated KPI values
6. Client-side `setHTML()` replaces each card's inner HTML with the new chart scripts
7. Lollipop chart and RFM chart remain unchanged during filtering

## Chart Details

| Chart | Builder | Type | Filtered? |
|-------|---------|------|-----------|
| State Revenue | `build_state_bar` | Lollipop (scatter + lines) | No — always shows all states |
| Revenue Hierarchy | `build_sunburst` | Sunburst (category → sub-category → region) | Yes |
| Revenue Trend | `build_animated_bar` | Animated bar race (month-by-month) | Yes |
| Sub-Category Perf. | `build_bubble_chart` | Scatter bubble (revenue vs profit, size = orders) | Yes |
| RFM Segments | `build_rfm_scatter` | Scatter (recency vs frequency, size = monetary) | No |
| Segment Drill-Down | `build_dropdown_bar` | Stacked bar with segment dropdown | Yes |

## Database Models

```python
class Customer(models.Model):
    customer_id = CharField(primary_key, max_length=20)
    customer_name = CharField(max_length=100)
    segment = CharField(max_length=50)
    country = CharField(max_length=50)
    city = CharField(max_length=100)
    state = CharField(max_length=50)
    region = CharField(max_length=50)
    postal_code = CharField(max_length=20)

class Order(models.Model):
    order_id = CharField(primary_key, max_length=50)
    order_date = DateField()
    ship_date = DateField()
    ship_mode = CharField(max_length=50)
    customer = ForeignKey(Customer)
    category = CharField(max_length=50)
    sub_category = CharField(max_length=50)
    product_name = CharField(max_length=255)
    sales = FloatField()
    profit = FloatField()
    discount = FloatField()
    quantity = IntegerField()
    state = CharField(max_length=50)
    region = CharField(max_length=50)

class RfmSegment(models.Model):
    customer = OneToOneField(Customer, primary_key)
    recency = IntegerField()
    frequency = IntegerField()
    monetary = FloatField()
    r_score = IntegerField()
    f_score = IntegerField()
    m_score = IntegerField()
    rfm_score = IntegerField()
    segment = CharField(max_length=50)
```

## URL Routing

| URL | View | Method | Purpose |
|-----|------|--------|---------|
| `/` | `dashboard_view` | GET | Main dashboard page |
| `/state/<str:name>/` | `state_dashboard_view` | GET (AJAX) | Filtered chart data |
| `/admin/` | Django admin | GET/POST | Data management |

## Static Files

- **Plotly.js**: `analytics/static/analytics/plotly.min.js` — self-hosted Plotly library (no external CDN dependency)
- The library is loaded via `{% static 'analytics/plotly.min.js' %}` in the template `<head>`

## JavaScript Behaviour

The client-side JavaScript in `dashboard.html` handles:

1. **Chart initialisation**: Plotly renders all 6 charts from inline JSON data
2. **Lollipop click handler**: Attaches `plotly_click` event → calls `filterByState()`
3. **filterByState(state)**: Sets filter badge, loads 4 chart cards via AJAX, updates KPIs
4. **resetFilter()**: Reloads the page to clear all filters
5. **setHTML(container, html)**: Safely replaces chart card content including re-executing inline `<script>` tags
