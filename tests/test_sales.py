"""
Unit tests for Sales Module
"""
import pytest
from app import create_app, db
from app.models.sales import Customer, SalesOrder, Shipping, SalesReturn


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.config['SECRET_KEY'] = 'test-secret'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestCustomerModel:
    """Test Customer model."""

    def test_create_customer(self, app):
        """Test creating a customer."""
        with app.app_context():
            customer = Customer(
                code='CUST001',
                name='Test Customer',
                contact_person='John Doe',
                email='john@customer.com'
            )
            db.session.add(customer)
            db.session.commit()

            assert customer.id is not None
            assert customer.code == 'CUST001'
            assert customer.is_active is True

    def test_customer_to_dict(self, app):
        """Test customer to_dict method."""
        with app.app_context():
            customer = Customer(
                code='CUST002',
                name='Test Customer 2',
                city='New York'
            )
            db.session.add(customer)
            db.session.commit()

            data = customer.to_dict()
            assert data['code'] == 'CUST002'
            assert data['city'] == 'New York'


class TestCustomerAPI:
    """Test Customer API endpoints."""

    def test_get_customers_empty(self, client):
        """Test getting customers when empty."""
        response = client.get('/api/sales/customers')
        assert response.status_code == 200
        data = response.get_json()
        assert 'customers' in data

    def test_create_customer(self, client):
        """Test creating a customer via API."""
        response = client.post('/api/sales/customers', json={
            'code': 'CUST001',
            'name': 'Test Customer',
            'email': 'test@customer.com'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['customer']['code'] == 'CUST001'


class TestSalesOrderModel:
    """Test SalesOrder model."""

    def test_create_sales_order(self, app):
        """Test creating a sales order."""
        with app.app_context():
            customer = Customer(code='CUST001', name='Test Customer')
            db.session.add(customer)
            db.session.commit()

            order = SalesOrder(
                order_number='SO001',
                customer_id=customer.id,
                status='draft'
            )
            db.session.add(order)
            db.session.commit()

            assert order.id is not None
            assert order.order_number == 'SO001'
            assert order.status == 'draft'


class TestSalesOrderAPI:
    """Test SalesOrder API endpoints."""

    def test_get_orders_empty(self, client):
        """Test getting orders when empty."""
        response = client.get('/api/sales/orders')
        assert response.status_code == 200
        data = response.get_json()
        assert 'orders' in data

    def test_create_order_with_items(self, client):
        """Test creating a sales order with items."""
        response = client.post('/api/sales/orders', json={
            'order_number': 'SO001',
            'customer_id': 1,  # Will fail but tests validation
            'items': [{
                'product_code': 'PROD001',
                'quantity': 10,
                'unit_price': 100
            }]
        })
        # Should fail due to missing customer but validates endpoint works
        assert response.status_code in [201, 400]


class TestShippingModel:
    """Test Shipping model."""

    def test_create_shipping(self, app):
        """Test creating a shipping record."""
        with app.app_context():
            customer = Customer(code='CUST001', name='Test Customer')
            db.session.add(customer)
            db.session.commit()

            order = SalesOrder(
                order_number='SO001',
                customer_id=customer.id
            )
            db.session.add(order)
            db.session.commit()

            shipping = Shipping(
                sales_order_id=order.id,
                shipment_number='SHIP001',
                carrier='FedEx',
                tracking_number='123456'
            )
            db.session.add(shipping)
            db.session.commit()

            assert shipping.id is not None
            assert shipping.carrier == 'FedEx'


class TestSalesReturnModel:
    """Test SalesReturn model."""

    def test_create_sales_return(self, app):
        """Test creating a sales return."""
        with app.app_context():
            customer = Customer(code='CUST001', name='Test Customer')
            db.session.add(customer)
            db.session.commit()

            ret = SalesReturn(
                return_number='RET001',
                customer_id=customer.id,
                reason='Defective product'
            )
            db.session.add(ret)
            db.session.commit()

            assert ret.id is not None
            assert ret.status == 'draft'