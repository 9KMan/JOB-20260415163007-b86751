# ERP System for Manufacturing & Distribution

A comprehensive Flask-based Enterprise Resource Planning (ERP) system designed for manufacturing and distribution companies.

## Tech Stack

- **Backend:** Flask 3.0 + Flask-RESTful
- **Database:** SQLAlchemy + PostgreSQL
- **Auth:** JWT (Flask-JWT-Extended)
- **Frontend:** Vanilla HTML/CSS/JS
- **Testing:** pytest
- **Deployment:** Docker

## Quick Start

```bash
# Backend
pip install -r requirements.txt
flask run

# Docker
docker-compose up --build
```

## Modules

| Module | Description |
|--------|-------------|
| Procurement | Supplier management, POs, price lists |
| Goods Receiving | GRN workflow, quality inspection |
| Production | BOM, work orders, scheduling |
| Packaging | Packaging orders, label integration |
| Sales | Customer orders, shipping, returns |
| Financial | Double-entry bookkeeping, AP/AR, invoicing |
| Reporting | Sales, procurement, AR/AP aging, P&L |

## Structure

```
app/
  models/      # SQLAlchemy models
  routes/      # API endpoints per module
  services/    # Business logic
  config.py    # Flask configuration
tests/         # pytest test suite
Dockerfile
docker-compose.yml
```
