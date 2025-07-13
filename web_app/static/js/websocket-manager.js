/* ============================================================================
   SQL ANALYZER ENTERPRISE - WEBSOCKET MANAGER
   Comprehensive WebSocket client for real-time communication
   ============================================================================ */

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.sessionId = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        this.messageQueue = [];
        this.subscriptions = new Set();
        this.eventHandlers = new Map();
        
        // Heartbeat configuration
        this.heartbeatInterval = null;
        this.heartbeatTimeout = null;
        this.heartbeatDelay = 30000; // 30 seconds
        
        this.init();
    }
    
    init() {
        this.sessionId = this.generateSessionId();
        this.setupEventHandlers();
        if (window.Utils) Utils.log('🔌 WebSocket Manager initialized with session:', this.sessionId);
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
    }
    
    connect() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            if (window.Utils) Utils.log('🔌 WebSocket already connected');
            return;
        }
        
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;
            
            if (window.Utils) Utils.log('🔌 Connecting to WebSocket:', wsUrl);
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = this.handleOpen.bind(this);
            this.socket.onmessage = this.handleMessage.bind(this);
            this.socket.onclose = this.handleClose.bind(this);
            this.socket.onerror = this.handleError.bind(this);
            
        } catch (error) {
            if (window.Utils) Utils.error('❌ WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }
    
    handleOpen(event) {
        if (window.Utils) Utils.log('✅ WebSocket connected successfully');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        // Process queued messages
        this.processMessageQueue();
        
        // Start heartbeat
        this.startHeartbeat();
        
        // Notify listeners
        this.emit('connected', { sessionId: this.sessionId });
        
        // Show connection notification
        if (window.showNotification) {
            showNotification('Conexión en tiempo real establecida', 'success', 3000);
        }
    }
    
    handleMessage(event) {
        try {
            const message = JSON.parse(event.data);
            if (window.Utils) Utils.log('📨 WebSocket message received:', message.type);
            
            // Handle system messages
            this.handleSystemMessage(message);
            
            // Emit to listeners
            this.emit(message.type, message);
            
        } catch (error) {
            if (window.Utils) Utils.error('❌ Error parsing WebSocket message:', error);
        }
    }
    
    handleSystemMessage(message) {
        switch (message.type) {
            case 'connection_established':
                if (window.Utils) Utils.log('🎉 Connection established:', message.server_info);
                break;
                
            case 'pong':
                // Reset heartbeat timeout
                if (this.heartbeatTimeout) {
                    clearTimeout(this.heartbeatTimeout);
                }
                break;
                
            case 'analysis_progress':
                this.handleAnalysisProgress(message);
                break;
                
            case 'analysis_complete':
                this.handleAnalysisComplete(message);
                break;
                
            case 'system_status':
                this.handleSystemStatus(message);
                break;
                
            case 'error':
                if (window.Utils) Utils.error('🚨 Server error:', message.message);
                if (window.showNotification) {
                    showNotification(`Error del servidor: ${message.message}`, 'error');
                }
                break;
        }
    }
    
    handleAnalysisProgress(message) {
        const { analysis_id, progress, status, message: progressMessage } = message;
        
        // Update progress bars
        const progressBar = document.querySelector(`[data-analysis-id="${analysis_id}"] .progress-bar`);
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.textContent = `${progress}%`;
        }
        
        // Update status text
        const statusElement = document.querySelector(`[data-analysis-id="${analysis_id}"] .status-text`);
        if (statusElement) {
            statusElement.textContent = progressMessage || `${progress}% completado`;
        }
        
        // Show notification for major milestones
        if (progress === 25 || progress === 50 || progress === 75) {
            if (window.showNotification) {
                showNotification(`Análisis ${progress}% completado`, 'info', 2000);
            }
        }
    }
    
    handleAnalysisComplete(message) {
        const { analysis_id, results } = message;
        
        // Update UI to show completion
        const analysisElement = document.querySelector(`[data-analysis-id="${analysis_id}"]`);
        if (analysisElement) {
            analysisElement.classList.add('analysis-complete');
            
            const progressBar = analysisElement.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = '100%';
                progressBar.textContent = 'Completado';
                progressBar.classList.add('bg-success');
            }
        }
        
        // Show completion notification
        if (window.showNotification) {
            showNotification('¡Análisis completado exitosamente!', 'success');
        }
        
        // Auto-navigate to results if on upload page
        if (window.appController && window.appController.currentView === 'upload') {
            setTimeout(() => {
                if (confirm('Análisis completado. ¿Deseas ver los resultados?')) {
                    window.appController.navigateToView('results');
                }
            }, 2000);
        }
    }
    
    handleSystemStatus(message) {
        const { data } = message;
        
        // Update system status indicators
        const statusElements = {
            'active-analyses': data.active_analyses,
            'uploaded-files': data.uploaded_files,
            'websocket-connections': data.websocket_connections
        };
        
        Object.entries(statusElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }
    
    handleClose(event) {
        if (window.Utils) Utils.log('🔌 WebSocket connection closed:', event.code, event.reason);
        this.isConnected = false;
        
        // Stop heartbeat
        this.stopHeartbeat();
        
        // Notify listeners
        this.emit('disconnected', { code: event.code, reason: event.reason });
        
        // Show disconnection notification
        if (window.showNotification) {
            showNotification('Conexión en tiempo real perdida', 'warning');
        }
        
        // Schedule reconnection if not intentional
        if (event.code !== 1000) {
            this.scheduleReconnect();
        }
    }
    
    handleError(error) {
        if (window.Utils) Utils.error('❌ WebSocket error:', error);
        this.emit('error', error);
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            if (window.Utils) Utils.error('❌ Max reconnection attempts reached');
            if (window.showNotification) {
                showNotification('No se pudo restablecer la conexión en tiempo real', 'error');
            }
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        if (window.Utils) Utils.log(`🔄 Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);
        
        setTimeout(() => {
            this.connect();
        }, delay);
    }
    
    send(message) {
        if (this.isConnected && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            // Queue message for later
            this.messageQueue.push(message);
            if (window.Utils) Utils.log('📤 Message queued (not connected):', message.type);
        }
    }
    
    processMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.send(message);
        }
    }
    
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'ping', timestamp: new Date().toISOString() });
                
                // Set timeout for pong response
                this.heartbeatTimeout = setTimeout(() => {
                    if (window.Utils) Utils.warn('⚠️ Heartbeat timeout - connection may be lost');
                    this.socket.close();
                }, 5000);
            }
        }, this.heartbeatDelay);
    }
    
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
        
        if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
            this.heartbeatTimeout = null;
        }
    }
    
    // Event system
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }
    
    off(event, handler) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }
    
    emit(event, data) {
        if (this.eventHandlers.has(event)) {
            this.eventHandlers.get(event).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    if (window.Utils) Utils.error(`❌ Error in event handler for ${event}:`, error);
                }
            });
        }
    }
    
    // Convenience methods
    subscribeToAnalysis(analysisId) {
        this.subscriptions.add(analysisId);
        this.send({
            type: 'subscribe_analysis',
            analysis_id: analysisId
        });
    }
    
    unsubscribeFromAnalysis(analysisId) {
        this.subscriptions.delete(analysisId);
        this.send({
            type: 'unsubscribe_analysis',
            analysis_id: analysisId
        });
    }
    
    requestSystemStatus() {
        this.send({ type: 'get_system_status' });
    }
    
    requestAnalysisHistory() {
        this.send({ type: 'get_analysis_history' });
    }
    
    requestFileList() {
        this.send({ type: 'request_file_list' });
    }
    
    setupEventHandlers() {
        // Setup default event handlers
        this.on('connected', () => {
            if (window.Utils) Utils.log('🎉 WebSocket event: Connected');
        });
        
        this.on('disconnected', () => {
            if (window.Utils) Utils.log('👋 WebSocket event: Disconnected');
        });
        
        this.on('error', (error) => {
            if (window.Utils) Utils.error('🚨 WebSocket event: Error', error);
        });
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.close(1000, 'Client disconnect');
        }
    }
    
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            sessionId: this.sessionId,
            reconnectAttempts: this.reconnectAttempts,
            subscriptions: Array.from(this.subscriptions),
            queuedMessages: this.messageQueue.length
        };
    }
}

// Make WebSocketManager globally available
window.WebSocketManager = WebSocketManager;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (!window.wsManager) {
        window.wsManager = new WebSocketManager();
        
        // Auto-connect after a brief delay
        setTimeout(() => {
            window.wsManager.connect();
        }, 1000);
        
        if (window.Utils) Utils.log('✅ WebSocket Manager auto-initialized');
    }
});
