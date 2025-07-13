/* ============================================================================
   SQL ANALYZER ENTERPRISE - AUTHENTICATION MODULE
   Handle authentication, login/logout, session management
   ============================================================================ */

class AuthManager {
    constructor() {
        this.sessionTimeout = 3600000; // 1 hour
        this.sessionCheckInterval = 60000; // 1 minute
        this.sessionTimer = null;
        this.lastActivity = Date.now();

        this.init();
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    init() {
        try {
            this.loadStoredAuth();
            this.startSessionMonitoring();
            this.setupActivityTracking();
            if (window.Utils) Utils.log('✅ AuthManager initialized successfully');
        } catch (error) {
            if (window.Utils) Utils.error('❌ AuthManager initialization failed:', error);
            this.handleInitializationError(error);
        }
    }

    handleInitializationError(error) {
        try {
            // Fallback initialization
            this.sessionId = null;
            this.userId = null;
            this.username = null;
            this.lastActivity = Date.now();
            if (window.Utils) Utils.warn('⚠️ AuthManager running in fallback mode');
        } catch (fallbackError) {
            if (window.Utils) Utils.error('❌ AuthManager fallback failed:', fallbackError);
        }
    }

    loadStoredAuth() {
        const sessionId = Utils.getStorage('sqlAnalyzer_sessionId');
        const userId = Utils.getStorage('sqlAnalyzer_userId');
        const username = Utils.getStorage('sqlAnalyzer_username');
        const lastActivity = Utils.getStorage('sqlAnalyzer_lastActivity');

        if (sessionId && userId && lastActivity) {
            // Check if session is still valid based on timeout
            const timeSinceLastActivity = Date.now() - lastActivity;
            if (timeSinceLastActivity < this.sessionTimeout) {
                this.sessionId = sessionId;
                this.userId = userId;
                this.username = username;
                this.lastActivity = lastActivity;
                this.updateActivity();
                return true;
            } else {
                // Session expired, clear stored data
                this.clearStoredAuth();
            }
        }

        return false;
    }

    // ========================================================================
    // AUTHENTICATION METHODS
    // ========================================================================

    async signIn(username, password, rememberMe = false) {
        try {
            // Validate input
            if (!username || username.length < 3) {
                throw Utils.createError('Username must be at least 3 characters', 'VALIDATION_ERROR');
            }

            if (!password || password.length < 4) {
                throw Utils.createError('Password must be at least 4 characters', 'VALIDATION_ERROR');
            }

            // For demo purposes, accept any valid credentials
            // In production, this would make an API call to validate credentials
            await this.simulateAuthDelay();

            // Create session
            const sessionResponse = await apiManager.createSession();

            if (!sessionResponse.session_id) {
                throw Utils.createError('Failed to create session', 'SESSION_ERROR');
            }

            // Store authentication data
            this.sessionId = sessionResponse.session_id;
            this.userId = sessionResponse.user_id;
            this.username = username;
            this.lastActivity = Date.now();

            this.saveAuthData(rememberMe);
            this.updateActivity();

            return {
                success: true,
                sessionId: this.sessionId,
                userId: this.userId,
                username: this.username
            };

        } catch (error) {
            Utils.logError(error, 'Authentication - Sign In');
            throw error;
        }
    }

    async signOut() {
        try {
            // Clear session on server if possible
            if (this.sessionId) {
                try {
                    await apiManager.request('/auth/session/logout', {
                        method: 'POST'
                    });
                } catch (error) {
                    // Ignore server errors during logout
                    if (window.Utils) Utils.warn('Server logout failed:', error);
                }
            }

            // Clear local data
            this.clearSession();

            return { success: true };

        } catch (error) {
            Utils.logError(error, 'Authentication - Sign Out');
            // Even if there's an error, clear local session
            this.clearSession();
            throw error;
        }
    }

    async refreshSession() {
        try {
            if (!this.sessionId) {
                throw Utils.createError('No active session to refresh', 'NO_SESSION');
            }

            const response = await apiManager.refreshSession();

            if (response.session_id) {
                this.sessionId = response.session_id;
                this.updateActivity();
                this.saveAuthData();
            }

            return response;

        } catch (error) {
            Utils.logError(error, 'Authentication - Refresh Session');
            // If refresh fails, clear session
            this.clearSession();
            throw error;
        }
    }

    async validateSession() {
        try {
            if (!this.sessionId) {
                return false;
            }

            const isValid = await apiManager.validateSession(this.sessionId);

            if (!isValid) {
                this.clearSession();
            } else {
                this.updateActivity();
            }

            return isValid;

        } catch (error) {
            Utils.logError(error, 'Authentication - Validate Session');
            this.clearSession();
            return false;
        }
    }

    // ========================================================================
    // SESSION MANAGEMENT
    // ========================================================================

    saveAuthData(persistent = false) {
        const storageType = persistent ? 'localStorage' : 'sessionStorage';

        Utils.setStorage('sqlAnalyzer_sessionId', this.sessionId, storageType);
        Utils.setStorage('sqlAnalyzer_userId', this.userId, storageType);
        Utils.setStorage('sqlAnalyzer_username', this.username, storageType);
        Utils.setStorage('sqlAnalyzer_lastActivity', this.lastActivity, storageType);

        if (persistent) {
            Utils.setStorage('sqlAnalyzer_remember', true, 'localStorage');
        }
    }

    clearStoredAuth() {
        // Clear from both storage types
        ['localStorage', 'sessionStorage'].forEach(storageType => {
            Utils.removeStorage('sqlAnalyzer_sessionId', storageType);
            Utils.removeStorage('sqlAnalyzer_userId', storageType);
            Utils.removeStorage('sqlAnalyzer_username', storageType);
            Utils.removeStorage('sqlAnalyzer_lastActivity', storageType);
        });

        Utils.removeStorage('sqlAnalyzer_remember', 'localStorage');
    }

    clearSession() {
        this.sessionId = null;
        this.userId = null;
        this.username = null;
        this.lastActivity = null;

        this.clearStoredAuth();
        this.stopSessionMonitoring();

        // Clear API manager session
        if (window.apiManager) {
            apiManager.clearSession();
        }
    }

    updateActivity() {
        this.lastActivity = Date.now();

        // Update stored activity time
        const storageType = Utils.getStorage('sqlAnalyzer_remember') ? 'localStorage' : 'sessionStorage';
        Utils.setStorage('sqlAnalyzer_lastActivity', this.lastActivity, storageType);
    }

    // ========================================================================
    // SESSION MONITORING
    // ========================================================================

    startSessionMonitoring() {
        this.stopSessionMonitoring(); // Clear any existing timer

        this.sessionTimer = setInterval(() => {
            this.checkSessionTimeout();
        }, this.sessionCheckInterval);
    }

    stopSessionMonitoring() {
        if (this.sessionTimer) {
            clearInterval(this.sessionTimer);
            this.sessionTimer = null;
        }
    }

    checkSessionTimeout() {
        if (!this.sessionId || !this.lastActivity) {
            return;
        }

        const timeSinceLastActivity = Date.now() - this.lastActivity;

        if (timeSinceLastActivity > this.sessionTimeout) {
            this.handleSessionTimeout();
        } else if (timeSinceLastActivity > this.sessionTimeout * 0.8) {
            // Warn user when 80% of session time has elapsed
            this.showSessionWarning();
        }
    }

    handleSessionTimeout() {
        this.clearSession();

        // Show timeout notification
        if (window.showNotification) {
            showNotification('Your session has expired. Please sign in again.', 'warning');
        }

        // Redirect to login page
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
    }

    showSessionWarning() {
        if (window.showNotification) {
            showNotification('Your session will expire soon. Please save your work.', 'info');
        }
    }

    // ========================================================================
    // ACTIVITY TRACKING
    // ========================================================================

    setupActivityTracking() {
        const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];

        const throttledUpdateActivity = Utils.throttle(() => {
            if (this.sessionId) {
                this.updateActivity();
            }
        }, 30000); // Update at most once every 30 seconds

        activityEvents.forEach(event => {
            document.addEventListener(event, throttledUpdateActivity, true);
        });
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    isAuthenticated() {
        return !!(this.sessionId && this.userId);
    }

    getSessionInfo() {
        return {
            sessionId: this.sessionId,
            userId: this.userId,
            username: this.username,
            lastActivity: this.lastActivity,
            isAuthenticated: this.isAuthenticated()
        };
    }

    getTimeUntilExpiry() {
        if (!this.lastActivity) return 0;

        const timeElapsed = Date.now() - this.lastActivity;
        const timeRemaining = this.sessionTimeout - timeElapsed;

        return Math.max(0, timeRemaining);
    }

    async simulateAuthDelay() {
        // Simulate network delay for authentication
        const delay = Math.random() * 1000 + 500; // 500-1500ms
        await Utils.delay(delay);
    }

    // ========================================================================
    // PASSWORD UTILITIES
    // ========================================================================

    validatePassword(password) {
        return Utils.validatePassword(password);
    }

    generateSecurePassword(length = 12) {
        const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?';
        let password = '';

        for (let i = 0; i < length; i++) {
            password += charset.charAt(Math.floor(Math.random() * charset.length));
        }

        return password;
    }

    // ========================================================================
    // ROUTE PROTECTION
    // ========================================================================

    requireAuth() {
        if (!this.isAuthenticated()) {
            // Store current page for redirect after login
            Utils.setStorage('sqlAnalyzer_redirectAfterLogin', window.location.pathname);

            // Redirect to login
            window.location.href = '/';
            return false;
        }

        return true;
    }

    redirectAfterLogin() {
        const redirectPath = Utils.getStorage('sqlAnalyzer_redirectAfterLogin');
        Utils.removeStorage('sqlAnalyzer_redirectAfterLogin');

        // Notify app controller of successful authentication
        if (window.appController) {
            appController.handleAuthenticationSuccess();
        } else if (redirectPath && redirectPath !== '/') {
            window.location.href = redirectPath;
        } else {
            window.location.href = '/dashboard';
        }
    }
}

// Create global instance
window.authManager = new AuthManager();
window.AuthManager = AuthManager;
