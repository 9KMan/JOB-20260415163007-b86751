"""
Procurement Module API Routes
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.procurement import Supplier, PurchaseRequisition, PurchaseRequisitionItem, PurchaseOrder, PurchaseOrderItem, PriceList

procurement_bp = Blueprint('procurement', __name__)


# Supplier Routes
@procurement_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    """Get all suppliers."""
    suppliers = Supplier.query.filter_by(is_active=True).all()
    return jsonify({'suppliers': [s.to_dict() for s in suppliers]})


@procurement_bp.route('/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """Get a single supplier by ID."""
    supplier = Supplier.query.get_or_404(supplier_id)
    return jsonify({'supplier': supplier.to_dict()})


@procurement_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    """Create a new supplier."""
    data = request.get_json()
    try:
        supplier = Supplier(
            code=data.get('code'),
            name=data.get('name'),
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            country=data.get('country'),
            tax_id=data.get('tax_id'),
            payment_terms=data.get('payment_terms'),
            rating=data.get('rating', 0)
        )
        db.session.add(supplier)
        db.session.commit()
        return jsonify({'message': 'Supplier created successfully', 'supplier': supplier.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@procurement_bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    """Update an existing supplier."""
    supplier = Supplier.query.get_or_404(supplier_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(supplier, key):
                setattr(supplier, key, value)
        db.session.commit()
        return jsonify({'message': 'Supplier updated successfully', 'supplier': supplier.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@procurement_bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    """Soft delete a supplier."""
    supplier = Supplier.query.get_or_404(supplier_id)
    supplier.is_active = False
    db.session.commit()
    return jsonify({'message': 'Supplier deactivated successfully'})


# Purchase Requisition Routes
@procurement_bp.route('/requisitions', methods=['GET'])
def get_requisitions():
    """Get all purchase requisitions."""
    requisitions = PurchaseRequisition.query.order_by(PurchaseRequisition.created_at.desc()).all()
    return jsonify({'requisitions': [r.to_dict() for r in requisitions]})


@procurement_bp.route('/requisitions/<int:requisition_id>', methods=['GET'])
def get_requisition(requisition_id):
    """Get a single requisition."""
    requisition = PurchaseRequisition.query.get_or_404(requisition_id)
    return jsonify({'requisition': requisition.to_dict()})


@procurement_bp.route('/requisitions', methods=['POST'])
def create_requisition():
    """Create a new purchase requisition."""
    data = request.get_json()
    try:
        requisition = PurchaseRequisition(
            requisition_number=data.get('requisition_number'),
            requester_name=data.get('requester_name'),
            department=data.get('department'),
            required_date=data.get('required_date'),
            status=data.get('status', 'draft'),
            notes=data.get('notes')
        )
        db.session.add(requisition)
        db.session.flush()

        # Add items if provided
        for item_data in data.get('items', []):
            item = PurchaseRequisitionItem(
                requisition_id=requisition.id,
                product_code=item_data.get('product_code'),
                description=item_data.get('description'),
                quantity=item_data.get('quantity'),
                unit=item_data.get('unit'),
                estimated_price=item_data.get('estimated_price')
            )
            db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'Requisition created successfully', 'requisition': requisition.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@procurement_bp.route('/requisitions/<int:requisition_id>', methods=['PUT'])
def update_requisition(requisition_id):
    """Update a purchase requisition."""
    requisition = PurchaseRequisition.query.get_or_404(requisition_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(requisition, key):
                setattr(requisition, key, value)
        db.session.commit()
        return jsonify({'message': 'Requisition updated successfully', 'requisition': requisition.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Purchase Order Routes
@procurement_bp.route('/orders', methods=['GET'])
def get_purchase_orders():
    """Get all purchase orders."""
    orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]})


@procurement_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_purchase_order(order_id):
    """Get a single purchase order."""
    order = PurchaseOrder.query.get_or_404(order_id)
    return jsonify({'order': order.to_dict()})


@procurement_bp.route('/orders', methods=['POST'])
def create_purchase_order():
    """Create a new purchase order."""
    data = request.get_json()
    try:
        order = PurchaseOrder(
            order_number=data.get('order_number'),
            supplier_id=data.get('supplier_id'),
            requisition_id=data.get('requisition_id'),
            expected_delivery_date=data.get('expected_delivery_date'),
            status=data.get('status', 'draft'),
            payment_terms=data.get('payment_terms'),
            shipping_terms=data.get('shipping_terms'),
            notes=data.get('notes')
        )
        db.session.add(order)
        db.session.flush()

        # Add items
        for item_data in data.get('items', []):
            item = PurchaseOrderItem(
                purchase_order_id=order.id,
                product_code=item_data.get('product_code'),
                description=item_data.get('description'),
                quantity=item_data.get('quantity'),
                unit=item_data.get('unit'),
                unit_price=item_data.get('unit_price'),
                tax_rate=item_data.get('tax_rate', 0)
            )
            db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'Purchase order created successfully', 'order': order.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@procurement_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_purchase_order(order_id):
    """Update a purchase order."""
    order = PurchaseOrder.query.get_or_404(order_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(order, key):
                setattr(order, key, value)
        db.session.commit()
        return jsonify({'message': 'Purchase order updated successfully', 'order': order.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@procurement_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_purchase_order(order_id):
    """Cancel a purchase order."""
    order = PurchaseOrder.query.get_or_404(order_id)
    order.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Purchase order cancelled successfully'})


# Price List Routes
@procurement_bp.route('/price-lists', methods=['GET'])
def get_price_lists():
    """Get all price lists."""
    price_lists = PriceList.query.filter_by(is_active=True).all()
    return jsonify({'price_lists': [p.to_dict() for p in price_lists]})


@procurement_bp.route('/price-lists', methods=['POST'])
def create_price_list():
    """Create a new price list entry."""
    data = request.get_json()
    try:
        price_list = PriceList(
            supplier_id=data.get('supplier_id'),
            product_code=data.get('product_code'),
            description=data.get('description'),
            unit_price=data.get('unit_price'),
            currency=data.get('currency', 'USD'),
            min_quantity=data.get('min_quantity', 1),
            effective_from=data.get('effective_from'),
            effective_to=data.get('effective_to'),
            is_active=data.get('is_active', True)
        )
        db.session.add(price_list)
        db.session.commit()
        return jsonify({'message': 'Price list created successfully', 'price_list': price_list.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@procurement_bp.route('/price-lists/<int:price_list_id>', methods=['PUT'])
def update_price_list(price_list_id):
    """Update a price list entry."""
    price_list = PriceList.query.get_or_404(price_list_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(price_list, key):
                setattr(price_list, key, value)
        db.session.commit()
        return jsonify({'message': 'Price list updated successfully', 'price_list': price_list.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400