# E-Commerce Sales Intelligence Dashboard

An interactive data analytics dashboard built with Django and Plotly that visualises 10,000 e-commerce transactions across 20 Indian states. Features cross-filtering by state, RFM customer segmentation, and six interactive chart types — all served without external CDN dependencies.

## Features

- **6 Interactive Charts**: State revenue lollipop, revenue hierarchy sunburst, animated monthly bar race, sub-category bubble chart, RFM segment scatter, and segment drill-down with dropdown
- **State Filter**: Click any state in the lollipop chart to filter KPIs, sunburst, trend, bubble, and drill-down charts to that state
- **RFM Segmentation**: Automatic customer segmentation (Champion, Loyal, At Risk, Lost, etc.) computed from transaction history
- **No External Dependencies**: Plotly.js served locally — no CDN requests at runtime
- **Responsive Layout**: Two-column grid adapts to different screen sizes

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 6 (Python) |
| Database | SQLite (Django ORM) |
| Data processing | Pandas, NumPy |
| Visualisation | Plotly.js (self-hosted) |
| Frontend | Vanilla JavaScript |

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py import_data
python manage.py runserver 0.0.0.0:8080
```

Open http://localhost:8080 in your browser.

### Django Admin

Access the admin interface at **http://localhost:8080/admin/** to manage orders, customers, and RFM segments.

```bash
# Create a superuser (admin) account
python manage.py createsuperuser

# Or reset an existing admin password
python manage.py changepassword admin
```

You'll be prompted for a username, email, and password. After logging in at `/admin/`, you can browse and edit `Customer`, `Order`, and `RfmSegment` records through Django's built-in admin UI.

## Documentation

- [Setup Guide](docs/setup.md) — detailed installation and configuration
- [Architecture](docs/architecture.md) — system design, data flow, and component details

## Project Structure

```
├── analytics/                  # Django application
│   ├── analysis/               # Plotly chart builders
│   ├── data/                   # Sample CSV data
│   ├── management/commands/    # import_data, compute_rfm
│   ├── static/analytics/       # Plotly.js library
│   ├── templates/analytics/    # Dashboard HTML template
│   ├── models.py               # Order, Customer, RfmSegment
│   └── views.py                # Dashboard and API views
├── dashboard_config/           # Django project settings
├── docs/                       # Documentation
├── db.sqlite3                  # SQLite database
├── manage.py
└── requirements.txt
```

## Charts

### Plotly Interactive Charts
| Chart | Description | Filterable |
|-------|-------------|------------|
| State Revenue | Horizontal lollipop chart — states ranked by revenue | Click to filter |
| Revenue Hierarchy | Sunburst — category → sub-category → region | — |
| Revenue Trend | Animated bar chart — month-by-month cumulative revenue | Yes |
| Product Performance | Bubble chart — sub-category revenue vs profit | Yes |
| RFM Segments | Scatter — customer recency vs frequency | — |
| Segment Drill-Down | Stacked bar with segment selector dropdown | Yes |

### Matplotlib & Seaborn Charts
| Chart | Description |
|-------|-------------|
| Category Distribution | Pie chart showing sales breakdown by category |
| State-wise Heatmap | Monthly sales heatmap across top 15 states |
| Profit by Sub-Category | Horizontal bar chart highlighting profitable vs unprofitable sub-categories |
| Sales by Region | Bar chart comparing total sales across regions |
| Discount Impact | Scatter plot showing correlation between discount and profit |
| RFM Segment Heatmap | Heatmap of average R, F, M scores by customer segment |
| Monthly Trend | Dual-axis line chart showing sales & profit trends over time |
| Product Performance Matrix | Bubble chart with orders count, revenue, and profit margins |
| Customer Segment Distribution | Bar chart showing customer count distribution across RFM segments |

## License

This project is licensed under the MIT License.
