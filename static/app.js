// API Configuration
// Use window.API_BASE_URL (set by auth.js which loads first)
// No const declaration here to avoid redeclaration error

// State
let currentOrderId = null;
let razorpayOptions = null;

// DOM Elements
const formContainer = document.getElementById('formContainer');
const birthForm = document.getElementById('birthForm');
const placeInput = document.getElementById('placeOfBirth');
const suggestionsDiv = document.getElementById('suggestions');
const submitBtn = document.getElementById('submitBtn');

// Location autocomplete
let locationSearchTimeout = null;
let currentSearchAbortController = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    if (!authManager.isAuthenticated()) {
        showAuthRequired();
        return;
    }
    
    // Fetch user info
    const user = await authManager.fetchUserInfo();
    if (user) {
        updateNavbarUserInfo();
    }
    
    // Show welcome page or dashboard based on URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('payment') === 'success') {
        showPaymentSuccess();
    } else if (urlParams.get('payment') === 'failed') {
        showPaymentFailure(urlParams.get('error') || 'Payment failed');
    } else {
        showWelcomePage();
    }
    
    // Setup form submission
    if (birthForm) {
        birthForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Setup location autocomplete
    if (placeInput) {
        setupLocationAutocomplete();
    }
});

// Show welcome page
function showWelcomePage() {
    hideAllSections();
    document.getElementById('welcomePage').style.display = 'block';
    document.getElementById('navbar').style.display = 'block';
    document.getElementById('header').style.display = 'none';
    updateNavbarUserInfo();
}

// Update navbar user info
function updateNavbarUserInfo() {
    const user = authManager.getCurrentUser();
    if (user) {
        const userNameEl = document.getElementById('userName');
        if (userNameEl) {
            userNameEl.textContent = user.name || (user.email ? user.email.split('@')[0] : 'User');
        }
    }
}

// Show auth required
function showAuthRequired() {
    hideAllSections();
    document.getElementById('authRequired').style.display = 'block';
    document.getElementById('header').style.display = 'block';
    document.getElementById('navbar').style.display = 'none';
}

// Hide all sections
function hideAllSections() {
    const sections = [
        'welcomePage', 'authRequired', 'dashboardContainer',
        'formContainer', 'paymentSuccess', 'paymentFailure', 'resultsContainer', 'chatContainer'
    ];
    sections.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.style.display = 'none';
        }
    });
    
    // Also ensure chat container is properly hidden
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer) {
        chatContainer.style.display = 'none';
    }
}

// Make hideAllSections globally accessible
window.hideAllSections = hideAllSections;

// Handle order type change
function handleOrderTypeChange() {
    const orderType = document.getElementById('orderType').value;
    const queryGroup = document.getElementById('queryGroup');
    const userQuery = document.getElementById('userQuery');
    const submitBtnText = document.getElementById('submitBtnText');
    const priceAmount = document.getElementById('priceAmount');
    
    if (orderType === 'query') {
        queryGroup.style.display = 'block';
        userQuery.required = true;
        submitBtnText.textContent = 'Pay and Predict';
        priceAmount.textContent = '5.00'; // Query price
    } else {
        queryGroup.style.display = 'none';
        userQuery.required = false;
        submitBtnText.textContent = 'Pay and Generate';
        priceAmount.textContent = '10.00'; // Full report price
    }
}

// Setup location autocomplete
function setupLocationAutocomplete() {
    if (!placeInput) return;
    
    let selectedIndex = -1;
    let currentSuggestions = [];
    
    placeInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        if (currentSearchAbortController) {
            currentSearchAbortController.abort();
        }
        
        if (query.length < 2) {
            suggestionsDiv.classList.remove('show');
            return;
        }
        
        clearTimeout(locationSearchTimeout);
        locationSearchTimeout = setTimeout(() => {
            searchLocations(query);
        }, 300);
    });
    
    placeInput.addEventListener('blur', () => {
        setTimeout(() => {
            suggestionsDiv.classList.remove('show');
        }, 200);
    });
    
    async function searchLocations(query) {
        currentSearchAbortController = new AbortController();
        
        try {
            const url = `https://nominatim.openstreetmap.org/search?` +
                `q=${encodeURIComponent(query)}` +
                `&countrycodes=in` +
                `&limit=10` +
                `&format=json` +
                `&addressdetails=1` +
                `&accept-language=en`;
            
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const response = await fetch(url, {
                signal: currentSearchAbortController.signal,
                headers: {
                    'User-Agent': 'AstroGuru-AI/1.0',
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            const suggestions = data.map(item => {
                const address = item.address || {};
                const parts = [];
                
                if (address.city || address.town || address.village) {
                    parts.push(address.city || address.town || address.village);
                }
                if (address.state) {
                    parts.push(address.state);
                }
                if (address.country) {
                    parts.push(address.country);
                }
                
                const locationString = parts.length > 0 
                    ? parts.join(', ')
                    : item.display_name;
                
                return {
                    display: locationString,
                    full: item.display_name,
                    lat: item.lat,
                    lon: item.lon,
                    city: address.city || address.town || address.village || '',
                    state: address.state || '',
                    country: address.country || 'India'
                };
            });
            
            currentSuggestions = suggestions;
            displaySuggestions(suggestions);
            selectedIndex = -1;
            
        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }
            console.error('Error searching locations:', error);
            suggestionsDiv.classList.remove('show');
        }
    }
    
    function displaySuggestions(suggestions) {
        if (suggestions.length === 0) {
            suggestionsDiv.classList.remove('show');
            return;
        }
        
        suggestionsDiv.innerHTML = suggestions.map((suggestion, index) => 
            `<div class="suggestion-item" data-index="${index}">
                <div class="suggestion-main">${highlightMatch(suggestion.display, placeInput.value)}</div>
                <div class="suggestion-detail">${suggestion.full}</div>
            </div>`
        ).join('');
        
        suggestionsDiv.classList.add('show');
        
        suggestionsDiv.querySelectorAll('.suggestion-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                const suggestion = suggestions[index];
                placeInput.value = suggestion.display;
                document.getElementById('latitude').value = suggestion.lat || '';
                document.getElementById('longitude').value = suggestion.lon || '';
                suggestionsDiv.classList.remove('show');
            });
        });
    }
    
    function highlightMatch(text, query) {
        if (!query) return text;
        const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }
    
    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (submitBtn.disabled) return;
    
    // Get form data
    const formData = new FormData(birthForm);
    const name = formData.get('name');
    const dateOfBirth = formData.get('dateOfBirth');
    const timeOfBirth = formData.get('timeOfBirth');
    const placeOfBirth = formData.get('placeOfBirth');
    const latitude = formData.get('latitude');
    const longitude = formData.get('longitude');
    const goals = Array.from(formData.getAll('goals'));
    
    // Validate
    if (!name || !dateOfBirth || !timeOfBirth || !placeOfBirth) {
        showNotification('Please fill in all required fields.', 'error');
        return;
    }
    
    if (goals.length === 0) {
        showNotification('Please select at least one goal.', 'error');
        return;
    }
    
    // Get order type and user query
    const orderType = formData.get('orderType') || 'full_report';
    const userQuery = formData.get('userQuery') || null;
    
    // Validate query for query type
    if (orderType === 'query' && !userQuery) {
        showNotification('Please enter your question for query type orders.', 'error');
        return;
    }
    
    // Build birth details
    const birthDetails = {
        name,
        dateOfBirth,
        timeOfBirth,
        placeOfBirth,
        latitude: latitude || null,
        longitude: longitude || null,
        goals
    };
    
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').textContent = 'Creating Order...';
    
    try {
        // Create order
        const orderResponse = await fetch(`${window.API_BASE_URL}/api/v1/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...authManager.getAuthHeaders()
            },
            body: JSON.stringify({ 
                birth_details: birthDetails,
                order_type: orderType,
                user_query: userQuery
            })
        });
        
        if (!orderResponse.ok) {
            if (orderResponse.status === 401) {
                authManager.clearAuth();
                showAuthRequired();
                return;
            }
            const error = await orderResponse.json();
            throw new Error(error.detail || 'Failed to create order');
        }
        
        const order = await orderResponse.json();
        currentOrderId = order.id;
        
        // Create payment
        const paymentResponse = await fetch(`${window.API_BASE_URL}/api/v1/payments/create?order_id=${order.id}`, {
            method: 'POST',
            headers: authManager.getAuthHeaders()
        });
        
        if (!paymentResponse.ok) {
            throw new Error('Failed to create payment');
        }
        
        const paymentData = await paymentResponse.json();
        
        // Initiate Razorpay payment
        initiateRazorpayPayment(paymentData);
        
    } catch (error) {
        console.error('Error creating order:', error);
        showNotification(error.message || 'Failed to create order. Please try again.', 'error');
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').textContent = 'Pay and Generate';
    }
}

// Initiate Razorpay payment
function initiateRazorpayPayment(paymentData) {
    // Load Razorpay script if not already loaded
    if (!window.Razorpay) {
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.onload = () => {
            openRazorpayCheckout(paymentData);
        };
        script.onerror = () => {
            showNotification('Failed to load payment gateway. Please try again.', 'error');
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').textContent = 'Pay and Generate';
        };
        document.body.appendChild(script);
    } else {
        openRazorpayCheckout(paymentData);
    }
}

// Open Razorpay checkout
function openRazorpayCheckout(paymentData) {
    const options = {
        key: paymentData.key_id,
        amount: paymentData.amount * 100, // Convert to paise
        currency: paymentData.currency || 'INR',
        name: 'AstroGuru AI',
        description: 'Vedic Astrology Analysis',
        order_id: paymentData.razorpay_order_id,
        handler: function(response) {
            verifyPayment(response);
        },
        prefill: {
            email: authManager.getCurrentUser()?.email || '',
            name: authManager.getCurrentUser()?.name || ''
        },
        theme: {
            color: '#6366f1'
        },
        modal: {
            ondismiss: function() {
                submitBtn.disabled = false;
                submitBtn.querySelector('.btn-text').textContent = 'Pay and Generate';
            }
        }
    };
    
    const razorpay = new window.Razorpay(options);
    razorpay.open();
}

// Verify payment
async function verifyPayment(razorpayResponse) {
    showLoading('Verifying payment...');
    
    try {
        const verifyResponse = await fetch(`${window.API_BASE_URL}/api/v1/payments/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...authManager.getAuthHeaders()
            },
            body: JSON.stringify({
                razorpay_order_id: razorpayResponse.razorpay_order_id,
                razorpay_payment_id: razorpayResponse.razorpay_payment_id,
                razorpay_signature: razorpayResponse.razorpay_signature
            })
        });
        
        if (!verifyResponse.ok) {
            const error = await verifyResponse.json();
            throw new Error(error.detail || 'Payment verification failed');
        }
        
        hideLoading();
        
        // Redirect to success page
        window.location.href = '/?payment=success';
        
    } catch (error) {
        hideLoading();
        console.error('Payment verification error:', error);
        window.location.href = `/?payment=failed&error=${encodeURIComponent(error.message)}`;
    }
}

// Show payment success
function showPaymentSuccess() {
    hideAllSections();
    document.getElementById('paymentSuccess').style.display = 'block';
    document.getElementById('navbar').style.display = 'block';
    document.getElementById('header').style.display = 'none';
    
    // Start polling for order status
    if (currentOrderId) {
        startOrderStatusPolling(currentOrderId);
    }
}

// Show payment failure
function showPaymentFailure(errorMsg) {
    hideAllSections();
    document.getElementById('paymentFailure').style.display = 'block';
    document.getElementById('navbar').style.display = 'block';
    document.getElementById('header').style.display = 'none';
    
    if (errorMsg) {
        document.getElementById('paymentErrorMsg').textContent = errorMsg;
    }
}

// Retry payment
function retryPayment() {
    if (currentOrderId) {
        retryPaymentForOrder(currentOrderId);
    } else {
        showForm();
    }
}

// Start order status polling
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
                    // Refresh dashboard if visible
                    if (typeof loadOrders === 'function') {
                        loadOrders();
                    }
                }
            }
        } catch (error) {
            console.error('Error polling order status:', error);
        }
    }, 5000);
    
    setTimeout(() => clearInterval(interval), 600000); // Stop after 10 minutes
}

// Show loading
function showLoading(text = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    if (overlay) {
        if (loadingText) loadingText.textContent = text;
        overlay.style.display = 'flex';
    }
}

// Hide loading
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const container = document.getElementById('notificationContainer') || document.body;
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Format markdown (for displaying analysis)
function formatMarkdown(text) {
    if (!text) return '';
    
    const lines = text.split('\n');
    let html = '';
    let inList = false;
    let inParagraph = false;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (!line) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            if (inParagraph) {
                html += '</p>';
                inParagraph = false;
            }
            continue;
        }
        
        if (line.startsWith('#### ')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += `<h4>${line.substring(5)}</h4>`;
        } else if (line.startsWith('### ')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += `<h3>${line.substring(4)}</h3>`;
        } else if (line.startsWith('## ')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += `<h2>${line.substring(3)}</h2>`;
        } else if (line.startsWith('# ')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += `<h1>${line.substring(2)}</h1>`;
        } else if (line.startsWith('---')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += '<hr>';
        } else if (line.match(/^[\-\*] /) || line.match(/^\d+\. /)) {
            if (!inList) {
                if (inParagraph) { html += '</p>'; inParagraph = false; }
                html += '<ul>';
                inList = true;
            }
            const listContent = line.replace(/^[\-\*] /, '').replace(/^\d+\. /, '');
            html += `<li>${processInlineMarkdown(listContent)}</li>`;
        } else {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            if (!inParagraph) {
                html += '<p>';
                inParagraph = true;
            } else {
                html += '<br>';
            }
            html += processInlineMarkdown(line);
        }
    }
    
    if (inList) html += '</ul>';
    if (inParagraph) html += '</p>';
    
    return html;
}

// Process inline markdown
function processInlineMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/__(.*?)__/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>');
}
