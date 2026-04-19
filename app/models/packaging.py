"""
Packaging Module Models
"""
from datetime import datetime
from app import db


class PackagingOrder(db.Model):
    """Packaging order model for packaging operations."""
    __tablename__ = 'packaging_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'))
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    quantity_to_pack = db.Column(db.Numeric(15, 2), nullable=False)
    unit = db.Column(db.String(20))
    packaging_type = db.Column(db.String(50))  # individual, case, pallet
    priority = db.Column(db.Integer, default=5)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, shipped
    scheduled_date = db.Column(db.Date)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    specifications = db.relationship('PackingSpecification', back_populates='packaging_order', lazy='dynamic', cascade='all, delete-orphan')
    labels = db.relationship('PackageLabel', back_populates='packaging_order', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'sales_order_id': self.sales_order_id,
            'work_order_id': self.work_order_id,
            'product_code': self.product_code,
            'description': self.description,
            'quantity_to_pack': float(self.quantity_to_pack) if self.quantity_to_pack else 0,
            'unit': self.unit,
            'packaging_type': self.packaging_type,
            'priority': self.priority,
            'status': self.status,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PackingSpecification(db.Model):
    """Packing specifications for products."""
    __tablename__ = 'packing_specifications'

    id = db.Column(db.Integer, primary_key=True)
    packaging_order_id = db.Column(db.Integer, db.ForeignKey('packaging_orders.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    specification_type = db.Column(db.String(50))  # label, box, pallet
    specification_code = db.Column(db.String(50))
    description = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 2), default=1)
    dimensions_length = db.Column(db.Numeric(10, 2))
    dimensions_width = db.Column(db.Numeric(10, 2))
    dimensions_height = db.Column(db.Numeric(10, 2))
    weight = db.Column(db.Numeric(10, 2))
    barcode = db.Column(db.String(100))
    qr_code = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    packaging_order = db.relationship('PackagingOrder', back_populates='specifications')

    def to_dict(self):
        return {
            'id': self.id,
            'packaging_order_id': self.packaging_order_id,
            'product_code': self.product_code,
            'specification_type': self.specification_type,
            'specification_code': self.specification_code,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else 1,
            'dimensions_length': float(self.dimensions_length) if self.dimensions_length else 0,
            'dimensions_width': float(self.dimensions_width) if self.dimensions_width else 0,
            'dimensions_height': float(self.dimensions_height) if self.dimensions_height else 0,
            'weight': float(self.weight) if self.weight else 0,
            'barcode': self.barcode,
            'qr_code': self.qr_code,
            'notes': self.notes
        }


class PackageLabel(db.Model):
    """Package labels for tracking."""
    __tablename__ = 'package_labels'

    id = db.Column(db.Integer, primary_key=True)
    packaging_order_id = db.Column(db.Integer, db.ForeignKey('packaging_orders.id'), nullable=False)
    label_number = db.Column(db.String(50), unique=True, nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(100))
    batch_number = db.Column(db.String(50))
    quantity = db.Column(db.Numeric(15, 2), default=1)
    printed = db.Column(db.Boolean, default=False)
    printed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    packaging_order = db.relationship('PackagingOrder', back_populates='labels')

    def to_dict(self):
        return {
            'id': self.id,
            'packaging_order_id': self.packaging_order_id,
            'label_number': self.label_number,
            'product_code': self.product_code,
            'serial_number': self.serial_number,
            'batch_number': self.batch_number,
            'quantity': float(self.quantity) if self.quantity else 1,
            'printed': self.printed,
            'printed_at': self.printed_at.isoformat() if self.printed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DispatchPlan(db.Model):
    """Dispatch plan model for shipping coordination."""
    __tablename__ = 'dispatch_plans'

    id = db.Column(db.Integer, primary_key=True)
    plan_number = db.Column(db.String(50), unique=True, nullable=False)
    shipment_date = db.Column(db.Date, nullable=False)
    carrier = db.Column(db.String(100))
    vehicle_number = db.Column(db.String(50))
    driver_name = db.Column(db.String(100))
    driver_contact = db.Column(db.String(20))
    destination_address = db.Column(db.Text)
    destination_city = db.Column(db.String(100))
    status = db.Column(db.String(20), default='planned')  # planned, in_transit, delivered, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('DispatchPlanItem', back_populates='dispatch_plan', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'plan_number': self.plan_number,
            'shipment_date': self.shipment_date.isoformat() if self.shipment_date else None,
            'carrier': self.carrier,
            'vehicle_number': self.vehicle_number,
            'driver_name': self.driver_name,
            'driver_contact': self.driver_contact,
            'destination_address': self.destination_address,
            'destination_city': self.destination_city,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DispatchPlanItem(db.Model):
    """Dispatch plan line items."""
    __tablename__ = 'dispatch_plan_items'

    id = db.Column(db.Integer, primary_key=True)
    dispatch_plan_id = db.Column(db.Integer, db.ForeignKey('dispatch_plans.id'), nullable=False)
    packaging_order_id = db.Column(db.Integer, db.ForeignKey('packaging_orders.id'))
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'))
    product_code = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Numeric(15, 2), nullable=False)
    unit = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    dispatch_plan = db.relationship('DispatchPlan', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id,
            'dispatch_plan_id': self.dispatch_plan_id,
            'packaging_order_id': self.packaging_order_id,
            'sales_order_id': self.sales_order_id,
            'product_code': self.product_code,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit': self.unit
        }