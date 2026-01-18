/**
 * Main Application JavaScript
 * Handles UI interactions and page functionality
 */

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Check authentication status
    updateAuthUI();
    
    // Load properties on homepage
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        loadProperties();
    }
    
    // Setup form handlers
    setupAuthForms();
    setupNavigation();
}

/**
 * Update UI based on authentication status
 */
function updateAuthUI() {
    const isAuthenticated = api.isAuthenticated();
    const user = api.getCurrentUser();
    
    // Update navigation
    const authLinks = document.querySelectorAll('.auth-link');
    const userMenu = document.getElementById('user-menu');
    const userInfo = document.getElementById('user-info');
    
    if (isAuthenticated && user) {
        // Show user menu
        authLinks.forEach(link => {
            if (link.classList.contains('login-link') || link.classList.contains('signup-link')) {
                link.style.display = 'none';
            }
        });
        
        if (userMenu) userMenu.style.display = 'block';
        if (userInfo) {
            userInfo.textContent = `${user.first_name} ${user.last_name}`;
            userInfo.style.display = 'block';
        }
    } else {
        // Show login/signup links
        authLinks.forEach(link => {
            if (link.classList.contains('login-link') || link.classList.contains('signup-link')) {
                link.style.display = 'block';
            }
        });
        
        if (userMenu) userMenu.style.display = 'none';
        if (userInfo) userInfo.style.display = 'none';
    }
}

/**
 * Load and display properties
 */
async function loadProperties() {
    const propertiesContainer = document.getElementById('properties-container');
    if (!propertiesContainer) return;
    
    try {
        propertiesContainer.innerHTML = '<div class="loading">Loading properties...</div>';
        const properties = await api.getProperties();
        
        if (properties.length === 0) {
            propertiesContainer.innerHTML = '<div class="no-properties">No properties available at the moment.</div>';
            return;
        }
        
        propertiesContainer.innerHTML = properties.map(property => {
            const price = property.price_per_night || property.price || 0;
            const rating = property.average_rating || 0;
            const reviewCount = property.review_count || 0;
            const imageUrl = property.image_url || '';
            const image = property.image || '';
            
            return `
            <div class="property-card" onclick="window.location.href='/properties/${property.id}/'">
                <div class="property-image">
                    ${imageUrl ? `<img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(property.title)}" onerror="this.parentElement.innerHTML='<div class=\\'placeholder-image\\'>🏠</div>'">` : 
                      image ? `<img src="${escapeHtml(image)}" alt="${escapeHtml(property.title)}" onerror="this.parentElement.innerHTML='<div class=\\'placeholder-image\\'>🏠</div>'">` :
                      '<div class="placeholder-image">🏠</div>'}
                </div>
                <div class="property-info">
                    <div class="property-header-row">
                        <h3>${escapeHtml(property.title)}</h3>
                        ${rating > 0 ? `<span class="property-rating">⭐ ${rating} (${reviewCount})</span>` : ''}
                    </div>
                    <p class="property-location">📍 ${escapeHtml(property.location || property.city || 'Location not specified')}</p>
                    <p class="property-description">${escapeHtml((property.description || '').substring(0, 150))}${(property.description || '').length > 150 ? '...' : ''}</p>
                    <div class="property-footer">
                        <span class="property-price">$${parseFloat(price).toFixed(2)}/night</span>
                        <button class="btn btn-primary" onclick="event.stopPropagation(); window.location.href='/properties/${property.id}/'">View Details</button>
                    </div>
                </div>
            </div>
        `;
        }).join('');
    } catch (error) {
        console.error('Error loading properties:', error);
        propertiesContainer.innerHTML = `<div class="error">Error loading properties: ${error.message}</div>`;
    }
}

/**
 * Setup authentication forms
 */
function setupAuthForms() {
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Signup form
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

/**
 * Handle login form submission
 */
async function handleLogin(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const errorDiv = form.querySelector('.error-message');
    
    const email = form.querySelector('#login-email').value;
    const password = form.querySelector('#login-password').value;
    
    // Clear previous errors
    if (errorDiv) errorDiv.textContent = '';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    try {
        const response = await api.login(email, password);
        
        if (response.access) {
            // Success - redirect based on user role or default to dashboard
            showNotification('Login successful!', 'success');
            setTimeout(() => {
                const user = response.user || api.getCurrentUser();
                // Redirect to dashboard for better UX (users can see their profile)
                // Can also redirect to '/' (homepage) if preferred
                const redirectUrl = '/dashboard/';
                window.location.href = redirectUrl;
            }, 1000);
        } else {
            throw new Error('Login failed');
        }
    } catch (error) {
        if (errorDiv) {
            errorDiv.textContent = error.message || 'Invalid email or password';
            errorDiv.style.display = 'block';
        }
        showNotification(error.message || 'Login failed', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Log In';
    }
}

/**
 * Handle signup form submission
 */
async function handleSignup(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const errorDiv = form.querySelector('.error-message');
    
    const formData = {
        email: form.querySelector('#signup-email').value,
        password: form.querySelector('#signup-password').value,
        first_name: form.querySelector('#signup-first-name').value,
        last_name: form.querySelector('#signup-last-name').value,
        phone_number: form.querySelector('#signup-phone').value || '',
        role: form.querySelector('#signup-role')?.value || 'guest',
    };
    
    // Validate password confirmation if exists
    const confirmPassword = form.querySelector('#signup-confirm-password');
    if (confirmPassword && confirmPassword.value !== formData.password) {
        if (errorDiv) {
            errorDiv.textContent = 'Passwords do not match';
            errorDiv.style.display = 'block';
        }
        return;
    }
    
    // Clear previous errors
    if (errorDiv) errorDiv.textContent = '';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating account...';
    
    try {
        const response = await api.register(formData);
        
        if (response.user) {
            // Auto-login after registration
            const loginResponse = await api.login(formData.email, formData.password);
            showNotification('Account created successfully!', 'success');
            setTimeout(() => {
                // Redirect to dashboard after registration
                window.location.href = '/dashboard/';
            }, 1000);
        }
    } catch (error) {
        if (errorDiv) {
            const errorMsg = error.message || 'Registration failed. Please check your information.';
            errorDiv.textContent = errorMsg;
            errorDiv.style.display = 'block';
        }
        showNotification(error.message || 'Registration failed', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign Up';
    }
}

/**
 * Handle logout
 */
async function handleLogout() {
    await api.logout();
    showNotification('Logged out successfully', 'success');
    updateAuthUI();
    setTimeout(() => {
        window.location.href = '/';
    }, 500);
}

/**
 * Setup navigation
 */
function setupNavigation() {
    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const nav = document.querySelector('.nav');
    
    if (mobileMenuBtn && nav) {
        mobileMenuBtn.addEventListener('click', () => {
            nav.classList.toggle('active');
        });
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

/**
 * Utility: Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * View property details
 */
function viewProperty(id) {
    window.location.href = `/properties/${id}/`;
}
