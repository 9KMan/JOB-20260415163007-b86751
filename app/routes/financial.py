"""
Financial Module API Routes
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.financial import (
    ChartOfAccounts, JournalEntry, JournalEntryLine, Invoice, Payment, LedgerEntry
)

financial_bp = Blueprint('financial', __name__)


# Chart of Accounts Routes
@financial_bp.route('/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts."""
    accounts = ChartOfAccounts.query.filter_by(is_active=True).all()
    return jsonify({'accounts': [a.to_dict() for a in accounts]})


@financial_bp.route('/accounts/<int:account_id>', methods=['GET'])
def get_account(account_id):
    """Get a single account."""
    account = ChartOfAccounts.query.get_or_404(account_id)
    return jsonify({'account': account.to_dict()})


@financial_bp.route('/accounts', methods=['POST'])
def create_account():
    """Create a new account."""
    data = request.get_json()
    try:
        account = ChartOfAccounts(
            account_code=data.get('account_code'),
            account_name=data.get('account_name'),
            account_type=data.get('account_type'),
            account_subtype=data.get('account_subtype'),
            parent_id=data.get('parent_id'),
            description=data.get('description')
        )
        db.session.add(account)
        db.session.commit()
        return jsonify({'message': 'Account created successfully', 'account': account.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@financial_bp.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    """Update an account."""
    account = ChartOfAccounts.query.get_or_404(account_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(account, key):
                setattr(account, key, value)
        db.session.commit()
        return jsonify({'message': 'Account updated successfully', 'account': account.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Journal Entry Routes
@financial_bp.route('/journal', methods=['GET'])
def get_journal_entries():
    """Get all journal entries."""
    entries = JournalEntry.query.order_by(JournalEntry.entry_date.desc()).all()
    return jsonify({'entries': [e.to_dict() for e in entries]})


@financial_bp.route('/journal/<int:entry_id>', methods=['GET'])
def get_journal_entry(entry_id):
    """Get a single journal entry."""
    entry = JournalEntry.query.get_or_404(entry_id)
    return jsonify({'entry': entry.to_dict()})


@financial_bp.route('/journal', methods=['POST'])
def create_journal_entry():
    """Create a new journal entry."""
    data = request.get_json()
    try:
        entry = JournalEntry(
            entry_number=data.get('entry_number'),
            description=data.get('description'),
            reference=data.get('reference'),
            entry_type=data.get('entry_type', 'general'),
            status=data.get('status', 'draft')
        )
        db.session.add(entry)
        db.session.flush()

        # Add lines
        for line_data in data.get('lines', []):
            line = JournalEntryLine(
                journal_entry_id=entry.id,
                account_id=line_data.get('account_id'),
                debit=line_data.get('debit', 0),
                credit=line_data.get('credit', 0),
                description=line_data.get('description')
            )
            db.session.add(line)
        db.session.commit()
        return jsonify({'message': 'Journal entry created successfully', 'entry': entry.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@financial_bp.route('/journal/<int:entry_id>/post', methods=['POST'])
def post_journal_entry(entry_id):
    """Post a journal entry."""
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.status == 'posted':
        return jsonify({'error': 'Entry already posted'}), 400
    entry.status = 'posted'
    from datetime import datetime
    entry.posted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Journal entry posted successfully', 'entry': entry.to_dict()})


# Invoice Routes
@financial_bp.route('/invoices', methods=['GET'])
def get_invoices():
    """Get all invoices."""
    invoices = Invoice.query.order_by(Invoice.invoice_date.desc()).all()
    return jsonify({'invoices': [i.to_dict() for i in invoices]})


@financial_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """Get a single invoice."""
    invoice = Invoice.query.get_or_404(invoice_id)
    return jsonify({'invoice': invoice.to_dict()})


@financial_bp.route('/invoices', methods=['POST'])
def create_invoice():
    """Create a new invoice."""
    data = request.get_json()
    try:
        invoice = Invoice(
            invoice_number=data.get('invoice_number'),
            invoice_type=data.get('invoice_type'),
            customer_id=data.get('customer_id'),
            supplier_id=data.get('supplier_id'),
            sales_order_id=data.get('sales_order_id'),
            purchase_order_id=data.get('purchase_order_id'),
            due_date=data.get('due_date'),
            status=data.get('status', 'draft'),
            subtotal=data.get('subtotal', 0),
            tax_amount=data.get('tax_amount', 0),
            discount_amount=data.get('discount_amount', 0),
            total_amount=data.get('total_amount', 0),
            notes=data.get('notes')
        )
        db.session.add(invoice)
        db.session.commit()
        return jsonify({'message': 'Invoice created successfully', 'invoice': invoice.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@financial_bp.route('/invoices/<int:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    """Update an invoice."""
    invoice = Invoice.query.get_or_404(invoice_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(invoice, key):
                setattr(invoice, key, value)
        db.session.commit()
        return jsonify({'message': 'Invoice updated successfully', 'invoice': invoice.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Payment Routes
@financial_bp.route('/payments', methods=['GET'])
def get_payments():
    """Get all payments."""
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return jsonify({'payments': [p.to_dict() for p in payments]})


@financial_bp.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """Get a single payment."""
    payment = Payment.query.get_or_404(payment_id)
    return jsonify({'payment': payment.to_dict()})


@financial_bp.route('/payments', methods=['POST'])
def create_payment():
    """Create a new payment."""
    data = request.get_json()
    try:
        payment = Payment(
            payment_number=data.get('payment_number'),
            payment_type=data.get('payment_type'),
            invoice_id=data.get('invoice_id'),
            customer_id=data.get('customer_id'),
            supplier_id=data.get('supplier_id'),
            payment_method=data.get('payment_method'),
            reference_number=data.get('reference_number'),
            amount=data.get('amount'),
            currency=data.get('currency', 'USD'),
            notes=data.get('notes')
        )
        db.session.add(payment)

        # Update invoice paid amount if linked
        if data.get('invoice_id'):
            invoice = Invoice.query.get(data.get('invoice_id'))
            if invoice:
                invoice.paid_amount = invoice.paid_amount + payment.amount
        db.session.commit()
        return jsonify({'message': 'Payment created successfully', 'payment': payment.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Ledger Routes
@financial_bp.route('/ledger', methods=['GET'])
def get_ledger_entries():
    """Get ledger entries with optional filtering."""
    query = LedgerEntry.query
    if request.args.get('account_id'):
        query = query.filter_by(account_id=request.args.get('account_id'))
    entries = query.order_by(LedgerEntry.entry_date.desc()).limit(100).all()
    return jsonify({'entries': [e.to_dict() for e in entries]})


@financial_bp.route('/ledger/account/<int:account_id>', methods=['GET'])
def get_account_ledger(account_id):
    """Get ledger entries for a specific account."""
    entries = LedgerEntry.query.filter_by(account_id=account_id).order_by(LedgerEntry.entry_date.asc()).all()
    return jsonify({'entries': [e.to_dict() for e in entries]})


# Financial Reports Routes
@financial_bp.route('/reports/balance-sheet', methods=['GET'])
def get_balance_sheet():
    """Generate balance sheet report data."""
    # Get asset, liability, equity accounts and their balances
    accounts = ChartOfAccounts.query.filter_by(is_active=True).all()
    report_data = {'assets': [], 'liabilities': [], 'equity': []}
    for account in accounts:
        balance = db.session.query(db.func.sum(LedgerEntry.debit) - db.func.sum(LedgerEntry.credit)).filter_by(account_id=account.id).scalar() or 0
        data = {'code': account.account_code, 'name': account.account_name, 'balance': float(balance)}
        if account.account_type == 'asset':
            report_data['assets'].append(data)
        elif account.account_type == 'liability':
            report_data['liabilities'].append(data)
        elif account.account_type == 'equity':
            report_data['equity'].append(data)
    return jsonify({'report': report_data})


@financial_bp.route('/reports/trial-balance', methods=['GET'])
def get_trial_balance():
    """Generate trial balance report data."""
    accounts = ChartOfAccounts.query.filter_by(is_active=True).all()
    report_data = []
    total_debit = 0
    total_credit = 0
    for account in accounts:
        debits = db.session.query(db.func.sum(LedgerEntry.debit)).filter_by(account_id=account.id).scalar() or 0
        credits = db.session.query(db.func.sum(LedgerEntry.credit)).filter_by(account_id=account.id).scalar() or 0
        balance = float(debits) - float(credits)
        report_data.append({
            'account_code': account.account_code,
            'account_name': account.account_name,
            'account_type': account.account_type,
            'debit': float(debits),
            'credit': float(credits),
            'balance': balance
        })
        if account.account_type in ('asset', 'expense'):
            total_debit += balance
        else:
            total_credit += balance
    return jsonify({'report': report_data, 'total_debit': total_debit, 'total_credit': total_credit})