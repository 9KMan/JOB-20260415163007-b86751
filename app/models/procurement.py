"""
Procurement Module Models
"""
from datetime import datetime
from app import db


class Supplier(db.Model):
    """Supplier master data model."""
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(100))
    rating = db.Column(db.Integer, default=0)  # 1-5 rating
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    purchase_orders = db.relationship('PurchaseOrder', back_populates='supplier', lazy='dynamic')
    price_lists = db.relationship('PriceList', back_populates='supplier', lazy='dynamic')

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
            'country': self.country,
            'tax_id': self.tax_id,
            'payment_terms': self.payment_terms,
            'rating': self.rating,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PurchaseRequisition(db.Model):
    """Purchase requisition model for internal material requests."""
    __tablename__ = 'purchase_requisitions'

    id = db.Column(db.Integer, primary_key=True)
    requisition_number = db.Column(db.String(50), unique=True, nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    requested_date = db.Column(db.DateTime, default=datetime.utcnow)
    required_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')  # draft, approved, rejected, closed
    notes = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('PurchaseRequisitionItem', back_populates='requisition', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'requisition_number': self.requisition_number,
            'requester_name': self.requester_name,
            'department': self.department,
            'requested_date': self.requested_date.isoformat() if self.requested_date else None,
            'required_date': self.required_date.isoformat() if self.required_date else None,
            'status': self.status,
            'notes': self.notes,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PurchaseRequisitionItem(db.Model):
    """Items within a purchase requisition."""
    __tablename__ = 'purchase_requisition_items'

    id = db.Column(db.Integer, primary_key=True)
    requisition_id = db.Column(db.Integer, db.ForeignKey('purchase_requisitions.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 2), nullable=False)
    unit = db.Column(db.String(20))
    estimated_price = db.Column(db.Numeric(15, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requisition = db.relationship('PurchaseRequisition', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id,
            'requisition_id': self.requisition_id,
            'product_code': self.product_code,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit': self.unit,
            'estimated_price': float(self.estimated_price) if self.estimated_price else 0
        }


class PurchaseOrder(db.Model):
    """Purchase order model for supplier orders."""
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    requisition_id = db.Column(db.Integer, db.ForeignKey('purchase_requisitions.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected delivery_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')  # draft, approved, sent, partially_received, received, cancelled
    payment_terms = db.Column(db.String(100))
    shipping_terms = db.Column(db.String(100))
    notes = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplier = db.relationship('Supplier', back_populates='purchase_orders')
    items = db.relationship('PurchaseOrderItem', back_populates='purchase_order', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'requisition_id': self.requisition_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'status': self.status,
            'payment_terms': self.payment_terms,
            'shipping_terms': self.shipping_terms,
            'notes': self.notes,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PurchaseOrderItem(db.Model):
    """Items within a purchase order."""
    __tablename__ = 'purchase_order_items'

    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 2), nullable=False)
    unit = db.Column(db.String(20))
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    purchase_order = db.relationship('PurchaseOrder', back_populates='items')

    @property
    def line_total(self):
        """Calculate line total including tax."""
        base_total = self.quantity * self.unit_price
        tax = base_total * (self.tax_rate / 100)
        return base_total + tax

    def to_dict(self):
        return {
            'id': self.id,
            'purchase_order_id': self.purchase_order_id,
            'product_code': self.product_code,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit': self.unit,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'line_total': float(self.line_total) if self.line_total else 0
        }


class PriceList(db.Model):
    """Price list for supplier products."""
    __tablename__ = 'price_lists'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    min_quantity = db.Column(db.Numeric(15, 2), default=1)
    effective_from = db.Column(db.Date, nullable=False)
    effective_to = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', back_populates='price_lists')

    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'product_code': self.product_code,
            'description': self.description,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'currency': self.currency,
            'min_quantity': float(self.min_quantity) if self.min_quantity else 1,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }