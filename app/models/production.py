"""
Production Module Models
"""
from datetime import datetime
from app import db


class BillOfMaterials(db.Model):
    """Bill of Materials model for product structures."""
    __tablename__ = 'bills_of_materials'

    id = db.Column(db.Integer, primary_key=True)
    bom_code = db.Column(db.String(50), unique=True, nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    version = db.Column(db.String(20), default='1.0')
    is_active = db.Column(db.Boolean, default=True)
    effective_from = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('BOMItem', back_populates='bom', lazy='dynamic', cascade='all, delete-orphan')
    work_orders = db.relationship('WorkOrder', back_populates='bom', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'bom_code': self.bom_code,
            'product_code': self.product_code,
            'description': self.description,
            'version': self.version,
            'is_active': self.is_active,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class BOMItem(db.Model):
    """Bill of Materials line items."""
    __tablename__ = 'bom_items'

    id = db.Column(db.Integer, primary_key=True)
    bom_id = db.Column(db.Integer, db.ForeignKey('bills_of_materials.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    quantity_required = db.Column(db.Numeric(15, 4), nullable=False)
    unit = db.Column(db.String(20))
    is_optional = db.Column(db.Boolean, default=False)
    scrap_percentage = db.Column(db.Numeric(5, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bom = db.relationship('BillOfMaterials', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id,
            'bom_id': self.bom_id,
            'product_code': self.product_code,
            'description': self.description,
            'quantity_required': float(self.quantity_required) if self.quantity_required else 0,
            'unit': self.unit,
            'is_optional': self.is_optional,
            'scrap_percentage': float(self.scrap_percentage) if self.scrap_percentage else 0
        }


class WorkOrder(db.Model):
    """Work order model for production orders."""
    __tablename__ = 'work_orders'

    id = db.Column(db.Integer, primary_key=True)
    work_order_number = db.Column(db.String(50), unique=True, nullable=False)
    bom_id = db.Column(db.Integer, db.ForeignKey('bills_of_materials.id'))
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    quantity = db.Column(db.Numeric(15, 2), nullable=False)
    unit = db.Column(db.String(20))
    priority = db.Column(db.Integer, default=5)  # 1-10 priority (1 = highest)
    status = db.Column(db.String(20), default='planned')  # planned, released, in_progress, completed, cancelled
    planned_start_date = db.Column(db.Date)
    planned_end_date = db.Column(db.Date)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    work_center = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bom = db.relationship('BillOfMaterials', back_populates='work_orders')
    operations = db.relationship('WorkOrderOperation', back_populates='work_order', lazy='dynamic', cascade='all, delete-orphan')
    material_allocations = db.relationship('MaterialAllocation', back_populates='work_order', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'work_order_number': self.work_order_number,
            'bom_id': self.bom_id,
            'product_code': self.product_code,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit': self.unit,
            'priority': self.priority,
            'status': self.status,
            'planned_start_date': self.planned_start_date.isoformat() if self.planned_start_date else None,
            'planned_end_date': self.planned_end_date.isoformat() if self.planned_end_date else None,
            'actual_start_date': self.actual_start_date.isoformat() if self.actual_start_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'work_center': self.work_center,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class WorkOrderOperation(db.Model):
    """Work order operations/steps in production."""
    __tablename__ = 'work_order_operations'

    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    operation_name = db.Column(db.String(100), nullable=False)
    work_center = db.Column(db.String(100))
    machine = db.Column(db.String(100))
    setup_time = db.Column(db.Numeric(6, 2))  # minutes
    run_time = db.Column(db.Numeric(6, 2))  # minutes per unit
    labor_required = db.Column(db.Numeric(6, 2))
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    work_order = db.relationship('WorkOrder', back_populates='operations')

    def to_dict(self):
        return {
            'id': self.id,
            'work_order_id': self.work_order_id,
            'sequence': self.sequence,
            'operation_name': self.operation_name,
            'work_center': self.work_center,
            'machine': self.machine,
            'setup_time': float(self.setup_time) if self.setup_time else 0,
            'run_time': float(self.run_time) if self.run_time else 0,
            'labor_required': float(self.labor_required) if self.labor_required else 0,
            'status': self.status,
            'notes': self.notes
        }


class MaterialAllocation(db.Model):
    """Material allocations for work orders from inventory."""
    __tablename__ = 'material_allocations'

    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    quantity_allocated = db.Column(db.Numeric(15, 4), nullable=False)
    quantity_used = db.Column(db.Numeric(15, 4), default=0)
    warehouse_location = db.Column(db.String(100))
    allocation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='allocated')  # allocated, partial, consumed, returned
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    work_order = db.relationship('WorkOrder', back_populates='material_allocations')

    def to_dict(self):
        return {
            'id': self.id,
            'work_order_id': self.work_order_id,
            'product_code': self.product_code,
            'quantity_allocated': float(self.quantity_allocated) if self.quantity_allocated else 0,
            'quantity_used': float(self.quantity_used) if self.quantity_used else 0,
            'warehouse_location': self.warehouse_location,
            'allocation_date': self.allocation_date.isoformat() if self.allocation_date else None,
            'status': self.status,
            'notes': self.notes
        }


class ProductionSchedule(db.Model):
    """Production schedule for planning."""
    __tablename__ = 'production_schedules'

    id = db.Column(db.Integer, primary_key=True)
    schedule_code = db.Column(db.String(50), unique=True, nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    total_hours = db.Column(db.Numeric(8, 2))
    status = db.Column(db.String(20), default='draft')  # draft, published, closed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    entries = db.relationship('ScheduleEntry', back_populates='schedule', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'schedule_code': self.schedule_code,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'total_hours': float(self.total_hours) if self.total_hours else 0,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ScheduleEntry(db.Model):
    """Individual entries in production schedule."""
    __tablename__ = 'schedule_entries'

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('production_schedules.id'), nullable=False)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    date = db.Column(db.Date, nullable=False)
    shift = db.Column(db.String(20))  # morning, afternoon, night
    work_center = db.Column(db.String(100))
    planned_hours = db.Column(db.Numeric(6, 2))
    actual_hours = db.Column(db.Numeric(6, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedule = db.relationship('ProductionSchedule', back_populates='entries')

    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'work_order_id': self.work_order_id,
            'date': self.date.isoformat() if self.date else None,
            'shift': self.shift,
            'work_center': self.work_center,
            'planned_hours': float(self.planned_hours) if self.planned_hours else 0,
            'actual_hours': float(self.actual_hours) if self.actual_hours else 0,
            'notes': self.notes
        }