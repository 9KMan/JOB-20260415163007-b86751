"""
Goods Receiving Module Models
"""
from datetime import datetime
from app import db


class GoodsReceivingNote(db.Model):
    """Goods receiving note model for incoming shipments."""
    __tablename__ = 'goods_receiving_notes'

    id = db.Column(db.Integer, primary_key=True)
    grn_number = db.Column(db.String(50), unique=True, nullable=False)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    received_date = db.Column(db.DateTime, default=datetime.utcnow)
    received_by = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, inspected, approved, rejected, received
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    purchase_order = db.relationship('PurchaseOrder', foreign_keys=[purchase_order_id])
    supplier = db.relationship('Supplier', foreign_keys=[supplier_id])
    items = db.relationship('GoodsReceivingNoteItem', back_populates='grn', lazy='dynamic', cascade='all, delete-orphan')
    inspection = db.relationship('Inspection', back_populates='grn', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'grn_number': self.grn_number,
            'purchase_order_id': self.purchase_order_id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'received_by': self.received_by,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class GoodsReceivingNoteItem(db.Model):
    """Items within a goods receiving note."""
    __tablename__ = 'goods_receiving_note_items'

    id = db.Column(db.Integer, primary_key=True)
    grn_id = db.Column(db.Integer, db.ForeignKey('goods_receiving_notes.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    expected_quantity = db.Column(db.Numeric(15, 2), nullable=False)
    received_quantity = db.Column(db.Numeric(15, 2), nullable=False)
    accepted_quantity = db.Column(db.Numeric(15, 2))
    rejected_quantity = db.Column(db.Numeric(15, 2))
    unit = db.Column(db.String(20))
    location = db.Column(db.String(100))
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    grn = db.relationship('GoodsReceivingNote', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id,
            'grn_id': self.grn_id,
            'product_code': self.product_code,
            'description': self.description,
            'expected_quantity': float(self.expected_quantity) if self.expected_quantity else 0,
            'received_quantity': float(self.received_quantity) if self.received_quantity else 0,
            'accepted_quantity': float(self.accepted_quantity) if self.accepted_quantity else 0,
            'rejected_quantity': float(self.rejected_quantity) if self.rejected_quantity else 0,
            'unit': self.unit,
            'location': self.location,
            'batch_number': self.batch_number,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None
        }


class Inspection(db.Model):
    """Quality inspection model for received goods."""
    __tablename__ = 'inspections'

    id = db.Column(db.Integer, primary_key=True)
    grn_id = db.Column(db.Integer, db.ForeignKey('goods_receiving_notes.id'), nullable=False)
    inspector_name = db.Column(db.String(100), nullable=False)
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow)
    inspection_type = db.Column(db.String(50))  # random, full, visual
    result = db.Column(db.String(20))  # pass, fail, conditional
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    grn = db.relationship('GoodsReceivingNote', back_populates='inspection')
    items = db.relationship('InspectionItem', back_populates='inspection', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'grn_id': self.grn_id,
            'inspector_name': self.inspector_name,
            'inspection_date': self.inspection_date.isoformat() if self.inspection_date else None,
            'inspection_type': self.inspection_type,
            'result': self.result,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class InspectionItem(db.Model):
    """Inspection line items for quality checks."""
    __tablename__ = 'inspection_items'

    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspections.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    quantity_checked = db.Column(db.Numeric(15, 2), nullable=False)
    quantity_passed = db.Column(db.Numeric(15, 2))
    quantity_failed = db.Column(db.Numeric(15, 2))
    defect_type = db.Column(db.String(100))
    defect_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    inspection = db.relationship('Inspection', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id,
            'inspection_id': self.inspection_id,
            'product_code': self.product_code,
            'quantity_checked': float(self.quantity_checked) if self.quantity_checked else 0,
            'quantity_passed': float(self.quantity_passed) if self.quantity_passed else 0,
            'quantity_failed': float(self.quantity_failed) if self.quantity_failed else 0,
            'defect_type': self.defect_type,
            'defect_notes': self.defect_notes
        }


class WarehouseAllocation(db.Model):
    """Warehouse allocation for received goods."""
    __tablename__ = 'warehouse_allocations'

    id = db.Column(db.Integer, primary_key=True)
    grn_item_id = db.Column(db.Integer, db.ForeignKey('goods_receiving_note_items.id'), nullable=False)
    warehouse_location = db.Column(db.String(100), nullable=False)
    zone = db.Column(db.String(50))
    rack = db.Column(db.String(50))
    bin = db.Column(db.String(50))
    quantity = db.Column(db.Numeric(15, 2), nullable=False)
    allocated_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'grn_item_id': self.grn_item_id,
            'warehouse_location': self.warehouse_location,
            'zone': self.zone,
            'rack': self.rack,
            'bin': self.bin,
            'quantity': float(self.quantity) if self.quantity else 0,
            'allocated_date': self.allocated_date.isoformat() if self.allocated_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ReturnToSupplier(db.Model):
    """Return to supplier model for rejected goods."""
    __tablename__ = 'returns_to_supplier'

    id = db.Column(db.Integer, primary_key=True)
    return_number = db.Column(db.String(50), unique=True, nullable=False)
    grn_id = db.Column(db.Integer, db.ForeignKey('goods_receiving_notes.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    return_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='draft')  # draft, sent, approved, received, closed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    grn = db.relationship('GoodsReceivingNote')
    supplier = db.relationship('Supplier')
    items = db.relationship('ReturnToSupplierItem', back_populates='return', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'return_number': self.return_number,
            'grn_id': self.grn_id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'reason': self.reason,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ReturnToSupplierItem(db.Model):
    """Items being returned to supplier."""
    __tablename__ = 'return_to_supplier_items'

    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('returns_to_supplier.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 2), nullable=False)
    unit = db.Column(db.String(20))
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    return = db.relationship('ReturnToSupplier', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id,
            'return_id': self.return_id,
            'product_code': self.product_code,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit': self.unit,
            'reason': self.reason
        }