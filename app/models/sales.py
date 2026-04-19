"""
Sales Module Models
"""
from datetime import datetime
from app import db


class Customer(db.Model):
    """Customer master data model."""
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(100))
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales_orders = db.relationship('SalesOrder', back_populates='customer', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'tax_id': self.tax_id,
            'payment_terms': self.payment_terms,
            'credit_limit': float(self.credit_limit) if self.credit_limit else 0,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SalesOrder(db.Model):
    """Sales order model."""
    __tablename__ = 'sales_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')  # draft, confirmed, in_production, shipped, delivered, cancelled
    payment_terms = db.Column(db.String(100))
    shipping_address = db.Column(db.Text)
    shipping_city = db.Column(db.String(100))
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    tax_percentage = db.Column(db.Numeric(5, 2), default=0)
    notes = db.Column(db.Text)
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = db.relationship('Customer', back_populates='sales_orders')
    items = db.relationship('SalesOrderItem', back_populates='sales_order', lazy='dynamic', cascade='all, delete-orphan')
    shipments = db.relationship('Shipping', back_populates='sales_order', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'status': self.status,
            'payment_terms': self.payment_terms,
            'shipping_address': self.shipping_address,
            'shipping_city': self.shipping_city,
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else 0,
            'tax_percentage': float(self.tax_percentage) if self.tax_percentage else 0,
            'notes': self.notes,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SalesOrderItem(db.Model):
    """Sales order line items."""
    __tablename__ = 'sales_order_items'

    id = db.Column(db.Integer, primary_key=True)
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 2), nullable=False)
    unit = db.Column(db.String(20))
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sales_order = db.relationship('SalesOrder', back_populates='items')

    @property
    def line_total(self):
        """Calculate line total."""
        base = self.quantity * self.unit_price
        discount = base * (self.discount_percentage / 100)
        taxable = base - discount
        tax = taxable * (self.tax_rate / 100)
        return taxable + tax

    def to_dict(self):
        return {
            'id': self.id,
            'sales_order_id': self.sales_order_id,
            'product_code': self.product_code,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit': self.unit,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else 0,
            'line_total': float(self.line_total) if self.line_total else 0
        }


class Shipping(db.Model):
    """Shipping records for sales orders."""
    __tablename__ = 'shippings'

    id = db.Column(db.Integer, primary_key=True)
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    shipment_number = db.Column(db.String(50), unique=True, nullable=False)
    shipment_date = db.Column(db.DateTime, default=datetime.utcnow)
    carrier = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100))
    shipped_by = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sales_order = db.relationship('SalesOrder', back_populates='shipments')

    def to_dict(self):
        return {
            'id': self.id,
            'sales_order_id': self.sales_order_id,
            'shipment_number': self.shipment_number,
            'shipment_date': self.shipment_date.isoformat() if self.shipment_date else None,
            'carrier': self.carrier,
            'tracking_number': self.tracking_number,
            'shipped_by': self.shipped_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SalesReturn(db.Model):
    """Sales returns model for customer returns."""
    __tablename__ = 'sales_returns'

    id = db.Column(db.Integer, primary_key=True)
    return_number = db.Column(db.String(50), unique=True, nullable=False)
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    return_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='draft')  # draft, received, inspected, approved, rejected, closed
    credit_amount = db.Column(db.Numeric(15, 2), default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales_order = db.relationship('SalesOrder')
    customer = db.relationship('Customer')
    items = db.relationship('SalesReturnItem', back_populates='return', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'return_number': self.return_number,
            'sales_order_id': self.sales_order_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'reason': self.reason,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status,
            'credit_amount': float(self.credit_amount) if self.credit_amount else 0,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SalesReturnItem(db.Model):
    """Sales return line items."""
    __tablename__ = 'sales_return_items'

    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('sales_returns.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 2), nullable=False)
    unit = db.Column(db.String(20))
    unit_price = db.Column(db.Numeric(15, 2))
    condition = db.Column(db.String(20))  # new, good, damaged
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    return = db.relationship('SalesReturn', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id,
            'return_id': self.return_id,
            'product_code': self.product_code,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit': self.unit,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'condition': self.condition,
            'notes': self.notes
        }