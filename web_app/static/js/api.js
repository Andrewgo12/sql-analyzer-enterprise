/* ============================================================================
   SQL ANALYZER ENTERPRISE - API MODULE
   Centralized API communication with Python backend
   ============================================================================ */

class APIManager {
    constructor() {
        this.baseURL = window.location.origin + '/api';
        this.defaultTimeout = 30000; // 30 seconds
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 second

        // Error throttling
        this.errorThrottle = new Map();
        this.maxErrorsPerMinute = 10;

        this.init();
    }

    async init() {
        // Wait for session manager to be ready
        if (window.SessionManager) {
            await window.SessionManager.init();
        }

        // Setup error handling
        this.setupErrorHandling();
    }

    // ========================================================================
    // SESSION MANAGEMENT (Delegated to SessionManager)
    // ========================================================================

    get sessionId() {
        return window.SessionManager ? window.SessionManager.sessionId : null;
    }

    async ensureValidSession() {
        if (window.SessionManager) {
            return await window.SessionManager.ensureValidSession();
        }
        return null;
    }

    getSessionHeaders() {
        if (window.SessionManager) {
            return window.SessionManager.getSessionHeaders();
        }
        return {};
    }

    // ========================================================================
    // ERROR HANDLING AND THROTTLING
    // ========================================================================

    setupErrorHandling() {
        // Global error handler for unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleGlobalError(event.reason);
        });

        // Global error handler for JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleGlobalError(event.error);
        });
    }

    handleGlobalError(error) {
        // Throttle error reporting
        if (this.shouldThrottleError(error)) {
            return;
        }

        console.error('Global error:', error);

        // Show user-friendly error message
        if (window.Utils) {
            Utils.showNotification('Se produjo un error inesperado. Por favor, inténtelo de nuevo.', 'error');
        }
    }

    shouldThrottleError(error) {
        const errorKey = error.message || error.toString();
        const now = Date.now();
        const minute = 60 * 1000;

        if (!this.errorThrottle.has(errorKey)) {
            this.errorThrottle.set(errorKey, []);
        }

        const errorTimes = this.errorThrottle.get(errorKey);

        // Remove errors older than 1 minute
        const recentErrors = errorTimes.filter(time => now - time < minute);
        this.errorThrottle.set(errorKey, recentErrors);

        // Check if we've exceeded the limit
        if (recentErrors.length >= this.maxErrorsPerMinute) {
            return true; // Throttle this error
        }

        // Add current error time
        recentErrors.push(now);
        return false;
    }

    showUserFriendlyError(error, context = '') {
        let message = 'Se produjo un error inesperado.';

        if (error.code === 'NETWORK_ERROR') {
            message = 'Error de conexión. Verifique su conexión a internet.';
        } else if (error.code === 'TIMEOUT') {
            message = 'La operación tardó demasiado tiempo. Inténtelo de nuevo.';
        } else if (error.code === 'UNAUTHORIZED') {
            message = 'Su sesión ha expirado. La página se recargará automáticamente.';
            setTimeout(() => window.location.reload(), 2000);
        } else if (error.code === 'FILE_TOO_LARGE') {
            message = 'El archivo es demasiado grande. El tamaño máximo permitido es 10GB.';
        } else if (error.code === 'INVALID_FILE_TYPE') {
            message = 'Tipo de archivo no válido. Solo se permiten archivos SQL y de texto.';
        }

        if (context) {
            message = `${context}: ${message}`;
        }

        if (window.Utils) {
            Utils.showNotification(message, 'error');
        }
    }

    // ========================================================================
    // CORE API METHODS
    // ========================================================================

    async request(endpoint, options = {}) {
        // Ensure we have a valid session
        await this.ensureValidSession();

        const url = `${this.baseURL}${endpoint}`;

        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...this.getSessionHeaders()
            },
            timeout: this.defaultTimeout
        };

        const finalOptions = { ...defaultOptions, ...options };

        // Merge headers properly
        if (options.headers) {
            finalOptions.headers = { ...defaultOptions.headers, ...options.headers };
        }

        // Handle request body
        if (finalOptions.body && typeof finalOptions.body === 'object' && !(finalOptions.body instanceof FormData)) {
            finalOptions.body = JSON.stringify(finalOptions.body);
        }

        try {
            const response = await this.fetchWithTimeout(url, finalOptions);

            if (!response.ok) {
                const error = await this.createErrorFromResponse(response);
                this.handleApiError(error);
                throw error;
            }

            // Handle different content types
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else if (contentType && contentType.includes('text/')) {
                return await response.text();
            } else {
                return await response.blob();
            }

        } catch (error) {
            if (!this.shouldThrottleError(error)) {
                console.error('API Request failed:', error);
                this.showUserFriendlyError(error, 'Error en la solicitud');
            }
            throw error;
        }
    }

    handleApiError(error) {
        if (window.SessionManager && (error.status === 401 || error.code === 'UNAUTHORIZED')) {
            window.SessionManager.handleSessionError(error);
        }
    }

    async fetchWithTimeout(url, options) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), options.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw Utils.createError('Request timeout', 'TIMEOUT_ERROR');
            }
            throw error;
        }
    }

    async handleErrorResponse(response) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        let errorCode = `HTTP_${response.status}`;
        let errorDetails = {};

        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
            errorCode = errorData.code || errorCode;
            errorDetails = errorData.details || {};
        } catch (e) {
            // Response is not JSON, use default error message
        }

        // Handle specific error codes
        if (response.status === 401) {
            this.clearSession();
            errorCode = 'UNAUTHORIZED';
            errorMessage = 'Session expired. Please sign in again.';
        } else if (response.status === 403) {
            errorCode = 'FORBIDDEN';
            errorMessage = 'Access denied.';
        } else if (response.status === 404) {
            errorCode = 'NOT_FOUND';
            errorMessage = 'Resource not found.';
        } else if (response.status >= 500) {
            errorCode = 'SERVER_ERROR';
            errorMessage = 'Server error. Please try again later.';
        }

        throw Utils.createError(errorMessage, errorCode, errorDetails);
    }

    // ========================================================================
    // AUTHENTICATION API
    // ========================================================================

    async createSession() {
        const response = await this.request('/auth/session', {
            method: 'POST'
        });

        if (response.session_id) {
            this.setSession(response.session_id);
            Utils.setStorage('sqlAnalyzer_userId', response.user_id);
        }

        return response;
    }

    async validateSession(sessionId = null) {
        const id = sessionId || this.sessionId;
        if (!id) return false;

        try {
            const response = await this.request(`/auth/session/${id}`);
            return response.valid === true;
        } catch (error) {
            if (error.code === 'UNAUTHORIZED') {
                this.clearSession();
            }
            return false;
        }
    }

    async refreshSession() {
        if (!this.sessionId) {
            return await this.createSession();
        }

        try {
            const response = await this.request('/auth/session/refresh', {
                method: 'POST'
            });

            if (response.session_id) {
                this.setSession(response.session_id);
            }

            return response;
        } catch (error) {
            // If refresh fails, create new session
            return await this.createSession();
        }
    }

    // ========================================================================
    // FILE UPLOAD API
    // ========================================================================

    async uploadFile(file, onProgress = null) {
        if (!this.sessionId) {
            await this.createSession();
        }

        const formData = new FormData();
        formData.append('file', file);

        const url = `${this.baseURL}/files/upload?session_id=${encodeURIComponent(this.sessionId)}`;

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // Handle progress
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete, e.loaded, e.total);
                    }
                });
            }

            // Handle completion
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (error) {
                        reject(Utils.createError('Invalid response format', 'PARSE_ERROR'));
                    }
                } else {
                    reject(Utils.createError(`Upload failed: ${xhr.statusText}`, `HTTP_${xhr.status}`));
                }
            });

            // Handle errors
            xhr.addEventListener('error', () => {
                reject(Utils.createError('Upload failed', 'NETWORK_ERROR'));
            });

            xhr.addEventListener('timeout', () => {
                reject(Utils.createError('Upload timeout', 'TIMEOUT_ERROR'));
            });

            // Configure and send request
            xhr.open('POST', url);
            xhr.timeout = 300000; // 5 minutes for large files
            xhr.send(formData);
        });
    }

    async getFileInfo(fileId) {
        return await this.request(`/files/${fileId}/info`);
    }

    async deleteFile(fileId) {
        return await this.request(`/files/${fileId}`, {
            method: 'DELETE'
        });
    }

    // ========================================================================
    // ANALYSIS API
    // ========================================================================

    async startAnalysis(fileId, options = {}) {
        const defaultOptions = {
            analysis_types: ['syntax', 'schema', 'security'],
            include_recommendations: true,
            detailed_errors: true
        };

        const analysisOptions = { ...defaultOptions, ...options };

        return await this.request('/analysis/start', {
            method: 'POST',
            body: {
                file_id: fileId,
                session_id: this.sessionId,
                ...analysisOptions
            }
        });
    }

    async getAnalysisStatus(analysisId) {
        return await this.request(`/analysis/${analysisId}/status`);
    }

    async getAnalysisResults(analysisId) {
        return await this.request(`/analysis/${analysisId}/results`);
    }

    async cancelAnalysis(analysisId) {
        return await this.request(`/analysis/${analysisId}/cancel`, {
            method: 'POST'
        });
    }

    // ========================================================================
    // RESULTS API
    // ========================================================================

    async exportResults(analysisId, format = 'html') {
        const response = await this.request(`/results/${analysisId}/export`, {
            method: 'POST',
            body: { format }
        });

        return response;
    }

    async shareResults(analysisId, options = {}) {
        return await this.request(`/results/${analysisId}/share`, {
            method: 'POST',
            body: options
        });
    }

    // ========================================================================
    // HISTORY API
    // ========================================================================

    async getAnalysisHistory(filters = {}) {
        const queryParams = new URLSearchParams();

        Object.keys(filters).forEach(key => {
            if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
                queryParams.append(key, filters[key]);
            }
        });

        const endpoint = `/history${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
        return await this.request(endpoint);
    }

    async deleteAnalysisHistory(analysisIds) {
        return await this.request('/history/delete', {
            method: 'POST',
            body: { analysis_ids: analysisIds }
        });
    }

    // ========================================================================
    // WEBSOCKET CONNECTION (Delegated to WebSocketManager)
    // ========================================================================

    createWebSocket(onMessage = null, onError = null, onClose = null) {
        if (!window.WebSocketManager) {
            console.error('WebSocketManager not available');
            return null;
        }

        // Register event handlers with the WebSocket manager
        if (onMessage) {
            window.WebSocketManager.on('message', onMessage);
        }

        if (onError) {
            window.WebSocketManager.on('error', onError);
        }

        if (onClose) {
            window.WebSocketManager.on('close', onClose);
        }

        // Return the WebSocket manager for compatibility
        return window.WebSocketManager;
    }

    // Enhanced WebSocket methods
    sendWebSocketMessage(message, requireAck = true) {
        if (window.WebSocketManager) {
            return window.WebSocketManager.sendMessage(message, requireAck);
        }
        return false;
    }

    getWebSocketStatus() {
        if (window.WebSocketManager) {
            return window.WebSocketManager.getStatus();
        }
        return { isConnected: false, isConnecting: false };
    }

    disconnectWebSocket() {
        if (window.WebSocketManager) {
            window.WebSocketManager.disconnect();
        }
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    async healthCheck() {
        try {
            const response = await this.request('/health');
            return response.status === 'ok';
        } catch (error) {
            return false;
        }
    }

    async getSystemInfo() {
        return await this.request('/system/info');
    }
}

// Create global instance
window.apiManager = new APIManager();
window.APIManager = APIManager;
