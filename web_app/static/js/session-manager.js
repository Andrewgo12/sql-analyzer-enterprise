/**
 * Enterprise Session Manager
 * Handles session creation, validation, and lifecycle management
 */

class SessionManager {
    constructor() {
        this.sessionId = null;
        this.userId = null;
        this.username = null;
        this.sessionExpiry = null;
        this.refreshTimer = null;
        this.isRefreshing = false;
        
        // Session configuration
        this.config = {
            sessionTimeout: 30 * 60 * 1000, // 30 minutes
            refreshInterval: 5 * 60 * 1000,  // 5 minutes
            maxRetries: 3,
            retryDelay: 1000
        };
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadSession();
            if (!this.sessionId || this.isSessionExpired()) {
                await this.createNewSession();
            }
            this.startRefreshTimer();
        } catch (error) {
            console.error('Session initialization failed:', error);
            await this.createNewSession();
        }
    }
    
    /**
     * Generate a cryptographically secure session ID
     */
    generateSessionId() {
        const array = new Uint8Array(32);
        crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }
    
    /**
     * Create a new session
     */
    async createNewSession() {
        try {
            this.sessionId = this.generateSessionId();
            this.userId = `user_${Date.now()}`;
            this.username = 'anonymous';
            this.sessionExpiry = Date.now() + this.config.sessionTimeout;
            
            // Save to storage
            this.saveSession();
            
            // Notify session creation
            this.dispatchSessionEvent('session-created', {
                sessionId: this.sessionId,
                userId: this.userId
            });
            
            if (window.Utils) {
                Utils.log('✅ Nueva sesión creada:', this.sessionId.substring(0, 8) + '...');
            }
            
            return {
                sessionId: this.sessionId,
                userId: this.userId,
                username: this.username,
                expiresAt: this.sessionExpiry
            };
            
        } catch (error) {
            console.error('Failed to create session:', error);
            throw new Error('No se pudo crear la sesión');
        }
    }
    
    /**
     * Load session from storage
     */
    async loadSession() {
        try {
            const sessionData = localStorage.getItem('sqlAnalyzer_session');
            if (sessionData) {
                const parsed = JSON.parse(sessionData);
                this.sessionId = parsed.sessionId;
                this.userId = parsed.userId;
                this.username = parsed.username;
                this.sessionExpiry = parsed.expiresAt;
                
                if (window.Utils) {
                    Utils.log('📂 Sesión cargada desde almacenamiento');
                }
            }
        } catch (error) {
            console.error('Failed to load session:', error);
            this.clearSession();
        }
    }
    
    /**
     * Save session to storage
     */
    saveSession() {
        try {
            const sessionData = {
                sessionId: this.sessionId,
                userId: this.userId,
                username: this.username,
                expiresAt: this.sessionExpiry,
                createdAt: Date.now()
            };
            
            localStorage.setItem('sqlAnalyzer_session', JSON.stringify(sessionData));
            
            // Also save individual items for backward compatibility
            localStorage.setItem('sqlAnalyzer_sessionId', this.sessionId);
            localStorage.setItem('sqlAnalyzer_userId', this.userId);
            localStorage.setItem('sqlAnalyzer_username', this.username);
            
        } catch (error) {
            console.error('Failed to save session:', error);
        }
    }
    
    /**
     * Clear session data
     */
    clearSession() {
        this.sessionId = null;
        this.userId = null;
        this.username = null;
        this.sessionExpiry = null;
        
        // Clear storage
        localStorage.removeItem('sqlAnalyzer_session');
        localStorage.removeItem('sqlAnalyzer_sessionId');
        localStorage.removeItem('sqlAnalyzer_userId');
        localStorage.removeItem('sqlAnalyzer_username');
        
        // Stop refresh timer
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
        
        this.dispatchSessionEvent('session-cleared');
    }
    
    /**
     * Check if session is expired
     */
    isSessionExpired() {
        if (!this.sessionExpiry) return true;
        return Date.now() >= this.sessionExpiry;
    }
    
    /**
     * Refresh session
     */
    async refreshSession() {
        if (this.isRefreshing) return;
        
        this.isRefreshing = true;
        
        try {
            // Extend session expiry
            this.sessionExpiry = Date.now() + this.config.sessionTimeout;
            this.saveSession();
            
            this.dispatchSessionEvent('session-refreshed', {
                sessionId: this.sessionId,
                expiresAt: this.sessionExpiry
            });
            
            if (window.Utils) {
                Utils.log('🔄 Sesión renovada');
            }
            
        } catch (error) {
            console.error('Failed to refresh session:', error);
            await this.createNewSession();
        } finally {
            this.isRefreshing = false;
        }
    }
    
    /**
     * Start automatic session refresh timer
     */
    startRefreshTimer() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        this.refreshTimer = setInterval(() => {
            if (this.isSessionExpired()) {
                this.createNewSession();
            } else {
                this.refreshSession();
            }
        }, this.config.refreshInterval);
    }
    
    /**
     * Validate session
     */
    async validateSession() {
        if (!this.sessionId) return false;
        if (this.isSessionExpired()) return false;
        
        try {
            // In a real implementation, this would make an API call
            // For now, we'll just check local validity
            return true;
        } catch (error) {
            console.error('Session validation failed:', error);
            return false;
        }
    }
    
    /**
     * Get current session info
     */
    getSessionInfo() {
        return {
            sessionId: this.sessionId,
            userId: this.userId,
            username: this.username,
            expiresAt: this.sessionExpiry,
            isValid: !this.isSessionExpired(),
            timeRemaining: this.sessionExpiry ? Math.max(0, this.sessionExpiry - Date.now()) : 0
        };
    }
    
    /**
     * Ensure valid session exists
     */
    async ensureValidSession() {
        if (!this.sessionId || this.isSessionExpired()) {
            await this.createNewSession();
        }
        return this.sessionId;
    }
    
    /**
     * Dispatch session events
     */
    dispatchSessionEvent(eventType, data = {}) {
        const event = new CustomEvent(`sqlAnalyzer:${eventType}`, {
            detail: { ...data, timestamp: Date.now() }
        });
        window.dispatchEvent(event);
    }
    
    /**
     * Get session headers for API requests
     */
    getSessionHeaders() {
        const headers = {};
        
        if (this.sessionId) {
            headers['X-Session-ID'] = this.sessionId;
            headers['X-User-ID'] = this.userId;
        }
        
        return headers;
    }
    
    /**
     * Handle session errors
     */
    handleSessionError(error) {
        console.error('Session error:', error);
        
        if (error.status === 401 || error.code === 'UNAUTHORIZED') {
            this.clearSession();
            this.createNewSession();
        }
    }
}

// Create global session manager instance
window.SessionManager = new SessionManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SessionManager;
}
