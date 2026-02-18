// Admin panel functionality

// Use window.API_BASE_URL (set by auth.js which loads first)
// No const declaration here to avoid redeclaration error
let currentPage = 1;
let pageSize = 50;
let totalOrders = 0;
let currentFilters = {};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    if (authManager.isAuthenticated() && authManager.isAdmin()) {
        showAdminDashboard();
    } else {
        showAdminLogin();
    }
    
    // Setup login form
    const loginForm = document.getElementById('adminLoginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleAdminLogin);
    }
});

// Show admin login
function showAdminLogin() {
    document.getElementById('adminLogin').style.display = 'block';
    document.getElementById('adminDashboard').style.display = 'none';
}

// Show admin dashboard
function showAdminDashboard() {
    document.getElementById('adminLogin').style.display = 'none';
    document.getElementById('adminDashboard').style.display = 'block';
    loadAdminStats();
    loadAdminOrders();
}

// Handle admin login
async function handleAdminLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('adminEmail').value;
    const password = document.getElementById('adminPassword').value;
    const errorDiv = document.getElementById('adminLoginError');
    
    try {
        await authManager.adminLogin(email, password);
        showAdminDashboard();
    } catch (error) {
        errorDiv.textContent = error.message || 'Login failed';
        errorDiv.style.display = 'block';
    }
}

// Load admin stats
async function loadAdminStats() {
    try {
        const response = await fetch(`${window.API_BASE_URL}/api/v1/admin/stats`, {
            headers: authManager.getAuthHeaders()
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                authManager.clearAuth();
                showAdminLogin();
                return;
            }
            throw new Error('Failed to load stats');
        }
        
        const stats = await response.json();
        
        document.getElementById('statTotalOrders').textContent = stats.total_orders || 0;
        document.getElementById('statRevenue').textContent = `₹${(stats.total_revenue || 0).toFixed(2)}`;
        document.getElementById('statCompleted').textContent = stats.orders_by_status?.completed || 0;
        document.getElementById('statProcessing').textContent = stats.orders_by_status?.processing || 0;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load admin orders
async function loadAdminOrders() {
    const tbody = document.getElementById('ordersTableBody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading">Loading orders...</td></tr>';
    
    // Get filters
    const status = document.getElementById('filterStatus')?.value || '';
    const userId = document.getElementById('filterUserId')?.value || '';
    
    currentFilters = {
        status: status || undefined,
        user_id: userId ? parseInt(userId) : undefined
    };
    
    try {
        const params = new URLSearchParams({
            limit: pageSize,
            offset: (currentPage - 1) * pageSize
        });
        
        if (currentFilters.status) params.append('status', currentFilters.status);
        if (currentFilters.user_id) params.append('user_id', currentFilters.user_id);
        
        const response = await fetch(`${window.API_BASE_URL}/api/v1/admin/orders?${params}`, {
            headers: authManager.getAuthHeaders()
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                authManager.clearAuth();
                showAdminLogin();
                return;
            }
            throw new Error('Failed to load orders');
        }
        
        const data = await response.json();
        totalOrders = data.total || 0;
        
        if (data.orders.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No orders found</td></tr>';
        } else {
            tbody.innerHTML = data.orders.map(order => createOrderRow(order)).join('');
            
            // Add click handlers
            data.orders.forEach(order => {
                const viewBtn = document.getElementById(`viewOrder_${order.id}`);
                if (viewBtn) {
                    viewBtn.addEventListener('click', () => viewOrderDetails(order.id));
                }
                
                const retryBtn = document.getElementById(`retryOrder_${order.id}`);
                if (retryBtn) {
                    retryBtn.addEventListener('click', () => retryAnalysis(order.id));
                }
                
                const refundBtn = document.getElementById(`refundOrder_${order.id}`);
                if (refundBtn) {
                    refundBtn.addEventListener('click', () => processRefund(order.id));
                }
            });
        }
        
        updatePagination();
        
    } catch (error) {
        console.error('Error loading orders:', error);
        tbody.innerHTML = '<tr><td colspan="6" class="error-state">Failed to load orders</td></tr>';
    }
}

// Create order row
function createOrderRow(order) {
    const date = new Date(order.created_at).toLocaleString();
    const statusClass = getStatusClass(order.status);
    const orderType = order.type || 'full_report';
    const typeBadge = orderType === 'query' 
        ? '<span class="type-badge type-query">Query</span>' 
        : '<span class="type-badge type-full-report">Full Report</span>';
    
    // Determine which action buttons to show
    // Only show retry for full_report type orders (not for query)
    const canRetry = orderType === 'full_report' && 
                     (order.status === 'failed' || order.status === 'completed') && 
                     order.payment && order.payment.status === 'success';
    const canRefund = order.status === 'completed' && 
                      order.payment && order.payment.status === 'success' && 
                      !order.payment.razorpay_refund_id;
    
    // Create button group with consistent styling
    let actionButtons = `<div class="action-buttons">`;
    actionButtons += `<button class="btn-action btn-view" id="viewOrder_${order.id}">View</button>`;
    
    if (canRetry) {
        actionButtons += `<button class="btn-action btn-retry" id="retryOrder_${order.id}">Re-trigger</button>`;
    }
    if (canRefund) {
        actionButtons += `<button class="btn-action btn-refund" id="refundOrder_${order.id}">Refund</button>`;
    }
    actionButtons += `</div>`;
    
    return `
        <tr>
            <td>#${order.id} ${typeBadge}</td>
            <td>${order.user_email || `User ${order.user_id}`}</td>
            <td>₹${order.amount.toFixed(2)}</td>
            <td><span class="status-badge ${statusClass}">${order.status}</span></td>
            <td>${date}</td>
            <td>
                ${actionButtons}
            </td>
        </tr>
    `;
}

// Get status class
function getStatusClass(status) {
    const map = {
        'payment_pending': 'status-pending',
        'processing': 'status-processing',
        'completed': 'status-completed',
        'failed': 'status-failed',
        'refunded': 'status-refunded'
    };
    return map[status] || 'status-pending';
}

// View order details
async function viewOrderDetails(orderId) {
    try {
        const response = await fetch(`${window.API_BASE_URL}/api/v1/admin/orders/${orderId}`, {
            headers: authManager.getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to load order details');
        }
        
        const order = await response.json();
        displayOrderDetails(order);
        
    } catch (error) {
        console.error('Error loading order details:', error);
        showNotification('Failed to load order details', 'error');
    }
}

// Display order details
function displayOrderDetails(order) {
    const modal = document.getElementById('orderModal');
    const details = document.getElementById('orderDetails');
    
    const birthDetails = order.birth_details ? JSON.stringify(order.birth_details, null, 2) : 'N/A';
    const analysisData = order.analysis_data ? JSON.stringify(order.analysis_data, null, 2) : 'N/A';
    
    // Determine which action buttons to show
    // Only show retry for full_report type orders (not for query)
    const canRetry = orderType === 'full_report' && 
                     (order.status === 'failed' || order.status === 'completed') && 
                     order.payment && order.payment.status === 'success';
    const canRefund = order.status === 'completed' && 
                      order.payment && order.payment.status === 'success' && 
                      !order.payment.razorpay_refund_id;
    
    // Create button group with consistent styling
    let actionButtons = '';
    if (canRetry || canRefund) {
        actionButtons += `<div class="action-buttons" style="margin-top: 16px; display: flex; gap: 12px;">`;
        if (canRetry) {
            actionButtons += `<button class="btn-action btn-retry" onclick="retryAnalysis(${order.id}); closeOrderModal();">Re-trigger Analysis</button>`;
        }
        if (canRefund) {
            actionButtons += `<button class="btn-action btn-refund" onclick="processRefund(${order.id}); closeOrderModal();">Process Refund</button>`;
        }
        actionButtons += `</div>`;
    }
    
    const orderType = order.type || 'full_report';
    const typeBadge = orderType === 'query' 
        ? '<span class="type-badge type-query">Query</span>' 
        : '<span class="type-badge type-full-report">Full Report</span>';
    
    details.innerHTML = `
        <div class="order-detail-section">
            <h3>Order Information</h3>
            <p><strong>Order ID:</strong> ${order.id} ${typeBadge}</p>
            <p><strong>Type:</strong> ${orderType}</p>
            <p><strong>Status:</strong> ${order.status}</p>
            <p><strong>Amount:</strong> ₹${order.amount.toFixed(2)}</p>
            <p><strong>Created:</strong> ${new Date(order.created_at).toLocaleString()}</p>
            <p><strong>Updated:</strong> ${new Date(order.updated_at).toLocaleString()}</p>
            ${actionButtons ? `<div style="margin-top: 16px;">${actionButtons}</div>` : ''}
        </div>
        
        <div class="order-detail-section">
            <h3>User Information</h3>
            ${order.user ? `
                <p><strong>Name:</strong> ${order.user.name}</p>
                <p><strong>Email:</strong> ${order.user.email}</p>
                <p><strong>User ID:</strong> ${order.user.id}</p>
            ` : '<p>User information not available</p>'}
        </div>
        
        <div class="order-detail-section">
            <h3>Payment Information</h3>
            ${order.payment ? `
                <p><strong>Payment ID:</strong> ${order.payment.id}</p>
                <p><strong>Razorpay Order ID:</strong> ${order.payment.razorpay_order_id || 'N/A'}</p>
                <p><strong>Razorpay Payment ID:</strong> ${order.payment.razorpay_payment_id || 'N/A'}</p>
                <p><strong>Status:</strong> ${order.payment.status}</p>
                <p><strong>Method:</strong> ${order.payment.payment_method || 'N/A'}</p>
                ${order.payment.razorpay_refund_id ? `
                    <p><strong>Refund ID:</strong> ${order.payment.razorpay_refund_id}</p>
                    <p><strong>Refund Amount:</strong> ₹${(order.payment.refund_amount || 0).toFixed(2)}</p>
                    <p><strong>Refund Status:</strong> ${order.payment.refund_status || 'N/A'}</p>
                ` : ''}
            ` : '<p>Payment information not available</p>'}
        </div>
        
        <div class="order-detail-section">
            <h3>Birth Details</h3>
            <pre>${birthDetails}</pre>
        </div>
        
        ${order.analysis_data ? `
        <div class="order-detail-section">
            <h3>Analysis Data</h3>
            <pre>${analysisData}</pre>
        </div>
        ` : ''}
        
        ${order.error_reason ? `
        <div class="order-detail-section">
            <h3>Error Reason</h3>
            <p class="error-text">${order.error_reason}</p>
        </div>
        ` : ''}
    `;
    
    modal.style.display = 'block';
}

// Close order modal
function closeOrderModal() {
    document.getElementById('orderModal').style.display = 'none';
}

// Change page
function changePage(delta) {
    const newPage = currentPage + delta;
    const totalPages = Math.ceil(totalOrders / pageSize);
    
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        loadAdminOrders();
    }
}

// Update pagination
function updatePagination() {
    const totalPages = Math.ceil(totalOrders / pageSize);
    document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${totalPages}`;
    
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage >= totalPages;
}

// Reset filters
function resetFilters() {
    document.getElementById('filterStatus').value = '';
    document.getElementById('filterUserId').value = '';
    currentPage = 1;
    loadAdminOrders();
}

// Retry analysis
async function retryAnalysis(orderId) {
    if (!confirm(`Are you sure you want to re-trigger analysis for order #${orderId}?`)) {
        return;
    }
    
    try {
        showNotification('Re-triggering analysis...', 'info');
        
        const response = await fetch(`${window.API_BASE_URL}/api/v1/admin/orders/${orderId}/retry-analysis`, {
            method: 'POST',
            headers: authManager.getAuthHeaders()
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to re-trigger analysis');
        }
        
        const result = await response.json();
        showNotification('Analysis re-triggered successfully', 'success');
        
        // Reload orders to show updated status
        loadAdminOrders();
        loadAdminStats();
        
    } catch (error) {
        console.error('Error retrying analysis:', error);
        showNotification(error.message || 'Failed to re-trigger analysis', 'error');
    }
}

// Process refund
async function processRefund(orderId) {
    if (!confirm(`Are you sure you want to process a refund for order #${orderId}? This action cannot be undone.`)) {
        return;
    }
    
    try {
        showNotification('Processing refund...', 'info');
        
        const response = await fetch(`${window.API_BASE_URL}/api/v1/admin/orders/${orderId}/refund`, {
            method: 'POST',
            headers: authManager.getAuthHeaders()
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to process refund');
        }
        
        const result = await response.json();
        showNotification(`Refund processed successfully. Refund ID: ${result.refund_id}`, 'success');
        
        // Reload orders to show updated status
        loadAdminOrders();
        loadAdminStats();
        
    } catch (error) {
        console.error('Error processing refund:', error);
        showNotification(error.message || 'Failed to process refund', 'error');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 100);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

