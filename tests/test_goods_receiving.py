"""
Unit tests for Goods Receiving Module
"""
import pytest
from app import create_app, db
from app.models.goods_receiving import GoodsReceivingNote, Inspection, WarehouseAllocation
from app.models.procurement import Supplier


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


class TestGRNModel:
    """Test Goods Receiving Note model."""

    def test_create_grn(self, app):
        """Test creating a GRN."""
        with app.app_context():
            supplier = Supplier(code='SUP001', name='Test Supplier')
            db.session.add(supplier)
            db.session.commit()

            grn = GoodsReceivingNote(
                grn_number='GRN001',
                supplier_id=supplier.id,
                received_by='Admin User',
                status='pending'
            )
            db.session.add(grn)
            db.session.commit()

            assert grn.id is not None
            assert grn.grn_number == 'GRN001'
            assert grn.status == 'pending'

    def test_grn_to_dict(self, app):
        """Test GRN to_dict method."""
        with app.app_context():
            supplier = Supplier(code='SUP001', name='Test Supplier')
            db.session.add(supplier)
            db.session.commit()

            grn = GoodsReceivingNote(
                grn_number='GRN002',
                supplier_id=supplier.id,
                received_by='Admin'
            )
            db.session.add(grn)
            db.session.commit()

            data = grn.to_dict()
            assert data['grn_number'] == 'GRN002'
            assert data['supplier_name'] == 'Test Supplier'


class TestGRNAPI:
    """Test GRN API endpoints."""

    def test_get_grn_list_empty(self, client):
        """Test getting GRN list when empty."""
        response = client.get('/api/goods-receiving/grn')
        assert response.status_code == 200
        data = response.get_json()
        assert 'grn_notes' in data

    def test_create_grn(self, client):
        """Test creating a GRN via API."""
        response = client.post('/api/goods-receiving/grn', json={
            'grn_number': 'GRN001',
            'received_by': 'Admin User',
            'status': 'pending',
            'items': [{
                'product_code': 'PROD001',
                'expected_quantity': 100,
                'received_quantity': 100
            }]
        })
        assert response.status_code == 201


class TestInspectionModel:
    """Test Inspection model."""

    def test_create_inspection(self, app):
        """Test creating an inspection."""
        with app.app_context():
            supplier = Supplier(code='SUP001', name='Test Supplier')
            db.session.add(supplier)
            db.session.commit()

            grn = GoodsReceivingNote(
                grn_number='GRN001',
                supplier_id=supplier.id,
                received_by='Admin'
            )
            db.session.add(grn)
            db.session.commit()

            inspection = Inspection(
                grn_id=grn.id,
                inspector_name='QA User',
                inspection_type='full',
                result='pass'
            )
            db.session.add(inspection)
            db.session.commit()

            assert inspection.id is not None
            assert inspection.result == 'pass'


class TestWarehouseAllocation:
    """Test Warehouse Allocation model."""

    def test_create_allocation(self, app):
        """Test creating warehouse allocation."""
        with app.app_context():
            supplier = Supplier(code='SUP001', name='Test Supplier')
            db.session.add(supplier)
            db.session.commit()

            grn = GoodsReceivingNote(
                grn_number='GRN001',
                supplier_id=supplier.id,
                received_by='Admin'
            )
            db.session.add(grn)
            db.session.flush()

            from app.models.goods_receiving import GoodsReceivingNoteItem
            grn_item = GoodsReceivingNoteItem(
                grn_id=grn.id,
                product_code='PROD001',
                expected_quantity=100,
                received_quantity=100
            )
            db.session.add(grn_item)
            db.session.commit()

            allocation = WarehouseAllocation(
                grn_item_id=grn_item.id,
                warehouse_location='WH-A-01',
                zone='A',
                rack='01',
                bin='01',
                quantity=100
            )
            db.session.add(allocation)
            db.session.commit()

            assert allocation.id is not None
            assert allocation.warehouse_location == 'WH-A-01'