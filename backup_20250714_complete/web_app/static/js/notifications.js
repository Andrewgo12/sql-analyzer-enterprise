/* ============================================================================
   SQL ANALYZER ENTERPRISE - NOTIFICATIONS MODULE
   Professional notification system with multiple types and animations
   ============================================================================ */

class NotificationManager {
    constructor() {
        this.notifications = new Map();
        this.container = null;
        this.maxNotifications = 5;
        this.defaultDuration = 5000;
        this.positions = {
            'top-right': { top: '20px', right: '20px' },
            'top-left': { top: '20px', left: '20px' },
            'bottom-right': { bottom: '20px', right: '20px' },
            'bottom-left': { bottom: '20px', left: '20px' },
            'top-center': { top: '20px', left: '50%', transform: 'translateX(-50%)' },
            'bottom-center': { bottom: '20px', left: '50%', transform: 'translateX(-50%)' }
        };
        this.currentPosition = 'top-right';

        this.init();
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    init() {
        this.createContainer();
        this.setupStyles();

        // Make notification functions globally available
        window.showNotification = (message, type = 'info', duration = 5000) => {
            this.show(message, type, duration);
        };

        window.hideNotification = (id) => {
            this.hide(id);
        };

        window.clearAllNotifications = () => {
            this.clearAll();
        };

        if (window.Utils) Utils.log('✅ Notification system initialized');
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = 'notification-container';
        this.updateContainerPosition();
        document.body.appendChild(this.container);
    }

    updateContainerPosition() {
        if (!this.container) return;

        const position = this.positions[this.currentPosition];
        Object.assign(this.container.style, {
            position: 'fixed',
            zIndex: '10000',
            pointerEvents: 'none',
            ...position
        });
    }

    setupStyles() {
        if (document.getElementById('notification-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification-container {
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 400px;
            }
            
            .notification-item {
                background: var(--bg-primary, #ffffff);
                border: 1px solid var(--border-color, #e2e8f0);
                border-radius: var(--border-radius, 8px);
                box-shadow: var(--shadow-lg, 0 10px 25px rgba(0, 0, 0, 0.1));
                padding: 16px;
                pointer-events: auto;
                transform: translateX(100%);
                opacity: 0;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
                min-width: 300px;
                max-width: 400px;
            }
            
            .notification-item.show {
                transform: translateX(0);
                opacity: 1;
            }
            
            .notification-item.hide {
                transform: translateX(100%);
                opacity: 0;
                margin-bottom: -80px;
            }
            
            .notification-item::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: var(--notification-color);
            }
            
            .notification-item.success {
                --notification-color: var(--success-color, #059669);
                border-left-color: var(--success-color, #059669);
            }
            
            .notification-item.error {
                --notification-color: var(--danger-color, #dc2626);
                border-left-color: var(--danger-color, #dc2626);
            }
            
            .notification-item.warning {
                --notification-color: var(--warning-color, #d97706);
                border-left-color: var(--warning-color, #d97706);
            }
            
            .notification-item.info {
                --notification-color: var(--info-color, #2563eb);
                border-left-color: var(--info-color, #2563eb);
            }
            
            .notification-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 8px;
            }
            
            .notification-title {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 600;
                color: var(--text-primary, #1f2937);
                font-size: 14px;
            }
            
            .notification-icon {
                font-size: 16px;
                color: var(--notification-color);
            }
            
            .notification-close {
                background: none;
                border: none;
                color: var(--text-muted, #6b7280);
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: all 0.2s;
                font-size: 14px;
            }
            
            .notification-close:hover {
                background: var(--bg-tertiary, #f3f4f6);
                color: var(--text-primary, #1f2937);
            }
            
            .notification-message {
                color: var(--text-secondary, #4b5563);
                font-size: 13px;
                line-height: 1.4;
                white-space: pre-wrap;
            }
            
            .notification-actions {
                margin-top: 12px;
                display: flex;
                gap: 8px;
                justify-content: flex-end;
            }
            
            .notification-action {
                padding: 4px 12px;
                border: 1px solid var(--border-color, #e2e8f0);
                border-radius: 4px;
                background: var(--bg-primary, #ffffff);
                color: var(--text-primary, #1f2937);
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .notification-action:hover {
                background: var(--bg-tertiary, #f3f4f6);
            }
            
            .notification-action.primary {
                background: var(--primary-color, #2563eb);
                color: white;
                border-color: var(--primary-color, #2563eb);
            }
            
            .notification-action.primary:hover {
                background: var(--primary-color-dark, #1d4ed8);
            }
            
            .notification-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 2px;
                background: var(--notification-color);
                transition: width linear;
            }
            
            @media (max-width: 768px) {
                .notification-container {
                    left: 10px !important;
                    right: 10px !important;
                    transform: none !important;
                    max-width: none;
                }
                
                .notification-item {
                    min-width: auto;
                    max-width: none;
                }
            }
        `;

        document.head.appendChild(styles);
    }

    // ========================================================================
    // NOTIFICATION CREATION
    // ========================================================================

    show(message, type = 'info', options = {}) {
        const id = Utils.generateId('notification');

        const notification = {
            id,
            message,
            type,
            title: options.title || this.getDefaultTitle(type),
            icon: options.icon || this.getDefaultIcon(type),
            duration: options.duration !== undefined ? options.duration : this.defaultDuration,
            persistent: options.persistent || false,
            actions: options.actions || [],
            onClick: options.onClick,
            onClose: options.onClose,
            createdAt: Date.now()
        };

        this.notifications.set(id, notification);
        this.renderNotification(notification);

        // Auto-dismiss if not persistent
        if (!notification.persistent && notification.duration > 0) {
            this.scheduleAutoDismiss(id, notification.duration);
        }

        // Limit number of notifications
        this.enforceMaxNotifications();

        return id;
    }

    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    error(message, options = {}) {
        return this.show(message, 'error', { duration: 0, ...options });
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    // ========================================================================
    // NOTIFICATION RENDERING
    // ========================================================================

    renderNotification(notification) {
        const element = document.createElement('div');
        element.className = `notification-item ${notification.type}`;
        element.id = `notification-${notification.id}`;

        element.innerHTML = `
            <div class="notification-header">
                <div class="notification-title">
                    <i class="notification-icon ${notification.icon}"></i>
                    ${Utils.sanitizeHtml(notification.title)}
                </div>
                <button class="notification-close" onclick="notificationManager.dismiss('${notification.id}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="notification-message">${Utils.sanitizeHtml(notification.message)}</div>
            ${this.renderActions(notification.actions, notification.id)}
            ${notification.duration > 0 && !notification.persistent ?
                `<div class="notification-progress" style="width: 100%"></div>` : ''}
        `;

        // Add click handler
        if (notification.onClick) {
            element.addEventListener('click', (e) => {
                if (!e.target.closest('.notification-close') && !e.target.closest('.notification-action')) {
                    notification.onClick(notification);
                }
            });
            element.style.cursor = 'pointer';
        }

        // Add to container
        this.container.appendChild(element);

        // Trigger animation
        requestAnimationFrame(() => {
            element.classList.add('show');
        });

        // Start progress animation
        if (notification.duration > 0 && !notification.persistent) {
            this.animateProgress(element, notification.duration);
        }
    }

    renderActions(actions, notificationId) {
        if (!actions || actions.length === 0) return '';

        return `
            <div class="notification-actions">
                ${actions.map(action => `
                    <button class="notification-action ${action.primary ? 'primary' : ''}" 
                            onclick="notificationManager.handleAction('${notificationId}', '${action.id}')">
                        ${action.icon ? `<i class="${action.icon}"></i> ` : ''}${Utils.sanitizeHtml(action.label)}
                    </button>
                `).join('')}
            </div>
        `;
    }

    // ========================================================================
    // NOTIFICATION MANAGEMENT
    // ========================================================================

    dismiss(id) {
        const notification = this.notifications.get(id);
        if (!notification) return;

        const element = document.getElementById(`notification-${id}`);
        if (element) {
            element.classList.add('hide');

            setTimeout(() => {
                element.remove();
            }, 300);
        }

        // Call onClose callback
        if (notification.onClose) {
            notification.onClose(notification);
        }

        this.notifications.delete(id);
    }

    dismissAll() {
        const ids = Array.from(this.notifications.keys());
        ids.forEach(id => this.dismiss(id));
    }

    dismissByType(type) {
        const notifications = Array.from(this.notifications.values());
        notifications
            .filter(n => n.type === type)
            .forEach(n => this.dismiss(n.id));
    }

    scheduleAutoDismiss(id, duration) {
        setTimeout(() => {
            this.dismiss(id);
        }, duration);
    }

    enforceMaxNotifications() {
        const notifications = Array.from(this.notifications.values())
            .sort((a, b) => a.createdAt - b.createdAt);

        while (notifications.length > this.maxNotifications) {
            const oldest = notifications.shift();
            this.dismiss(oldest.id);
        }
    }

    animateProgress(element, duration) {
        const progressBar = element.querySelector('.notification-progress');
        if (!progressBar) return;

        progressBar.style.transition = `width ${duration}ms linear`;

        requestAnimationFrame(() => {
            progressBar.style.width = '0%';
        });
    }

    // ========================================================================
    // ACTION HANDLING
    // ========================================================================

    handleAction(notificationId, actionId) {
        const notification = this.notifications.get(notificationId);
        if (!notification) return;

        const action = notification.actions.find(a => a.id === actionId);
        if (!action) return;

        // Execute action handler
        if (action.handler) {
            action.handler(notification, action);
        }

        // Auto-dismiss unless specified otherwise
        if (action.dismissOnClick !== false) {
            this.dismiss(notificationId);
        }
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    getDefaultTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };
        return titles[type] || 'Notification';
    }

    getDefaultIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || 'fas fa-bell';
    }

    setPosition(position) {
        if (this.positions[position]) {
            this.currentPosition = position;
            this.updateContainerPosition();
        }
    }

    setMaxNotifications(max) {
        this.maxNotifications = max;
        this.enforceMaxNotifications();
    }

    getActiveNotifications() {
        return Array.from(this.notifications.values());
    }

    hasNotifications() {
        return this.notifications.size > 0;
    }

    getNotificationCount() {
        return this.notifications.size;
    }
}

// Create global instance and functions
window.notificationManager = new NotificationManager();
window.NotificationManager = NotificationManager;

// Global convenience functions
window.showNotification = (message, type = 'info', options = {}) => {
    return notificationManager.show(message, type, options);
};

window.showSuccess = (message, options = {}) => {
    return notificationManager.success(message, options);
};

window.showError = (message, options = {}) => {
    return notificationManager.error(message, options);
};

window.showWarning = (message, options = {}) => {
    return notificationManager.warning(message, options);
};

window.showInfo = (message, options = {}) => {
    return notificationManager.info(message, options);
};
