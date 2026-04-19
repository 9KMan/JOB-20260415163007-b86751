"""
Sales Module API Routes
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.sales import (
    Customer, SalesOrder, SalesOrderItem, Shipping, SalesReturn, SalesReturnItem
)

sales_bp = Blueprint('sales', __name__)


# Customer Routes
@sales_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers."""
    customers = Customer.query.filter_by(is_active=True).all()
    return jsonify({'customers': [c.to_dict() for c in customers]})


@sales_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a single customer."""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({'customer': customer.to_dict()})


@sales_bp.route('/customers', methods=['POST'])
def create_customer():
    """Create a new customer."""
    data = request.get_json()
    try:
        customer = Customer(
            code=data.get('code'),
            name=data.get('name'),
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country'),
            postal_code=data.get('postal_code'),
            tax_id=data.get('tax_id'),
            payment_terms=data.get('payment_terms'),
            credit_limit=data.get('credit_limit', 0)
        )
        db.session.add(customer)
        db.session.commit()
        return jsonify({'message': 'Customer created successfully', 'customer': customer.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@sales_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update a customer."""
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        db.session.commit()
        return jsonify({'message': 'Customer updated successfully', 'customer': customer.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@sales_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Soft delete a customer."""
    customer = Customer.query.get_or_404(customer_id)
    customer.is_active = False
    db.session.commit()
    return jsonify({'message': 'Customer deactivated successfully'})


# Sales Order Routes
@sales_bp.route('/orders', methods=['GET'])
def get_sales_orders():
    """Get all sales orders."""
    orders = SalesOrder.query.order_by(SalesOrder.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]})


@sales_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_sales_order(order_id):
    """Get a single sales order."""
    order = SalesOrder.query.get_or_404(order_id)
    return jsonify({'order': order.to_dict()})


@sales_bp.route('/orders', methods=['POST'])
def create_sales_order():
    """Create a new sales order."""
    data = request.get_json()
    try:
        order = SalesOrder(
            order_number=data.get('order_number'),
            customer_id=data.get('customer_id'),
            delivery_date=data.get('delivery_date'),
            status=data.get('status', 'draft'),
            payment_terms=data.get('payment_terms'),
            shipping_address=data.get('shipping_address'),
            shipping_city=data.get('shipping_city'),
            discount_percentage=data.get('discount_percentage', 0),
            tax_percentage=data.get('tax_percentage', 0),
            notes=data.get('notes')
        )
        db.session.add(order)
        db.session.flush()

        subtotal = 0
        # Add items
        for item_data in data.get('items', []):
            item = SalesOrderItem(
                sales_order_id=order.id,
                product_code=item_data.get('product_code'),
                description=item_data.get('description'),
                quantity=item_data.get('quantity'),
                unit=item_data.get('unit'),
                unit_price=item_data.get('unit_price'),
                tax_rate=item_data.get('tax_rate', 0),
                discount_percentage=item_data.get('discount_percentage', 0)
            )
            db.session.add(item)
            subtotal += item.line_total

        order.subtotal = subtotal
        order.tax_amount = subtotal * (order.tax_percentage / 100)
        order.discount_amount = subtotal * (order.discount_percentage / 100)
        order.total_amount = subtotal + order.tax_amount - order.discount_amount
        db.session.commit()
        return jsonify({'message': 'Sales order created successfully', 'order': order.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@sales_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_sales_order(order_id):
    """Update a sales order."""
    order = SalesOrder.query.get_or_404(order_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(order, key):
                setattr(order, key, value)
        db.session.commit()
        return jsonify({'message': 'Sales order updated successfully', 'order': order.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@sales_bp.route('/orders/<int:order_id>/confirm', methods=['POST'])
def confirm_sales_order(order_id):
    """Confirm a sales order."""
    order = SalesOrder.query.get_or_404(order_id)
    order.status = 'confirmed'
    db.session.commit()
    return jsonify({'message': 'Sales order confirmed', 'order': order.to_dict()})


@sales_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_sales_order(order_id):
    """Cancel a sales order."""
    order = SalesOrder.query.get_or_404(order_id)
    order.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Sales order cancelled', 'order': order.to_dict()})


# Shipping Routes
@sales_bp.route('/shippings', methods=['GET'])
def get_shippings():
    """Get all shippings."""
    shippings = Shipping.query.order_by(Shipping.shipment_date.desc()).all()
    return jsonify({'shippings': [s.to_dict() for s in shippings]})


@sales_bp.route('/shippings/<int:shipping_id>', methods=['GET'])
def get_shipping(shipping_id):
    """Get a single shipping record."""
    shipping = Shipping.query.get_or_404(shipping_id)
    return jsonify({'shipping': shipping.to_dict()})


@sales_bp.route('/shippings', methods=['POST'])
def create_shipping():
    """Create a new shipping record."""
    data = request.get_json()
    try:
        shipping = Shipping(
            sales_order_id=data.get('sales_order_id'),
            shipment_number=data.get('shipment_number'),
            carrier=data.get('carrier'),
            tracking_number=data.get('tracking_number'),
            shipped_by=data.get('shipped_by'),
            notes=data.get('notes')
        )
        db.session.add(shipping)
        db.session.commit()
        return jsonify({'message': 'Shipping created successfully', 'shipping': shipping.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Sales Return Routes
@sales_bp.route('/returns', methods=['GET'])
def get_sales_returns():
    """Get all sales returns."""
    returns = SalesReturn.query.order_by(SalesReturn.created_at.desc()).all()
    return jsonify({'returns': [r.to_dict() for r in returns]})


@sales_bp.route('/returns/<int:return_id>', methods=['GET'])
def get_sales_return(return_id):
    """Get a single sales return."""
    ret = SalesReturn.query.get_or_404(return_id)
    return jsonify({'return': ret.to_dict()})


@sales_bp.route('/returns', methods=['POST'])
def create_sales_return():
    """Create a new sales return."""
    data = request.get_json()
    try:
        ret = SalesReturn(
            return_number=data.get('return_number'),
            sales_order_id=data.get('sales_order_id'),
            customer_id=data.get('customer_id'),
            reason=data.get('reason'),
            status=data.get('status', 'draft'),
            notes=data.get('notes')
        )
        db.session.add(ret)
        db.session.flush()

        # Add items
        for item_data in data.get('items', []):
            item = SalesReturnItem(
                return_id=ret.id,
                product_code=item_data.get('product_code'),
                description=item_data.get('description'),
                quantity=item_data.get('quantity'),
                unit=item_data.get('unit'),
                unit_price=item_data.get('unit_price'),
                condition=item_data.get('condition'),
                notes=item_data.get('notes')
            )
            db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'Sales return created successfully', 'return': ret.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@sales_bp.route('/returns/<int:return_id>', methods=['PUT'])
def update_sales_return(return_id):
    """Update a sales return."""
    ret = SalesReturn.query.get_or_404(return_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(ret, key):
                setattr(ret, key, value)
        db.session.commit()
        return jsonify({'message': 'Sales return updated successfully', 'return': ret.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400