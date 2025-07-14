/**
 * UTILIDADES SIMPLIFICADAS - SIN WEBSOCKET
 * Sistema robusto sin dependencias problemáticas
 */

window.SimpleUtils = {
    // Logging simple
    log: function(message, type = 'info') {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] [${type.toUpperCase()}] ${message}`);
    },

    // Mostrar notificaciones
    showNotification: function(message, type = 'info', duration = 5000) {
        this.log(`Notification: ${message}`, type);
        
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `alert alert-${this.getBootstrapClass(type)} alert-dismissible fade show`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 500px;
        `;
        
        notification.innerHTML = `
            <strong>${this.getTypeIcon(type)}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remover después del tiempo especificado
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    },

    // Convertir tipo a clase Bootstrap
    getBootstrapClass: function(type) {
        const mapping = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return mapping[type] || 'info';
    },

    // Obtener icono para tipo
    getTypeIcon: function(type) {
        const icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        };
        return icons[type] || 'ℹ️';
    },

    // Subir archivo de manera simple
    uploadFile: function(fileInput, onProgress, onComplete, onError) {
        const file = fileInput.files[0];
        if (!file) {
            onError('No se seleccionó archivo');
            return;
        }

        // Validaciones básicas
        if (file.size > 50 * 1024 * 1024) { // 50MB
            onError('Archivo demasiado grande (máximo 50MB)');
            return;
        }

        const allowedTypes = ['.sql', '.txt'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExtension)) {
            onError('Tipo de archivo no permitido. Use archivos .sql o .txt');
            return;
        }

        // Crear FormData
        const formData = new FormData();
        formData.append('file', file);

        // Configurar XMLHttpRequest
        const xhr = new XMLHttpRequest();

        // Manejar progreso
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                onProgress(percentComplete);
            }
        });

        // Manejar respuesta
        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    onComplete(response);
                } catch (e) {
                    onError('Error procesando respuesta del servidor');
                }
            } else {
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    onError(errorResponse.error || 'Error en el servidor');
                } catch (e) {
                    onError(`Error del servidor (${xhr.status})`);
                }
            }
        });

        // Manejar errores
        xhr.addEventListener('error', function() {
            onError('Error de conexión con el servidor');
        });

        // Enviar petición
        xhr.open('POST', '/api/analyze');
        xhr.send(formData);
    },

    // Descargar archivo
    downloadFile: function(format, filename = null) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const downloadName = filename || `sql_analysis_${timestamp}.${format}`;
        
        // Crear enlace de descarga
        const link = document.createElement('a');
        link.href = `/api/download/${format}`;
        link.download = downloadName;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showNotification(`Descargando ${downloadName}`, 'success');
    },

    // Formatear resultados de análisis
    formatAnalysisResults: function(results) {
        if (!results.processed_successfully) {
            return `<div class="alert alert-danger">❌ Error: ${results.error}</div>`;
        }

        let html = `
            <div class="analysis-results">
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5 class="card-title">Score de Calidad</h5>
                                <h2 class="text-${this.getScoreColor(results.quality_score)}">${results.quality_score}%</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Estadísticas</h5>
                                <p><strong>Líneas:</strong> ${results.lines}</p>
                                <p><strong>Errores:</strong> ${results.summary.total_errors}</p>
                                <p><strong>Advertencias:</strong> ${results.summary.total_warnings}</p>
                                <p><strong>Tablas:</strong> ${results.summary.tables_found}</p>
                            </div>
                        </div>
                    </div>
                </div>
        `;

        // Mostrar errores y advertencias
        if (results.errors && results.errors.length > 0) {
            html += '<div class="card mb-3"><div class="card-body"><h5 class="card-title">Errores y Advertencias</h5>';
            results.errors.forEach(error => {
                const alertClass = error.severity === 'ERROR' ? 'danger' : 'warning';
                const icon = error.severity === 'ERROR' ? '❌' : '⚠️';
                html += `
                    <div class="alert alert-${alertClass}">
                        ${icon} <strong>Línea ${error.line}:</strong> ${error.message}
                        ${error.code ? `<br><code>${error.code}</code>` : ''}
                    </div>
                `;
            });
            html += '</div></div>';
        }

        // Mostrar recomendaciones
        if (results.recommendations && results.recommendations.length > 0) {
            html += '<div class="card mb-3"><div class="card-body"><h5 class="card-title">Recomendaciones</h5>';
            results.recommendations.forEach(rec => {
                const priorityClass = rec.priority === 'HIGH' ? 'danger' : 'warning';
                html += `
                    <div class="alert alert-${priorityClass}">
                        <strong>${rec.title}</strong><br>
                        ${rec.description}
                    </div>
                `;
            });
            html += '</div></div>';
        }

        html += '</div>';
        return html;
    },

    // Obtener color para score
    getScoreColor: function(score) {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'danger';
    },

    // Inicializar sistema
    init: function() {
        this.log('SimpleUtils inicializado correctamente');
        
        // Deshabilitar WebSocket si existe
        if (window.WebSocket) {
            this.log('WebSocket detectado - usando modo simple sin WebSocket');
        }
        
        // Configurar manejo global de errores
        window.addEventListener('error', (e) => {
            this.log(`Error global capturado: ${e.message}`, 'error');
        });
        
        this.showNotification('Sistema inicializado correctamente', 'success', 3000);
    }
};

// Auto-inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.SimpleUtils.init();
});

// Alias para compatibilidad
window.Utils = window.SimpleUtils;
