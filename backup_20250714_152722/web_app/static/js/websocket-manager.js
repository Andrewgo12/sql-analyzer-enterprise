/**
 * Enterprise WebSocket Manager
 * Handles WebSocket connections with automatic reconnection, error handling, and fallback mechanisms
 */

class WebSocketManager {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.isConnecting = false;
        this.shouldReconnect = true;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectIntervals = [1000, 2000, 4000, 8000, 16000]; // Exponential backoff
        this.reconnectTimer = null;
        this.pingTimer = null;
        this.lastPong = Date.now();
        
        // Message queues
        this.messageQueue = [];
        this.pendingMessages = new Map();
        this.messageId = 0;
        
        // Event handlers
        this.eventHandlers = {
            open: [],
            message: [],
            error: [],
            close: [],
            reconnect: [],
            fallback: []
        };
        
        // Configuration
        this.config = {
            pingInterval: 30000,        // 30 seconds
            pongTimeout: 10000,         // 10 seconds
            maxMessageQueue: 100,       // Maximum queued messages
            messageTimeout: 30000,      // Message response timeout
            fallbackEnabled: true,      // Enable HTTP polling fallback
            fallbackInterval: 5000      // HTTP polling interval
        };
        
        // Fallback mechanism
        this.fallbackActive = false;
        this.fallbackTimer = null;
        this.httpPollingEndpoint = '/api/events/poll';
        
        this.init();
    }
    
    async init() {
        // Listen for session events
        window.addEventListener('sqlAnalyzer:session-created', (event) => {
            this.connect();
        });
        
        window.addEventListener('sqlAnalyzer:session-cleared', (event) => {
            this.disconnect();
        });
        
        // Start connection if session exists
        if (window.SessionManager && window.SessionManager.sessionId) {
            this.connect();
        }
    }
    
    /**
     * Connect to WebSocket server
     */
    async connect() {
        if (this.isConnecting || this.isConnected) {
            return;
        }
        
        try {
            this.isConnecting = true;
            
            // Ensure we have a valid session
            await window.SessionManager.ensureValidSession();
            
            const sessionId = window.SessionManager.sessionId;
            if (!sessionId) {
                throw new Error('No valid session available');
            }
            
            // Construct WebSocket URL
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${sessionId}`;
            
            if (window.Utils) {
                Utils.log('🔌 Conectando WebSocket:', wsUrl.replace(sessionId, sessionId.substring(0, 8) + '...'));
            }
            
            // Create WebSocket connection
            this.ws = new WebSocket(wsUrl);
            this.setupEventHandlers();
            
        } catch (error) {
            this.isConnecting = false;
            this.handleConnectionError(error);
        }
    }
    
    /**
     * Setup WebSocket event handlers
     */
    setupEventHandlers() {
        this.ws.onopen = (event) => {
            this.isConnected = true;
            this.isConnecting = false;
            this.reconnectAttempts = 0;
            this.lastPong = Date.now();
            
            if (window.Utils) {
                Utils.log('✅ WebSocket conectado exitosamente');
            }
            
            // Start ping/pong mechanism
            this.startPingPong();
            
            // Process queued messages
            this.processMessageQueue();
            
            // Stop fallback if active
            this.stopFallback();
            
            // Notify handlers
            this.notifyHandlers('open', event);
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                // Handle pong messages
                if (data.type === 'pong') {
                    this.lastPong = Date.now();
                    return;
                }
                
                // Handle message acknowledgments
                if (data.type === 'ack' && data.messageId) {
                    this.handleMessageAck(data.messageId);
                    return;
                }
                
                // Notify message handlers
                this.notifyHandlers('message', data);
                
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
                if (window.Utils) {
                    Utils.error('Error al procesar mensaje WebSocket:', error);
                }
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.handleConnectionError(error);
        };
        
        this.ws.onclose = (event) => {
            this.isConnected = false;
            this.isConnecting = false;
            
            if (window.Utils) {
                Utils.log('🔌 WebSocket desconectado:', event.code, event.reason);
            }
            
            // Stop ping/pong
            this.stopPingPong();
            
            // Notify handlers
            this.notifyHandlers('close', event);
            
            // Attempt reconnection if needed
            if (this.shouldReconnect && event.code !== 1000) {
                this.scheduleReconnect();
            }
        };
    }
    
    /**
     * Handle connection errors
     */
    handleConnectionError(error) {
        this.isConnected = false;
        this.isConnecting = false;
        
        console.error('WebSocket connection error:', error);
        
        // Notify error handlers
        this.notifyHandlers('error', error);
        
        // Start fallback mechanism if enabled
        if (this.config.fallbackEnabled && !this.fallbackActive) {
            this.startFallback();
        }
        
        // Schedule reconnection
        if (this.shouldReconnect) {
            this.scheduleReconnect();
        }
    }
    
    /**
     * Schedule reconnection with exponential backoff
     */
    scheduleReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            if (window.Utils) {
                Utils.error('❌ Máximo número de intentos de reconexión alcanzado');
            }
            this.startFallback();
            return;
        }
        
        const intervalIndex = Math.min(this.reconnectAttempts, this.reconnectIntervals.length - 1);
        const delay = this.reconnectIntervals[intervalIndex];
        
        if (window.Utils) {
            Utils.log(`🔄 Reintentando conexión en ${delay}ms (intento ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
        }
        
        this.reconnectTimer = setTimeout(() => {
            this.reconnectAttempts++;
            this.notifyHandlers('reconnect', { attempt: this.reconnectAttempts });
            this.connect();
        }, delay);
    }
    
    /**
     * Start ping/pong mechanism
     */
    startPingPong() {
        this.stopPingPong();
        
        this.pingTimer = setInterval(() => {
            if (this.isConnected) {
                // Check if last pong was received within timeout
                if (Date.now() - this.lastPong > this.config.pongTimeout) {
                    if (window.Utils) {
                        Utils.error('❌ Ping timeout - reconectando...');
                    }
                    this.ws.close(1000, 'Ping timeout');
                    return;
                }
                
                // Send ping
                this.sendMessage({ type: 'ping', timestamp: Date.now() }, false);
            }
        }, this.config.pingInterval);
    }
    
    /**
     * Stop ping/pong mechanism
     */
    stopPingPong() {
        if (this.pingTimer) {
            clearInterval(this.pingTimer);
            this.pingTimer = null;
        }
    }
    
    /**
     * Send message through WebSocket
     */
    sendMessage(message, requireAck = true) {
        if (!this.isConnected) {
            // Queue message for later
            if (this.messageQueue.length < this.config.maxMessageQueue) {
                this.messageQueue.push({ message, requireAck, timestamp: Date.now() });
            }
            return false;
        }
        
        try {
            // Add message ID if acknowledgment is required
            if (requireAck) {
                message.messageId = ++this.messageId;
                this.pendingMessages.set(message.messageId, {
                    message,
                    timestamp: Date.now(),
                    timeout: setTimeout(() => {
                        this.handleMessageTimeout(message.messageId);
                    }, this.config.messageTimeout)
                });
            }
            
            this.ws.send(JSON.stringify(message));
            return true;
            
        } catch (error) {
            console.error('Error sending WebSocket message:', error);
            return false;
        }
    }
    
    /**
     * Process queued messages
     */
    processMessageQueue() {
        while (this.messageQueue.length > 0 && this.isConnected) {
            const { message, requireAck } = this.messageQueue.shift();
            this.sendMessage(message, requireAck);
        }
    }
    
    /**
     * Handle message acknowledgment
     */
    handleMessageAck(messageId) {
        const pending = this.pendingMessages.get(messageId);
        if (pending) {
            clearTimeout(pending.timeout);
            this.pendingMessages.delete(messageId);
        }
    }
    
    /**
     * Handle message timeout
     */
    handleMessageTimeout(messageId) {
        const pending = this.pendingMessages.get(messageId);
        if (pending) {
            console.error('Message timeout:', pending.message);
            this.pendingMessages.delete(messageId);
            
            // Optionally retry the message
            this.sendMessage(pending.message, true);
        }
    }
    
    /**
     * Start HTTP polling fallback
     */
    startFallback() {
        if (this.fallbackActive || !this.config.fallbackEnabled) {
            return;
        }
        
        this.fallbackActive = true;
        
        if (window.Utils) {
            Utils.log('🔄 Iniciando mecanismo de respaldo HTTP polling');
        }
        
        this.notifyHandlers('fallback', { active: true });
        
        this.fallbackTimer = setInterval(async () => {
            try {
                const response = await fetch(this.httpPollingEndpoint, {
                    method: 'GET',
                    headers: window.SessionManager.getSessionHeaders()
                });
                
                if (response.ok) {
                    const events = await response.json();
                    if (events && events.length > 0) {
                        events.forEach(event => {
                            this.notifyHandlers('message', event);
                        });
                    }
                }
                
            } catch (error) {
                console.error('HTTP polling error:', error);
            }
        }, this.config.fallbackInterval);
    }
    
    /**
     * Stop HTTP polling fallback
     */
    stopFallback() {
        if (!this.fallbackActive) {
            return;
        }
        
        this.fallbackActive = false;
        
        if (this.fallbackTimer) {
            clearInterval(this.fallbackTimer);
            this.fallbackTimer = null;
        }
        
        if (window.Utils) {
            Utils.log('✅ Mecanismo de respaldo desactivado');
        }
        
        this.notifyHandlers('fallback', { active: false });
    }
    
    /**
     * Disconnect WebSocket
     */
    disconnect() {
        this.shouldReconnect = false;
        
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        this.stopPingPong();
        this.stopFallback();
        
        if (this.ws) {
            this.ws.close(1000, 'Manual disconnect');
            this.ws = null;
        }
        
        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        
        // Clear message queues
        this.messageQueue = [];
        this.pendingMessages.clear();
    }
    
    /**
     * Add event handler
     */
    on(event, handler) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].push(handler);
        }
    }
    
    /**
     * Remove event handler
     */
    off(event, handler) {
        if (this.eventHandlers[event]) {
            const index = this.eventHandlers[event].indexOf(handler);
            if (index > -1) {
                this.eventHandlers[event].splice(index, 1);
            }
        }
    }
    
    /**
     * Notify event handlers
     */
    notifyHandlers(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in ${event} handler:`, error);
                }
            });
        }
    }
    
    /**
     * Get connection status
     */
    getStatus() {
        return {
            isConnected: this.isConnected,
            isConnecting: this.isConnecting,
            reconnectAttempts: this.reconnectAttempts,
            fallbackActive: this.fallbackActive,
            queuedMessages: this.messageQueue.length,
            pendingMessages: this.pendingMessages.size
        };
    }
}

// Create global WebSocket manager instance
window.WebSocketManager = new WebSocketManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketManager;
}
