/* ============================================================================
   SQL ANALYZER ENTERPRISE - EVENTS MODULE
   Master event handler for all user interactions across all views
   ============================================================================ */

class EventManager {
    constructor() {
        this.eventListeners = new Map();
        this.globalHandlers = new Map();
        this.delegatedEvents = new Map();
        this.customEvents = new Map();

        this.init();
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    init() {
        this.setupGlobalEventHandlers();
        this.setupKeyboardShortcuts();
        this.setupFormHandlers();
        this.setupModalHandlers();
        this.setupNotificationHandlers();
        this.setupErrorHandlers();
    }

    // ========================================================================
    // GLOBAL EVENT HANDLERS
    // ========================================================================

    setupGlobalEventHandlers() {
        // Document ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.handleDocumentReady();
            });
        } else {
            this.handleDocumentReady();
        }

        // Window load
        window.addEventListener('load', () => {
            this.handleWindowLoad();
        });

        // Window resize
        window.addEventListener('resize', Utils.debounce(() => {
            this.handleWindowResize();
        }, 250));

        // Window scroll
        window.addEventListener('scroll', Utils.throttle(() => {
            this.handleWindowScroll();
        }, 100));

        // Visibility change
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });

        // Online/offline
        window.addEventListener('online', () => {
            this.handleOnlineStatusChange(true);
        });

        window.addEventListener('offline', () => {
            this.handleOnlineStatusChange(false);
        });

        // Before unload
        window.addEventListener('beforeunload', (e) => {
            this.handleBeforeUnload(e);
        });

        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            this.handleUnhandledRejection(e);
        });

        // Global error handler
        window.addEventListener('error', (e) => {
            this.handleGlobalError(e);
        });
    }

    // ========================================================================
    // KEYBOARD SHORTCUTS
    // ========================================================================

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcut(e);
        });
    }

    handleKeyboardShortcut(e) {
        // Skip if user is typing in input fields
        if (this.isTypingInInput(e.target)) {
            return;
        }

        const key = e.key.toLowerCase();
        const ctrl = e.ctrlKey || e.metaKey;
        const alt = e.altKey;
        const shift = e.shiftKey;

        // Global shortcuts
        if (ctrl && !alt && !shift) {
            switch (key) {
                case 'k':
                    e.preventDefault();
                    this.openGlobalSearch();
                    break;
                case '/':
                    e.preventDefault();
                    this.openHelp();
                    break;
                case 'n':
                    e.preventDefault();
                    this.createNewAnalysis();
                    break;
                case 's':
                    e.preventDefault();
                    this.saveCurrentWork();
                    break;
            }
        }

        // Alt shortcuts
        if (alt && !ctrl && !shift) {
            switch (key) {
                case '1':
                    e.preventDefault();
                    this.navigateToView('/dashboard');
                    break;
                case '2':
                    e.preventDefault();
                    this.navigateToView('/history');
                    break;
                case '3':
                    e.preventDefault();
                    this.navigateToView('/profile');
                    break;
                case '4':
                    e.preventDefault();
                    this.navigateToView('/settings');
                    break;
            }
        }

        // Escape key
        if (key === 'escape') {
            this.handleEscapeKey();
        }

        // Enter key
        if (key === 'enter') {
            this.handleEnterKey(e);
        }
    }

    isTypingInInput(element) {
        const tagName = element.tagName.toLowerCase();
        const inputTypes = ['input', 'textarea', 'select'];
        const contentEditable = element.contentEditable === 'true';

        return inputTypes.includes(tagName) || contentEditable;
    }

    // ========================================================================
    // FORM HANDLERS
    // ========================================================================

    setupFormHandlers() {
        // Delegate form events
        document.addEventListener('submit', (e) => {
            this.handleFormSubmit(e);
        });

        document.addEventListener('input', (e) => {
            this.handleFormInput(e);
        });

        document.addEventListener('change', (e) => {
            this.handleFormChange(e);
        });

        document.addEventListener('focus', (e) => {
            this.handleFormFocus(e);
        }, true);

        document.addEventListener('blur', (e) => {
            this.handleFormBlur(e);
        }, true);
    }

    handleFormSubmit(e) {
        const form = e.target;

        // Prevent double submission
        if (form.dataset.submitting === 'true') {
            e.preventDefault();
            return;
        }

        // Mark as submitting
        form.dataset.submitting = 'true';

        // Add loading state
        this.addFormLoadingState(form);

        // Custom form handlers
        if (form.id === 'authForm') {
            this.handleAuthFormSubmit(e);
        } else if (form.id === 'profileForm') {
            this.handleProfileFormSubmit(e);
        } else if (form.classList.contains('analysis-form')) {
            this.handleAnalysisFormSubmit(e);
        }

        // Reset submitting state after a delay
        setTimeout(() => {
            form.dataset.submitting = 'false';
            this.removeFormLoadingState(form);
        }, 1000);
    }

    handleFormInput(e) {
        const input = e.target;

        // Real-time validation
        if (input.dataset.validate) {
            this.validateInput(input);
        }

        // Auto-save for certain forms
        if (input.closest('.auto-save-form')) {
            this.scheduleAutoSave(input.closest('form'));
        }

        // Update activity timestamp
        if (window.authManager) {
            authManager.updateActivity();
        }
    }

    handleFormChange(e) {
        const input = e.target;

        // Handle specific input types
        if (input.type === 'file') {
            this.handleFileInputChange(e);
        } else if (input.classList.contains('settings-toggle')) {
            this.handleSettingsToggle(e);
        }
    }

    // ========================================================================
    // MODAL HANDLERS
    // ========================================================================

    setupModalHandlers() {
        // Modal show/hide events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-enterprise')) {
                this.closeModal(e.target.id);
            }
        });

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeTopModal();
            }
        });
    }

    // ========================================================================
    // NOTIFICATION HANDLERS
    // ========================================================================

    setupNotificationHandlers() {
        // Auto-dismiss notifications
        this.setupNotificationAutoDismiss();

        // Notification click handlers
        document.addEventListener('click', (e) => {
            if (e.target.closest('.notification-item')) {
                this.handleNotificationClick(e);
            }
        });
    }

    setupNotificationAutoDismiss() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE &&
                        node.classList.contains('notification-item')) {
                        this.scheduleNotificationDismiss(node);
                    }
                });
            });
        });

        const notificationContainer = document.getElementById('notification-container');
        if (notificationContainer) {
            observer.observe(notificationContainer, { childList: true });
        }
    }

    // ========================================================================
    // ERROR HANDLERS
    // ========================================================================

    setupErrorHandlers() {
        // API error handling
        this.on('api-error', (error) => {
            this.handleAPIError(error);
        });

        // Upload error handling
        this.on('upload-error', (error) => {
            this.handleUploadError(error);
        });

        // Analysis error handling
        this.on('analysis-error', (error) => {
            this.handleAnalysisError(error);
        });
    }

    // ========================================================================
    // CUSTOM EVENT SYSTEM
    // ========================================================================

    on(eventName, handler) {
        if (!this.customEvents.has(eventName)) {
            this.customEvents.set(eventName, []);
        }
        this.customEvents.get(eventName).push(handler);
    }

    off(eventName, handler) {
        if (this.customEvents.has(eventName)) {
            const handlers = this.customEvents.get(eventName);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    emit(eventName, data) {
        if (this.customEvents.has(eventName)) {
            this.customEvents.get(eventName).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    Utils.logError(error, `Custom event handler error: ${eventName}`);
                }
            });
        }
    }

    // ========================================================================
    // SPECIFIC EVENT HANDLERS
    // ========================================================================

    handleDocumentReady() {
        // Initialize all managers
        this.initializeManagers();

        // Setup tooltips
        this.initializeTooltips();

        // Setup accessibility features
        this.setupAccessibility();

        // Emit ready event
        this.emit('app-ready');
    }

    handleWindowLoad() {
        // Hide loading screens
        this.hideLoadingScreens();

        // Initialize heavy components
        this.initializeHeavyComponents();

        // Emit loaded event
        this.emit('app-loaded');
    }

    handleWindowResize() {
        // Update responsive components
        this.updateResponsiveComponents();

        // Resize charts
        if (window.resultsManager) {
            resultsManager.resizeCharts();
        }

        // Emit resize event
        this.emit('window-resize', {
            width: window.innerWidth,
            height: window.innerHeight
        });
    }

    handleWindowScroll() {
        // Update scroll-dependent components
        this.updateScrollComponents();

        // Emit scroll event
        this.emit('window-scroll', {
            scrollY: window.scrollY,
            scrollX: window.scrollX
        });
    }

    handleVisibilityChange() {
        const isVisible = !document.hidden;

        if (isVisible) {
            // Page became visible
            this.handlePageVisible();
        } else {
            // Page became hidden
            this.handlePageHidden();
        }

        this.emit('visibility-change', { visible: isVisible });
    }

    handleOnlineStatusChange(isOnline) {
        // Update UI based on connection status
        this.updateConnectionStatus(isOnline);

        if (isOnline) {
            // Reconnect WebSockets
            if (window.analysisManager) {
                analysisManager.setupWebSocket();
            }
        }

        this.emit('connection-change', { online: isOnline });
    }

    handleBeforeUnload(e) {
        // Check for unsaved changes
        if (this.hasUnsavedChanges()) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }

        // Save state before leaving
        this.saveApplicationState();
    }

    handleUnhandledRejection(e) {
        Utils.logError(e.reason, 'Unhandled Promise Rejection');

        // Show user-friendly error message
        if (window.showNotification) {
            showNotification('An unexpected error occurred. Please try again.', 'error');
        }

        // Prevent default browser error handling
        e.preventDefault();
    }

    handleGlobalError(e) {
        Utils.logError(e.error, 'Global Error');

        // Show user-friendly error message
        if (window.showNotification) {
            showNotification('An error occurred. Please refresh the page if problems persist.', 'error');
        }
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    initializeManagers() {
        // Ensure all managers are initialized
        if (!window.authManager) {
            window.authManager = new AuthManager();
        }

        if (!window.apiManager) {
            window.apiManager = new APIManager();
        }

        if (!window.uploadManager) {
            window.uploadManager = new UploadManager();
        }

        if (!window.analysisManager) {
            window.analysisManager = new AnalysisManager();
        }

        if (!window.navigationManager) {
            window.navigationManager = new NavigationManager();
        }
    }

    openGlobalSearch() {
        // Implement global search functionality
        if (window.Utils) Utils.log('Global search opened');
    }

    openHelp() {
        if (window.showModal) {
            showModal('helpModal');
        }
    }

    createNewAnalysis() {
        if (window.location.pathname !== '/dashboard') {
            window.location.href = '/dashboard';
        } else {
            // Focus on upload area
            const uploadArea = document.getElementById('dropzone');
            if (uploadArea) {
                uploadArea.scrollIntoView({ behavior: 'smooth' });
                uploadArea.classList.add('highlight');
                setTimeout(() => {
                    uploadArea.classList.remove('highlight');
                }, 2000);
            }
        }
    }

    saveCurrentWork() {
        // Save current form data or analysis state
        this.emit('save-requested');
    }

    navigateToView(path) {
        if (window.navigationManager) {
            navigationManager.navigateTo(path);
        } else {
            window.location.href = path;
        }
    }

    handleEscapeKey() {
        // Close top modal or cancel current operation
        this.closeTopModal();
    }

    handleEnterKey(e) {
        // Handle enter key in specific contexts
        if (e.target.classList.contains('search-input')) {
            this.performSearch(e.target.value);
        }
    }

    closeTopModal() {
        const openModals = document.querySelectorAll('.modal-enterprise.show');
        if (openModals.length > 0) {
            const topModal = openModals[openModals.length - 1];
            this.closeModal(topModal.id);
        }
    }

    closeModal(modalId) {
        if (window.closeModal) {
            closeModal(modalId);
        }
    }

    hasUnsavedChanges() {
        // Check for unsaved form data
        const forms = document.querySelectorAll('form[data-dirty="true"]');
        return forms.length > 0;
    }

    saveApplicationState() {
        // Save current application state
        if (window.authManager) {
            authManager.updateActivity();
        }

        if (window.navigationManager) {
            navigationManager.saveNavigationHistory();
        }
    }

    updateConnectionStatus(isOnline) {
        const statusElements = document.querySelectorAll('#connection-status');
        statusElements.forEach(element => {
            element.textContent = isOnline ? 'Connected' : 'Offline';
            element.className = `badge ${isOnline ? 'bg-success' : 'bg-danger'}`;
        });
    }

    // ========================================================================
    // MISSING METHODS - ADDED FOR COMPATIBILITY
    // ========================================================================

    hideLoadingScreens() {
        // Hide all loading screens
        const loadingScreens = document.querySelectorAll('.loading-screen, .loading-overlay, .spinner-overlay');
        loadingScreens.forEach(screen => {
            screen.style.display = 'none';
            screen.classList.add('hidden');
        });

        // Remove loading class from body
        document.body.classList.remove('loading');

        if (window.Utils) Utils.log('Loading screens hidden');
    }

    handleFormFocus(e) {
        const element = e.target;

        // Add focus styling
        if (element.matches('input, textarea, select')) {
            element.classList.add('focused');

            // Handle specific input types
            if (element.type === 'file') {
                element.closest('.file-input-wrapper')?.classList.add('focused');
            }
        }
    }

    handleFormBlur(e) {
        const element = e.target;

        // Remove focus styling
        if (element.matches('input, textarea, select')) {
            element.classList.remove('focused');

            // Handle specific input types
            if (element.type === 'file') {
                element.closest('.file-input-wrapper')?.classList.remove('focused');
            }
        }
    }

    handleFileInputChange(e) {
        const input = e.target;
        const files = input.files;

        if (files && files.length > 0) {
            // Update file input display
            const wrapper = input.closest('.file-input-wrapper');
            if (wrapper) {
                const label = wrapper.querySelector('.file-input-label');
                if (label) {
                    label.textContent = files.length === 1 ? files[0].name : `${files.length} files selected`;
                }
            }

            // Emit file change event
            this.emit('file-input-change', {
                input: input,
                files: Array.from(files)
            });
        }
    }

    updateScrollComponents() {
        // Update scroll-dependent components
        const scrollY = window.scrollY;
        const scrollX = window.scrollX;

        // Update sticky headers
        const stickyHeaders = document.querySelectorAll('.sticky-header');
        stickyHeaders.forEach(header => {
            if (scrollY > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });

        // Update scroll progress indicators
        const progressBars = document.querySelectorAll('.scroll-progress');
        progressBars.forEach(bar => {
            const progress = (scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
            bar.style.width = `${Math.min(progress, 100)}%`;
        });
    }

    updateResponsiveComponents() {
        // Update responsive components based on window size
        const width = window.innerWidth;
        const height = window.innerHeight;

        // Update mobile/desktop classes
        document.body.classList.toggle('mobile', width < 768);
        document.body.classList.toggle('tablet', width >= 768 && width < 1024);
        document.body.classList.toggle('desktop', width >= 1024);

        // Update responsive tables
        const tables = document.querySelectorAll('.responsive-table');
        tables.forEach(table => {
            if (width < 768) {
                table.classList.add('mobile-view');
            } else {
                table.classList.remove('mobile-view');
            }
        });

        // Emit resize event
        this.emit('responsive-update', { width, height });
    }

    // ========================================================================
    // CLEANUP
    // ========================================================================

    destroy() {
        // Remove all event listeners
        this.eventListeners.forEach((listener, element) => {
            element.removeEventListener(listener.event, listener.handler);
        });

        this.eventListeners.clear();
        this.globalHandlers.clear();
        this.delegatedEvents.clear();
        this.customEvents.clear();
    }
}

// Create global instance
window.eventManager = new EventManager();
window.EventManager = EventManager;
