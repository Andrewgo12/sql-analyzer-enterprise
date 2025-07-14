/* ============================================================================
   SQL ANALYZER ENTERPRISE - ANALYSIS MODULE
   Analysis management, start/stop/cancel operations, real-time monitoring
   ============================================================================ */

class AnalysisManager {
    constructor() {
        this.activeAnalyses = new Map();
        this.analysisHistory = [];
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 5000;

        this.init();
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    init() {
        this.loadAnalysisHistory();
        this.setupWebSocket();
        this.setupEventListeners();
    }

    loadAnalysisHistory() {
        this.analysisHistory = Utils.getStorage('sqlAnalyzer_analysisHistory', []);
    }

    saveAnalysisHistory() {
        Utils.setStorage('sqlAnalyzer_analysisHistory', this.analysisHistory);
    }

    setupEventListeners() {
        // Listen for page visibility changes to handle reconnection
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && !this.websocket) {
                this.setupWebSocket();
            }
        });

        // Listen for online/offline events
        window.addEventListener('online', () => {
            if (!this.websocket) {
                this.setupWebSocket();
            }
        });

        window.addEventListener('offline', () => {
            this.closeWebSocket();
        });
    }

    // ========================================================================
    // WEBSOCKET MANAGEMENT
    // ========================================================================

    setupWebSocket() {
        // Simplified - no authentication required for basic functionality
        if (false) { // Disable WebSocket for simplified version
            return;
        }

        try {
            this.websocket = apiManager.createWebSocket(
                (data) => this.handleWebSocketMessage(data),
                (error) => this.handleWebSocketError(error),
                (event) => this.handleWebSocketClose(event)
            );
        } catch (error) {
            Utils.logError(error, 'WebSocket setup failed');
            this.scheduleReconnect();
        }
    }

    closeWebSocket() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'analysis_progress':
                this.updateAnalysisProgress(data.analysis_id, data.progress);
                break;
            case 'analysis_complete':
                this.handleAnalysisComplete(data.analysis_id, data.results);
                break;
            case 'analysis_error':
                this.handleAnalysisError(data.analysis_id, data.error);
                break;
            case 'analysis_cancelled':
                this.handleAnalysisCancelled(data.analysis_id);
                break;
            default:
                if (window.Utils) Utils.log('Unknown WebSocket message type:', data.type);
        }
    }

    handleWebSocketError(error) {
        Utils.logError(error, 'WebSocket error');
        this.scheduleReconnect();
    }

    handleWebSocketClose(event) {
        if (window.Utils) Utils.log('WebSocket closed:', event.code, event.reason);
        this.websocket = null;

        if (event.code !== 1000) { // Not a normal closure
            this.scheduleReconnect();
        }
    }

    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            if (window.Utils) Utils.error('Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff

        setTimeout(() => {
            if (!this.websocket) {
                this.setupWebSocket();
            }
        }, delay);
    }

    // ========================================================================
    // ANALYSIS OPERATIONS
    // ========================================================================

    async startAnalysis(fileId, options = {}) {
        try {
            // Validate inputs
            if (!fileId) {
                throw Utils.createError('File ID is required', 'VALIDATION_ERROR');
            }

            // Simplified - no authentication required for basic functionality

            // Prepare analysis options
            const defaultOptions = {
                analysis_types: ['syntax', 'schema', 'security'],
                include_recommendations: true,
                detailed_errors: true,
                generate_visualizations: true
            };

            const analysisOptions = { ...defaultOptions, ...options };

            // Start the analysis
            const response = await apiManager.startAnalysis(fileId, analysisOptions);

            if (!response.analysis_id) {
                throw Utils.createError('Invalid analysis response', 'API_ERROR');
            }

            // Create analysis tracking object
            const analysis = {
                id: response.analysis_id,
                fileId: fileId,
                fileName: response.file_name || 'Unknown',
                status: 'starting',
                progress: 0,
                startTime: Date.now(),
                endTime: null,
                options: analysisOptions,
                results: null,
                error: null
            };

            // Add to active analyses
            this.activeAnalyses.set(analysis.id, analysis);

            // Update UI
            this.showAnalysisProgress(analysis);
            this.updateAnalysisDisplay();

            // Show notification
            if (window.showNotification) {
                showNotification(`Analysis started for ${analysis.fileName}`, 'info');
            }

            return analysis;

        } catch (error) {
            Utils.logError(error, 'Start analysis failed');

            if (window.showNotification) {
                showNotification(`Failed to start analysis: ${error.message}`, 'error');
            }

            throw error;
        }
    }

    async cancelAnalysis(analysisId) {
        try {
            const analysis = this.activeAnalyses.get(analysisId);
            if (!analysis) {
                throw Utils.createError('Analysis not found', 'NOT_FOUND');
            }

            // Call API to cancel
            await apiManager.cancelAnalysis(analysisId);

            // Update local state
            analysis.status = 'cancelling';
            this.updateAnalysisProgress(analysisId, analysis.progress);

            if (window.showNotification) {
                showNotification(`Cancelling analysis for ${analysis.fileName}`, 'info');
            }

        } catch (error) {
            Utils.logError(error, 'Cancel analysis failed');

            if (window.showNotification) {
                showNotification(`Failed to cancel analysis: ${error.message}`, 'error');
            }

            throw error;
        }
    }

    async getAnalysisStatus(analysisId) {
        try {
            const response = await apiManager.getAnalysisStatus(analysisId);

            // Update local analysis object
            const analysis = this.activeAnalyses.get(analysisId);
            if (analysis) {
                analysis.status = response.status;
                analysis.progress = response.progress || analysis.progress;

                if (response.status === 'completed' || response.status === 'failed') {
                    analysis.endTime = Date.now();
                }

                this.updateAnalysisProgress(analysisId, analysis.progress);
            }

            return response;

        } catch (error) {
            Utils.logError(error, 'Get analysis status failed');
            throw error;
        }
    }

    async getAnalysisResults(analysisId) {
        try {
            const response = await apiManager.getAnalysisResults(analysisId);

            // Update local analysis object
            const analysis = this.activeAnalyses.get(analysisId);
            if (analysis) {
                analysis.results = response;
                analysis.status = 'completed';
                analysis.endTime = Date.now();
            }

            return response;

        } catch (error) {
            Utils.logError(error, 'Get analysis results failed');
            throw error;
        }
    }

    // ========================================================================
    // PROGRESS TRACKING
    // ========================================================================

    updateAnalysisProgress(analysisId, progress) {
        const analysis = this.activeAnalyses.get(analysisId);
        if (!analysis) return;

        analysis.progress = progress;

        // Update progress UI
        this.updateProgressDisplay(analysis);

        // Update analysis display
        this.updateAnalysisDisplay();
    }

    handleAnalysisComplete(analysisId, results) {
        const analysis = this.activeAnalyses.get(analysisId);
        if (!analysis) return;

        analysis.status = 'completed';
        analysis.progress = 100;
        analysis.endTime = Date.now();
        analysis.results = results;

        // Move to history
        this.moveToHistory(analysis);

        // Update UI
        this.hideAnalysisProgress(analysisId);
        this.updateAnalysisDisplay();

        // Show completion notification
        if (window.showNotification) {
            showNotification(`Analysis completed for ${analysis.fileName}`, 'success');
        }

        // Auto-navigate to results if this is the only active analysis
        if (this.activeAnalyses.size === 0) {
            this.navigateToResults(analysisId);
        }
    }

    handleAnalysisError(analysisId, error) {
        const analysis = this.activeAnalyses.get(analysisId);
        if (!analysis) return;

        analysis.status = 'failed';
        analysis.endTime = Date.now();
        analysis.error = error;

        // Move to history
        this.moveToHistory(analysis);

        // Update UI
        this.hideAnalysisProgress(analysisId);
        this.updateAnalysisDisplay();

        // Show error notification
        if (window.showNotification) {
            showNotification(`Analysis failed for ${analysis.fileName}: ${error.message}`, 'error');
        }
    }

    handleAnalysisCancelled(analysisId) {
        const analysis = this.activeAnalyses.get(analysisId);
        if (!analysis) return;

        analysis.status = 'cancelled';
        analysis.endTime = Date.now();

        // Move to history
        this.moveToHistory(analysis);

        // Update UI
        this.hideAnalysisProgress(analysisId);
        this.updateAnalysisDisplay();

        // Show cancellation notification
        if (window.showNotification) {
            showNotification(`Analysis cancelled for ${analysis.fileName}`, 'info');
        }
    }

    // ========================================================================
    // UI MANAGEMENT
    // ========================================================================

    showAnalysisProgress(analysis) {
        const progressContainer = this.getOrCreateProgressContainer();

        const progressElement = Utils.createElement('div', {
            className: 'analysis-progress-item',
            id: `analysis-progress-${analysis.id}`
        });

        progressElement.innerHTML = `
            <div class="analysis-info">
                <div class="analysis-filename">
                    <i class="fas fa-cogs me-2"></i>
                    Analyzing: ${Utils.sanitizeHtml(analysis.fileName)}
                </div>
                <div class="analysis-types">
                    ${analysis.options.analysis_types.map(type =>
            `<span class="badge bg-secondary me-1">${Utils.capitalizeFirst(type)}</span>`
        ).join('')}
                </div>
            </div>
            <div class="analysis-progress">
                <div class="progress-bar" style="width: ${analysis.progress}%"></div>
                <div class="progress-text">${analysis.progress}%</div>
            </div>
            <div class="analysis-actions">
                <button class="btn-cancel" onclick="analysisManager.cancelAnalysis('${analysis.id}')">
                    <i class="fas fa-stop"></i> Cancel
                </button>
            </div>
        `;

        progressContainer.appendChild(progressElement);
        this.showProgressContainer();
    }

    updateProgressDisplay(analysis) {
        const progressElement = document.getElementById(`analysis-progress-${analysis.id}`);
        if (!progressElement) return;

        const progressBar = progressElement.querySelector('.progress-bar');
        const progressText = progressElement.querySelector('.progress-text');

        if (progressBar) {
            progressBar.style.width = `${analysis.progress}%`;
        }

        if (progressText) {
            progressText.textContent = `${analysis.progress}%`;
        }

        // Update status-specific styling
        progressElement.className = `analysis-progress-item status-${analysis.status}`;
    }

    hideAnalysisProgress(analysisId) {
        const progressElement = document.getElementById(`analysis-progress-${analysisId}`);
        if (progressElement) {
            // Fade out animation
            progressElement.style.opacity = '0';
            setTimeout(() => {
                progressElement.remove();
                this.hideProgressContainerIfEmpty();
            }, 300);
        }
    }

    getOrCreateProgressContainer() {
        let container = document.getElementById('analysis-progress-container');
        if (!container) {
            container = Utils.createElement('div', {
                id: 'analysis-progress-container',
                className: 'analysis-progress-container'
            });

            // Insert after the upload area
            const uploadArea = document.getElementById('upload-area');
            if (uploadArea) {
                uploadArea.parentNode.insertBefore(container, uploadArea.nextSibling);
            } else {
                document.body.appendChild(container);
            }
        }
        return container;
    }

    showProgressContainer() {
        const container = document.getElementById('analysis-progress-container');
        if (container) {
            container.style.display = 'block';
        }
    }

    hideProgressContainerIfEmpty() {
        const container = document.getElementById('analysis-progress-container');
        if (container && container.children.length === 0) {
            container.style.display = 'none';
        }
    }

    updateAnalysisDisplay() {
        // Update analysis count in UI
        const analysisCountElement = document.getElementById('analyses-count');
        if (analysisCountElement) {
            analysisCountElement.textContent = this.analysisHistory.length;
        }

        // Update active analysis indicator
        const activeCount = this.activeAnalyses.size;
        const statusElement = document.getElementById('analysis-status');
        if (statusElement) {
            if (activeCount > 0) {
                statusElement.textContent = `${activeCount} Running`;
                statusElement.className = 'badge bg-warning';
            } else {
                statusElement.textContent = 'Ready';
                statusElement.className = 'badge bg-success';
            }
        }
    }

    // ========================================================================
    // HISTORY MANAGEMENT
    // ========================================================================

    moveToHistory(analysis) {
        // Remove from active analyses
        this.activeAnalyses.delete(analysis.id);

        // Add to history
        this.analysisHistory.unshift({
            id: analysis.id,
            fileId: analysis.fileId,
            fileName: analysis.fileName,
            status: analysis.status,
            startTime: analysis.startTime,
            endTime: analysis.endTime,
            processingTime: analysis.endTime - analysis.startTime,
            options: analysis.options,
            results: analysis.results,
            error: analysis.error,
            timestamp: new Date().toISOString()
        });

        // Keep only last 100 analyses
        if (this.analysisHistory.length > 100) {
            this.analysisHistory.splice(100);
        }

        // Save to storage
        this.saveAnalysisHistory();
    }

    getAnalysisFromHistory(analysisId) {
        return this.analysisHistory.find(analysis => analysis.id === analysisId);
    }

    deleteFromHistory(analysisIds) {
        const idsToDelete = Array.isArray(analysisIds) ? analysisIds : [analysisIds];

        this.analysisHistory = this.analysisHistory.filter(
            analysis => !idsToDelete.includes(analysis.id)
        );

        this.saveAnalysisHistory();
        this.updateAnalysisDisplay();
    }

    clearHistory() {
        this.analysisHistory = [];
        this.saveAnalysisHistory();
        this.updateAnalysisDisplay();
    }

    // ========================================================================
    // NAVIGATION HELPERS
    // ========================================================================

    navigateToResults(analysisId) {
        // Check if we're already on the results page
        if (window.location.pathname === '/results') {
            // Update the results view with new analysis
            if (window.resultsManager) {
                resultsManager.loadAnalysis(analysisId);
            }
        } else {
            // Navigate to results page
            window.location.href = `/results?id=${analysisId}`;
        }
    }

    // ========================================================================
    // PUBLIC API
    // ========================================================================

    getActiveAnalyses() {
        return Array.from(this.activeAnalyses.values());
    }

    getAnalysisHistory() {
        return [...this.analysisHistory];
    }

    isAnalysisActive(analysisId) {
        return this.activeAnalyses.has(analysisId);
    }

    getAnalysisById(analysisId) {
        return this.activeAnalyses.get(analysisId) || this.getAnalysisFromHistory(analysisId);
    }

    cancelAllAnalyses() {
        const activeIds = Array.from(this.activeAnalyses.keys());
        return Promise.all(activeIds.map(id => this.cancelAnalysis(id)));
    }
}

// Create global instance
window.analysisManager = new AnalysisManager();
window.AnalysisManager = AnalysisManager;
