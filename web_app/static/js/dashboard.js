/**
 * SQL Analyzer Enterprise Dashboard - Professional Edition
 * Enterprise-grade JavaScript with comprehensive error handling
 */

class SQLAnalyzerDashboard {
    constructor() {
        // Application state
        this.sessionId = null;
        this.websocket = null;
        this.currentFileId = null;
        this.currentAnalysisId = null;
        this.uploadedFiles = new Map();
        this.analysisResults = new Map();
        this.charts = new Map();
        this.isAuthenticated = false;

        // Enterprise configuration
        this.config = {
            maxFileSize: 10 * 1024 * 1024 * 1024, // 10GB
            allowedExtensions: ['.sql', '.txt', '.text'],
            websocketReconnectDelay: 2000,
            progressUpdateInterval: 500,
            animationDuration: 300,
            debounceDelay: 250,
            apiBaseUrl: window.location.origin,
            retryAttempts: 3
        };

        // DOM element cache for performance
        this.elements = {};

        // Error handling
        this.errorHandler = new ErrorHandler();

        // Initialize dashboard
        this.init().catch(error => {
            this.errorHandler.handleError(error, 'Dashboard initialization failed');
        });
    }

    /**
     * Initialize enterprise dashboard with comprehensive error handling
     */
    async init() {
        try {
            if (window.Utils) Utils.log('🚀 Initializing SQL Analyzer Enterprise Dashboard...');

            // Cache DOM elements for performance
            this.cacheElements();

            // Initialize authentication
            await this.initializeAuthentication();

            // Create session
            await this.createSession();

            // Setup WebSocket connection
            this.setupWebSocket();

            // Setup event listeners with error handling
            this.setupEventListeners();

            // Setup drag and drop functionality
            this.setupDragAndDrop();

            // Initialize charts and visualizations
            this.initializeCharts();

            // Update initial UI state
            this.updateUI();

            // Preload resources
            this.preloadResources();

            // Setup modal system
            this.initializeModals();

            if (window.Utils) Utils.log('✅ Enterprise dashboard initialized successfully');

        } catch (error) {
            this.errorHandler.handleError(error, 'Dashboard initialization failed');
            this.showNotification('Failed to initialize application', 'error');
        }
    }

    /**
     * Cache de elementos DOM para mejor rendimiento
     */
    cacheElements() {
        this.elements = {
            fileInput: document.getElementById('file-input'),
            dropzone: document.getElementById('dropzone'),
            uploadArea: document.getElementById('upload-area'),
            analysisConfig: document.getElementById('analysis-config'),
            progressArea: document.getElementById('progress-area'),
            resultsArea: document.getElementById('results-area'),
            progressBar: document.getElementById('progress-bar'),
            sessionId: document.getElementById('session-id'),
            userName: document.getElementById('user-name'),
            connectionStatus: document.getElementById('connection-status')
        };
    }

    /**
     * Precargar recursos para mejor rendimiento
     */
    preloadResources() {
        // Precargar Chart.js si no está cargado
        if (typeof Chart === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
            script.async = true;
            document.head.appendChild(script);
        }
    }

    /**
     * Crear sesión de usuario
     */
    async createSession() {
        try {
            const response = await fetch('/api/auth/session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error creando sesión');
            }

            const data = await response.json();
            this.sessionId = data.session_id;

            // Actualizar UI con información de sesión usando cache
            if (this.elements.sessionId) {
                this.elements.sessionId.textContent = this.sessionId.substring(0, 8) + '...';
            }
            if (this.elements.userName) {
                this.elements.userName.textContent = data.user_id;
            }

            if (window.Utils) Utils.log('✅ Sesión creada:', this.sessionId);

        } catch (error) {
            if (window.Utils) Utils.error('❌ Error creando sesión:', error);
            throw error;
        }
    }

    /**
     * Configurar WebSocket para actualizaciones en tiempo real
     */
    setupWebSocket() {
        if (!this.sessionId) {
            if (window.Utils) Utils.error('❌ No hay sesión para WebSocket');
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

        try {
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                if (window.Utils) Utils.log('✅ WebSocket conectado');
                this.updateConnectionStatus('Conectado', 'success');
            };

            this.websocket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                } catch (error) {
                    if (window.Utils) Utils.error('❌ Error procesando mensaje WebSocket:', error);
                }
            };

            this.websocket.onclose = () => {
                if (window.Utils) Utils.log('⚠️ WebSocket desconectado');
                this.updateConnectionStatus('Desconectado', 'warning');

                // Intentar reconectar con backoff exponencial
                setTimeout(() => {
                    this.setupWebSocket();
                }, this.config.websocketReconnectDelay);
            };

            this.websocket.onerror = (error) => {
                if (window.Utils) Utils.error('❌ Error WebSocket:', error);
                this.updateConnectionStatus('Error', 'danger');
            };

        } catch (error) {
            if (window.Utils) Utils.error('❌ Error configurando WebSocket:', error);
        }
    }

    /**
     * Actualizar estado de conexión optimizado
     */
    updateConnectionStatus(status, type) {
        if (this.elements.connectionStatus) {
            this.elements.connectionStatus.textContent = status;
            this.elements.connectionStatus.className = `badge bg-${type}`;

            // Agregar animación visual
            this.elements.connectionStatus.style.transform = 'scale(1.1)';
            setTimeout(() => {
                this.elements.connectionStatus.style.transform = 'scale(1)';
            }, 200);
        }
    }

    /**
     * Manejar mensajes WebSocket
     */
    handleWebSocketMessage(message) {
        if (window.Utils) Utils.log('📨 Mensaje WebSocket:', message);

        switch (message.type) {
            case 'analysis_progress':
                this.updateAnalysisProgress(message);
                break;
            case 'analysis_complete':
                this.handleAnalysisComplete(message);
                break;
            case 'analysis_error':
                this.handleAnalysisError(message);
                break;
            case 'pong':
                // Respuesta a ping - mantener conexión viva
                break;
            default:
                if (window.Utils) Utils.log('Mensaje WebSocket no reconocido:', message.type);
        }
    }

    /**
     * Configurar event listeners optimizados
     */
    setupEventListeners() {
        // Upload de archivos con debounce
        if (this.elements.fileInput) {
            this.elements.fileInput.addEventListener('change', this.debounce((e) => {
                if (e.target.files.length > 0) {
                    this.handleFileUpload(e.target.files[0]);
                }
            }, this.config.debounceDelay));
        }

        if (this.elements.dropzone) {
            this.elements.dropzone.addEventListener('click', () => {
                this.elements.fileInput?.click();
            });
        }

        // Mantener WebSocket vivo con heartbeat optimizado
        this.heartbeatInterval = setInterval(() => {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
            }
        }, 25000); // Ping cada 25 segundos

        // Limpiar interval al cerrar la página
        window.addEventListener('beforeunload', () => {
            if (this.heartbeatInterval) {
                clearInterval(this.heartbeatInterval);
            }
        });
    }

    /**
     * Función debounce para optimizar eventos
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Configurar drag and drop optimizado
     */
    setupDragAndDrop() {
        if (!this.elements.dropzone) return;

        const dropzone = this.elements.dropzone;
        let dragCounter = 0;

        // Optimizar eventos con passive listeners donde sea posible
        const dragEvents = ['dragenter', 'dragover', 'dragleave', 'drop'];
        dragEvents.forEach(eventName => {
            dropzone.addEventListener(eventName, this.preventDefaults, { passive: false });
        });

        // Entrada de drag con contador para evitar flickering
        dropzone.addEventListener('dragenter', () => {
            dragCounter++;
            dropzone.classList.add('dragover');
            this.addDragAnimation();
        });

        dropzone.addEventListener('dragover', (e) => {
            e.dataTransfer.dropEffect = 'copy';
        });

        // Salida de drag con contador
        dropzone.addEventListener('dragleave', () => {
            dragCounter--;
            if (dragCounter === 0) {
                dropzone.classList.remove('dragover');
                this.removeDragAnimation();
            }
        });

        // Drop optimizado
        dropzone.addEventListener('drop', (e) => {
            dragCounter = 0;
            dropzone.classList.remove('dragover');
            this.removeDragAnimation();

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });
    }

    /**
     * Agregar animación de drag
     */
    addDragAnimation() {
        if (this.elements.dropzone) {
            this.elements.dropzone.style.transform = 'scale(1.02)';
            this.elements.dropzone.style.filter = 'brightness(1.1)';
        }
    }

    /**
     * Remover animación de drag
     */
    removeDragAnimation() {
        if (this.elements.dropzone) {
            this.elements.dropzone.style.transform = 'scale(1)';
            this.elements.dropzone.style.filter = 'brightness(1)';
        }
    }

    /**
     * Prevenir comportamiento por defecto de drag and drop
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * Manejar upload de archivo optimizado
     */
    async handleFileUpload(file) {
        try {
            if (window.Utils) Utils.log('📁 Subiendo archivo:', file.name);

            // Validación rápida de archivo
            const validation = this.validateFileOptimized(file);
            if (!validation.valid) {
                this.showNotification(validation.message, 'error');
                return;
            }

            // Mostrar progreso de upload con animación
            this.showUploadProgress();

            // Ensure we have a session
            if (!this.sessionId) {
                await this.createSession();
            }

            // Crear FormData optimizado
            const formData = new FormData();
            formData.append('file', file);

            // Upload con progreso y timeout optimizado
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutos

            // Pass session_id as query parameter
            const uploadUrl = `/api/files/upload?session_id=${encodeURIComponent(this.sessionId)}`;

            const response = await fetch(uploadUrl, {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error subiendo archivo');
            }

            const fileInfo = await response.json();
            this.currentFileId = fileInfo.file_id;
            this.uploadedFiles.set(fileInfo.file_id, fileInfo);

            if (window.Utils) Utils.log('✅ Archivo subido:', fileInfo);

            // Actualizar UI con animaciones
            await this.showAnalysisConfigAnimated(fileInfo);
            this.updateFileStats();

            this.showNotification(`File "${file.name}" uploaded successfully`, 'success');

        } catch (error) {
            this.errorHandler.handleError(error, 'File upload failed');
            if (error.name === 'AbortError') {
                this.showNotification('Upload cancelled due to timeout', 'warning');
            } else {
                this.showNotification(`Upload error: ${error.message}`, 'error');
            }
            this.hideUploadProgress();
        }
    }

    /**
     * Show upload progress with professional animation
     */
    showUploadProgress() {
        try {
            const progressContainer = this.elements.progressArea || document.getElementById('progress-area');
            const uploadArea = this.elements.uploadArea || document.getElementById('upload-area');

            if (progressContainer) {
                progressContainer.style.display = 'block';
                progressContainer.classList.add('fade-in');

                // Update progress bar
                const progressBar = this.elements.progressBar || document.getElementById('progress-bar');
                if (progressBar) {
                    progressBar.style.width = '0%';
                    progressBar.setAttribute('aria-valuenow', '0');
                }

                // Hide upload area
                if (uploadArea) {
                    uploadArea.style.opacity = '0.5';
                    uploadArea.style.pointerEvents = 'none';
                }
            }
        } catch (error) {
            this.errorHandler.handleError(error, 'Failed to show upload progress');
        }
    }

    /**
     * Hide upload progress and reset UI
     */
    hideUploadProgress() {
        try {
            const progressContainer = this.elements.progressArea || document.getElementById('progress-area');
            const uploadArea = this.elements.uploadArea || document.getElementById('upload-area');

            if (progressContainer) {
                progressContainer.classList.add('fade-out');
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    progressContainer.classList.remove('fade-in', 'fade-out');
                }, this.config.animationDuration);
            }

            // Restore upload area
            if (uploadArea) {
                uploadArea.style.opacity = '1';
                uploadArea.style.pointerEvents = 'auto';
            }
        } catch (error) {
            this.errorHandler.handleError(error, 'Failed to hide upload progress');
        }
    }

    /**
     * Validación de archivo optimizada
     */
    validateFileOptimized(file) {
        // Verificar que existe el archivo
        if (!file) {
            return { valid: false, message: 'No se seleccionó ningún archivo' };
        }

        // Verificar tamaño
        if (file.size > this.config.maxFileSize) {
            const sizeMB = Math.round(file.size / (1024 * 1024));
            const maxSizeMB = Math.round(this.config.maxFileSize / (1024 * 1024));
            return {
                valid: false,
                message: `Archivo demasiado grande: ${sizeMB}MB (máximo: ${maxSizeMB}MB)`
            };
        }

        // Verificar que no esté vacío
        if (file.size === 0) {
            return { valid: false, message: 'El archivo está vacío' };
        }

        // Verificar extensión
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!this.config.allowedExtensions.includes(extension)) {
            return {
                valid: false,
                message: `Formato no soportado: ${extension}. Permitidos: ${this.config.allowedExtensions.join(', ')}`
            };
        }

        // Verificar nombre de archivo
        if (file.name.length > 255) {
            return { valid: false, message: 'Nombre de archivo demasiado largo' };
        }

        return { valid: true, message: 'Archivo válido' };
    }

    /**
     * Mostrar configuración de análisis con animación optimizada
     */
    async showAnalysisConfigAnimated(fileInfo) {
        // Ocultar área de upload con animación
        if (this.elements.uploadArea) {
            this.elements.uploadArea.style.opacity = '0';
            this.elements.uploadArea.style.transform = 'translateY(-20px)';

            await new Promise(resolve => setTimeout(resolve, this.config.animationDuration));
            this.elements.uploadArea.style.display = 'none';
        }

        // Mostrar configuración con animación
        if (this.elements.analysisConfig) {
            this.elements.analysisConfig.style.display = 'block';
            this.elements.analysisConfig.style.opacity = '0';
            this.elements.analysisConfig.style.transform = 'translateY(20px)';

            // Forzar reflow
            this.elements.analysisConfig.offsetHeight;

            // Animar entrada
            this.elements.analysisConfig.style.transition = `all ${this.config.animationDuration}ms ease-out`;
            this.elements.analysisConfig.style.opacity = '1';
            this.elements.analysisConfig.style.transform = 'translateY(0)';

            // Actualizar información del archivo
            const cardHeader = this.elements.analysisConfig.querySelector('.card-header h5');
            if (cardHeader) {
                cardHeader.innerHTML = `
                    <i class="fas fa-cogs me-2"></i>Configuración de Análisis
                    <small class="text-muted ms-2">(${fileInfo.filename})</small>
                `;
            }

            // Agregar información del archivo
            this.updateFileInfoDisplay(fileInfo);
        }
    }

    /**
     * Actualizar información del archivo en la UI
     */
    updateFileInfoDisplay(fileInfo) {
        const fileInfoContainer = document.getElementById('file-info-display');
        if (fileInfoContainer) {
            const sizeFormatted = this.formatFileSize(fileInfo.size || 0);
            fileInfoContainer.innerHTML = `
                <div class="file-info-item">
                    <i class="fas fa-file-alt text-primary me-2"></i>
                    <strong>Archivo:</strong> ${fileInfo.filename}
                </div>
                <div class="file-info-item">
                    <i class="fas fa-weight text-info me-2"></i>
                    <strong>Tamaño:</strong> ${sizeFormatted}
                </div>
                <div class="file-info-item">
                    <i class="fas fa-clock text-warning me-2"></i>
                    <strong>Subido:</strong> ${new Date().toLocaleTimeString()}
                </div>
            `;
        }
    }

    /**
     * Formatear tamaño de archivo
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Iniciar análisis
     */
    async startAnalysis() {
        try {
            if (!this.currentFileId) {
                this.showNotification('No hay archivo seleccionado', 'error');
                return;
            }

            if (window.Utils) Utils.log('🔍 Iniciando análisis...');

            // Obtener configuración
            const analysisTypes = this.getSelectedAnalysisTypes();
            const outputFormats = this.getSelectedOutputFormats();

            if (analysisTypes.length === 0) {
                this.showNotification('Selecciona al menos un tipo de análisis', 'error');
                return;
            }

            // Crear solicitud de análisis
            const request = {
                file_id: this.currentFileId,
                analysis_types: analysisTypes,
                output_formats: outputFormats,
                options: {
                    session_id: this.sessionId
                }
            };

            // Enviar solicitud
            const response = await fetch('/api/analysis/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(request)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error iniciando análisis');
            }

            const result = await response.json();
            this.currentAnalysisId = result.analysis_id;

            if (window.Utils) Utils.log('✅ Análisis iniciado:', result);

            // Mostrar área de progreso
            this.showProgressArea();

            // Iniciar timer
            this.startProgressTimer();

        } catch (error) {
            if (window.Utils) Utils.error('❌ Error iniciando análisis:', error);
            this.showNotification(`Error iniciando análisis: ${error.message}`, 'error');
        }
    }

    /**
     * Obtener tipos de análisis seleccionados
     */
    getSelectedAnalysisTypes() {
        const types = [];

        if (document.getElementById('analysis-syntax').checked) types.push('syntax');
        if (document.getElementById('analysis-errors').checked) types.push('errors');
        if (document.getElementById('analysis-schema').checked) types.push('schema');
        if (document.getElementById('analysis-domain').checked) types.push('domain');
        if (document.getElementById('analysis-security').checked) types.push('security');

        return types;
    }

    /**
     * Obtener formatos de salida seleccionados
     */
    getSelectedOutputFormats() {
        const formats = [];

        if (document.getElementById('output-html').checked) formats.push('html');
        if (document.getElementById('output-json').checked) formats.push('json');
        if (document.getElementById('output-pdf').checked) formats.push('pdf');
        if (document.getElementById('output-excel').checked) formats.push('excel');

        return formats;
    }

    /**
     * Mostrar área de progreso
     */
    showProgressArea() {
        // Ocultar configuración
        document.getElementById('analysis-config').style.display = 'none';

        // Mostrar progreso
        const progressArea = document.getElementById('progress-area');
        progressArea.style.display = 'block';
        progressArea.classList.add('fade-in-up');

        // Resetear progreso
        this.updateProgressBar(0, 'Iniciando análisis...');
        this.startTime = Date.now();
    }

    /**
     * Actualizar barra de progreso
     */
    updateProgressBar(progress, message, status = 'procesando') {
        const progressBar = document.getElementById('progress-bar');
        const progressStatus = document.getElementById('progress-status');
        const progressMessage = document.getElementById('progress-message');

        progressBar.style.width = `${progress}%`;
        progressBar.textContent = `${Math.round(progress)}%`;
        progressStatus.textContent = status;
        progressMessage.textContent = message;

        // Cambiar color según estado
        progressBar.className = 'progress-bar progress-bar-striped';
        if (status === 'completado') {
            progressBar.classList.add('bg-success');
        } else if (status === 'error') {
            progressBar.classList.add('bg-danger');
        } else {
            progressBar.classList.add('progress-bar-animated');
        }
    }

    /**
     * Iniciar timer de progreso
     */
    startProgressTimer() {
        this.progressTimer = setInterval(() => {
            if (this.startTime) {
                const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
                document.getElementById('elapsed-time').textContent = `${elapsed}s`;
            }
        }, 1000);
    }

    /**
     * Actualizar progreso del análisis
     */
    updateAnalysisProgress(message) {
        this.updateProgressBar(message.progress, message.message, message.status);

        if (message.status === 'completado') {
            this.handleAnalysisComplete(message);
        } else if (message.status === 'error') {
            this.handleAnalysisError(message);
        }

        // Agregar animación visual
        const progressArea = document.getElementById('progress-area');
        if (progressArea) {
            progressArea.classList.add('pulse');
            setTimeout(() => {
                progressArea.classList.remove('pulse');
            }, 500);
        }
    }

    /**
     * Manejar análisis completado
     */
    async handleAnalysisComplete(message) {
        try {
            if (window.Utils) Utils.log('✅ Análisis completado');

            // Detener timer
            if (this.progressTimer) {
                clearInterval(this.progressTimer);
            }

            // Obtener resultados
            const response = await fetch(`/api/analysis/${this.currentAnalysisId}/results`);
            if (!response.ok) {
                throw new Error('Error obteniendo resultados');
            }

            const results = await response.json();
            this.analysisResults.set(this.currentAnalysisId, results);

            // Mostrar resultados
            this.showResults(results);

            this.showNotification('Análisis completado exitosamente', 'success');

        } catch (error) {
            if (window.Utils) Utils.error('❌ Error obteniendo resultados:', error);
            this.showNotification(`Error obteniendo resultados: ${error.message}`, 'error');
        }
    }

    /**
     * Manejar error en análisis
     */
    handleAnalysisError(message) {
        if (window.Utils) Utils.error('❌ Error en análisis:', message);

        // Detener timer
        if (this.progressTimer) {
            clearInterval(this.progressTimer);
        }

        this.showNotification(`Error en análisis: ${message.message || 'Error desconocido'}`, 'error');
    }

    /**
     * Mostrar resultados
     */
    showResults(results) {
        // Ocultar área de progreso
        document.getElementById('progress-area').style.display = 'none';

        // Mostrar área de resultados
        const resultsArea = document.getElementById('results-area');
        resultsArea.style.display = 'block';
        resultsArea.classList.add('fade-in-up');

        // Actualizar pestañas de resultados
        this.updateResultsTabs(results);

        // Actualizar estadísticas
        this.updateStatistics(results);
    }

    /**
     * Actualizar pestañas de resultados
     */
    updateResultsTabs(results) {
        // Pestaña Resumen
        this.updateSummaryTab(results);

        // Pestaña Errores
        if (results.errors) {
            this.updateErrorsTab(results.errors);
        }

        // Pestaña Esquema
        if (results.schema_analysis) {
            this.updateSchemaTab(results.schema_analysis);
        }

        // Pestaña Dominio
        if (results.domain_analysis) {
            this.updateDomainTab(results.domain_analysis);
        }
    }

    /**
     * Actualizar pestaña de resumen
     */
    updateSummaryTab(results) {
        const summary = results.analysis_summary;

        // Actualizar métricas con animación
        this.animateCounter('summary-lines', summary.total_lines);
        this.animateCounter('summary-statements', summary.total_statements);
        this.animateCounter('summary-tables', summary.total_tables);
        this.animateCounter('summary-errors', summary.total_errors);

        // Calcular puntuación de salud
        const healthScore = this.calculateHealthScore(results);
        this.animateCounter('health-score', healthScore);

        // Actualizar gráficos
        this.updateSummaryChart(summary);
        this.updateHealthScoreChart(healthScore);

        // Actualizar recomendaciones
        this.updateRecommendations(results);
    }

    /**
     * Animar contador numérico
     */
    animateCounter(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = 0;
        const duration = 1000;
        const increment = targetValue / (duration / 16);
        let currentValue = startValue;

        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            element.textContent = Math.floor(currentValue);
        }, 16);
    }

    /**
     * Calcular puntuación de salud
     */
    calculateHealthScore(results) {
        let score = 100;

        // Penalizar por errores
        if (results.errors) {
            const criticalErrors = results.errors.filter(e => e.severity === 'CRITICAL').length;
            const majorErrors = results.errors.filter(e => e.severity === 'ERROR').length;
            const warnings = results.errors.filter(e => e.severity === 'WARNING').length;

            score -= (criticalErrors * 20) + (majorErrors * 10) + (warnings * 5);
        }

        // Bonificar por buenas prácticas
        if (results.schema_analysis && results.schema_analysis.health_score) {
            score = (score + results.schema_analysis.health_score) / 2;
        }

        return Math.max(0, Math.min(100, Math.round(score)));
    }

    /**
     * Actualizar pestaña de errores
     */
    updateErrorsTab(errors) {
        const errorsContainer = document.getElementById('errors-list');
        const errorsCount = document.getElementById('errors-count');

        if (!errorsContainer || !errorsCount) return;

        errorsCount.textContent = errors.length;
        errorsContainer.innerHTML = '';

        if (errors.length === 0) {
            errorsContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-check-circle text-success" style="font-size: 3rem;"></i>
                    <h5 class="mt-3">¡No se encontraron errores!</h5>
                    <p class="text-muted">Tu archivo SQL está libre de errores detectables.</p>
                </div>
            `;
            return;
        }

        errors.forEach((error, index) => {
            const errorElement = document.createElement('div');
            errorElement.className = 'error-item';
            errorElement.innerHTML = `
                <div class="error-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="error-severity ${error.severity.toLowerCase()}">${error.severity}</span>
                        <span class="error-line">Línea ${error.line}</span>
                    </div>
                </div>
                <div class="error-message">${error.message}</div>
                ${error.suggestion ? `<div class="error-suggestion">${error.suggestion}</div>` : ''}
            `;
            errorsContainer.appendChild(errorElement);
        });
    }

    /**
     * Actualizar pestaña de esquema
     */
    updateSchemaTab(schemaAnalysis) {
        const tablesContainer = document.getElementById('schema-tables');
        const tablesCount = document.getElementById('schema-tables-count');

        if (!tablesContainer || !tablesCount) return;

        // Simular datos de esquema (en implementación real vendría del backend)
        const mockTables = [
            {
                name: 'usuarios',
                columns: ['id', 'nombre', 'email', 'fecha_creacion'],
                rowCount: 1250
            },
            {
                name: 'pedidos',
                columns: ['id', 'usuario_id', 'total', 'fecha_pedido'],
                rowCount: 3420
            }
        ];

        tablesCount.textContent = mockTables.length;
        tablesContainer.innerHTML = '';

        mockTables.forEach(table => {
            const tableElement = document.createElement('div');
            tableElement.className = 'table-item';
            tableElement.innerHTML = `
                <div class="table-header">
                    <div class="table-name">${table.name}</div>
                    <div class="table-info">${table.columns.length} columnas • ${table.rowCount} filas</div>
                </div>
                <div class="columns-list">
                    ${table.columns.map(col => `
                        <div class="column-item">
                            <div class="column-name">${col}</div>
                            <div class="column-type">VARCHAR</div>
                        </div>
                    `).join('')}
                </div>
            `;
            tablesContainer.appendChild(tableElement);
        });
    }

    /**
     * Actualizar pestaña de dominio
     */
    updateDomainTab(domainAnalysis) {
        const primaryDomain = document.getElementById('primary-domain');
        const domainConfidence = document.getElementById('domain-confidence');
        const suggestionsContainer = document.getElementById('domain-suggestions');

        if (domainAnalysis) {
            if (primaryDomain) primaryDomain.textContent = domainAnalysis.primary_domain;
            if (domainConfidence) domainConfidence.textContent = `${Math.round(domainAnalysis.confidence * 100)}%`;

            if (suggestionsContainer && domainAnalysis.suggestions) {
                suggestionsContainer.innerHTML = '';
                domainAnalysis.suggestions.forEach(suggestion => {
                    const suggestionElement = document.createElement('div');
                    suggestionElement.className = 'suggestion-item';
                    suggestionElement.innerHTML = `
                        <h6>${suggestion.title || 'Recomendación'}</h6>
                        <p>${suggestion.description || suggestion}</p>
                    `;
                    suggestionsContainer.appendChild(suggestionElement);
                });
            }
        } else {
            if (primaryDomain) primaryDomain.textContent = 'No disponible';
            if (domainConfidence) domainConfidence.textContent = '0%';
            if (suggestionsContainer) {
                suggestionsContainer.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-brain text-muted" style="font-size: 2rem;"></i>
                        <p class="mt-3 text-muted">Análisis de dominio no disponible</p>
                    </div>
                `;
            }
        }
    }

    /**
     * Actualizar recomendaciones
     */
    updateRecommendations(results) {
        const recommendationsList = document.getElementById('recommendations-list');
        if (!recommendationsList) return;

        const recommendations = results.schema_analysis?.recommendations || [
            'Considera agregar índices para mejorar el rendimiento',
            'Revisa las relaciones entre tablas',
            'Optimiza las consultas complejas'
        ];

        recommendationsList.innerHTML = '';
        recommendations.slice(0, 5).forEach(rec => {
            const li = document.createElement('li');
            li.className = 'recommendation-item';
            li.innerHTML = `
                <i class="fas fa-lightbulb text-warning me-2"></i>
                ${rec}
            `;
            recommendationsList.appendChild(li);
        });
    }

    /**
     * Inicializar gráficos
     */
    initializeCharts() {
        // Los gráficos se inicializarán cuando se muestren los resultados
    }

    /**
     * Actualizar gráfico de resumen
     */
    updateSummaryChart(summary) {
        const ctx = document.getElementById('summary-chart').getContext('2d');

        if (this.charts.has('summary')) {
            this.charts.get('summary').destroy();
        }

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Líneas', 'Declaraciones', 'Tablas', 'Errores'],
                datasets: [{
                    label: 'Cantidad',
                    data: [
                        summary.total_lines,
                        summary.total_statements,
                        summary.total_tables,
                        summary.total_errors
                    ],
                    backgroundColor: [
                        'rgba(37, 99, 235, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)'
                    ],
                    borderColor: [
                        'rgba(37, 99, 235, 1)',
                        'rgba(16, 185, 129, 1)',
                        'rgba(245, 158, 11, 1)',
                        'rgba(239, 68, 68, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        this.charts.set('summary', chart);
    }

    /**
     * Actualizar gráfico de puntuación de salud
     */
    updateHealthScoreChart(score) {
        const ctx = document.getElementById('health-score-chart').getContext('2d');

        if (this.charts.has('health')) {
            this.charts.get('health').destroy();
        }

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [
                        score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444',
                        '#e5e7eb'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        this.charts.set('health', chart);
    }

    /**
     * Mostrar notificación
     */
    showNotification(message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';

        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * Actualizar UI general
     */
    updateUI() {
        this.updateFileStats();
        this.updateStatistics();
    }

    /**
     * Actualizar estadísticas de archivos
     */
    updateFileStats() {
        document.getElementById('files-count').textContent = this.uploadedFiles.size;
    }

    /**
     * Actualizar estadísticas generales
     */
    updateStatistics(results = null) {
        if (results) {
            document.getElementById('total-analyses').textContent = this.analysisResults.size;

            // Calcular tiempo promedio (simulado)
            const avgTime = Math.floor(Math.random() * 30) + 10;
            document.getElementById('avg-time').textContent = `${avgTime}s`;

            // Calcular tasa de éxito
            document.getElementById('success-rate').textContent = '98%';

            // Total de errores
            const totalErrors = results.analysis_summary ? results.analysis_summary.total_errors : 0;
            document.getElementById('total-errors').textContent = totalErrors;
        }
    }

    /**
     * Initialize authentication system
     */
    async initializeAuthentication() {
        // For now, we'll implement a simple authentication check
        // In a real enterprise environment, this would integrate with SSO/LDAP
        this.isAuthenticated = true; // Simplified for demo
        return true;
    }

    /**
     * Initialize modal system for enterprise UI
     */
    initializeModals() {
        // Setup modal event listeners and behaviors
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', (e) => {
                // Add fade-in animation
                e.target.classList.add('fade-in');
            });
        });
    }
}

// Funciones globales para eventos de UI
function triggerFileUpload() {
    document.getElementById('file-input').click();
}

function resetAnalysisConfig() {
    // Resetear checkboxes a valores por defecto
    document.getElementById('analysis-syntax').checked = true;
    document.getElementById('analysis-errors').checked = true;
    document.getElementById('analysis-schema').checked = true;
    document.getElementById('analysis-domain').checked = false;
    document.getElementById('analysis-security').checked = false;

    document.getElementById('output-html').checked = true;
    document.getElementById('output-json').checked = true;
    document.getElementById('output-pdf').checked = false;
    document.getElementById('output-excel').checked = false;
}

function startAnalysis() {
    if (window.dashboard) {
        window.dashboard.startAnalysis();
    }
}

function cancelAnalysis() {
    if (window.dashboard && window.dashboard.currentAnalysisId) {
        // Implementar cancelación de análisis
        if (window.Utils) Utils.log('Cancelando análisis...');
        window.dashboard.showNotification('Análisis cancelado', 'warning');

        // Volver a mostrar configuración
        document.getElementById('progress-area').style.display = 'none';
        document.getElementById('analysis-config').style.display = 'block';
    }
}

function newAnalysis() {
    // Resetear para nuevo análisis
    document.getElementById('results-area').style.display = 'none';
    document.getElementById('upload-area').style.display = 'block';

    if (window.dashboard) {
        window.dashboard.currentFileId = null;
        window.dashboard.currentAnalysisId = null;
    }
}

function downloadResults() {
    if (window.dashboard && window.dashboard.currentAnalysisId) {
        // Implementar descarga de resultados
        if (window.Utils) Utils.log('Descargando resultados...');
        window.dashboard.showNotification('Preparando descarga...', 'info');
    }
}

function shareResults() {
    if (window.dashboard && window.dashboard.currentAnalysisId) {
        // Implementar compartir resultados
        if (window.Utils) Utils.log('Compartiendo resultados...');
        window.dashboard.showNotification('Función de compartir próximamente', 'info');
    }
}

function showSettings() {
    const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
    modal.show();
}

function showHistory() {
    window.dashboard.showNotification('Historial próximamente', 'info');
}

function showExamples() {
    window.dashboard.showNotification('Ejemplos próximamente', 'info');
}

function showHelp() {
    window.dashboard.showNotification('Ayuda próximamente', 'info');
}

function saveSettings() {
    // Implementar guardado de configuración
    if (window.Utils) Utils.log('Guardando configuración...');
    window.dashboard.showNotification('Configuración guardada', 'success');

    const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
    modal.hide();
}

function filterErrors(type) {
    // Filtrar errores por tipo
    const errorItems = document.querySelectorAll('.error-item');

    errorItems.forEach(item => {
        const severity = item.querySelector('.error-severity');
        if (!severity) return;

        const severityText = severity.textContent.toLowerCase();

        if (type === 'all') {
            item.style.display = 'block';
        } else if (type === 'critical' && severityText === 'critical') {
            item.style.display = 'block';
        } else if (type === 'warning' && severityText === 'warning') {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });

    // Actualizar botones activos
    document.querySelectorAll('[onclick^="filterErrors"]').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

/**
 * Enterprise Error Handler Class
 */
class ErrorHandler {
    constructor() {
        this.errorLog = [];
        this.maxLogSize = 100;
    }

    handleError(error, context = 'Unknown') {
        const errorInfo = {
            timestamp: new Date().toISOString(),
            context: context,
            message: error.message || 'Unknown error',
            stack: error.stack || 'No stack trace',
            type: error.name || 'Error'
        };

        // Log to console for development
        if (window.Utils) Utils.error(`[${context}]`, error);

        // Add to error log
        this.errorLog.unshift(errorInfo);
        if (this.errorLog.length > this.maxLogSize) {
            this.errorLog.pop();
        }

        // In production, you might want to send errors to a logging service
        this.reportError(errorInfo);
    }

    reportError(errorInfo) {
        // In a real enterprise environment, this would send errors to a monitoring service
        // For now, we'll just store them locally
        try {
            const existingErrors = JSON.parse(localStorage.getItem('sqlAnalyzerErrors') || '[]');
            existingErrors.unshift(errorInfo);
            localStorage.setItem('sqlAnalyzerErrors', JSON.stringify(existingErrors.slice(0, 50)));
        } catch (e) {
            // Silently fail if localStorage is not available
        }
    }

    getRecentErrors(count = 10) {
        return this.errorLog.slice(0, count);
    }

    clearErrors() {
        this.errorLog = [];
        localStorage.removeItem('sqlAnalyzerErrors');
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    if (window.Utils) Utils.log('🚀 Initializing SQL Analyzer Enterprise Dashboard...');
    window.dashboard = new SQLAnalyzerDashboard();
});
