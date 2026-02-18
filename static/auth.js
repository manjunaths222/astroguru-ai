// Authentication management

// Initialize API_BASE_URL if not already set (auth.js loads first)
if (typeof window.API_BASE_URL === 'undefined') {
    window.API_BASE_URL = window.location.origin;
}
// Use window.API_BASE_URL directly to avoid const redeclaration
const AUTH_ENDPOINT = `${window.API_BASE_URL}/api/v1/auth`;

// Token management
const TOKEN_KEY = 'astroguru_token';
const USER_KEY = 'astroguru_user';

class AuthManager {
    constructor() {
        this.token = localStorage.getItem(TOKEN_KEY);
        this.user = JSON.parse(localStorage.getItem(USER_KEY) || 'null');
    }

    // Get stored token
    getToken() {
        return this.token;
    }

    // Get current user
    getCurrentUser() {
        return this.user;
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.token;
    }

    // Check if user is admin
    isAdmin() {
        return this.user && this.user.type === 'admin';
    }

    // Store token and user
    setAuth(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    }

    // Clear auth
    clearAuth() {
        this.token = null;
        this.user = null;
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    }

    // Get auth headers
    getAuthHeaders() {
        if (!this.token) {
            return {};
        }
        return {
            'Authorization': `Bearer ${this.token}`
        };
    }

    // Initiate Google OAuth
    async initiateGoogleLogin() {
        try {
            const response = await fetch(`${AUTH_ENDPOINT}/google`);
            const data = await response.json();
            if (data.auth_url) {
                window.location.href = data.auth_url;
            } else {
                throw new Error('Failed to get OAuth URL');
            }
        } catch (error) {
            console.error('Error initiating Google login:', error);
            showNotification('Failed to initiate login. Please try again.', 'error');
        }
    }

    // Handle OAuth callback
    async handleOAuthCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        
        if (token) {
            this.setAuth(token, null);
            // Fetch user info
            await this.fetchUserInfo();
            // Redirect to home
            window.location.href = '/';
        }
    }

    // Fetch current user info
    async fetchUserInfo() {
        try {
            const response = await fetch(`${AUTH_ENDPOINT}/me`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const user = await response.json();
                this.user = user;
                localStorage.setItem(USER_KEY, JSON.stringify(user));
                return user;
            } else if (response.status === 401) {
                this.clearAuth();
                return null;
            } else {
                throw new Error('Failed to fetch user info');
            }
        } catch (error) {
            console.error('Error fetching user info:', error);
            return null;
        }
    }

    // Admin login
    async adminLogin(email, password) {
        try {
            const response = await fetch(`${AUTH_ENDPOINT}/admin/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                const data = await response.json();
                this.setAuth(data.access_token, { type: 'admin', email });
                return true;
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }
        } catch (error) {
            console.error('Admin login error:', error);
            throw error;
        }
    }

    // Logout
    logout() {
        this.clearAuth();
        window.location.href = '/';
    }
}

// Global auth manager instance
const authManager = new AuthManager();

// Helper function to show notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Remove after delay
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Check auth on page load
document.addEventListener('DOMContentLoaded', () => {
    // Handle OAuth callback if on callback page
    if (window.location.pathname.includes('/auth/callback')) {
        authManager.handleOAuthCallback();
    }
    
    // Check if user is authenticated
    if (authManager.isAuthenticated()) {
        // Verify token is still valid
        authManager.fetchUserInfo().catch(() => {
            // Token invalid, redirect to login
            if (!window.location.pathname.includes('/admin')) {
                showAuthRequired();
            }
        });
    } else {
        // Not authenticated, show login if not on admin page
        if (!window.location.pathname.includes('/admin')) {
            showAuthRequired();
        }
    }
});

// Show auth required UI
function showAuthRequired() {
    const mainContent = document.querySelector('.main-content');
    if (mainContent && !document.getElementById('authRequired')) {
        const authDiv = document.createElement('div');
        authDiv.id = 'authRequired';
        authDiv.className = 'auth-required';
        authDiv.innerHTML = `
            <div class="auth-required-content">
                <h2>Welcome to AstroGuru AI</h2>
                <p>Please login to continue</p>
                <button class="btn-primary" onclick="authManager.initiateGoogleLogin()">
                    <span>🔐 Login with Google</span>
                </button>
            </div>
        `;
        mainContent.innerHTML = '';
        mainContent.appendChild(authDiv);
    }
}

