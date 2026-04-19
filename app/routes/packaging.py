"""
Packaging Module API Routes
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.packaging import (
    PackagingOrder, PackingSpecification, PackageLabel, DispatchPlan, DispatchPlanItem
)

packaging_bp = Blueprint('packaging', __name__)


# Packaging Order Routes
@packaging_bp.route('/orders', methods=['GET'])
def get_packaging_orders():
    """Get all packaging orders."""
    orders = PackagingOrder.query.order_by(PackagingOrder.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]})


@packaging_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_packaging_order(order_id):
    """Get a single packaging order."""
    order = PackagingOrder.query.get_or_404(order_id)
    return jsonify({'order': order.to_dict()})


@packaging_bp.route('/orders', methods=['POST'])
def create_packaging_order():
    """Create a new packaging order."""
    data = request.get_json()
    try:
        order = PackagingOrder(
            order_number=data.get('order_number'),
            sales_order_id=data.get('sales_order_id'),
            work_order_id=data.get('work_order_id'),
            product_code=data.get('product_code'),
            description=data.get('description'),
            quantity_to_pack=data.get('quantity_to_pack'),
            unit=data.get('unit'),
            packaging_type=data.get('packaging_type'),
            priority=data.get('priority', 5),
            status=data.get('status', 'pending'),
            scheduled_date=data.get('scheduled_date'),
            notes=data.get('notes')
        )
        db.session.add(order)
        db.session.commit()
        return jsonify({'message': 'Packaging order created successfully', 'order': order.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@packaging_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_packaging_order(order_id):
    """Update a packaging order."""
    order = PackagingOrder.query.get_or_404(order_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(order, key):
                setattr(order, key, value)
        db.session.commit()
        return jsonify({'message': 'Packaging order updated successfully', 'order': order.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@packaging_bp.route('/orders/<int:order_id>/start', methods=['POST'])
def start_packaging_order(order_id):
    """Start a packaging order."""
    order = PackagingOrder.query.get_or_404(order_id)
    from datetime import datetime
    order.status = 'in_progress'
    order.started_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Packaging order started', 'order': order.to_dict()})


@packaging_bp.route('/orders/<int:order_id>/complete', methods=['POST'])
def complete_packaging_order(order_id):
    """Complete a packaging order."""
    order = PackagingOrder.query.get_or_404(order_id)
    from datetime import datetime
    order.status = 'completed'
    order.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Packaging order completed', 'order': order.to_dict()})


# Packing Specification Routes
@packaging_bp.route('/specifications', methods=['GET'])
def get_specifications():
    """Get all packing specifications."""
    specs = PackingSpecification.query.all()
    return jsonify({'specifications': [s.to_dict() for s in specs]})


@packaging_bp.route('/specifications', methods=['POST'])
def create_specification():
    """Create a new packing specification."""
    data = request.get_json()
    try:
        spec = PackingSpecification(
            packaging_order_id=data.get('packaging_order_id'),
            product_code=data.get('product_code'),
            specification_type=data.get('specification_type'),
            specification_code=data.get('specification_code'),
            description=data.get('description'),
            quantity=data.get('quantity', 1),
            dimensions_length=data.get('dimensions_length'),
            dimensions_width=data.get('dimensions_width'),
            dimensions_height=data.get('dimensions_height'),
            weight=data.get('weight'),
            barcode=data.get('barcode'),
            qr_code=data.get('qr_code'),
            notes=data.get('notes')
        )
        db.session.add(spec)
        db.session.commit()
        return jsonify({'message': 'Specification created successfully', 'specification': spec.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Package Label Routes
@packaging_bp.route('/labels', methods=['GET'])
def get_labels():
    """Get all package labels."""
    labels = PackageLabel.query.order_by(PackageLabel.created_at.desc()).all()
    return jsonify({'labels': [l.to_dict() for l in labels]})


@packaging_bp.route('/labels', methods=['POST'])
def create_label():
    """Create a new package label."""
    data = request.get_json()
    try:
        label = PackageLabel(
            packaging_order_id=data.get('packaging_order_id'),
            label_number=data.get('label_number'),
            product_code=data.get('product_code'),
            serial_number=data.get('serial_number'),
            batch_number=data.get('batch_number'),
            quantity=data.get('quantity', 1)
        )
        db.session.add(label)
        db.session.commit()
        return jsonify({'message': 'Label created successfully', 'label': label.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@packaging_bp.route('/labels/<int:label_id>/print', methods=['POST'])
def print_label(label_id):
    """Mark a label as printed."""
    label = PackageLabel.query.get_or_404(label_id)
    from datetime import datetime
    label.printed = True
    label.printed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Label marked as printed', 'label': label.to_dict()})


# Dispatch Plan Routes
@packaging_bp.route('/dispatch', methods=['GET'])
def get_dispatch_plans():
    """Get all dispatch plans."""
    plans = DispatchPlan.query.order_by(DispatchPlan.created_at.desc()).all()
    return jsonify({'dispatch_plans': [p.to_dict() for p in plans]})


@packaging_bp.route('/dispatch/<int:plan_id>', methods=['GET'])
def get_dispatch_plan(plan_id):
    """Get a single dispatch plan."""
    plan = DispatchPlan.query.get_or_404(plan_id)
    return jsonify({'dispatch_plan': plan.to_dict()})


@packaging_bp.route('/dispatch', methods=['POST'])
def create_dispatch_plan():
    """Create a new dispatch plan."""
    data = request.get_json()
    try:
        plan = DispatchPlan(
            plan_number=data.get('plan_number'),
            shipment_date=data.get('shipment_date'),
            carrier=data.get('carrier'),
            vehicle_number=data.get('vehicle_number'),
            driver_name=data.get('driver_name'),
            driver_contact=data.get('driver_contact'),
            destination_address=data.get('destination_address'),
            destination_city=data.get('destination_city'),
            status=data.get('status', 'planned'),
            notes=data.get('notes')
        )
        db.session.add(plan)
        db.session.flush()

        # Add items
        for item_data in data.get('items', []):
            item = DispatchPlanItem(
                dispatch_plan_id=plan.id,
                packaging_order_id=item_data.get('packaging_order_id'),
                sales_order_id=item_data.get('sales_order_id'),
                product_code=item_data.get('product_code'),
                quantity=item_data.get('quantity'),
                unit=item_data.get('unit')
            )
            db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'Dispatch plan created successfully', 'dispatch_plan': plan.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@packaging_bp.route('/dispatch/<int:plan_id>', methods=['PUT'])
def update_dispatch_plan(plan_id):
    """Update a dispatch plan."""
    plan = DispatchPlan.query.get_or_404(plan_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
        db.session.commit()
        return jsonify({'message': 'Dispatch plan updated successfully', 'dispatch_plan': plan.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400