# ERP System — Technical Specification

## Overview

Flask-based ERP for manufacturing & distribution covering 7 core modules.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask 3.0, Flask-RESTful, SQLAlchemy |
| Database | PostgreSQL |
| Auth | JWT (Flask-JWT-Extended) |
| Frontend | Vanilla HTML/CSS/JS |
| Testing | pytest |
| Deploy | Docker + docker-compose |

## Module Specifications

### 1. Procurement Module
- **Models:** Supplier, PurchaseRequisition, PurchaseOrder, SupplierPriceList
- **API Routes:** `/api/procurement/*`
- **Features:** Supplier CRUD, PR creation, PO with multi-item, price list management

### 2. Goods Receiving Module
- **Models:** GoodsReceivingNote, QualityInspection, WarehouseAllocation
- **API Routes:** `/api/goods-receiving/*`
- **Features:** GRN creation, QC workflow, warehouse allocation, returns

### 3. Production Module
- **Models:** BillOfMaterials, WorkOrder, ProductionSchedule
- **API Routes:** `/api/production/*`
- **Features:** BOM management, work orders, scheduling, WIP tracking

### 4. Packaging Module
- **Models:** PackagingOrder, PackingSpecification, Label
- **API Routes:** `/api/packaging/*`
- **Features:** Packaging orders, spec management, label integration

### 5. Sales Module
- **Models:** Customer, SalesOrder, ShippingRecord, SalesReturn
- **API Routes:** `/api/sales/*`
- **Features:** Customer management, order lifecycle, shipping, returns

### 6. Financial Module
- **Models:** ChartOfAccounts, JournalEntry, AccountPayable, AccountReceivable, Invoice
- **API Routes:** `/api/financial/*`
- **Features:** Double-entry bookkeeping, AP/AR management, invoicing

### 7. Reporting Module
- **Models:** ReportConfig
- **API Routes:** `/api/reporting/*`
- **Reports:** Sales by customer/product, procurement, production efficiency, AR/AP aging, P&L, Balance Sheet

## API Structure

```
/api/
  procurement/
    suppliers/
    purchase-requisitions/
    purchase-orders/
    price-lists/
  goods-receiving/
    grn/
    quality-inspection/
    warehouse-allocations/
  production/
    bom/
    work-orders/
    schedules/
  packaging/
    orders/
    specifications/
  sales/
    customers/
    orders/
    shipping/
    returns/
  financial/
    accounts/
    journal/
    ap/
    ar/
    invoices/
  reporting/
    sales/
    procurement/
    production/
    aging/
    financial/
```

## Authentication

JWT Bearer token required for all `/api/*` routes except `/api/auth/*`.

## Database

PostgreSQL with SQLAlchemy ORM. Connection via `DATABASE_URL` env var.
