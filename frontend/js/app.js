// ERP System Frontend JavaScript
const API_BASE = '/api';

// State Management
const state = {
    suppliers: [],
    customers: [],
    purchaseOrders: [],
    salesOrders: [],
    workOrders: [],
    accounts: []
};

// Navigation
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const module = e.target.dataset.module;

        // Update active nav
        document.querySelectorAll('.nav-menu a').forEach(l => l.classList.remove('active'));
        e.target.classList.add('active');

        // Update active content
        document.querySelectorAll('.module-content').forEach(c => c.classList.remove('active'));
        document.getElementById(module).classList.add('active');

        // Update title
        document.getElementById('module-title').textContent = e.target.textContent;

        // Load module data
        loadModuleData(module);
    });
});

// Mobile Menu Toggle
document.getElementById('menu-toggle').addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('open');
});

// Modal Functions
function showModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
    document.getElementById('modal-overlay').style.display = 'block';
}

function hideModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.getElementById('modal-overlay').style.display = 'none';
}

document.getElementById('modal-overlay').addEventListener('click', () => {
    document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
    document.getElementById('modal-overlay').style.display = 'none';
});

// Load Module Data
async function loadModuleData(module) {
    switch(module) {
        case 'dashboard':
            await loadDashboard();
            break;
        case 'procurement':
            await loadSuppliers();
            break;
        case 'sales':
            await loadCustomers();
            break;
        case 'financial':
            await loadAccounts();
            break;
        case 'production':
            await loadWorkOrders();
            break;
    }
}

// Dashboard
async function loadDashboard() {
    try {
        const [suppliersRes, poRes, soRes, woRes, plRes] = await Promise.all([
            fetch(`${API_BASE}/procurement/suppliers`),
            fetch(`${API_BASE}/procurement/orders`),
            fetch(`${API_BASE}/sales/orders`),
            fetch(`${API_BASE}/production/work-orders`),
            fetch(`${API_BASE}/financial/reports/profit-loss`)
        ]);

        const suppliers = await suppliersRes.json();
        const purchaseOrders = await poRes.json();
        const salesOrders = await soRes.json();
        const workOrders = await woRes.json();
        const profitLoss = await plRes.json();

        document.getElementById('metric-suppliers').textContent = suppliers.suppliers?.length || 0;
        document.getElementById('metric-purchase-orders').textContent = purchaseOrders.orders?.length || 0;
        document.getElementById('metric-sales-orders').textContent = salesOrders.orders?.length || 0;
        document.getElementById('metric-work-orders').textContent = workOrders.work_orders?.length || 0;
        document.getElementById('metric-revenue').textContent = `$${(profitLoss.revenue || 0).toLocaleString()}`;
        document.getElementById('metric-expenses').textContent = `$${(profitLoss.expenses || 0).toLocaleString()}`;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Suppliers
async function loadSuppliers() {
    try {
        const res = await fetch(`${API_BASE}/procurement/suppliers`);
        const data = await res.json();
        state.suppliers = data.suppliers || [];
        renderTable('suppliers-tbody', state.suppliers, ['code', 'name', 'contact_person', 'email', 'rating'], ['code', 'name', 'contact', 'email', 'rating']);
    } catch (error) {
        console.error('Error loading suppliers:', error);
    }
}

document.getElementById('supplier-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);

    try {
        const res = await fetch(`${API_BASE}/procurement/suppliers`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (res.ok) {
            hideModal('supplier-modal');
            e.target.reset();
            await loadSuppliers();
        }
    } catch (error) {
        console.error('Error saving supplier:', error);
    }
});

// Customers
async function loadCustomers() {
    try {
        const res = await fetch(`${API_BASE}/sales/customers`);
        const data = await res.json();
        state.customers = data.customers || [];
        renderTable('customers-tbody', state.customers, ['code', 'name', 'contact_person', 'email', 'city'], ['code', 'name', 'contact', 'email', 'city']);
    } catch (error) {
        console.error('Error loading customers:', error);
    }
}

document.getElementById('customer-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);

    try {
        const res = await fetch(`${API_BASE}/sales/customers`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (res.ok) {
            hideModal('customer-modal');
            e.target.reset();
            await loadCustomers();
        }
    } catch (error) {
        console.error('Error saving customer:', error);
    }
});

// Chart of Accounts
async function loadAccounts() {
    try {
        const res = await fetch(`${API_BASE}/financial/accounts`);
        const data = await res.json();
        state.accounts = data.accounts || [];
        renderTable('accounts-tbody', state.accounts, ['account_code', 'account_name', 'account_type', 'account_subtype'], ['code', 'name', 'type', 'subtype']);
    } catch (error) {
        console.error('Error loading accounts:', error);
    }
}

// Work Orders
async function loadWorkOrders() {
    try {
        const res = await fetch(`${API_BASE}/production/work-orders`);
        const data = await res.json();
        state.workOrders = data.work_orders || [];
        renderTable('work-orders-tbody', state.workOrders, ['work_order_number', 'product_code', 'quantity', 'status', 'priority'], ['order', 'product', 'qty', 'status', 'priority']);
    } catch (error) {
        console.error('Error loading work orders:', error);
    }
}

// GRN
async function loadGRN() {
    try {
        const res = await fetch(`${API_BASE}/goods-receiving/grn`);
        const data = await res.json();
        const grns = data.grn_notes || [];
        renderTable('grn-tbody', grns, ['grn_number', 'supplier_name', 'received_date', 'received_by', 'status'], ['grn', 'supplier', 'date', 'received by', 'status']);
    } catch (error) {
        console.error('Error loading GRN:', error);
    }
}

// Packaging Orders
async function loadPackagingOrders() {
    try {
        const res = await fetch(`${API_BASE}/packaging/orders`);
        const data = await res.json();
        const orders = data.orders || [];
        renderTable('packaging-tbody', orders, ['order_number', 'product_code', 'quantity_to_pack', 'status'], ['order', 'product', 'qty', 'status']);
    } catch (error) {
        console.error('Error loading packaging orders:', error);
    }
}

// Render Table Helper
function renderTable(tbodyId, data, fields, headers) {
    const tbody = document.getElementById(tbodyId);
    tbody.innerHTML = '';

    data.forEach(item => {
        const row = document.createElement('tr');
        fields.forEach(field => {
            const td = document.createElement('td');
            let value = item[field];
            if (field === 'quantity' || field === 'quantity_to_pack') {
                value = parseFloat(value).toFixed(2);
            }
            td.textContent = value || '-';
            row.appendChild(td);
        });

        // Actions cell
        const td = document.createElement('td');
        td.innerHTML = '<button class="btn btn-sm">View</button>';
        row.appendChild(td);

        tbody.appendChild(row);
    });
}

// Reports
async function loadReport(reportType) {
    const endpoint = {
        'sales-summary': '/reporting/sales/summary',
        'procurement-summary': '/reporting/procurement/summary',
        'production-efficiency': '/reporting/production/efficiency',
        'ar-aging': '/reporting/financial/ar-aging',
        'ap-aging': '/reporting/financial/ap-aging',
        'profit-loss': '/reporting/financial/profit-loss'
    }[reportType];

    if (!endpoint) return;

    try {
        const res = await fetch(`${API_BASE}${endpoint}`);
        const data = await res.json();
        console.log(`${reportType} report:`, data);
        alert(`${reportType} report loaded. Check console for details.`);
    } catch (error) {
        console.error('Error loading report:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

// Helper for select options
function getStatusClass(status) {
    const statusClasses = {
        'draft': 'bg-gray-100',
        'pending': 'bg-yellow-100',
        'confirmed': 'bg-blue-100',
        'in_progress': 'bg-blue-200',
        'completed': 'bg-green-100',
        'cancelled': 'bg-red-100',
        'sent': 'bg-orange-100',
        'paid': 'bg-green-100',
        'overdue': 'bg-red-100'
    };
    return statusClasses[status] || '';
}