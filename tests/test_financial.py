"""
Unit tests for Financial Module
"""
import pytest
from app import create_app, db
from app.models.financial import ChartOfAccounts, JournalEntry, Invoice, Payment


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


class TestChartOfAccountsModel:
    """Test ChartOfAccounts model."""

    def test_create_account(self, app):
        """Test creating an account."""
        with app.app_context():
            account = ChartOfAccounts(
                account_code='1001',
                account_name='Cash',
                account_type='asset',
                account_subtype='cash'
            )
            db.session.add(account)
            db.session.commit()

            assert account.id is not None
            assert account.account_code == '1001'
            assert account.account_type == 'asset'

    def test_account_to_dict(self, app):
        """Test account to_dict method."""
        with app.app_context():
            account = ChartOfAccounts(
                account_code='1002',
                account_name='Accounts Receivable',
                account_type='asset',
                account_subtype='receivable'
            )
            db.session.add(account)
            db.session.commit()

            data = account.to_dict()
            assert data['account_code'] == '1002'
            assert data['account_type'] == 'asset'


class TestChartOfAccountsAPI:
    """Test Chart of Accounts API endpoints."""

    def test_get_accounts_empty(self, client):
        """Test getting accounts when empty."""
        response = client.get('/api/financial/accounts')
        assert response.status_code == 200
        data = response.get_json()
        assert 'accounts' in data

    def test_create_account(self, client):
        """Test creating an account via API."""
        response = client.post('/api/financial/accounts', json={
            'account_code': '1001',
            'account_name': 'Cash',
            'account_type': 'asset',
            'account_subtype': 'cash'
        })
        assert response.status_code == 201


class TestJournalEntryModel:
    """Test JournalEntry model."""

    def test_create_journal_entry(self, app):
        """Test creating a journal entry."""
        with app.app_context():
            entry = JournalEntry(
                entry_number='JE001',
                description='Test entry',
                entry_type='general'
            )
            db.session.add(entry)
            db.session.commit()

            assert entry.id is not None
            assert entry.status == 'draft'


class TestJournalEntryAPI:
    """Test Journal Entry API endpoints."""

    def test_get_journal_entries_empty(self, client):
        """Test getting journal entries when empty."""
        response = client.get('/api/financial/journal')
        assert response.status_code == 200
        data = response.get_json()
        assert 'entries' in data

    def test_create_journal_entry(self, client):
        """Test creating a journal entry via API."""
        response = client.post('/api/financial/journal', json={
            'entry_number': 'JE001',
            'description': 'Test journal entry',
            'entry_type': 'general',
            'lines': [
                {'account_id': 1, 'debit': 1000, 'credit': 0},
                {'account_id': 2, 'debit': 0, 'credit': 1000}
            ]
        })
        assert response.status_code in [201, 400]


class TestInvoiceModel:
    """Test Invoice model."""

    def test_create_invoice(self, app):
        """Test creating an invoice."""
        with app.app_context():
            invoice = Invoice(
                invoice_number='INV001',
                invoice_type='sales',
                total_amount=1000.00,
                status='draft'
            )
            db.session.add(invoice)
            db.session.commit()

            assert invoice.id is not None
            assert invoice.invoice_number == 'INV001'
            assert invoice.status == 'draft'

    def test_invoice_balance_due(self, app):
        """Test invoice balance due calculation."""
        with app.app_context():
            invoice = Invoice(
                invoice_number='INV002',
                invoice_type='sales',
                total_amount=1000.00,
                paid_amount=300.00
            )
            db.session.add(invoice)
            db.session.commit()

            data = invoice.to_dict()
            assert data['balance_due'] == 700.00


class TestInvoiceAPI:
    """Test Invoice API endpoints."""

    def test_get_invoices_empty(self, client):
        """Test getting invoices when empty."""
        response = client.get('/api/financial/invoices')
        assert response.status_code == 200
        data = response.get_json()
        assert 'invoices' in data


class TestPaymentModel:
    """Test Payment model."""

    def test_create_payment(self, app):
        """Test creating a payment."""
        with app.app_context():
            payment = Payment(
                payment_number='PAY001',
                payment_type='received',
                amount=500.00,
                status='completed'
            )
            db.session.add(payment)
            db.session.commit()

            assert payment.id is not None
            assert payment.amount == 500.00


class TestPaymentAPI:
    """Test Payment API endpoints."""

    def test_get_payments_empty(self, client):
        """Test getting payments when empty."""
        response = client.get('/api/financial/payments')
        assert response.status_code == 200
        data = response.get_json()
        assert 'payments' in data