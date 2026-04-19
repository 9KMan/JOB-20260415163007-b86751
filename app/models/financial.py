"""
Financial Module Models
"""
from datetime import datetime
from app import db


class ChartOfAccounts(db.Model):
    """Chart of accounts model."""
    __tablename__ = 'chart_of_accounts'

    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(50), unique=True, nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # asset, liability, equity, revenue, expense
    account_subtype = db.Column(db.String(50))  # bank, cash, receivable, payable, etc.
    parent_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'))
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = db.relationship('ChartOfAccounts', remote_side=[id], backref='subaccounts')
    entries = db.relationship('LedgerEntry', back_populates='account', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'account_code': self.account_code,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'account_subtype': self.account_subtype,
            'parent_id': self.parent_id,
            'is_active': self.is_active,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class JournalEntry(db.Model):
    """Journal entry model for financial transactions."""
    __tablename__ = 'journal_entries'

    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(50), unique=True, nullable=False)
    entry_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))
    reference = db.Column(db.String(100))
    entry_type = db.Column(db.String(50))  # general, invoice, payment, receipt, adjustment
    status = db.Column(db.String(20), default='draft')  # draft, posted, reversed
    posted_by = db.Column(db.String(100))
    posted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lines = db.relationship('JournalEntryLine', back_populates='entry', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'entry_number': self.entry_number,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'description': self.description,
            'reference': self.reference,
            'entry_type': self.entry_type,
            'status': self.status,
            'posted_by': self.posted_by,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class JournalEntryLine(db.Model):
    """Journal entry line items."""
    __tablename__ = 'journal_entry_lines'

    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'), nullable=False)
    debit = db.Column(db.Numeric(15, 2), default=0)
    credit = db.Column(db.Numeric(15, 2), default=0)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entry = db.relationship('JournalEntry', back_populates='lines')
    account = db.relationship('ChartOfAccounts', back_populates='entries')

    def to_dict(self):
        return {
            'id': self.id,
            'journal_entry_id': self.journal_entry_id,
            'account_id': self.account_id,
            'account_name': self.account.account_name if self.account else None,
            'debit': float(self.debit) if self.debit else 0,
            'credit': float(self.credit) if self.credit else 0,
            'description': self.description
        }


class Invoice(db.Model):
    """Invoice model for accounts receivable and payable."""
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_type = db.Column(db.String(20), nullable=False)  # sales, purchase
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'))
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'))
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, overdue, cancelled
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    paid_amount = db.Column(db.Numeric(15, 2), default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = db.relationship('Customer', foreign_keys=[customer_id])
    supplier = db.relationship('Supplier', foreign_keys=[supplier_id])
    sales_order = db.relationship('SalesOrder', foreign_keys=[sales_order_id])
    purchase_order = db.relationship('PurchaseOrder', foreign_keys=[purchase_order_id])
    payments = db.relationship('Payment', back_populates='invoice', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'invoice_type': self.invoice_type,
            'customer_id': self.customer_id,
            'supplier_id': self.supplier_id,
            'sales_order_id': self.sales_order_id,
            'purchase_order_id': self.purchase_order_id,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0,
            'balance_due': float(self.total_amount - self.paid_amount) if self.total_amount else 0,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Payment(db.Model):
    """Payment model for transactions."""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), unique=True, nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # received, made
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))  # cash, check, bank_transfer, credit_card
    reference_number = db.Column(db.String(100))
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed, reversed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    invoice = db.relationship('Invoice', back_populates='payments')
    customer = db.relationship('Customer', foreign_keys=[customer_id])
    supplier = db.relationship('Supplier', foreign_keys=[supplier_id])

    def to_dict(self):
        return {
            'id': self.id,
            'payment_number': self.payment_number,
            'payment_type': self.payment_type,
            'invoice_id': self.invoice_id,
            'customer_id': self.customer_id,
            'supplier_id': self.supplier_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'amount': float(self.amount) if self.amount else 0,
            'currency': self.currency,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class LedgerEntry(db.Model):
    """General ledger entry model."""
    __tablename__ = 'ledger_entries'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'), nullable=False)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'))
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))
    entry_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))
    reference = db.Column(db.String(100))
    debit = db.Column(db.Numeric(15, 2), default=0)
    credit = db.Column(db.Numeric(15, 2), default=0)
    balance = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    account = db.relationship('ChartOfAccounts', back_populates='entries')

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'account_name': self.account.account_name if self.account else None,
            'journal_entry_id': self.journal_entry_id,
            'invoice_id': self.invoice_id,
            'payment_id': self.payment_id,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'description': self.description,
            'reference': self.reference,
            'debit': float(self.debit) if self.debit else 0,
            'credit': float(self.credit) if self.credit else 0,
            'balance': float(self.balance) if self.balance else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }