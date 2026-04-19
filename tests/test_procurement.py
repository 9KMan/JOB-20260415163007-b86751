"""
Unit tests for Procurement Module
"""
import pytest
from app import create_app, db
from app.models.procurement import Supplier, PurchaseOrder, PriceList


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


class TestSupplierModel:
    """Test Supplier model."""

    def test_create_supplier(self, app):
        """Test creating a supplier."""
        with app.app_context():
            supplier = Supplier(
                code='SUP001',
                name='Test Supplier',
                contact_person='John Doe',
                email='john@test.com',
                phone='1234567890',
                rating=5
            )
            db.session.add(supplier)
            db.session.commit()

            assert supplier.id is not None
            assert supplier.code == 'SUP001'
            assert supplier.name == 'Test Supplier'
            assert supplier.rating == 5
            assert supplier.is_active is True

    def test_supplier_to_dict(self, app):
        """Test supplier to_dict method."""
        with app.app_context():
            supplier = Supplier(
                code='SUP002',
                name='Test Supplier 2',
                email='test@test.com'
            )
            db.session.add(supplier)
            db.session.commit()

            data = supplier.to_dict()
            assert data['code'] == 'SUP002'
            assert data['name'] == 'Test Supplier 2'
            assert data['email'] == 'test@test.com'


class TestSupplierAPI:
    """Test Supplier API endpoints."""

    def test_get_suppliers_empty(self, client):
        """Test getting suppliers when none exist."""
        response = client.get('/api/procurement/suppliers')
        assert response.status_code == 200
        data = response.get_json()
        assert 'suppliers' in data
        assert len(data['suppliers']) == 0

    def test_create_supplier(self, client):
        """Test creating a supplier via API."""
        response = client.post('/api/procurement/suppliers', json={
            'code': 'SUP001',
            'name': 'Test Supplier',
            'contact_person': 'John Doe',
            'email': 'john@test.com'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['supplier']['code'] == 'SUP001'

    def test_get_supplier(self, client):
        """Test getting a single supplier."""
        # Create supplier first
        client.post('/api/procurement/suppliers', json={
            'code': 'SUP002',
            'name': 'Test Supplier 2'
        })

        response = client.get('/api/procurement/suppliers/1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['supplier']['code'] == 'SUP002'


class TestPurchaseOrderModel:
    """Test PurchaseOrder model."""

    def test_create_purchase_order(self, app):
        """Test creating a purchase order."""
        with app.app_context():
            supplier = Supplier(code='SUP001', name='Test Supplier')
            db.session.add(supplier)
            db.session.commit()

            order = PurchaseOrder(
                order_number='PO001',
                supplier_id=supplier.id,
                status='draft'
            )
            db.session.add(order)
            db.session.commit()

            assert order.id is not None
            assert order.order_number == 'PO001'
            assert order.status == 'draft'
            assert order.supplier.name == 'Test Supplier'


class TestPurchaseOrderAPI:
    """Test PurchaseOrder API endpoints."""

    def test_get_orders_empty(self, client):
        """Test getting orders when none exist."""
        response = client.get('/api/procurement/orders')
        assert response.status_code == 200
        data = response.get_json()
        assert 'orders' in data

    def test_create_order_requires_supplier(self, client):
        """Test that creating order without supplier fails."""
        response = client.post('/api/procurement/orders', json={
            'order_number': 'PO001'
        })
        assert response.status_code == 400


class TestPriceListModel:
    """Test PriceList model."""

    def test_create_price_list(self, app):
        """Test creating a price list entry."""
        with app.app_context():
            supplier = Supplier(code='SUP001', name='Test Supplier')
            db.session.add(supplier)
            db.session.commit()

            price_list = PriceList(
                supplier_id=supplier.id,
                product_code='PROD001',
                unit_price=100.00,
                currency='USD'
            )
            db.session.add(price_list)
            db.session.commit()

            assert price_list.id is not None
            assert price_list.unit_price == 100.00
            assert price_list.is_active is True