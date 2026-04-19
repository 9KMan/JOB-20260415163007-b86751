"""
Production Module API Routes
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.production import (
    BillOfMaterials, BOMItem, WorkOrder, WorkOrderOperation,
    MaterialAllocation, ProductionSchedule, ScheduleEntry
)

production_bp = Blueprint('production', __name__)


# Bill of Materials Routes
@production_bp.route('/bom', methods=['GET'])
def get_bom_list():
    """Get all bills of materials."""
    bom_list = BillOfMaterials.query.filter_by(is_active=True).all()
    return jsonify({'bom_list': [b.to_dict() for b in bom_list]})


@production_bp.route('/bom/<int:bom_id>', methods=['GET'])
def get_bom(bom_id):
    """Get a single bill of materials."""
    bom = BillOfMaterials.query.get_or_404(bom_id)
    return jsonify({'bom': bom.to_dict()})


@production_bp.route('/bom', methods=['POST'])
def create_bom():
    """Create a new bill of materials."""
    data = request.get_json()
    try:
        bom = BillOfMaterials(
            bom_code=data.get('bom_code'),
            product_code=data.get('product_code'),
            description=data.get('description'),
            version=data.get('version', '1.0'),
            effective_from=data.get('effective_from'),
            notes=data.get('notes')
        )
        db.session.add(bom)
        db.session.flush()

        # Add items
        for item_data in data.get('items', []):
            item = BOMItem(
                bom_id=bom.id,
                product_code=item_data.get('product_code'),
                description=item_data.get('description'),
                quantity_required=item_data.get('quantity_required'),
                unit=item_data.get('unit'),
                is_optional=item_data.get('is_optional', False),
                scrap_percentage=item_data.get('scrap_percentage', 0)
            )
            db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'BOM created successfully', 'bom': bom.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@production_bp.route('/bom/<int:bom_id>', methods=['PUT'])
def update_bom(bom_id):
    """Update a bill of materials."""
    bom = BillOfMaterials.query.get_or_404(bom_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(bom, key):
                setattr(bom, key, value)
        db.session.commit()
        return jsonify({'message': 'BOM updated successfully', 'bom': bom.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Work Order Routes
@production_bp.route('/work-orders', methods=['GET'])
def get_work_orders():
    """Get all work orders."""
    orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).all()
    return jsonify({'work_orders': [o.to_dict() for o in orders]})


@production_bp.route('/work-orders/<int:order_id>', methods=['GET'])
def get_work_order(order_id):
    """Get a single work order."""
    order = WorkOrder.query.get_or_404(order_id)
    return jsonify({'work_order': order.to_dict()})


@production_bp.route('/work-orders', methods=['POST'])
def create_work_order():
    """Create a new work order."""
    data = request.get_json()
    try:
        order = WorkOrder(
            work_order_number=data.get('work_order_number'),
            bom_id=data.get('bom_id'),
            product_code=data.get('product_code'),
            description=data.get('description'),
            quantity=data.get('quantity'),
            unit=data.get('unit'),
            priority=data.get('priority', 5),
            status=data.get('status', 'planned'),
            planned_start_date=data.get('planned_start_date'),
            planned_end_date=data.get('planned_end_date'),
            work_center=data.get('work_center'),
            notes=data.get('notes')
        )
        db.session.add(order)
        db.session.flush()

        # Add operations if provided
        for op_data in data.get('operations', []):
            op = WorkOrderOperation(
                work_order_id=order.id,
                sequence=op_data.get('sequence'),
                operation_name=op_data.get('operation_name'),
                work_center=op_data.get('work_center'),
                machine=op_data.get('machine'),
                setup_time=op_data.get('setup_time'),
                run_time=op_data.get('run_time'),
                labor_required=op_data.get('labor_required')
            )
            db.session.add(op)
        db.session.commit()
        return jsonify({'message': 'Work order created successfully', 'work_order': order.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@production_bp.route('/work-orders/<int:order_id>', methods=['PUT'])
def update_work_order(order_id):
    """Update a work order."""
    order = WorkOrder.query.get_or_404(order_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(order, key):
                setattr(order, key, value)
        db.session.commit()
        return jsonify({'message': 'Work order updated successfully', 'work_order': order.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@production_bp.route('/work-orders/<int:order_id>/start', methods=['POST'])
def start_work_order(order_id):
    """Start a work order (change status to in_progress)."""
    order = WorkOrder.query.get_or_404(order_id)
    order.status = 'in_progress'
    from datetime import datetime
    order.actual_start_date = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Work order started', 'work_order': order.to_dict()})


@production_bp.route('/work-orders/<int:order_id>/complete', methods=['POST'])
def complete_work_order(order_id):
    """Complete a work order."""
    order = WorkOrder.query.get_or_404(order_id)
    order.status = 'completed'
    from datetime import datetime
    order.actual_end_date = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Work order completed', 'work_order': order.to_dict()})


# Material Allocation Routes
@production_bp.route('/material-allocations', methods=['GET'])
def get_material_allocations():
    """Get all material allocations."""
    allocations = MaterialAllocation.query.all()
    return jsonify({'allocations': [a.to_dict() for a in allocations]})


@production_bp.route('/material-allocations', methods=['POST'])
def create_material_allocation():
    """Create a new material allocation."""
    data = request.get_json()
    try:
        allocation = MaterialAllocation(
            work_order_id=data.get('work_order_id'),
            product_code=data.get('product_code'),
            quantity_allocated=data.get('quantity_allocated'),
            warehouse_location=data.get('warehouse_location'),
            notes=data.get('notes')
        )
        db.session.add(allocation)
        db.session.commit()
        return jsonify({'message': 'Material allocation created successfully', 'allocation': allocation.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Production Schedule Routes
@production_bp.route('/schedules', methods=['GET'])
def get_schedules():
    """Get all production schedules."""
    schedules = ProductionSchedule.query.order_by(ProductionSchedule.period_start.desc()).all()
    return jsonify({'schedules': [s.to_dict() for s in schedules]})


@production_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """Get a single schedule."""
    schedule = ProductionSchedule.query.get_or_404(schedule_id)
    return jsonify({'schedule': schedule.to_dict()})


@production_bp.route('/schedules', methods=['POST'])
def create_schedule():
    """Create a new production schedule."""
    data = request.get_json()
    try:
        schedule = ProductionSchedule(
            schedule_code=data.get('schedule_code'),
            period_start=data.get('period_start'),
            period_end=data.get('period_end'),
            status=data.get('status', 'draft'),
            notes=data.get('notes')
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify({'message': 'Schedule created successfully', 'schedule': schedule.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400