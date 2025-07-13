/* ============================================================================
   SQL ANALYZER ENTERPRISE - NAVIGATION MODULE
   View switching, routing, breadcrumb management, history tracking
   ============================================================================ */

class NavigationManager {
    constructor() {
        this.currentView = null;
        this.navigationHistory = [];
        this.maxHistoryLength = 50;
        this.routes = new Map();
        this.breadcrumbs = [];

        this.init();
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    init() {
        try {
            this.setupRoutes();
            this.detectCurrentView();
            this.setupEventListeners();
            this.updateBreadcrumbs();
            this.loadNavigationHistory();
            if (window.Utils) {
                Utils.log('✅ NavigationManager initialized successfully');
            }
        } catch (error) {
            if (window.Utils) Utils.error('❌ NavigationManager initialization failed:', error);
            this.handleInitializationError(error);
        }
    }

    handleInitializationError(error) {
        // Fallback initialization for critical functionality
        try {
            this.currentView = 'auth';
            this.navigationHistory = [];
            this.breadcrumbs = [];
            if (window.Utils) Utils.warn('⚠️ NavigationManager running in fallback mode');
        } catch (fallbackError) {
            if (window.Utils) Utils.error('❌ NavigationManager fallback failed:', fallbackError);
        }
    }

    setupRoutes() {
        // Define application routes
        this.routes.set('/', {
            name: 'Authentication',
            title: 'Sign In - SQL Analyzer Enterprise',
            icon: 'fas fa-sign-in-alt',
            requiresAuth: false
        });

        this.routes.set('/auth', {
            name: 'Authentication',
            title: 'Sign In - SQL Analyzer Enterprise',
            icon: 'fas fa-sign-in-alt',
            requiresAuth: false
        });

        this.routes.set('/dashboard', {
            name: 'Dashboard',
            title: 'Dashboard - SQL Analyzer Enterprise',
            icon: 'fas fa-tachometer-alt',
            requiresAuth: true,
            parent: null
        });

        this.routes.set('/profile', {
            name: 'Profile',
            title: 'User Profile - SQL Analyzer Enterprise',
            icon: 'fas fa-user',
            requiresAuth: true,
            parent: '/dashboard'
        });

        this.routes.set('/settings', {
            name: 'Settings',
            title: 'Settings - SQL Analyzer Enterprise',
            icon: 'fas fa-cog',
            requiresAuth: true,
            parent: '/dashboard'
        });

        this.routes.set('/history', {
            name: 'History',
            title: 'Analysis History - SQL Analyzer Enterprise',
            icon: 'fas fa-history',
            requiresAuth: true,
            parent: '/dashboard'
        });

        this.routes.set('/results', {
            name: 'Results',
            title: 'Analysis Results - SQL Analyzer Enterprise',
            icon: 'fas fa-chart-line',
            requiresAuth: true,
            parent: '/history'
        });
    }

    detectCurrentView() {
        const path = window.location.pathname;
        this.currentView = this.routes.get(path) || null;

        if (this.currentView) {
            document.title = this.currentView.title;
        }
    }

    setupEventListeners() {
        try {
            // Handle browser back/forward buttons
            if (window && window.addEventListener) {
                window.addEventListener('popstate', (e) => {
                    try {
                        this.handlePopState(e);
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ PopState handler error:', error);
                    }
                });
            }

            // Handle navigation links
            if (document && document.addEventListener) {
                document.addEventListener('click', (e) => {
                    try {
                        const link = e.target.closest('a[href]');
                        if (link && this.shouldInterceptNavigation(link)) {
                            e.preventDefault();
                            this.navigateTo(link.href);
                        }

                        // Handle nav-link clicks with data-view
                        const navLink = e.target.closest('.nav-link[data-view]');
                        if (navLink) {
                            e.preventDefault();
                            const view = navLink.getAttribute('data-view');
                            this.navigateTo(view);
                        }
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ Click handler error:', error);
                    }
                });

                // Handle page visibility changes
                document.addEventListener('visibilitychange', () => {
                    try {
                        if (!document.hidden) {
                            this.updateLastVisited();
                        }
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ Visibility change handler error:', error);
                    }
                });
            }

            // Handle before unload
            if (window && window.addEventListener) {
                window.addEventListener('beforeunload', () => {
                    try {
                        this.saveNavigationHistory();
                    } catch (error) {
                        if (window.Utils) Utils.error('❌ Before unload handler error:', error);
                    }
                });
            }

            if (window.Utils) {
                Utils.log('✅ Event listeners setup successfully');
            }
        } catch (error) {
            if (window.Utils) Utils.error('❌ setupEventListeners failed:', error);
        }
    }

    // ========================================================================
    // NAVIGATION METHODS
    // ========================================================================

    navigateTo(url, options = {}) {
        const { replace = false, state = null } = options;

        // Parse URL
        const urlObj = new URL(url, window.location.origin);
        const path = urlObj.pathname;
        const route = this.routes.get(path);

        if (!route) {
            if (window.Utils) Utils.warn(`Unknown route: ${path}`);
            return false;
        }

        // Check authentication requirements
        if (route.requiresAuth && !this.isAuthenticated()) {
            this.redirectToAuth(path);
            return false;
        }

        // Add to navigation history
        if (!replace) {
            this.addToHistory(this.currentView, window.location.href);
        }

        // Update browser history
        if (replace) {
            window.history.replaceState(state, route.title, url);
        } else {
            window.history.pushState(state, route.title, url);
        }

        // Update current view
        this.currentView = route;
        document.title = route.title;

        // Update breadcrumbs
        this.updateBreadcrumbs();

        // Navigate to the new page
        window.location.href = url;

        return true;
    }

    goBack() {
        if (this.navigationHistory.length > 0) {
            const previousEntry = this.navigationHistory.pop();
            this.navigateTo(previousEntry.url, { replace: true });
        } else {
            window.history.back();
        }
    }

    goForward() {
        window.history.forward();
    }

    goHome() {
        if (this.isAuthenticated()) {
            this.navigateTo('/dashboard');
        } else {
            this.navigateTo('/');
        }
    }

    refresh() {
        window.location.reload();
    }

    // ========================================================================
    // BREADCRUMB MANAGEMENT
    // ========================================================================

    updateBreadcrumbs() {
        this.breadcrumbs = this.buildBreadcrumbPath(this.currentView);
        this.renderBreadcrumbs();
    }

    buildBreadcrumbPath(route) {
        const path = [];
        let current = route;

        while (current) {
            path.unshift({
                name: current.name,
                url: this.getRouteUrl(current),
                icon: current.icon,
                active: current === route
            });

            // Find parent route
            if (current.parent) {
                current = this.routes.get(current.parent);
            } else {
                current = null;
            }
        }

        return path;
    }

    getRouteUrl(route) {
        // Find the URL for a route object
        for (const [url, routeObj] of this.routes.entries()) {
            if (routeObj === route) {
                return url;
            }
        }
        return '/';
    }

    renderBreadcrumbs() {
        const breadcrumbContainer = document.querySelector('.breadcrumb');
        if (!breadcrumbContainer || this.breadcrumbs.length <= 1) {
            return;
        }

        breadcrumbContainer.innerHTML = this.breadcrumbs.map((crumb, index) => {
            const isLast = index === this.breadcrumbs.length - 1;

            if (isLast) {
                return `
                    <li class="breadcrumb-item active" aria-current="page">
                        <i class="${crumb.icon} me-1"></i>
                        ${crumb.name}
                    </li>
                `;
            } else {
                return `
                    <li class="breadcrumb-item">
                        <a href="${crumb.url}">
                            <i class="${crumb.icon} me-1"></i>
                            ${crumb.name}
                        </a>
                    </li>
                `;
            }
        }).join('');
    }

    // ========================================================================
    // HISTORY MANAGEMENT
    // ========================================================================

    addToHistory(route, url) {
        if (!route || !url) return;

        const entry = {
            route: route,
            url: url,
            timestamp: Date.now(),
            title: route.title
        };

        // Remove duplicate entries
        this.navigationHistory = this.navigationHistory.filter(
            item => item.url !== url
        );

        // Add to beginning
        this.navigationHistory.unshift(entry);

        // Limit history length
        if (this.navigationHistory.length > this.maxHistoryLength) {
            this.navigationHistory.splice(this.maxHistoryLength);
        }

        this.saveNavigationHistory();
    }

    loadNavigationHistory() {
        const stored = Utils.getStorage('sqlAnalyzer_navigationHistory', []);
        this.navigationHistory = stored.slice(0, this.maxHistoryLength);
    }

    saveNavigationHistory() {
        Utils.setStorage('sqlAnalyzer_navigationHistory', this.navigationHistory);
    }

    clearHistory() {
        this.navigationHistory = [];
        this.saveNavigationHistory();
    }

    getRecentPages(limit = 10) {
        return this.navigationHistory.slice(0, limit);
    }

    // ========================================================================
    // EVENT HANDLERS
    // ========================================================================

    handlePopState(e) {
        // Handle browser back/forward navigation
        this.detectCurrentView();
        this.updateBreadcrumbs();
    }

    shouldInterceptNavigation(link) {
        // Check if we should handle this navigation internally
        const href = link.getAttribute('href');

        // Don't intercept external links
        if (href.startsWith('http') && !href.startsWith(window.location.origin)) {
            return false;
        }

        // Don't intercept links with target="_blank"
        if (link.getAttribute('target') === '_blank') {
            return false;
        }

        // Don't intercept download links
        if (link.hasAttribute('download')) {
            return false;
        }

        // Don't intercept mailto/tel links
        if (href.startsWith('mailto:') || href.startsWith('tel:')) {
            return false;
        }

        return true;
    }

    // ========================================================================
    // AUTHENTICATION HELPERS
    // ========================================================================

    isAuthenticated() {
        return window.authManager ? authManager.isAuthenticated() : false;
    }

    redirectToAuth(returnUrl = null) {
        if (returnUrl) {
            Utils.setStorage('sqlAnalyzer_redirectAfterLogin', returnUrl);
        }

        this.navigateTo('/', { replace: true });
    }

    handleAuthenticationSuccess() {
        const redirectUrl = Utils.getStorage('sqlAnalyzer_redirectAfterLogin');
        Utils.removeStorage('sqlAnalyzer_redirectAfterLogin');

        if (redirectUrl && this.routes.has(redirectUrl)) {
            this.navigateTo(redirectUrl);
        } else {
            this.navigateTo('/dashboard');
        }
    }

    handleAuthenticationFailure() {
        this.navigateTo('/');
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    getCurrentRoute() {
        return this.currentView;
    }

    getCurrentPath() {
        return window.location.pathname;
    }

    getRouteByPath(path) {
        return this.routes.get(path);
    }

    getAllRoutes() {
        return Array.from(this.routes.entries()).map(([path, route]) => ({
            path,
            ...route
        }));
    }

    updateLastVisited() {
        if (this.currentView) {
            Utils.setStorage('sqlAnalyzer_lastVisited', {
                path: window.location.pathname,
                timestamp: Date.now(),
                title: this.currentView.title
            });
        }
    }

    getLastVisited() {
        return Utils.getStorage('sqlAnalyzer_lastVisited');
    }

    // ========================================================================
    // NAVIGATION SHORTCUTS
    // ========================================================================

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Only handle shortcuts when not in input fields
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            // Ctrl/Cmd + shortcuts
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'h':
                        e.preventDefault();
                        this.navigateTo('/dashboard');
                        break;
                    case 'u':
                        e.preventDefault();
                        this.navigateTo('/profile');
                        break;
                    case ',':
                        e.preventDefault();
                        this.navigateTo('/settings');
                        break;
                    case 'r':
                        e.preventDefault();
                        this.navigateTo('/results');
                        break;
                }
            }

            // Alt + shortcuts
            if (e.altKey) {
                switch (e.key) {
                    case 'ArrowLeft':
                        e.preventDefault();
                        this.goBack();
                        break;
                    case 'ArrowRight':
                        e.preventDefault();
                        this.goForward();
                        break;
                }
            }
        });
    }

    // ========================================================================
    // PROGRESS TRACKING
    // ========================================================================

    showNavigationProgress() {
        // Show a progress indicator during navigation
        const progressBar = document.createElement('div');
        progressBar.id = 'navigation-progress';
        progressBar.className = 'navigation-progress';
        progressBar.innerHTML = '<div class="progress-bar"></div>';

        document.body.appendChild(progressBar);

        // Animate progress
        setTimeout(() => {
            progressBar.querySelector('.progress-bar').style.width = '100%';
        }, 10);
    }

    hideNavigationProgress() {
        const progressBar = document.getElementById('navigation-progress');
        if (progressBar) {
            progressBar.remove();
        }
    }

    // ========================================================================
    // ANALYTICS AND TRACKING
    // ========================================================================

    trackPageView(route) {
        // Track page views for analytics
        const pageView = {
            path: window.location.pathname,
            title: route.title,
            timestamp: Date.now(),
            referrer: document.referrer,
            userAgent: navigator.userAgent
        };

        // Store locally (in production, send to analytics service)
        const pageViews = Utils.getStorage('sqlAnalyzer_pageViews', []);
        pageViews.unshift(pageView);

        // Keep only last 100 page views
        if (pageViews.length > 100) {
            pageViews.splice(100);
        }

        Utils.setStorage('sqlAnalyzer_pageViews', pageViews);
    }

    getPageViewStats() {
        const pageViews = Utils.getStorage('sqlAnalyzer_pageViews', []);

        // Calculate statistics
        const stats = {
            totalViews: pageViews.length,
            uniquePages: new Set(pageViews.map(pv => pv.path)).size,
            mostVisited: this.getMostVisitedPages(pageViews),
            recentViews: pageViews.slice(0, 10)
        };

        return stats;
    }

    getMostVisitedPages(pageViews) {
        const counts = {};
        pageViews.forEach(pv => {
            counts[pv.path] = (counts[pv.path] || 0) + 1;
        });

        return Object.entries(counts)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 5)
            .map(([path, count]) => ({ path, count }));
    }
}

// Create global instance
window.navigationManager = new NavigationManager();
window.NavigationManager = NavigationManager;
