# Setup Guide

## Prerequisites

- Python 3.12+
- pip (Python package manager)
- Git (optional)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd ecommerce-dashboard
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py migrate
```

### 5. Import sample data

```bash
python manage.py import_data
```

This loads 10,000 transactions into the database from `analytics/data/ecommerce.csv`.

### 6. Compute RFM segments (optional but recommended)

```bash
python manage.py compute_rfm
```

This calculates Recency, Frequency, and Monetary values per customer and assigns RFM segments.

### 7. Create an admin user (optional)

```bash
python manage.py createsuperuser
```

You'll be prompted for a username, email, and password. This gives you access to the Django admin interface at `/admin/`.

### 8. Start the development server

```bash
python manage.py runserver 0.0.0.0:8080
```

Open http://localhost:8080 in your browser.

## Quick Start (all steps)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py import_data
python manage.py compute_rfm
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8080
```

## Project Structure

```
ecommerce-dashboard/
├── analytics/                  # Django application
│   ├── analysis/               # Chart builders (Plotly)
│   ├── data/                   # Sample CSV data
│   ├── management/commands/    # Custom management commands
│   ├── migrations/             # Database migrations
│   ├── static/analytics/       # Static assets (Plotly.js)
│   ├── templates/analytics/    # HTML templates
│   ├── models.py               # Database models
│   ├── views.py                # View handlers
│   └── urls.py                 # App-level URL routes
├── dashboard_config/           # Django project configuration
│   ├── settings.py             # Settings
│   └── urls.py                 # Root URL configuration
├── docs/                       # Documentation
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── db.sqlite3                  # SQLite database
└── README.md                   # Project overview
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `No data found` error | Run `python manage.py import_data` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Port 8080 already in use | Use a different port: `python manage.py runserver 0.0.0.0:8081` |
| Charts not rendering | Check browser console for JavaScript errors. Plotly.js is served locally from `static/analytics/plotly.min.js`. |
| Blank page | Ensure Django static files are being served correctly. Use `python manage.py collectstatic --noinput` if using production settings. |
