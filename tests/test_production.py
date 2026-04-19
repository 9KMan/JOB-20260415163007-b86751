"""
Unit tests for Production Module
"""
import pytest
from app import create_app, db
from app.models.production import BillOfMaterials, WorkOrder, ProductionSchedule


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


class TestBOMModel:
    """Test Bill of Materials model."""

    def test_create_bom(self, app):
        """Test creating a BOM."""
        with app.app_context():
            bom = BillOfMaterials(
                bom_code='BOM001',
                product_code='FINISHED001',
                description='Finished Product BOM',
                version='1.0'
            )
            db.session.add(bom)
            db.session.commit()

            assert bom.id is not None
            assert bom.bom_code == 'BOM001'
            assert bom.is_active is True

    def test_bom_to_dict(self, app):
        """Test BOM to_dict method."""
        with app.app_context():
            bom = BillOfMaterials(
                bom_code='BOM002',
                product_code='PROD002',
                description='Test BOM'
            )
            db.session.add(bom)
            db.session.commit()

            data = bom.to_dict()
            assert data['bom_code'] == 'BOM002'
            assert data['product_code'] == 'PROD002'


class TestBOMAPI:
    """Test BOM API endpoints."""

    def test_get_bom_list_empty(self, client):
        """Test getting BOM list when empty."""
        response = client.get('/api/production/bom')
        assert response.status_code == 200
        data = response.get_json()
        assert 'bom_list' in data

    def test_create_bom(self, client):
        """Test creating a BOM via API."""
        response = client.post('/api/production/bom', json={
            'bom_code': 'BOM001',
            'product_code': 'FINISHED001',
            'description': 'Test BOM',
            'items': [{
                'product_code': 'RAW001',
                'quantity_required': 10,
                'unit': 'KG'
            }]
        })
        assert response.status_code == 201


class TestWorkOrderModel:
    """Test Work Order model."""

    def test_create_work_order(self, app):
        """Test creating a work order."""
        with app.app_context():
            bom = BillOfMaterials(
                bom_code='BOM001',
                product_code='FINISHED001'
            )
            db.session.add(bom)
            db.session.commit()

            order = WorkOrder(
                work_order_number='WO001',
                bom_id=bom.id,
                product_code='FINISHED001',
                quantity=100,
                status='planned'
            )
            db.session.add(order)
            db.session.commit()

            assert order.id is not None
            assert order.work_order_number == 'WO001'
            assert order.status == 'planned'


class TestWorkOrderAPI:
    """Test Work Order API endpoints."""

    def test_get_work_orders_empty(self, client):
        """Test getting work orders when empty."""
        response = client.get('/api/production/work-orders')
        assert response.status_code == 200
        data = response.get_json()
        assert 'work_orders' in data

    def test_create_work_order(self, client):
        """Test creating a work order via API."""
        response = client.post('/api/production/work-orders', json={
            'work_order_number': 'WO001',
            'product_code': 'FINISHED001',
            'quantity': 100,
            'status': 'planned'
        })
        assert response.status_code == 201

    def test_start_work_order(self, client):
        """Test starting a work order."""
        # Create work order first
        client.post('/api/production/work-orders', json={
            'work_order_number': 'WO002',
            'product_code': 'FINISHED001',
            'quantity': 50
        })

        response = client.post('/api/production/work-orders/1/start')
        assert response.status_code == 200
        data = response.get_json()
        assert data['work_order']['status'] == 'in_progress'


class TestProductionSchedule:
    """Test Production Schedule model."""

    def test_create_schedule(self, app):
        """Test creating a production schedule."""
        with app.app_context():
            schedule = ProductionSchedule(
                schedule_code='SCH001',
                period_start='2024-01-01',
                period_end='2024-01-31',
                status='draft'
            )
            db.session.add(schedule)
            db.session.commit()

            assert schedule.id is not None
            assert schedule.status == 'draft'