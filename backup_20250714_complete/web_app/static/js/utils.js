/* ============================================================================
   SQL ANALYZER ENTERPRISE - UTILITIES MODULE
   Shared utilities, formatters, validators, and helper functions
   ============================================================================ */

class Utils {
    // Performance optimization cache
    static cache = new Map();
    static debounceTimers = new Map();

    // Debug mode (set to false for production)
    static DEBUG_MODE = true; // Set to false for production

    // Safe logging function
    static log(...args) {
        if (this.DEBUG_MODE && console && console.log) {
            console.log('[SQL Analyzer]', ...args);
        }
    }

    static warn(...args) {
        if (this.DEBUG_MODE && console && console.warn) {
            console.warn('[SQL Analyzer]', ...args);
        }
    }

    static error(...args) {
        // Always log errors
        if (console && console.error) {
            console.error('[SQL Analyzer ERROR]', ...args);
        }
    }

    // ========================================================================
    // PERFORMANCE UTILITIES
    // ========================================================================

    static debounce(func, wait, key = 'default') {
        return (...args) => {
            if (this.debounceTimers.has(key)) {
                clearTimeout(this.debounceTimers.get(key));
            }

            const timer = setTimeout(() => {
                func.apply(this, args);
                this.debounceTimers.delete(key);
            }, wait);

            this.debounceTimers.set(key, timer);
        };
    }

    static throttle(func, limit, key = 'default') {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    static memoize(func, keyGenerator = (...args) => JSON.stringify(args)) {
        return (...args) => {
            const key = keyGenerator(...args);
            if (this.cache.has(key)) {
                return this.cache.get(key);
            }
            const result = func(...args);
            this.cache.set(key, result);
            return result;
        };
    }

    // ========================================================================
    // VALIDATION UTILITIES
    // ========================================================================

    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    static validatePassword(password) {
        return {
            isValid: password.length >= 4,
            minLength: password.length >= 4,
            hasUppercase: /[A-Z]/.test(password),
            hasLowercase: /[a-z]/.test(password),
            hasNumbers: /\d/.test(password),
            hasSpecialChars: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };
    }

    static validateFileType(file, allowedTypes = ['.sql', '.txt', '.text', '.pdf']) {
        if (!file) return false;

        const fileName = file.name.toLowerCase();
        const fileExtension = '.' + fileName.split('.').pop();

        return allowedTypes.includes(fileExtension);
    }

    static validateFileSize(file, maxSizeBytes = 10 * 1024 * 1024 * 1024) { // 10GB default
        if (!file) return false;
        return file.size <= maxSizeBytes;
    }

    static validateSessionId(sessionId) {
        if (!sessionId) return false;
        // UUID v4 format validation
        const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
        return uuidRegex.test(sessionId);
    }

    // ========================================================================
    // ASYNC UTILITIES
    // ========================================================================

    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    static async timeout(promise, ms) {
        const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Operation timed out')), ms)
        );

        return Promise.race([promise, timeoutPromise]);
    }

    // ========================================================================
    // ID GENERATION UTILITIES
    // ========================================================================

    static generateId(prefix = '') {
        const timestamp = Date.now().toString(36);
        const randomStr = Math.random().toString(36).substring(2, 15);
        return prefix ? `${prefix}_${timestamp}_${randomStr}` : `${timestamp}_${randomStr}`;
    }

    static generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // ========================================================================
    // FORMATTING UTILITIES
    // ========================================================================

    static formatFileSize(bytes) {
        if (bytes === 0) return '0 B';

        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    static formatTime(seconds) {
        if (seconds < 60) return `${seconds}s`;

        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;

        if (minutes < 60) {
            return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
        }

        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;

        return `${hours}h ${remainingMinutes}m`;
    }

    static formatDate(dateString, options = {}) {
        const date = new Date(dateString);

        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };

        const formatOptions = { ...defaultOptions, ...options };

        return date.toLocaleDateString('en-US', formatOptions);
    }

    static formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;

        return this.formatDate(dateString);
    }

    static formatNumber(number, decimals = 0) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    }

    static formatPercentage(value, total, decimals = 1) {
        if (total === 0) return '0%';
        const percentage = (value / total) * 100;
        return `${percentage.toFixed(decimals)}%`;
    }

    // ========================================================================
    // STRING UTILITIES
    // ========================================================================

    static truncateText(text, maxLength = 100, suffix = '...') {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength - suffix.length) + suffix;
    }

    static capitalizeFirst(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }

    static camelToKebab(str) {
        return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase();
    }

    static kebabToCamel(str) {
        return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    }

    static sanitizeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    static generateId(prefix = 'id') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // ========================================================================
    // ARRAY AND OBJECT UTILITIES
    // ========================================================================

    static deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const clonedObj = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = this.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    }

    static groupBy(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key];
            groups[group] = groups[group] || [];
            groups[group].push(item);
            return groups;
        }, {});
    }

    static sortBy(array, key, direction = 'asc') {
        return [...array].sort((a, b) => {
            const aVal = a[key];
            const bVal = b[key];

            if (aVal < bVal) return direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return direction === 'asc' ? 1 : -1;
            return 0;
        });
    }

    static filterBy(array, filters) {
        return array.filter(item => {
            return Object.keys(filters).every(key => {
                const filterValue = filters[key];
                const itemValue = item[key];

                if (filterValue === '' || filterValue === null || filterValue === undefined) {
                    return true;
                }

                if (typeof filterValue === 'string') {
                    return itemValue.toString().toLowerCase().includes(filterValue.toLowerCase());
                }

                return itemValue === filterValue;
            });
        });
    }

    // ========================================================================
    // DOM UTILITIES
    // ========================================================================

    static createElement(tag, attributes = {}, children = []) {
        const element = document.createElement(tag);

        Object.keys(attributes).forEach(key => {
            if (key === 'className') {
                element.className = attributes[key];
            } else if (key === 'innerHTML') {
                element.innerHTML = attributes[key];
            } else if (key === 'textContent') {
                element.textContent = attributes[key];
            } else {
                element.setAttribute(key, attributes[key]);
            }
        });

        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else {
                element.appendChild(child);
            }
        });

        return element;
    }

    static addEventListeners(element, events) {
        Object.keys(events).forEach(eventType => {
            element.addEventListener(eventType, events[eventType]);
        });
    }

    static removeAllChildren(element) {
        while (element.firstChild) {
            element.removeChild(element.firstChild);
        }
    }

    static toggleClass(element, className, force) {
        if (force !== undefined) {
            element.classList.toggle(className, force);
        } else {
            element.classList.toggle(className);
        }
    }

    // ========================================================================
    // ASYNC UTILITIES
    // ========================================================================

    static debounce(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }

    static throttle(func, limit) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    static retry(fn, maxAttempts = 3, delayMs = 1000) {
        return new Promise((resolve, reject) => {
            let attempts = 0;

            const attempt = async () => {
                try {
                    const result = await fn();
                    resolve(result);
                } catch (error) {
                    attempts++;
                    if (attempts >= maxAttempts) {
                        reject(error);
                    } else {
                        setTimeout(attempt, delayMs * attempts);
                    }
                }
            };

            attempt();
        });
    }

    // ========================================================================
    // STORAGE UTILITIES
    // ========================================================================

    static setStorage(key, value, type = 'localStorage') {
        try {
            const storage = type === 'sessionStorage' ? sessionStorage : localStorage;
            storage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            if (window.Utils) Utils.warn(`Failed to save to ${type}:`, error);
            return false;
        }
    }

    static getStorage(key, defaultValue = null, type = 'localStorage') {
        try {
            const storage = type === 'sessionStorage' ? sessionStorage : localStorage;
            const item = storage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            if (window.Utils) Utils.warn(`Failed to read from ${type}:`, error);
            return defaultValue;
        }
    }

    static removeStorage(key, type = 'localStorage') {
        try {
            const storage = type === 'sessionStorage' ? sessionStorage : localStorage;
            storage.removeItem(key);
            return true;
        } catch (error) {
            if (window.Utils) Utils.warn(`Failed to remove from ${type}:`, error);
            return false;
        }
    }

    static clearStorage(type = 'localStorage') {
        try {
            const storage = type === 'sessionStorage' ? sessionStorage : localStorage;
            storage.clear();
            return true;
        } catch (error) {
            if (window.Utils) Utils.warn(`Failed to clear ${type}:`, error);
            return false;
        }
    }

    // ========================================================================
    // NOTIFICATION UTILITIES
    // ========================================================================

    static showNotification(message, type = 'info', duration = 5000) {
        try {
            // Create notification container if it doesn't exist
            let container = document.getElementById('notification-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'notification-container';
                container.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    max-width: 400px;
                `;
                document.body.appendChild(container);
            }

            // Create notification element
            const notification = document.createElement('div');
            notification.className = `alert alert-${this.getBootstrapAlertClass(type)} alert-dismissible fade show`;
            notification.style.cssText = `
                margin-bottom: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border: none;
                border-radius: 8px;
            `;

            // Add icon based on type
            const icon = this.getNotificationIcon(type);

            notification.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="${icon} me-2"></i>
                    <div class="flex-grow-1">${this.escapeHtml(message)}</div>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;

            // Add to container
            container.appendChild(notification);

            // Auto-remove after duration
            if (duration > 0) {
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.classList.remove('show');
                        setTimeout(() => {
                            if (notification.parentNode) {
                                notification.parentNode.removeChild(notification);
                            }
                        }, 150);
                    }
                }, duration);
            }

            return notification;
        } catch (error) {
            this.error('Failed to show notification:', error);
            // Fallback to alert
            alert(`${type.toUpperCase()}: ${message}`);
            return null;
        }
    }

    static getBootstrapAlertClass(type) {
        const typeMap = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info',
            'danger': 'danger'
        };
        return typeMap[type] || 'info';
    }

    static getNotificationIcon(type) {
        const iconMap = {
            'success': 'fas fa-check-circle text-success',
            'error': 'fas fa-exclamation-circle text-danger',
            'warning': 'fas fa-exclamation-triangle text-warning',
            'info': 'fas fa-info-circle text-info',
            'danger': 'fas fa-exclamation-circle text-danger'
        };
        return iconMap[type] || 'fas fa-info-circle text-info';
    }

    static hideNotification(notification) {
        if (notification && notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 150);
        }
    }

    static clearAllNotifications() {
        const container = document.getElementById('notification-container');
        if (container) {
            container.innerHTML = '';
        }
    }

    // ========================================================================
    // ERROR HANDLING UTILITIES
    // ========================================================================

    static createError(message, code = 'UNKNOWN_ERROR', details = {}) {
        const error = new Error(message);
        error.code = code;
        error.details = details;
        error.timestamp = new Date().toISOString();
        return error;
    }

    static logError(error, context = '') {
        const errorInfo = {
            message: error.message,
            code: error.code || 'UNKNOWN_ERROR',
            stack: error.stack,
            context,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };

        if (window.Utils) Utils.error('Application Error:', errorInfo);

        // In production, you might want to send this to an error tracking service
        // this.sendErrorToService(errorInfo);
    }

    static handleAsyncError(promise, context = '') {
        return promise.catch(error => {
            this.logError(error, context);
            throw error;
        });
    }

    // SQL Analyzer specific formatters
    static formatErrorType(type) {
        const typeMap = {
            'syntax': 'Sintaxis',
            'semantic': 'Semántica',
            'performance': 'Rendimiento',
            'security': 'Seguridad',
            'logic': 'Lógica',
            'style': 'Estilo',
            'warning': 'Advertencia',
            'critical': 'Crítico',
            'high': 'Alto',
            'medium': 'Medio',
            'low': 'Bajo'
        };
        return typeMap[type?.toLowerCase()] || type || 'Desconocido';
    }

    static formatFormatName(format) {
        const formatMap = {
            'enhanced_sql': 'SQL Mejorado',
            'html_report': 'Reporte HTML',
            'interactive_html': 'HTML Interactivo',
            'pdf_report': 'Reporte PDF',
            'json_analysis': 'Análisis JSON',
            'xml_report': 'Reporte XML',
            'csv_summary': 'Resumen CSV',
            'excel_workbook': 'Libro Excel',
            'word_document': 'Documento Word',
            'markdown_docs': 'Documentación Markdown',
            'latex_report': 'Reporte LaTeX',
            'powerpoint': 'Presentación PowerPoint',
            'sqlite_database': 'Base de Datos SQLite',
            'zip_archive': 'Archivo ZIP',
            'plain_text': 'Texto Plano',
            'yaml_config': 'Configuración YAML',
            'schema_diagram': 'Diagrama de Esquema',
            'jupyter_notebook': 'Notebook Jupyter',
            'python_script': 'Script Python'
        };
        return formatMap[format] || format?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Formato Desconocido';
    }
}

// Export for use in other modules
window.Utils = Utils;
