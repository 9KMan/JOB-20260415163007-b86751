"""
Reporting Module API Routes
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.reporting import ReportConfiguration
from app.models.sales import SalesOrder, Customer
from app.models.procurement import PurchaseOrder, Supplier
from app.models.production import WorkOrder
from app.models.financial import Invoice, LedgerEntry, ChartOfAccounts
from sqlalchemy import func

reporting_bp = Blueprint('reporting', __name__)


@reporting_bp.route('/configurations', methods=['GET'])
def get_report_configs():
    """Get all report configurations."""
    configs = ReportConfiguration.query.filter_by(is_active=True).all()
    return jsonify({'configurations': [c.to_dict() for c in configs]})


@reporting_bp.route('/configurations/<int:config_id>', methods=['GET'])
def get_report_config(config_id):
    """Get a single report configuration."""
    config = ReportConfiguration.query.get_or_404(config_id)
    return jsonify({'configuration': config.to_dict()})


@reporting_bp.route('/configurations', methods=['POST'])
def create_report_config():
    """Create a new report configuration."""
    data = request.get_json()
    try:
        config = ReportConfiguration(
            report_code=data.get('report_code'),
            report_name=data.get('report_name'),
            report_type=data.get('report_type'),
            description=data.get('description'),
            query_definition=data.get('query_definition'),
            parameters=data.get('parameters'),
            column_definitions=data.get('column_definitions'),
            grouping=data.get('grouping'),
            sorting=data.get('sorting'),
            created_by=data.get('created_by')
        )
        db.session.add(config)
        db.session.commit()
        return jsonify({'message': 'Report configuration created successfully', 'configuration': config.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Sales Reports
@reporting_bp.route('/sales/summary', methods=['GET'])
def get_sales_summary():
    """Get sales summary report."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    query = db.session.query(
        SalesOrder.order_number,
        Customer.name.label('customer_name'),
        SalesOrder.order_date,
        SalesOrder.total_amount,
        SalesOrder.status
    ).join(Customer, SalesOrder.customer_id == Customer.id)

    if start_date:
        query = query.filter(SalesOrder.order_date >= start_date)
    if end_date:
        query = query.filter(SalesOrder.order_date <= end_date)

    orders = query.all()
    return jsonify({
        'orders': [{
            'order_number': o.order_number,
            'customer_name': o.customer_name,
            'order_date': o.order_date.isoformat() if o.order_date else None,
            'total_amount': float(o.total_amount) if o.total_amount else 0,
            'status': o.status
        } for o in orders]
    })


@reporting_bp.route('/sales/by-customer', methods=['GET'])
def get_sales_by_customer():
    """Get sales grouped by customer."""
    results = db.session.query(
        Customer.id,
        Customer.code,
        Customer.name,
        func.count(SalesOrder.id).label('order_count'),
        func.coalesce(func.sum(SalesOrder.total_amount), 0).label('total_sales')
    ).outerjoin(SalesOrder, Customer.id == SalesOrder.customer_id).group_by(Customer.id).all()

    return jsonify({
        'customers': [{
            'id': r.id,
            'code': r.code,
            'name': r.name,
            'order_count': r.order_count,
            'total_sales': float(r.total_sales)
        } for r in results]
    })


@reporting_bp.route('/sales/by-product', methods=['GET'])
def get_sales_by_product():
    """Get sales grouped by product."""
    from app.models.sales import SalesOrderItem
    results = db.session.query(
        SalesOrderItem.product_code,
        func.sum(SalesOrderItem.quantity).label('total_quantity'),
        func.sum(SalesOrderItem.quantity * SalesOrderItem.unit_price).label('total_revenue')
    ).join(SalesOrder).filter(SalesOrder.status != 'cancelled').group_by(SalesOrderItem.product_code).all()

    return jsonify({
        'products': [{
            'product_code': r.product_code,
            'total_quantity': float(r.total_quantity) if r.total_quantity else 0,
            'total_revenue': float(r.total_revenue) if r.total_revenue else 0
        } for r in results]
    })


# Procurement Reports
@reporting_bp.route('/procurement/summary', methods=['GET'])
def get_procurement_summary():
    """Get procurement summary report."""
    results = db.session.query(
        PurchaseOrder.order_number,
        Supplier.name.label('supplier_name'),
        PurchaseOrder.order_date,
        PurchaseOrder.total_amount,
        PurchaseOrder.status
    ).join(Supplier, PurchaseOrder.supplier_id == Supplier.id).all()

    return jsonify({
        'orders': [{
            'order_number': o.order_number,
            'supplier_name': o.supplier_name,
            'order_date': o.order_date.isoformat() if o.order_date else None,
            'total_amount': float(o.total_amount) if o.total_amount else 0,
            'status': o.status
        } for o in results]
    })


@reporting_bp.route('/procurement/by-supplier', methods=['GET'])
def get_procurement_by_supplier():
    """Get procurement grouped by supplier."""
    results = db.session.query(
        Supplier.id,
        Supplier.code,
        Supplier.name,
        func.count(PurchaseOrder.id).label('order_count'),
        func.coalesce(func.sum(PurchaseOrder.total_amount), 0).label('total_purchases')
    ).outerjoin(PurchaseOrder, Supplier.id == PurchaseOrder.supplier_id).group_by(Supplier.id).all()

    return jsonify({
        'suppliers': [{
            'id': r.id,
            'code': r.code,
            'name': r.name,
            'order_count': r.order_count,
            'total_purchases': float(r.total_purchases)
        } for r in results]
    })


# Production Reports
@reporting_bp.route('/production/summary', methods=['GET'])
def get_production_summary():
    """Get production summary report."""
    orders = WorkOrder.query.all()
    return jsonify({
        'work_orders': [{
            'work_order_number': o.work_order_number,
            'product_code': o.product_code,
            'quantity': float(o.quantity) if o.quantity else 0,
            'status': o.status,
            'planned_start_date': o.planned_start_date.isoformat() if o.planned_start_date else None,
            'planned_end_date': o.planned_end_date.isoformat() if o.planned_end_date else None
        } for o in orders]
    })


@reporting_bp.route('/production/efficiency', methods=['GET'])
def get_production_efficiency():
    """Get production efficiency report."""
    completed = WorkOrder.query.filter_by(status='completed').count()
    total = WorkOrder.query.count()
    efficiency = (completed / total * 100) if total > 0 else 0
    return jsonify({
        'total_work_orders': total,
        'completed': completed,
        'in_progress': WorkOrder.query.filter_by(status='in_progress').count(),
        'planned': WorkOrder.query.filter_by(status='planned').count(),
        'efficiency_rate': round(efficiency, 2)
    })


# Inventory Reports
@reporting_bp.route('/inventory/value', methods=['GET'])
def get_inventory_value():
    """Get inventory value report."""
    # This is a simplified placeholder - in real ERP would have inventory tables
    return jsonify({
        'message': 'Inventory value report - requires inventory module integration',
        'note': 'This report would calculate inventory value from inventory master data'
    })


# Financial Reports
@reporting_bp.route('/financial/ar-aging', methods=['GET'])
def get_ar_aging():
    """Get accounts receivable aging report."""
    invoices = Invoice.query.filter_by(invoice_type='sales', status='sent').all()
    aging_data = {'current': 0, '30_days': 0, '60_days': 0, '90_days': 0, 'over_90': 0}
    from datetime import datetime, timedelta

    for inv in invoices:
        balance = float(inv.total_amount - inv.paid_amount)
        if balance <= 0:
            continue
        age_days = (datetime.utcnow().date() - inv.due_date).days if inv.due_date else 0
        if age_days <= 0:
            aging_data['current'] += balance
        elif age_days <= 30:
            aging_data['30_days'] += balance
        elif age_days <= 60:
            aging_data['60_days'] += balance
        elif age_days <= 90:
            aging_data['90_days'] += balance
        else:
            aging_data['over_90'] += balance
    return jsonify({'ar_aging': aging_data})


@reporting_bp.route('/financial/ap-aging', methods=['GET'])
def get_ap_aging():
    """Get accounts payable aging report."""
    invoices = Invoice.query.filter_by(invoice_type='purchase', status='sent').all()
    aging_data = {'current': 0, '30_days': 0, '60_days': 0, '90_days': 0, 'over_90': 0}
    from datetime import datetime

    for inv in invoices:
        balance = float(inv.total_amount - inv.paid_amount)
        if balance <= 0:
            continue
        age_days = (datetime.utcnow().date() - inv.due_date).days if inv.due_date else 0
        if age_days <= 0:
            aging_data['current'] += balance
        elif age_days <= 30:
            aging_data['30_days'] += balance
        elif age_days <= 60:
            aging_data['60_days'] += balance
        elif age_days <= 90:
            aging_data['90_days'] += balance
        else:
            aging_data['over_90'] += balance
    return jsonify({'ap_aging': aging_data})


@reporting_bp.route('/financial/profit-loss', methods=['GET'])
def get_profit_loss():
    """Get profit and loss report."""
    # Calculate revenue from sales invoices
    revenue = db.session.query(func.coalesce(func.sum(Invoice.total_amount), 0)).filter(
        Invoice.invoice_type == 'sales',
        Invoice.status.in_(['sent', 'paid'])
    ).scalar() or 0

    # Calculate expenses from purchase invoices and ledger entries
    expenses = db.session.query(func.coalesce(func.sum(Invoice.total_amount), 0)).filter(
        Invoice.invoice_type == 'purchase',
        Invoice.status.in_(['sent', 'paid'])
    ).scalar() or 0

    return jsonify({
        'revenue': float(revenue),
        'expenses': float(expenses),
        'net_profit': float(revenue) - float(expenses)
    })