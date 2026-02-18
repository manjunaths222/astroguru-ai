// Dashboard functionality

// Use window.API_BASE_URL (set by auth.js which loads first)
// No const declaration here to avoid redeclaration error

// Show dashboard
function showDashboard() {
    hideAllSections();
    document.getElementById('dashboardContainer').style.display = 'block';
    document.getElementById('navbar').style.display = 'block';
    document.getElementById('header').style.display = 'none';
    loadUserProfile();
    loadOrders();
}

// Load user profile
async function loadUserProfile() {
    try {
        // Always fetch fresh user info to ensure we have the latest data
        const user = await authManager.fetchUserInfo();
        if (user) {
            // Use name if available, otherwise use email prefix, fallback to "User"
            const displayName = user.name || (user.email ? user.email.split('@')[0] : 'User');
            
            const profileNameEl = document.getElementById('profileName');
            const userNameEl = document.getElementById('userName');
            const profileEmailEl = document.getElementById('profileEmail');
            
            if (profileNameEl) profileNameEl.textContent = displayName;
            if (userNameEl) userNameEl.textContent = displayName;
            if (profileEmailEl) profileEmailEl.textContent = user.email || '';
            
            if (user.picture_url) {
                const img = document.getElementById('userPicture');
                if (img) {
                    img.src = user.picture_url;
                    img.style.display = 'block';
                }
            }
        } else {
            // Fallback if fetch fails
            const storedUser = authManager.getCurrentUser();
            if (storedUser) {
                const displayName = storedUser.name || (storedUser.email ? storedUser.email.split('@')[0] : 'User');
                const profileNameEl = document.getElementById('profileName');
                const userNameEl = document.getElementById('userName');
                if (profileNameEl) profileNameEl.textContent = displayName;
                if (userNameEl) userNameEl.textContent = displayName;
            }
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
        // Fallback to stored user
        const storedUser = authManager.getCurrentUser();
        if (storedUser) {
            const displayName = storedUser.name || (storedUser.email ? storedUser.email.split('@')[0] : 'User');
            const profileNameEl = document.getElementById('profileName');
            const userNameEl = document.getElementById('userName');
            if (profileNameEl) profileNameEl.textContent = displayName;
            if (userNameEl) userNameEl.textContent = displayName;
        }
    }
}

// Load orders
async function loadOrders() {
    const chatQueriesList = document.getElementById('chatQueriesList');
    const fullReportsList = document.getElementById('fullReportsList');
    
    chatQueriesList.innerHTML = '<div class="loading">Loading chat queries...</div>';
    fullReportsList.innerHTML = '<div class="loading">Loading full reports...</div>';
    
    try {
        const response = await fetch(`${window.API_BASE_URL}/api/v1/orders`, {
            headers: authManager.getAuthHeaders()
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                authManager.clearAuth();
                showAuthRequired();
                return;
            }
            throw new Error('Failed to load orders');
        }
        
        const orders = await response.json();
        
        // Separate orders by type
        const chatQueries = orders.filter(order => order.type === 'query');
        const fullReports = orders.filter(order => order.type === 'full_report');
        
        // Display chat queries
        if (chatQueries.length === 0) {
            chatQueriesList.innerHTML = '<div class="empty-state">No chat queries yet. Create your first query!</div>';
        } else {
            chatQueriesList.innerHTML = chatQueries.map(order => createOrderCard(order)).join('');
            // Add event listeners for chat queries
            chatQueries.forEach(order => {
                if (order.status === 'completed') {
                    const viewBtn = document.getElementById(`viewOrder_${order.id}`);
                    if (viewBtn && viewBtn.textContent.includes('Chat')) {
                        viewBtn.addEventListener('click', () => showChat(order.id));
                    }
                }
            });
        }
        
        // Display full reports
        if (fullReports.length === 0) {
            fullReportsList.innerHTML = '<div class="empty-state">No full reports yet. Start your first analysis!</div>';
        } else {
            fullReportsList.innerHTML = fullReports.map(order => createOrderCard(order)).join('');
            // Add event listeners for full reports
            fullReports.forEach(order => {
                if (order.status === 'completed' && order.analysis_data) {
                    const viewBtn = document.getElementById(`viewOrder_${order.id}`);
                    if (viewBtn) {
                        viewBtn.addEventListener('click', () => viewOrderAnalysis(order));
                    }
                }
            });
        }
        
    } catch (error) {
        console.error('Error loading orders:', error);
        chatQueriesList.innerHTML = '<div class="error-state">Failed to load orders. Please try again.</div>';
        fullReportsList.innerHTML = '<div class="error-state">Failed to load orders. Please try again.</div>';
    }
}

// Switch tabs
function switchTab(tabName) {
    // Update tab buttons
    const chatTab = document.getElementById('chatQueriesTab');
    const reportsTab = document.getElementById('fullReportsTab');
    const chatPane = document.getElementById('chatQueriesPane');
    const reportsPane = document.getElementById('fullReportsPane');
    
    if (tabName === 'chatQueries') {
        chatTab.classList.add('active');
        reportsTab.classList.remove('active');
        chatPane.classList.add('active');
        reportsPane.classList.remove('active');
    } else {
        reportsTab.classList.add('active');
        chatTab.classList.remove('active');
        reportsPane.classList.add('active');
        chatPane.classList.remove('active');
    }
}

// Create order card
function createOrderCard(order) {
    const statusClass = getStatusClass(order.status);
    const statusText = getStatusText(order.status);
    const date = new Date(order.created_at).toLocaleDateString();
    
    // Get order type badge
    const orderType = order.type || 'full_report';
    const typeBadge = orderType === 'query' 
        ? '<span class="type-badge type-query">Query</span>' 
        : '<span class="type-badge type-full-report">Full Report</span>';
    
    // Show query indicator for query orders
    let queryInfo = '';
    if (orderType === 'query' && order.status === 'completed') {
        queryInfo = '<p class="message-info"><strong>Type:</strong> Query - Click "View Chat" to see conversation</p>';
    }
    
    let actions = '';
    if (order.status === 'payment_pending') {
        actions = `<button class="btn-small btn-primary" onclick="retryPaymentForOrder(${order.id})">Pay Now</button>`;
    } else if (order.status === 'completed') {
        if (orderType === 'query') {
            actions = `<button class="btn-small btn-primary" onclick="showChat(${order.id})">View Chat</button>`;
        } else if (order.analysis_data) {
            actions = `<button class="btn-small btn-primary" id="viewOrder_${order.id}">View Report</button>`;
        }
    } else if (order.status === 'failed') {
        actions = `<span class="error-text">${order.error_reason || 'Failed'}</span>`;
    }
    
    return `
        <div class="order-card">
            <div class="order-header">
                <div>
                    <h4>Order #${order.id} ${typeBadge}</h4>
                    <p class="order-date">${date}</p>
                </div>
                <span class="status-badge ${statusClass}">${statusText}</span>
            </div>
            <div class="order-body">
                <p><strong>Amount:</strong> ₹${order.amount.toFixed(2)}</p>
                ${order.birth_details ? `<p><strong>Name:</strong> ${order.birth_details.name || 'N/A'}</p>` : ''}
                ${queryInfo}
            </div>
            <div class="order-actions">
                ${actions}
            </div>
        </div>
    `;
}

// Get status class
function getStatusClass(status) {
    const statusMap = {
        'payment_pending': 'status-pending',
        'processing': 'status-processing',
        'completed': 'status-completed',
        'failed': 'status-failed'
    };
    return statusMap[status] || 'status-pending';
}

// Get status text
function getStatusText(status) {
    const textMap = {
        'payment_pending': 'Payment Pending',
        'processing': 'Processing',
        'completed': 'Completed',
        'failed': 'Failed'
    };
    return textMap[status] || status;
}

// View order analysis
function viewOrderAnalysis(order) {
    hideAllSections();
    document.getElementById('resultsContainer').style.display = 'block';
    document.getElementById('navbar').style.display = 'block';
    document.getElementById('header').style.display = 'none';
    
    const analysisData = order.analysis_data;
    if (!analysisData) {
        return;
    }
    
    // Display analysis
    if (analysisData.summary) {
        document.getElementById('summarySection').style.display = 'block';
        document.getElementById('summaryContent').innerHTML = formatMarkdown(analysisData.summary);
    }
    
    let hasDetails = false;
    if (analysisData.chart_data_analysis) {
        document.getElementById('chartSection').style.display = 'block';
        document.getElementById('chartContent').innerHTML = formatMarkdown(analysisData.chart_data_analysis);
        hasDetails = true;
    }
    
    if (analysisData.dasha_analysis) {
        document.getElementById('dashaSection').style.display = 'block';
        document.getElementById('dashaContent').innerHTML = formatMarkdown(analysisData.dasha_analysis);
        hasDetails = true;
    }
    
    if (analysisData.goal_analysis) {
        document.getElementById('goalSection').style.display = 'block';
        document.getElementById('goalContent').innerHTML = formatMarkdown(analysisData.goal_analysis);
        hasDetails = true;
    }
    
    if (analysisData.recommendations) {
        document.getElementById('recommendationsSection').style.display = 'block';
        document.getElementById('recommendationsContent').innerHTML = formatMarkdown(analysisData.recommendations);
        hasDetails = true;
    }
    
    if (hasDetails) {
        document.getElementById('expandableSections').style.display = 'block';
    }
    
    // Setup toggle button
    const toggleBtn = document.getElementById('toggleDetailsBtn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const isVisible = document.getElementById('detailedSections').style.display !== 'none';
            document.getElementById('detailedSections').style.display = isVisible ? 'none' : 'block';
            const spans = toggleBtn.querySelectorAll('span');
            spans[0].style.display = isVisible ? 'inline' : 'none';
            spans[1].style.display = isVisible ? 'none' : 'inline';
        });
    }
}

// Retry payment for order
async function retryPaymentForOrder(orderId) {
    try {
        showLoading('Creating payment...');
        const response = await fetch(`${window.API_BASE_URL}/api/v1/payments/create?order_id=${orderId}`, {
            method: 'POST',
            headers: authManager.getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to create payment');
        }
        
        const paymentData = await response.json();
        hideLoading();
        
        // Redirect to Razorpay
        initiateRazorpayPayment(paymentData);
    } catch (error) {
        hideLoading();
        showNotification('Failed to create payment. Please try again.', 'error');
    }
}

// Hide all sections
function hideAllSections() {
    document.getElementById('welcomePage').style.display = 'none';
    document.getElementById('authRequired').style.display = 'none';
    document.getElementById('dashboardContainer').style.display = 'none';
    document.getElementById('formContainer').style.display = 'none';
    document.getElementById('paymentSuccess').style.display = 'none';
    document.getElementById('paymentFailure').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'none';
}

// Show form (make it globally accessible)
function showForm() {
    hideAllSections();
    const formContainer = document.getElementById('formContainer');
    const navbar = document.getElementById('navbar');
    const header = document.getElementById('header');
    
    if (formContainer) {
        formContainer.style.display = 'block';
    }
    if (navbar) {
        navbar.style.display = 'block';
    }
    if (header) {
        header.style.display = 'none';
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Make showForm globally accessible
window.showForm = showForm;

// Poll order status
function startOrderStatusPolling(orderId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${window.API_BASE_URL}/api/v1/orders/${orderId}`, {
                headers: authManager.getAuthHeaders()
            });
            
            if (response.ok) {
                const order = await response.json();
                if (order.status === 'completed' || order.status === 'failed') {
                    clearInterval(interval);
                    loadOrders(); // Refresh orders list
                    if (order.status === 'completed') {
                        showNotification('Your analysis is complete! Check your dashboard.', 'success');
                    }
                }
            }
        } catch (error) {
            console.error('Error polling order status:', error);
        }
    }, 5000); // Poll every 5 seconds
    
    // Stop polling after 10 minutes
    setTimeout(() => clearInterval(interval), 600000);
}

