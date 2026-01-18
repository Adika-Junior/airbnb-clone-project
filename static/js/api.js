/**
 * API Client for Airbnb Clone
 * Handles all API calls to the backend
 */

const API_BASE_URL = window.location.origin;

class APIClient {
    constructor() {
        this.token = localStorage.getItem('auth_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    /**
     * Get authorization headers
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(options.requireAuth !== false),
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json().catch(() => ({}));
            
            if (!response.ok) {
                if (response.status === 401 && this.refreshToken) {
                    // Try to refresh token
                    const refreshed = await this.refreshAuthToken();
                    if (refreshed) {
                        // Retry original request
                        config.headers['Authorization'] = `Bearer ${this.token}`;
                        const retryResponse = await fetch(url, config);
                        const retryData = await retryResponse.json().catch(() => ({}));
                        if (retryResponse.ok) {
                            return retryData;
                        }
                    }
                }
                throw new Error(data.detail || data.message || data.error || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Authentication Methods
     */
    async register(userData) {
        const data = await this.request('/api/auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData),
            requireAuth: false,
        });
        return data;
    }

    async login(email, password) {
        const data = await this.request('/api/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
            requireAuth: false,
        });
        
        if (data.access && data.refresh) {
            this.setTokens(data.access, data.refresh);
            localStorage.setItem('user', JSON.stringify(data.user || {}));
        }
        
        return data;
    }

    async logout() {
        this.token = null;
        this.refreshToken = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }

    async refreshAuthToken() {
        if (!this.refreshToken) return false;
        
        try {
            const data = await this.request('/api/token/refresh/', {
                method: 'POST',
                body: JSON.stringify({ refresh: this.refreshToken }),
                requireAuth: false,
            });
            
            if (data.access) {
                this.setTokens(data.access, this.refreshToken);
                return true;
            }
        } catch (error) {
            this.logout();
        }
        
        return false;
    }

    setTokens(access, refresh) {
        this.token = access;
        this.refreshToken = refresh;
        localStorage.setItem('auth_token', access);
        localStorage.setItem('refresh_token', refresh);
    }

    getCurrentUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }

    isAuthenticated() {
        return !!this.token;
    }

    /**
     * User Methods
     */
    async getCurrentUserProfile() {
        return await this.request('/api/auth/me/');
    }

    /**
     * Properties Methods
     */
    async getProperties(filters = {}) {
        const queryParams = new URLSearchParams(filters).toString();
        const url = `/api/properties/api/list/${queryParams ? '?' + queryParams : ''}`;
        return await this.request(url, {
            requireAuth: false,
        });
    }
    
    async getPropertiesOld() {
        // Backward compatibility
        return await this.getProperties();
    }
    
    async getProperty(id) {
        return await this.request(`/api/properties/api/${id}/`, {
            requireAuth: false,
        });
    }
    
    async createProperty(propertyData) {
        return await this.request('/api/properties/api/create/', {
            method: 'POST',
            body: JSON.stringify(propertyData),
        });
    }
    
    async getPropertyReviews(propertyId) {
        return await this.request(`/api/properties/api/${propertyId}/reviews/`, {
            requireAuth: false,
        });
    }
    
    async addReview(propertyId, reviewData) {
        return await this.request(`/api/properties/api/${propertyId}/add-review/`, {
            method: 'POST',
            body: JSON.stringify(reviewData),
            requireAuth: false, // Allows anonymous
        });
    }

    /**
     * Travel Methods
     */
    async getTravelListings() {
        return await this.request('/api/travel/listings/', {
            requireAuth: false,
        });
    }

    async createTravelListing(listingData) {
        return await this.request('/api/travel/listings/', {
            method: 'POST',
            body: JSON.stringify(listingData),
        });
    }

    async getBookings() {
        return await this.request('/api/travel/bookings/');
    }
    
    async createBooking(bookingData) {
        return await this.request('/api/travel/bookings/create/', {
            method: 'POST',
            body: JSON.stringify(bookingData),
            requireAuth: false, // Allows anonymous
        });
    }
    
    async getUserBookings() {
        return await this.request('/api/travel/bookings/my/');
    }
    
    async cancelBooking(bookingId) {
        return await this.request(`/api/travel/bookings/${bookingId}/cancel/`, {
            method: 'POST',
        });
    }

    /**
     * Messaging Methods
     */
    async getConversations() {
        return await this.request('/api/messaging/conversations/');
    }

    async getMessages(conversationId) {
        return await this.request(`/api/messaging/messages/?conversation=${conversationId}`);
    }

    async sendMessage(conversationId, messageBody) {
        return await this.request('/api/messaging/messages/', {
            method: 'POST',
            body: JSON.stringify({
                conversation: conversationId,
                message_body: messageBody,
            }),
        });
    }
}

// Create global API client instance
const api = new APIClient();
