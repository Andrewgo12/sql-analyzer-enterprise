/* ============================================================================
   SQL ANALYZER ENTERPRISE - API MODULE
   Centralized API communication with Python backend
   ============================================================================ */

class APIManager {
    constructor() {
        this.baseURL = window.location.origin + '/api';
        this.sessionId = null;
        this.defaultTimeout = 30000; // 30 seconds
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 second

        this.loadSession();
    }

    // ========================================================================
    // SESSION MANAGEMENT
    // ========================================================================

    loadSession() {
        try {
            this.sessionId = Utils.getStorage('sqlAnalyzer_sessionId');
            if (this.sessionId) {
                if (window.Utils) Utils.log('✅ Session loaded successfully');
            }
        } catch (error) {
            if (window.Utils) Utils.error('❌ Failed to load session:', error);
            this.sessionId = null;
        }
    }

    setSession(sessionId) {
        this.sessionId = sessionId;
        Utils.setStorage('sqlAnalyzer_sessionId', sessionId);
    }

    clearSession() {
        this.sessionId = null;
        Utils.removeStorage('sqlAnalyzer_sessionId');
        Utils.removeStorage('sqlAnalyzer_userId');
        Utils.removeStorage('sqlAnalyzer_username');
    }

    // ========================================================================
    // CORE API METHODS
    // ========================================================================

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: this.defaultTimeout
        };

        // Add session ID to headers if available
        if (this.sessionId) {
            defaultOptions.headers['X-Session-ID'] = this.sessionId;
        }

        const finalOptions = { ...defaultOptions, ...options };

        // Handle request body
        if (finalOptions.body && typeof finalOptions.body === 'object' && !(finalOptions.body instanceof FormData)) {
            finalOptions.body = JSON.stringify(finalOptions.body);
        }

        try {
            const response = await this.fetchWithTimeout(url, finalOptions);

            if (!response.ok) {
                await this.handleErrorResponse(response);
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
            Utils.logError(error, `API Request: ${endpoint}`);
            throw error;
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
    // WEBSOCKET CONNECTION
    // ========================================================================

    createWebSocket(onMessage = null, onError = null, onClose = null) {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/${this.sessionId}`;

        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            if (window.Utils) Utils.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (onMessage) onMessage(data);
            } catch (error) {
                if (window.Utils) Utils.error('WebSocket message parse error:', error);
            }
        };

        ws.onerror = (error) => {
            if (window.Utils) Utils.error('WebSocket error:', error);
            if (onError) onError(error);
        };

        ws.onclose = (event) => {
            if (window.Utils) Utils.log('WebSocket closed:', event.code, event.reason);
            if (onClose) onClose(event);
        };

        return ws;
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
