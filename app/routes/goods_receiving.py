"""
Goods Receiving Module API Routes
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.goods_receiving import (
    GoodsReceivingNote, GoodsReceivingNoteItem, Inspection, InspectionItem,
    WarehouseAllocation, ReturnToSupplier, ReturnToSupplierItem
)

goods_receiving_bp = Blueprint('goods_receiving', __name__)


# Goods Receiving Note Routes
@goods_receiving_bp.route('/grn', methods=['GET'])
def get_grn_list():
    """Get all goods receiving notes."""
    grn_notes = GoodsReceivingNote.query.order_by(GoodsReceivingNote.created_at.desc()).all()
    return jsonify({'grn_notes': [g.to_dict() for g in grn_notes]})


@goods_receiving_bp.route('/grn/<int:grn_id>', methods=['GET'])
def get_grn(grn_id):
    """Get a single goods receiving note."""
    grn = GoodsReceivingNote.query.get_or_404(grn_id)
    return jsonify({'grn': grn.to_dict()})


@goods_receiving_bp.route('/grn', methods=['POST'])
def create_grn():
    """Create a new goods receiving note."""
    data = request.get_json()
    try:
        grn = GoodsReceivingNote(
            grn_number=data.get('grn_number'),
            purchase_order_id=data.get('purchase_order_id'),
            supplier_id=data.get('supplier_id'),
            received_by=data.get('received_by'),
            status=data.get('status', 'pending'),
            notes=data.get('notes')
        )
        db.session.add(grn)
        db.session.flush()

        # Add items
        for item_data in data.get('items', []):
            item = GoodsReceivingNoteItem(
                grn_id=grn.id,
                product_code=item_data.get('product_code'),
                description=item_data.get('description'),
                expected_quantity=item_data.get('expected_quantity'),
                received_quantity=item_data.get('received_quantity'),
                accepted_quantity=item_data.get('accepted_quantity'),
                rejected_quantity=item_data.get('rejected_quantity'),
                unit=item_data.get('unit'),
                location=item_data.get('location'),
                batch_number=item_data.get('batch_number'),
                expiry_date=item_data.get('expiry_date')
            )
            db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'GRN created successfully', 'grn': grn.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@goods_receiving_bp.route('/grn/<int:grn_id>', methods=['PUT'])
def update_grn(grn_id):
    """Update a goods receiving note."""
    grn = GoodsReceivingNote.query.get_or_404(grn_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(grn, key):
                setattr(grn, key, value)
        db.session.commit()
        return jsonify({'message': 'GRN updated successfully', 'grn': grn.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Inspection Routes
@goods_receiving_bp.route('/inspections', methods=['GET'])
def get_inspections():
    """Get all inspections."""
    inspections = Inspection.query.order_by(Inspection.inspection_date.desc()).all()
    return jsonify({'inspections': [i.to_dict() for i in inspections]})


@goods_receiving_bp.route('/inspections/<int:inspection_id>', methods=['GET'])
def get_inspection(inspection_id):
    """Get a single inspection."""
    inspection = Inspection.query.get_or_404(inspection_id)
    return jsonify({'inspection': inspection.to_dict()})


@goods_receiving_bp.route('/inspections', methods=['POST'])
def create_inspection():
    """Create a new inspection."""
    data = request.get_json()
    try:
        inspection = Inspection(
            grn_id=data.get('grn_id'),
            inspector_name=data.get('inspector_name'),
            inspection_type=data.get('inspection_type'),
            result=data.get('result'),
            notes=data.get('notes')
        )
        db.session.add(inspection)
        db.session.flush()

        # Add items
        for item_data in data.get('items', []):
            item = InspectionItem(
                inspection_id=inspection.id,
                product_code=item_data.get('product_code'),
                quantity_checked=item_data.get('quantity_checked'),
                quantity_passed=item_data.get('quantity_passed'),
                quantity_failed=item_data.get('quantity_failed'),
                defect_type=item_data.get('defect_type'),
                defect_notes=item_data.get('defect_notes')
            )
            db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'Inspection created successfully', 'inspection': inspection.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Warehouse Allocation Routes
@goods_receiving_bp.route('/allocations', methods=['GET'])
def get_allocations():
    """Get all warehouse allocations."""
    allocations = WarehouseAllocation.query.all()
    return jsonify({'allocations': [a.to_dict() for a in allocations]})


@goods_receiving_bp.route('/allocations', methods=['POST'])
def create_allocation():
    """Create a new warehouse allocation."""
    data = request.get_json()
    try:
        allocation = WarehouseAllocation(
            grn_item_id=data.get('grn_item_id'),
            warehouse_location=data.get('warehouse_location'),
            zone=data.get('zone'),
            rack=data.get('rack'),
            bin=data.get('bin'),
            quantity=data.get('quantity'),
            notes=data.get('notes')
        )
        db.session.add(allocation)
        db.session.commit()
        return jsonify({'message': 'Allocation created successfully', 'allocation': allocation.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Return to Supplier Routes
@goods_receiving_bp.route('/returns', methods=['GET'])
def get_returns():
    """Get all returns to supplier."""
    returns = ReturnToSupplier.query.order_by(ReturnToSupplier.created_at.desc()).all()
    return jsonify({'returns': [r.to_dict() for r in returns]})


@goods_receiving_bp.route('/returns/<int:return_id>', methods=['GET'])
def get_return(return_id):
    """Get a single return."""
    ret = ReturnToSupplier.query.get_or_404(return_id)
    return jsonify({'return': ret.to_dict()})


@goods_receiving_bp.route('/returns', methods=['POST'])
def create_return():
    """Create a new return to supplier."""
    data = request.get_json()
    try:
        ret = ReturnToSupplier(
            return_number=data.get('return_number'),
            grn_id=data.get('grn_id'),
            supplier_id=data.get('supplier_id'),
            reason=data.get('reason'),
            status=data.get('status', 'draft'),
            notes=data.get('notes')
        )
        db.session.add(ret)
        db.session.flush()

        # Add items
        for item_data in data.get('items', []):
            item = ReturnToSupplierItem(
                return_id=ret.id,
                product_code=item_data.get('product_code'),
                description=item_data.get('description'),
                quantity=item_data.get('quantity'),
                unit=item_data.get('unit'),
                reason=item_data.get('reason')
            )
            db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'Return created successfully', 'return': ret.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@goods_receiving_bp.route('/returns/<int:return_id>', methods=['PUT'])
def update_return(return_id):
    """Update a return."""
    ret = ReturnToSupplier.query.get_or_404(return_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(ret, key):
                setattr(ret, key, value)
        db.session.commit()
        return jsonify({'message': 'Return updated successfully', 'return': ret.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400