/* ============================================================================
   SQL ANALYZER ENTERPRISE - MODALS MODULE
   Professional modal system with animations and accessibility
   ============================================================================ */

class ModalManager {
    constructor() {
        this.activeModals = new Map();
        this.modalStack = [];
        this.backdropElement = null;
        this.scrollbarWidth = 0;

        this.init();
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    init() {
        this.calculateScrollbarWidth();
        this.setupStyles();
        this.setupEventListeners();

        // Make modal functions globally available
        window.showModal = (options) => {
            return this.show(options);
        };

        window.hideModal = (modalId) => {
            this.hide(modalId);
        };

        window.confirmDialog = (message, options = {}) => {
            return this.confirm(message, options);
        };

        window.alertDialog = (message, options = {}) => {
            return this.alert(message, options);
        };

        if (window.Utils) Utils.log('✅ Modal system initialized');
    }

    calculateScrollbarWidth() {
        const outer = document.createElement('div');
        outer.style.visibility = 'hidden';
        outer.style.overflow = 'scroll';
        outer.style.msOverflowStyle = 'scrollbar';
        document.body.appendChild(outer);

        const inner = document.createElement('div');
        outer.appendChild(inner);

        this.scrollbarWidth = outer.offsetWidth - inner.offsetWidth;
        outer.parentNode.removeChild(outer);
    }

    setupStyles() {
        if (document.getElementById('modal-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'modal-styles';
        styles.textContent = `
            .modal-enterprise {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1050;
                display: none;
                overflow-x: hidden;
                overflow-y: auto;
                outline: 0;
            }
            
            .modal-enterprise.show {
                display: flex;
                align-items: center;
                justify-content: center;
                animation: modalFadeIn 0.3s ease-out;
            }
            
            .modal-enterprise.hide {
                animation: modalFadeOut 0.3s ease-in;
            }
            
            .modal-backdrop {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(2px);
                z-index: 1040;
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .modal-backdrop.show {
                opacity: 1;
            }
            
            .modal-dialog {
                position: relative;
                width: auto;
                margin: 1rem;
                pointer-events: none;
                transform: scale(0.9) translateY(-20px);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .modal-enterprise.show .modal-dialog {
                transform: scale(1) translateY(0);
                pointer-events: auto;
            }
            
            .modal-content {
                position: relative;
                display: flex;
                flex-direction: column;
                width: 100%;
                pointer-events: auto;
                background: var(--bg-primary, #ffffff);
                border: 1px solid var(--border-color, #e2e8f0);
                border-radius: var(--border-radius-lg, 12px);
                box-shadow: var(--shadow-xl, 0 25px 50px rgba(0, 0, 0, 0.15));
                outline: 0;
                overflow: hidden;
            }
            
            .modal-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1.5rem;
                border-bottom: 1px solid var(--border-color, #e2e8f0);
                background: var(--bg-secondary, #f8fafc);
            }
            
            .modal-title {
                margin: 0;
                font-size: 1.25rem;
                font-weight: 600;
                color: var(--text-primary, #1f2937);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .modal-close {
                background: none;
                border: none;
                color: var(--text-muted, #6b7280);
                cursor: pointer;
                padding: 0.5rem;
                border-radius: var(--border-radius, 6px);
                transition: all 0.2s;
                font-size: 1.25rem;
                line-height: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 2rem;
                height: 2rem;
            }
            
            .modal-close:hover {
                background: var(--bg-tertiary, #f3f4f6);
                color: var(--text-primary, #1f2937);
            }
            
            .modal-body {
                position: relative;
                flex: 1 1 auto;
                padding: 1.5rem;
                overflow-y: auto;
                max-height: 70vh;
            }
            
            .modal-footer {
                display: flex;
                align-items: center;
                justify-content: flex-end;
                gap: 0.75rem;
                padding: 1.5rem;
                border-top: 1px solid var(--border-color, #e2e8f0);
                background: var(--bg-secondary, #f8fafc);
            }
            
            .modal-sm .modal-dialog { max-width: 300px; }
            .modal-md .modal-dialog { max-width: 500px; }
            .modal-lg .modal-dialog { max-width: 800px; }
            .modal-xl .modal-dialog { max-width: 1140px; }
            .modal-fullscreen .modal-dialog { 
                width: 100vw; 
                max-width: none; 
                height: 100vh; 
                margin: 0; 
            }
            .modal-fullscreen .modal-content { 
                height: 100%; 
                border: 0; 
                border-radius: 0; 
            }
            
            @keyframes modalFadeIn {
                from {
                    opacity: 0;
                }
                to {
                    opacity: 1;
                }
            }
            
            @keyframes modalFadeOut {
                from {
                    opacity: 1;
                }
                to {
                    opacity: 0;
                }
            }
            
            body.modal-open {
                overflow: hidden;
                padding-right: var(--scrollbar-compensation, 0);
            }
            
            @media (max-width: 768px) {
                .modal-dialog {
                    margin: 0.5rem;
                    max-width: calc(100% - 1rem);
                }
                
                .modal-header,
                .modal-body,
                .modal-footer {
                    padding: 1rem;
                }
                
                .modal-body {
                    max-height: 60vh;
                }
            }
        `;

        document.head.appendChild(styles);
    }

    setupEventListeners() {
        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modalStack.length > 0) {
                const topModal = this.modalStack[this.modalStack.length - 1];
                if (topModal.options.keyboard !== false) {
                    this.hide(topModal.id);
                }
            }
        });

        // Handle backdrop clicks
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-enterprise') && this.modalStack.length > 0) {
                const topModal = this.modalStack[this.modalStack.length - 1];
                if (topModal.options.backdrop !== false) {
                    this.hide(topModal.id);
                }
            }
        });
    }

    // ========================================================================
    // MODAL CREATION AND MANAGEMENT
    // ========================================================================

    show(id, options = {}) {
        // Check if modal element exists
        let modalElement = document.getElementById(id);

        if (!modalElement) {
            // Create modal dynamically if it doesn't exist
            modalElement = this.createModal(id, options);
        }

        const modal = {
            id,
            element: modalElement,
            options: {
                backdrop: true,
                keyboard: true,
                focus: true,
                size: 'md',
                ...options
            },
            isShown: false
        };

        this.activeModals.set(id, modal);
        this.modalStack.push(modal);

        // Show modal
        this.showModal(modal);

        return modal;
    }

    hide(id) {
        const modal = this.activeModals.get(id);
        if (!modal || !modal.isShown) return;

        this.hideModal(modal);
    }

    hideAll() {
        const modals = Array.from(this.activeModals.values());
        modals.forEach(modal => {
            if (modal.isShown) {
                this.hideModal(modal);
            }
        });
    }

    toggle(id, options = {}) {
        const modal = this.activeModals.get(id);
        if (modal && modal.isShown) {
            this.hide(id);
        } else {
            this.show(id, options);
        }
    }

    // ========================================================================
    // MODAL DISPLAY LOGIC
    // ========================================================================

    showModal(modal) {
        const { element, options } = modal;

        // Set size class
        element.className = `modal-enterprise modal-${options.size}`;

        // Show backdrop
        this.showBackdrop();

        // Prevent body scroll
        this.preventBodyScroll();

        // Show modal
        element.style.display = 'flex';

        // Trigger reflow
        element.offsetHeight;

        // Add show class for animation
        element.classList.add('show');

        // Focus management
        if (options.focus) {
            this.setFocus(element);
        }

        modal.isShown = true;

        // Trigger shown event
        this.triggerEvent(element, 'shown.modal', { modal });
    }

    hideModal(modal) {
        const { element } = modal;

        // Add hide class for animation
        element.classList.add('hide');

        // Wait for animation to complete
        setTimeout(() => {
            element.style.display = 'none';
            element.classList.remove('show', 'hide');

            // Remove from stack
            const index = this.modalStack.indexOf(modal);
            if (index > -1) {
                this.modalStack.splice(index, 1);
            }

            // Hide backdrop if no more modals
            if (this.modalStack.length === 0) {
                this.hideBackdrop();
                this.restoreBodyScroll();
            }

            modal.isShown = false;
            this.activeModals.delete(modal.id);

            // Trigger hidden event
            this.triggerEvent(element, 'hidden.modal', { modal });

        }, 300);
    }

    // ========================================================================
    // BACKDROP MANAGEMENT
    // ========================================================================

    showBackdrop() {
        if (this.backdropElement) return;

        this.backdropElement = document.createElement('div');
        this.backdropElement.className = 'modal-backdrop';
        document.body.appendChild(this.backdropElement);

        // Trigger reflow
        this.backdropElement.offsetHeight;

        // Show backdrop
        this.backdropElement.classList.add('show');
    }

    hideBackdrop() {
        if (!this.backdropElement) return;

        this.backdropElement.classList.remove('show');

        setTimeout(() => {
            if (this.backdropElement) {
                this.backdropElement.remove();
                this.backdropElement = null;
            }
        }, 300);
    }

    // ========================================================================
    // BODY SCROLL MANAGEMENT
    // ========================================================================

    preventBodyScroll() {
        if (document.body.classList.contains('modal-open')) return;

        document.body.style.setProperty('--scrollbar-compensation', `${this.scrollbarWidth}px`);
        document.body.classList.add('modal-open');
    }

    restoreBodyScroll() {
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('--scrollbar-compensation');
    }

    // ========================================================================
    // FOCUS MANAGEMENT
    // ========================================================================

    setFocus(element) {
        // Find first focusable element
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        } else {
            element.focus();
        }
    }

    // ========================================================================
    // DYNAMIC MODAL CREATION
    // ========================================================================

    createModal(id, options) {
        const modal = document.createElement('div');
        modal.id = id;
        modal.className = 'modal-enterprise';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', `${id}-title`);
        modal.setAttribute('aria-hidden', 'true');

        modal.innerHTML = `
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="${id}-title">
                            ${options.icon ? `<i class="${options.icon}"></i>` : ''}
                            ${options.title || 'Modal'}
                        </h5>
                        <button type="button" class="modal-close" onclick="modalManager.hide('${id}')" aria-label="Close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        ${options.content || ''}
                    </div>
                    ${options.footer ? `
                        <div class="modal-footer">
                            ${options.footer}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        return modal;
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    isShown(id) {
        const modal = this.activeModals.get(id);
        return modal ? modal.isShown : false;
    }

    getActiveModals() {
        return Array.from(this.activeModals.values()).filter(modal => modal.isShown);
    }

    getTopModal() {
        return this.modalStack.length > 0 ? this.modalStack[this.modalStack.length - 1] : null;
    }

    triggerEvent(element, eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail,
            bubbles: true,
            cancelable: true
        });
        element.dispatchEvent(event);
    }

    // ========================================================================
    // CONFIRMATION DIALOGS
    // ========================================================================

    confirm(message, options = {}) {
        return new Promise((resolve) => {
            const id = 'confirm-modal-' + Date.now();

            const modal = this.show(id, {
                title: options.title || 'Confirm',
                icon: options.icon || 'fas fa-question-circle',
                size: options.size || 'sm',
                content: `<p>${Utils.sanitizeHtml(message)}</p>`,
                footer: `
                    <button type="button" class="btn-enterprise btn-secondary" onclick="modalManager.hide('${id}'); modalManager.resolveConfirm(false)">
                        ${options.cancelText || 'Cancel'}
                    </button>
                    <button type="button" class="btn-enterprise btn-primary" onclick="modalManager.hide('${id}'); modalManager.resolveConfirm(true)">
                        ${options.confirmText || 'Confirm'}
                    </button>
                `,
                backdrop: false,
                keyboard: false
            });

            this.confirmResolver = resolve;
        });
    }

    resolveConfirm(result) {
        if (this.confirmResolver) {
            this.confirmResolver(result);
            this.confirmResolver = null;
        }
    }

    alert(message, options = {}) {
        return new Promise((resolve) => {
            const id = 'alert-modal-' + Date.now();

            const modal = this.show(id, {
                title: options.title || 'Alert',
                icon: options.icon || 'fas fa-info-circle',
                size: options.size || 'sm',
                content: `<p>${Utils.sanitizeHtml(message)}</p>`,
                footer: `
                    <button type="button" class="btn-enterprise btn-primary" onclick="modalManager.hide('${id}'); modalManager.resolveAlert()">
                        ${options.okText || 'OK'}
                    </button>
                `,
                backdrop: false,
                keyboard: true
            });

            this.alertResolver = resolve;
        });
    }

    resolveAlert() {
        if (this.alertResolver) {
            this.alertResolver();
            this.alertResolver = null;
        }
    }
}

// Create global instance and functions
window.modalManager = new ModalManager();
window.ModalManager = ModalManager;

// Global convenience functions
window.showModal = (id, options = {}) => {
    return modalManager.show(id, options);
};

window.hideModal = (id) => {
    return modalManager.hide(id);
};

window.toggleModal = (id, options = {}) => {
    return modalManager.toggle(id, options);
};

window.confirmDialog = (message, options = {}) => {
    return modalManager.confirm(message, options);
};

window.alertDialog = (message, options = {}) => {
    return modalManager.alert(message, options);
};
