# ERP System for Manufacturing & Distribution

A comprehensive Flask-based Enterprise Resource Planning (ERP) system designed for manufacturing and distribution companies. This system integrates modules for procurement, goods receiving, production, packaging, sales, and financial management.

## Features

### 1. Procurement Module
- Supplier management with ratings and payment terms
- Purchase requisitions
- Purchase orders with multi-item support
- Supplier price lists
- Purchase tracking and status management

### 2. Goods Receiving Module
- Goods Receiving Notes (GRN)
- Quality inspection workflow
- Warehouse allocation
- Return to supplier management

### 3. Production Module
- Bill of Materials (BOM) management
- Work order creation and tracking
- Production scheduling
- Material allocation tracking
- Work in progress monitoring

### 4. Packaging Module
- Packaging order management
- Packing specifications
- Label printing integration
- Dispatch planning

### 5. Sales Module
- Customer management
- Sales orders with pricing and discounts
- Shipping coordination
- Sales returns handling

### 6. Financial Module
- Chart of accounts
- Double-entry bookkeeping via journal entries
- Accounts payable and receivable
- Invoice management
- Payment processing
- Financial reports (Balance Sheet, Trial Balance)

### 7. Reporting Module
- Sales reports (by customer, by product)
- Procurement reports
- Production efficiency reports
- AR/AP aging reports
- Profit & Loss statement

## Technology Stack

- **Backend**: Flask 3.0 with Flask-RESTful
- **Database**: SQLAlchemy ORM with PostgreSQL
- **Authentication**: JWT (Flask-JWT-Extended)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Testing**: pytest with Flask-Testing
- **Deployment**: Docker & Docker Compose

## Project Structure

```
/home/deploy/squad/build-worker/JOB-20260415163007-b86751/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── models/               # SQLAlchemy models
│   │   ├── procurement.py
│   │   ├── goods_receiving.py
│   │   ├── production.py
│   │   ├── packaging.py
│   │   ├── sales.py
│   │   ├── financial.py
│   │   └── reporting.py
│   ├── routes/               # API routes
│   │   ├── procurement.py
│   │   ├── goods_receiving.py
│   │   ├── production.py
│   │   ├── packaging.py
│   │   ├── sales.py
│   │   ├── financial.py
│   │   └── reporting.py
│   └── services/             # Business logic
├── frontend/
│   ├── index.html
│   ├── css/styles.css
│   └── js/app.js
├── tests/                    # Unit tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (for containerized deployment)

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/9KMan/JOB-20260415163007-b86751.git
cd JOB-20260415163007-b86751
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Create the database:
```bash
createdb erp_db
# Or using psql:
# CREATE DATABASE erp_db;
# CREATE USER erp_user WITH PASSWORD 'erp_password';
# GRANT ALL PRIVILEGES ON DATABASE erp_db TO erp_user;
```

6. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

7. Run the application:
```bash
flask run
```

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

2. The API will be available at `http://localhost:5000`

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### Procurement
- `GET /procurement/suppliers` - List all suppliers
- `POST /procurement/suppliers` - Create supplier
- `GET /procurement/orders` - List purchase orders
- `POST /procurement/orders` - Create purchase order
- `GET /procurement/requisitions` - List requisitions
- `GET /procurement/price-lists` - List price lists

#### Goods Receiving
- `GET /goods-receiving/grn` - List GRN records
- `POST /goods-receiving/grn` - Create GRN
- `GET /goods-receiving/inspections` - List inspections
- `POST /goods-receiving/inspections` - Create inspection
- `GET /goods-receiving/allocations` - List allocations
- `POST /goods-receiving/allocations` - Create allocation
- `GET /goods-receiving/returns` - List returns

#### Production
- `GET /production/bom` - List BOMs
- `POST /production/bom` - Create BOM
- `GET /production/work-orders` - List work orders
- `POST /production/work-orders` - Create work order
- `POST /production/work-orders/{id}/start` - Start work order
- `POST /production/work-orders/{id}/complete` - Complete work order
- `GET /production/schedules` - List schedules

#### Packaging
- `GET /packaging/orders` - List packaging orders
- `POST /packaging/orders` - Create packaging order
- `GET /packaging/specifications` - List specifications
- `POST /packaging/specifications` - Create specification
- `GET /packaging/labels` - List labels
- `POST /packaging/labels` - Create label
- `GET /packaging/dispatch` - List dispatch plans

#### Sales
- `GET /sales/customers` - List customers
- `POST /sales/customers` - Create customer
- `GET /sales/orders` - List sales orders
- `POST /sales/orders` - Create sales order
- `POST /sales/orders/{id}/confirm` - Confirm order
- `GET /sales/shippings` - List shipments
- `GET /sales/returns` - List returns

#### Financial
- `GET /financial/accounts` - List accounts
- `POST /financial/accounts` - Create account
- `GET /financial/journal` - List journal entries
- `POST /financial/journal` - Create journal entry
- `POST /financial/journal/{id}/post` - Post entry
- `GET /financial/invoices` - List invoices
- `POST /financial/invoices` - Create invoice
- `GET /financial/payments` - List payments
- `POST /financial/payments` - Create payment
- `GET /financial/ledger` - List ledger entries

#### Reporting
- `GET /reporting/sales/summary` - Sales summary
- `GET /reporting/sales/by-customer` - Sales by customer
- `GET /reporting/sales/by-product` - Sales by product
- `GET /reporting/procurement/summary` - Procurement summary
- `GET /reporting/procurement/by-supplier` - By supplier
- `GET /reporting/production/summary` - Production summary
- `GET /reporting/production/efficiency` - Efficiency report
- `GET /reporting/financial/ar-aging` - AR aging
- `GET /reporting/financial/ap-aging` - AP aging
- `GET /reporting/financial/profit-loss` - P&L report

## Running Tests

```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## Frontend

The frontend provides a dashboard interface with:
- Module-based navigation
- Data tables with CRUD operations
- Modal forms for creating/editing records
- Report generation interface

Access the frontend at `http://localhost:5000/`

## Security

- JWT-based authentication
- Password hashing for sensitive data
- SQL injection protection via SQLAlchemy ORM
- CORS configuration for cross-origin requests

## License

MIT License

## Author

Freelancer.com Bid Submission - ERP System for Manufacturing/Distribution