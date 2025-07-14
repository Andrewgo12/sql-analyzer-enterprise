/**
 * SQL Analyzer Enterprise - Clean Architecture Utils
 * Sistema de utilidades robusto sin WebSocket
 */

window.Utils = {
    // Configuración
    config: {
        maxFileSize: 50 * 1024 * 1024, // 50MB
        allowedExtensions: ['.sql', '.txt'],
        notificationDuration: 5000,
        apiEndpoints: {
            analyze: '/api/analyze',
            download: '/api/download',
            health: '/api/health'
        }
    },

    // Sistema de logging
    log: function(message, type = 'info') {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [${type.toUpperCase()}] ${message}`;
        
        if (type === 'error') {
            console.error(logMessage);
        } else if (type === 'warning') {
            console.warn(logMessage);
        } else {
            console.log(logMessage);
        }
    },

    // Sistema de notificaciones
    showNotification: function(message, type = 'info', duration = null) {
        this.log(`Notification: ${message}`, type);
        
        const container = this.getNotificationContainer();
        const notification = this.createNotificationElement(message, type);
        
        container.appendChild(notification);
        
        // Auto-remover
        const timeout = duration || this.config.notificationDuration;
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, timeout);
        
        return notification;
    },

    getNotificationContainer: function() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        return container;
    },

    createNotificationElement: function(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${this.getBootstrapClass(type)} alert-dismissible fade show notification`;
        
        notification.innerHTML = `
            <strong>${this.getTypeIcon(type)}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        return notification;
    },

    getBootstrapClass: function(type) {
        const mapping = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return mapping[type] || 'info';
    },

    getTypeIcon: function(type) {
        const icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        };
        return icons[type] || 'ℹ️';
    },

    // Validación de archivos
    validateFile: function(file) {
        if (!file) {
            return { valid: false, error: 'No se seleccionó archivo' };
        }

        // Validar tamaño
        if (file.size > this.config.maxFileSize) {
            const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
            const maxMB = (this.config.maxFileSize / (1024 * 1024)).toFixed(0);
            return { 
                valid: false, 
                error: `Archivo demasiado grande (${sizeMB}MB). Máximo: ${maxMB}MB` 
            };
        }

        // Validar extensión
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!this.config.allowedExtensions.includes(extension)) {
            return { 
                valid: false, 
                error: `Extensión no válida. Permitidas: ${this.config.allowedExtensions.join(', ')}` 
            };
        }

        return { valid: true };
    },

    // Formatear resultados de análisis
    formatAnalysisResults: function(results) {
        if (!results.processed_successfully) {
            return `
                <div class="alert alert-danger">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>Error en el Análisis</h6>
                    <p class="mb-0">${results.error || 'Error desconocido'}</p>
                </div>
            `;
        }

        let html = `
            <div class="analysis-results">
                <!-- Quality Score -->
                <div class="quality-score">
                    <div class="quality-score-number ${this.getScoreClass(results.quality_score)}">
                        ${results.quality_score}%
                    </div>
                    <div class="quality-score-label">Score de Calidad</div>
                </div>

                <!-- Statistics -->
                <div class="row mb-4">
                    <div class="col-md-3 text-center">
                        <div class="stat-item">
                            <div class="stat-number">${results.lines || 0}</div>
                            <div class="stat-label">Líneas</div>
                        </div>
                    </div>
                    <div class="col-md-3 text-center">
                        <div class="stat-item">
                            <div class="stat-number">${results.summary?.total_errors || 0}</div>
                            <div class="stat-label">Errores</div>
                        </div>
                    </div>
                    <div class="col-md-3 text-center">
                        <div class="stat-item">
                            <div class="stat-number">${results.summary?.total_warnings || 0}</div>
                            <div class="stat-label">Advertencias</div>
                        </div>
                    </div>
                    <div class="col-md-3 text-center">
                        <div class="stat-item">
                            <div class="stat-number">${results.summary?.tables_found || 0}</div>
                            <div class="stat-label">Tablas</div>
                        </div>
                    </div>
                </div>
        `;

        // Mostrar errores y advertencias
        if (results.errors && results.errors.length > 0) {
            html += '<h6><i class="fas fa-exclamation-circle me-2"></i>Errores y Advertencias</h6>';
            results.errors.forEach(error => {
                const itemClass = error.severity === 'ERROR' ? 'error' : 'warning';
                const icon = error.severity === 'ERROR' ? '❌' : '⚠️';
                html += `
                    <div class="error-item ${itemClass}">
                        <strong>${icon} Línea ${error.line}:</strong> ${error.message}
                        ${error.code ? `<br><code class="text-muted">${error.code}</code>` : ''}
                    </div>
                `;
            });
        }

        // Mostrar recomendaciones
        if (results.recommendations && results.recommendations.length > 0) {
            html += '<h6 class="mt-4"><i class="fas fa-lightbulb me-2"></i>Recomendaciones</h6>';
            results.recommendations.forEach(rec => {
                const priorityClass = rec.priority === 'HIGH' ? 'danger' : 'warning';
                html += `
                    <div class="alert alert-${priorityClass}">
                        <strong>${rec.title}</strong><br>
                        ${rec.description}
                    </div>
                `;
            });
        }

        html += '</div>';
        return html;
    },

    getScoreClass: function(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'poor';
    },

    // Descargar archivo
    downloadFile: function(format, filename = null) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const downloadName = filename || `sql_analysis_${timestamp}.${format}`;
        
        const link = document.createElement('a');
        link.href = `${this.config.apiEndpoints.download}/${format}`;
        link.download = downloadName;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showNotification(`Descargando ${downloadName}`, 'success');
    },

    // Verificar salud del sistema
    checkHealth: function() {
        return fetch(this.config.apiEndpoints.health)
            .then(response => response.json())
            .then(data => {
                this.log('Health check successful', 'info');
                return data;
            })
            .catch(error => {
                this.log(`Health check failed: ${error}`, 'error');
                return null;
            });
    },

    // Inicializar sistema
    init: function() {
        this.log('Utils system initializing...');
        
        // Configurar manejo global de errores
        window.addEventListener('error', (e) => {
            this.log(`Global error: ${e.message}`, 'error');
        });

        // Configurar manejo de promesas rechazadas
        window.addEventListener('unhandledrejection', (e) => {
            this.log(`Unhandled promise rejection: ${e.reason}`, 'error');
        });

        // Verificar salud del sistema
        this.checkHealth().then(health => {
            if (health) {
                this.showNotification('Sistema inicializado correctamente', 'success', 3000);
            } else {
                this.showNotification('Sistema iniciado con advertencias', 'warning', 3000);
            }
        });

        this.log('Utils system initialized successfully');
    },

    // Utilidades adicionales
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    formatTimestamp: function(timestamp) {
        return new Date(timestamp).toLocaleString('es-ES');
    },

    debounce: function(func, wait) {
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
};

// Auto-inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    if (window.Utils) {
        window.Utils.init();
    }
});
