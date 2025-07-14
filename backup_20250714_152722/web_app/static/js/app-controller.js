/* ============================================================================
   SQL ANALYZER ENTERPRISE - APPLICATION CONTROLLER
   Main application controller for navigation and view management
   ============================================================================ */

class AppController {
    constructor() {
        this.currentView = null;
        this.isAuthenticated = false;
        this.views = new Map();
        this.sidebarCollapsed = false;
        this.isMobile = window.innerWidth < 768;

        this.init();
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    init() {
        this.setupEventListeners();
        this.checkAuthentication();
        this.registerViews();
        this.handleInitialRoute();
    }

    setupEventListeners() {
        // Window resize handler
        window.addEventListener('resize', () => {
            this.isMobile = window.innerWidth < 768;
            this.updateSidebarForScreenSize();
        });

        // Browser navigation
        window.addEventListener('popstate', (e) => {
            this.handlePopState(e);
        });

        // Click outside to close mobile sidebar
        document.addEventListener('click', (e) => {
            if (this.isMobile && !e.target.closest('.app-sidebar') && !e.target.closest('.sidebar-toggle')) {
                this.closeSidebar();
            }
        });
    }

    registerViews() {
        // Register all available views
        this.views.set('auth', {
            name: 'Authentication',
            requiresAuth: false,
            template: 'auth',
            title: 'Sign In - SQL Analyzer Enterprise'
        });

        this.views.set('dashboard', {
            name: 'Dashboard',
            requiresAuth: true,
            template: 'dashboard',
            title: 'Dashboard - SQL Analyzer Enterprise'
        });

        this.views.set('upload', {
            name: 'Upload Files',
            requiresAuth: true,
            template: 'upload',
            title: 'Upload Files - SQL Analyzer Enterprise'
        });

        this.views.set('history', {
            name: 'Analysis History',
            requiresAuth: true,
            template: 'history',
            title: 'Analysis History - SQL Analyzer Enterprise'
        });

        this.views.set('results', {
            name: 'Results',
            requiresAuth: true,
            template: 'results',
            title: 'Analysis Results - SQL Analyzer Enterprise'
        });

        this.views.set('analyzer', {
            name: 'SQL Analyzer',
            requiresAuth: true,
            template: 'analyzer',
            title: 'SQL Analyzer - SQL Analyzer Enterprise'
        });

        this.views.set('optimizer', {
            name: 'Performance Optimizer',
            requiresAuth: true,
            template: 'optimizer',
            title: 'Performance Optimizer - SQL Analyzer Enterprise'
        });

        this.views.set('security', {
            name: 'Security Scanner',
            requiresAuth: true,
            template: 'security',
            title: 'Security Scanner - SQL Analyzer Enterprise'
        });

        this.views.set('profile', {
            name: 'Profile',
            requiresAuth: true,
            template: 'profile',
            title: 'Profile - SQL Analyzer Enterprise'
        });

        this.views.set('settings', {
            name: 'Settings',
            requiresAuth: true,
            template: 'settings',
            title: 'Settings - SQL Analyzer Enterprise'
        });
    }

    // ========================================================================
    // AUTHENTICATION MANAGEMENT
    // ========================================================================

    checkAuthentication() {
        // Check if user is authenticated
        if (window.authManager) {
            this.isAuthenticated = authManager.isAuthenticated();
        } else {
            // Fallback check
            this.isAuthenticated = !!Utils.getStorage('sqlAnalyzer_sessionId');
        }

        if (window.Utils) Utils.log('🔐 Authentication check:', this.isAuthenticated);
        this.updateUIForAuthState();
    }

    updateUIForAuthState() {
        const authView = document.getElementById('auth-view');
        const mainApp = document.getElementById('main-app');

        if (window.Utils) Utils.log('🎨 Updating UI for auth state:', this.isAuthenticated);

        if (this.isAuthenticated) {
            if (authView) authView.style.display = 'none';
            if (mainApp) mainApp.style.display = 'flex';
            this.updateUserInfo();
        } else {
            if (authView) authView.style.display = 'block';
            if (mainApp) mainApp.style.display = 'none';
            this.loadAuthView();
        }
    }

    updateUserInfo() {
        const userAvatar = document.getElementById('user-avatar');
        const username = Utils.getStorage('sqlAnalyzer_username', 'User');

        if (userAvatar) {
            userAvatar.textContent = username.charAt(0).toUpperCase();
        }
    }

    handleAuthenticationSuccess() {
        this.isAuthenticated = true;
        this.updateUIForAuthState();
        this.navigateToView('dashboard');

        if (window.showNotification) {
            showNotification('Welcome to SQL Analyzer Enterprise!', 'success');
        }
    }

    handleSignOut() {
        this.isAuthenticated = false;
        this.currentView = null;
        this.updateUIForAuthState();
        this.loadAuthView();

        // Clear any stored data
        if (window.authManager) {
            authManager.clearSession();
        }

        if (window.showNotification) {
            showNotification('You have been signed out successfully', 'info');
        }
    }

    // ========================================================================
    // NAVIGATION MANAGEMENT
    // ========================================================================

    handleInitialRoute() {
        const path = window.location.pathname;
        const viewName = path.substring(1) || 'dashboard';

        if (this.isAuthenticated) {
            this.navigateToView(viewName);
        } else {
            this.loadAuthView();
        }
    }

    navigateToView(viewName, options = {}) {
        const view = this.views.get(viewName);

        if (!view) {
            if (window.Utils) Utils.warn(`View '${viewName}' not found`);
            this.navigateToView('dashboard');
            return;
        }

        // Check authentication requirements
        if (view.requiresAuth && !this.isAuthenticated) {
            this.loadAuthView();
            return;
        }

        // Update URL without page reload
        if (!options.skipHistory) {
            const url = viewName === 'dashboard' ? '/' : `/${viewName}`;
            window.history.pushState({ view: viewName }, view.title, url);
        }

        // Update page title
        document.title = view.title;

        // Update navigation state
        this.updateNavigationState(viewName);

        // Load view content
        this.loadViewContent(viewName);

        // Close mobile sidebar
        if (this.isMobile) {
            this.closeSidebar();
        }

        this.currentView = viewName;
    }

    updateNavigationState(viewName) {
        // Update active navigation item
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.view === viewName) {
                link.classList.add('active');
            }
        });
    }

    async loadViewContent(viewName) {
        const contentContainer = document.getElementById('content-container');

        if (!contentContainer) {
            if (window.Utils) Utils.error('Content container not found');
            return;
        }

        try {
            // Show loading state
            this.showLoading();

            // Add timeout for content loading
            const loadingPromise = this.getViewContent(viewName);
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Content loading timeout')), 10000)
            );

            const content = await Promise.race([loadingPromise, timeoutPromise]);

            // Update content with fade effect
            contentContainer.style.opacity = '0';

            setTimeout(() => {
                contentContainer.innerHTML = content;
                contentContainer.style.opacity = '1';

                // Initialize view-specific functionality
                this.initializeViewFunctionality(viewName);
            }, 150);

        } catch (error) {
            if (window.Utils) Utils.error('Error loading view content:', error);
            contentContainer.innerHTML = this.getErrorContent(error.message);
            contentContainer.style.opacity = '1';

            // Track error for analytics
            this.trackNavigationError(viewName, error);
        } finally {
            // Hide loading state
            setTimeout(() => this.hideLoading(), 200);
        }
    }

    async getViewContent(viewName) {
        switch (viewName) {
            case 'dashboard':
                return await this.loadDashboardContent();
            case 'upload':
                return await this.loadUploadContent();
            case 'history':
                return await this.loadHistoryContent();
            case 'results':
                return await this.loadResultsContent();
            case 'analyzer':
                return await this.loadAnalyzerContent();
            case 'optimizer':
                return await this.loadOptimizerContent();
            case 'security':
                return await this.loadSecurityContent();
            case 'profile':
                return await this.loadProfileContent();
            case 'settings':
                return await this.loadSettingsContent();
            default:
                if (window.Utils) Utils.warn(`Unknown view: ${viewName}, falling back to dashboard`);
                return await this.loadDashboardContent();
        }
    }

    trackNavigationError(viewName, error) {
        const errorData = {
            view: viewName,
            error: error.message,
            timestamp: Date.now(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };

        // Store error for debugging
        const errors = Utils.getStorage('sqlAnalyzer_navigationErrors', []);
        errors.unshift(errorData);

        // Keep only last 50 errors
        if (errors.length > 50) {
            errors.splice(50);
        }

        Utils.setStorage('sqlAnalyzer_navigationErrors', errors);
    }

    async loadAuthView() {
        const authView = document.getElementById('auth-view');

        try {
            // Load auth content from the existing auth.html template
            const response = await fetch('/auth');
            const html = await response.text();

            // Extract the body content from the auth template
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const authContent = doc.body.innerHTML;

            authView.innerHTML = authContent;

            // Initialize auth functionality
            this.initializeAuthFunctionality();

        } catch (error) {
            if (window.Utils) Utils.error('Error loading auth view:', error);
            authView.innerHTML = this.getAuthFallbackContent();
        }
    }

    // ========================================================================
    // SIDEBAR MANAGEMENT
    // ========================================================================

    toggleSidebar() {
        if (this.isMobile) {
            const sidebar = document.getElementById('app-sidebar');
            const backdrop = document.getElementById('sidebar-backdrop');

            sidebar.classList.toggle('show');
            backdrop.classList.toggle('show');
        }
    }

    closeSidebar() {
        if (this.isMobile) {
            const sidebar = document.getElementById('app-sidebar');
            const backdrop = document.getElementById('sidebar-backdrop');

            sidebar.classList.remove('show');
            backdrop.classList.remove('show');
        }
    }

    toggleSidebarCollapse() {
        if (!this.isMobile) {
            const sidebar = document.getElementById('app-sidebar');
            this.sidebarCollapsed = !this.sidebarCollapsed;

            if (this.sidebarCollapsed) {
                sidebar.classList.add('collapsed');
            } else {
                sidebar.classList.remove('collapsed');
            }
        }
    }

    updateSidebarForScreenSize() {
        const sidebar = document.getElementById('app-sidebar');
        const backdrop = document.getElementById('sidebar-backdrop');

        if (!this.isMobile) {
            // Desktop: remove mobile classes
            sidebar.classList.remove('show');
            backdrop.classList.remove('show');
        } else {
            // Mobile: remove collapsed state
            sidebar.classList.remove('collapsed');
            this.sidebarCollapsed = false;
        }
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    showLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('show');
        }
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.remove('show');
        }
    }

    handlePopState(e) {
        if (e.state && e.state.view) {
            this.navigateToView(e.state.view, { skipHistory: true });
        } else {
            // Handle browser back to root
            const path = window.location.pathname;
            const viewName = path.substring(1) || 'dashboard';
            this.navigateToView(viewName, { skipHistory: true });
        }
    }

    getErrorContent(message) {
        return `
            <div class="text-center py-5">
                <i class="fas fa-exclamation-triangle text-warning fa-3x mb-3"></i>
                <h4>Error Loading Content</h4>
                <p class="text-muted">${Utils.sanitizeHtml(message)}</p>
                <button class="btn-enterprise btn-primary" onclick="location.reload()">
                    <i class="fas fa-redo me-2"></i>Reload Page
                </button>
            </div>
        `;
    }

    getAuthFallbackContent() {
        return `
            <div class="auth-container">
                <div class="auth-card">
                    <div class="text-center mb-4">
                        <h2>SQL Analyzer Enterprise</h2>
                        <p class="text-muted">Please sign in to continue</p>
                    </div>
                    <form id="authForm">
                        <div class="mb-3">
                            <input type="text" class="form-control" placeholder="Username" required>
                        </div>
                        <div class="mb-3">
                            <input type="password" class="form-control" placeholder="Password" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Sign In</button>
                    </form>
                </div>
            </div>
        `;
    }

    // ========================================================================
    // CONTENT LOADING METHODS
    // ========================================================================

    async loadDashboardContent() {
        return `
            <!-- Dashboard Header -->
            <header class="dashboard-header mb-4" role="banner">
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                    <div class="dashboard-title-section">
                        <h1 class="h2 mb-2 text-primary fw-bold" id="dashboard-title">
                            <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                        </h1>
                        <p class="text-muted mb-0 fs-6">
                            Bienvenido al Analizador SQL Empresarial - Su centro de control para análisis SQL avanzado
                        </p>
                        <small class="text-success">
                            <i class="fas fa-circle me-1"></i>Sistema operativo - Última actualización: ${new Date().toLocaleDateString()}
                        </small>
                    </div>
                    <div class="dashboard-actions d-flex gap-2 flex-wrap">
                        <button class="btn-enterprise btn-primary" onclick="navigateToView('upload')"
                                aria-label="Iniciar nuevo análisis SQL">
                            <i class="fas fa-plus me-2"></i>Nuevo Análisis
                        </button>
                        <button class="btn-enterprise btn-outline" onclick="navigateToView('history')"
                                aria-label="Ver historial de análisis">
                            <i class="fas fa-history me-2"></i>Historial
                        </button>
                        <div class="dropdown">
                            <button class="btn-enterprise btn-outline dropdown-toggle" type="button"
                                    data-bs-toggle="dropdown" aria-expanded="false" aria-label="Más opciones">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" data-action="runNavigationTests">
                                    <i class="fas fa-vial me-2"></i>Ejecutar Pruebas
                                </a></li>
                                <li><a class="dropdown-item" href="#" data-action="exportDashboardReport">
                                    <i class="fas fa-download me-2"></i>Exportar Reporte
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="#" data-action="navigateToSettings">
                                    <i class="fas fa-cog me-2"></i>Configuración
                                </a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Enhanced Statistics Cards -->
            <section class="dashboard-stats mb-5" role="region" aria-labelledby="stats-heading">
                <h2 id="stats-heading" class="visually-hidden">Estadísticas del Sistema</h2>
                <div class="row g-4">
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="card-enterprise stat-card" role="article" tabindex="0">
                            <div class="card-body-enterprise">
                                <div class="d-flex align-items-center">
                                    <div class="flex-shrink-0">
                                        <div class="stat-icon bg-primary" aria-hidden="true">
                                            <i class="fas fa-file-code"></i>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <div class="stat-value" id="files-count" aria-live="polite">0</div>
                                        <div class="stat-label">Archivos Analizados</div>
                                        <div class="stat-trend">
                                            <small class="text-success">
                                                <i class="fas fa-arrow-up me-1"></i>+12% este mes
                                            </small>
                                        </div>
                                    </div>
                                </div>
                                <div class="stat-progress mt-3">
                                    <div class="progress progress-enterprise">
                                        <div class="progress-bar-enterprise bg-primary" style="width: 75%"
                                             role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="card-enterprise stat-card" role="article" tabindex="0">
                            <div class="card-body-enterprise">
                                <div class="d-flex align-items-center">
                                    <div class="flex-shrink-0">
                                        <div class="stat-icon bg-success" aria-hidden="true">
                                            <i class="fas fa-check-double"></i>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <div class="stat-value" id="analyses-count" aria-live="polite">0</div>
                                        <div class="stat-label">Análisis Completados</div>
                                        <div class="stat-trend">
                                            <small class="text-success">
                                                <i class="fas fa-arrow-up me-1"></i>+8% esta semana
                                            </small>
                                        </div>
                                    </div>
                                </div>
                                <div class="stat-progress mt-3">
                                    <div class="progress progress-enterprise">
                                        <div class="progress-bar-enterprise bg-success" style="width: 92%"
                                             role="progressbar" aria-valuenow="92" aria-valuemin="0" aria-valuemax="100">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="card-enterprise stat-card" role="article" tabindex="0">
                            <div class="card-body-enterprise">
                                <div class="d-flex align-items-center">
                                    <div class="flex-shrink-0">
                                        <div class="stat-icon bg-warning" aria-hidden="true">
                                            <i class="fas fa-chart-line"></i>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <div class="stat-value" id="success-rate" aria-live="polite">98.5%</div>
                                        <div class="stat-label">Tasa de Éxito</div>
                                        <div class="stat-trend">
                                            <small class="text-success">
                                                <i class="fas fa-arrow-up me-1"></i>+2.1% mejora
                                            </small>
                                        </div>
                                    </div>
                                </div>
                                <div class="stat-progress mt-3">
                                    <div class="progress progress-enterprise">
                                        <div class="progress-bar-enterprise bg-warning" style="width: 98.5%"
                                             role="progressbar" aria-valuenow="98.5" aria-valuemin="0" aria-valuemax="100">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="card-enterprise stat-card" role="article" tabindex="0">
                            <div class="card-body-enterprise">
                                <div class="d-flex align-items-center">
                                    <div class="flex-shrink-0">
                                        <div class="stat-icon bg-info" aria-hidden="true">
                                            <i class="fas fa-stopwatch"></i>
                                        </div>
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <div class="stat-value" id="avg-time" aria-live="polite">2.3s</div>
                                        <div class="stat-label">Tiempo Promedio</div>
                                        <div class="stat-trend">
                                            <small class="text-success">
                                                <i class="fas fa-arrow-down me-1"></i>-15% más rápido
                                            </small>
                                        </div>
                                    </div>
                                </div>
                                <div class="stat-progress mt-3">
                                    <div class="progress progress-enterprise">
                                        <div class="progress-bar-enterprise bg-info" style="width: 85%"
                                             role="progressbar" aria-valuenow="85" aria-valuemin="0" aria-valuemax="100">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Enhanced Quick Actions Section -->
            <section class="dashboard-actions mb-5" role="region" aria-labelledby="actions-heading">
                <div class="row g-4">
                    <div class="col-lg-8">
                        <div class="card-enterprise">
                            <div class="card-header-enterprise d-flex justify-content-between align-items-center">
                                <h3 id="actions-heading" class="h5 mb-0">
                                    <i class="fas fa-bolt me-2 text-primary"></i>Acciones Rápidas
                                </h3>
                                <span class="badge bg-primary">4 herramientas disponibles</span>
                            </div>
                            <div class="card-body-enterprise">
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <div class="quick-action-card" onclick="navigateToView('upload')"
                                             role="button" tabindex="0" aria-label="Subir archivo SQL para análisis"
                                             onkeypress="if(event.key==='Enter') navigateToView('upload')">
                                            <div class="action-icon-wrapper">
                                                <i class="fas fa-cloud-upload-alt action-icon"></i>
                                            </div>
                                            <h6 class="action-title">Subir Archivo SQL</h6>
                                            <p class="action-description">Carga y analiza archivos SQL, TXT o PDF con contenido SQL</p>
                                            <div class="action-features">
                                                <small class="text-muted">
                                                    <i class="fas fa-check me-1"></i>Hasta 10GB
                                                    <i class="fas fa-check me-1 ms-2"></i>Múltiples formatos
                                                </small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="quick-action-card" onclick="navigateToView('analyzer')"
                                             role="button" tabindex="0" aria-label="Analizador SQL en línea"
                                             onkeypress="if(event.key==='Enter') navigateToView('analyzer')">
                                            <div class="action-icon-wrapper">
                                                <i class="fas fa-search-plus action-icon"></i>
                                            </div>
                                            <h6 class="action-title">Analizador SQL</h6>
                                            <p class="action-description">Analiza sintaxis SQL y estructura de consultas en tiempo real</p>
                                            <div class="action-features">
                                                <small class="text-muted">
                                                    <i class="fas fa-check me-1"></i>Sintaxis
                                                    <i class="fas fa-check me-1 ms-2"></i>Estructura
                                                </small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="quick-action-card" onclick="navigateToView('security')"
                                             role="button" tabindex="0" aria-label="Escáner de seguridad SQL"
                                             onkeypress="if(event.key==='Enter') navigateToView('security')">
                                            <div class="action-icon-wrapper">
                                                <i class="fas fa-shield-virus action-icon"></i>
                                            </div>
                                            <h6 class="action-title">Escáner de Seguridad</h6>
                                            <p class="action-description">Detecta vulnerabilidades y problemas de seguridad SQL</p>
                                            <div class="action-features">
                                                <small class="text-muted">
                                                    <i class="fas fa-check me-1"></i>SQL Injection
                                                    <i class="fas fa-check me-1 ms-2"></i>Mejores prácticas
                                                </small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="quick-action-card" onclick="navigateToView('optimizer')"
                                             role="button" tabindex="0" aria-label="Optimizador de rendimiento SQL"
                                             onkeypress="if(event.key==='Enter') navigateToView('optimizer')">
                                            <div class="action-icon-wrapper">
                                                <i class="fas fa-tachometer-alt action-icon"></i>
                                            </div>
                                            <h6 class="action-title">Optimizador</h6>
                                            <p class="action-description">Mejora el rendimiento y eficiencia de consultas SQL</p>
                                            <div class="action-features">
                                                <small class="text-muted">
                                                    <i class="fas fa-check me-1"></i>Índices
                                                    <i class="fas fa-check me-1 ms-2"></i>Consultas
                                                </small>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Additional Tools Row -->
                                <div class="row g-3 mt-2">
                                    <div class="col-12">
                                        <div class="additional-tools">
                                            <h6 class="text-muted mb-3">
                                                <i class="fas fa-tools me-2"></i>Herramientas Adicionales
                                            </h6>
                                            <div class="d-flex flex-wrap gap-2">
                                                <button class="btn btn-outline-primary btn-sm" onclick="navigateToView('history')">
                                                    <i class="fas fa-history me-1"></i>Historial
                                                </button>
                                                <button class="btn btn-outline-secondary btn-sm" onclick="navigateToView('results')">
                                                    <i class="fas fa-chart-bar me-1"></i>Resultados
                                                </button>
                                                <button class="btn btn-outline-info btn-sm" onclick="showDashboardHelp()">
                                                    <i class="fas fa-question-circle me-1"></i>Ayuda
                                                </button>
                                                <button class="btn btn-outline-success btn-sm" onclick="exportDashboardReport()">
                                                    <i class="fas fa-download me-1"></i>Exportar
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4">
                        <div class="card-enterprise">
                            <div class="card-header-enterprise d-flex justify-content-between align-items-center">
                                <h3 class="h5 mb-0">
                                    <i class="fas fa-clock me-2 text-info"></i>Actividad Reciente
                                </h3>
                                <button class="btn btn-outline-primary btn-sm" onclick="navigateToView('history')"
                                        aria-label="Ver todo el historial">
                                    <i class="fas fa-external-link-alt"></i>
                                </button>
                            </div>
                            <div class="card-body-enterprise">
                                <div id="recent-activity-list" role="log" aria-live="polite">
                                    <!-- Sample Recent Activities -->
                                    <div class="activity-item">
                                        <div class="activity-icon bg-success">
                                            <i class="fas fa-check"></i>
                                        </div>
                                        <div class="activity-content">
                                            <div class="activity-title">Análisis completado</div>
                                            <div class="activity-description">database_schema.sql</div>
                                            <div class="activity-time">Hace 2 minutos</div>
                                        </div>
                                    </div>

                                    <div class="activity-item">
                                        <div class="activity-icon bg-primary">
                                            <i class="fas fa-upload"></i>
                                        </div>
                                        <div class="activity-content">
                                            <div class="activity-title">Archivo subido</div>
                                            <div class="activity-description">user_queries.sql</div>
                                            <div class="activity-time">Hace 15 minutos</div>
                                        </div>
                                    </div>

                                    <div class="activity-item">
                                        <div class="activity-icon bg-warning">
                                            <i class="fas fa-exclamation-triangle"></i>
                                        </div>
                                        <div class="activity-content">
                                            <div class="activity-title">Advertencia detectada</div>
                                            <div class="activity-description">optimization_needed.sql</div>
                                            <div class="activity-time">Hace 1 hora</div>
                                        </div>
                                    </div>

                                    <div class="activity-item">
                                        <div class="activity-icon bg-info">
                                            <i class="fas fa-shield-alt"></i>
                                        </div>
                                        <div class="activity-content">
                                            <div class="activity-title">Escaneo de seguridad</div>
                                            <div class="activity-description">security_audit.sql</div>
                                            <div class="activity-time">Hace 2 horas</div>
                                        </div>
                                    </div>
                                </div>

                                <div class="activity-footer mt-3 pt-3 border-top">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">
                                            <i class="fas fa-info-circle me-1"></i>
                                            Últimas 4 actividades
                                        </small>
                                        <button class="btn btn-link btn-sm p-0" onclick="refreshRecentActivity()"
                                                aria-label="Actualizar actividad reciente">
                                            <i class="fas fa-sync-alt"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- System Status Section -->
            <section class="system-status mb-4" role="region" aria-labelledby="status-heading">
                <div class="row g-4">
                    <div class="col-lg-6">
                        <div class="card-enterprise">
                            <div class="card-header-enterprise">
                                <h3 id="status-heading" class="h5 mb-0">
                                    <i class="fas fa-server me-2 text-success"></i>Estado del Sistema
                                </h3>
                            </div>
                            <div class="card-body-enterprise">
                                <div class="status-grid">
                                    <div class="status-item">
                                        <div class="status-indicator bg-success"></div>
                                        <div class="status-info">
                                            <div class="status-label">Servidor API</div>
                                            <div class="status-value">Operativo</div>
                                        </div>
                                    </div>
                                    <div class="status-item">
                                        <div class="status-indicator bg-success"></div>
                                        <div class="status-info">
                                            <div class="status-label">Base de Datos</div>
                                            <div class="status-value">Conectada</div>
                                        </div>
                                    </div>
                                    <div class="status-item">
                                        <div class="status-indicator bg-warning"></div>
                                        <div class="status-info">
                                            <div class="status-label">Almacenamiento</div>
                                            <div class="status-value">78% usado</div>
                                        </div>
                                    </div>
                                    <div class="status-item">
                                        <div class="status-indicator bg-success"></div>
                                        <div class="status-info">
                                            <div class="status-label">Procesamiento</div>
                                            <div class="status-value">Normal</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-6">
                        <div class="card-enterprise">
                            <div class="card-header-enterprise">
                                <h3 class="h5 mb-0">
                                    <i class="fas fa-chart-pie me-2 text-primary"></i>Resumen de Uso
                                </h3>
                            </div>
                            <div class="card-body-enterprise">
                                <div class="usage-summary">
                                    <div class="usage-item">
                                        <div class="usage-label">Archivos procesados hoy</div>
                                        <div class="usage-value">24</div>
                                        <div class="usage-bar">
                                            <div class="usage-progress" style="width: 60%"></div>
                                        </div>
                                    </div>
                                    <div class="usage-item">
                                        <div class="usage-label">Tiempo total de análisis</div>
                                        <div class="usage-value">2h 15m</div>
                                        <div class="usage-bar">
                                            <div class="usage-progress" style="width: 45%"></div>
                                        </div>
                                    </div>
                                    <div class="usage-item">
                                        <div class="usage-label">Errores detectados</div>
                                        <div class="usage-value">3</div>
                                        <div class="usage-bar">
                                            <div class="usage-progress bg-warning" style="width: 15%"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        `;
    }

    async loadUploadContent() {
        return `
            <!-- Enhanced Upload Header -->
            <header class="upload-header mb-4" role="banner">
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                    <div class="upload-title-section">
                        <div class="d-flex align-items-center gap-3 mb-2">
                            <button class="btn btn-outline-secondary" onclick="navigateBack()"
                                    aria-label="Volver al dashboard">
                                <i class="fas fa-arrow-left me-2"></i>Volver
                            </button>
                            <h1 class="h2 mb-0 text-primary fw-bold">
                                <i class="fas fa-cloud-upload-alt me-2"></i>Subir Archivos
                            </h1>
                        </div>
                        <p class="text-muted mb-1">
                            Carga archivos SQL, TXT o PDF para análisis avanzado
                        </p>
                        <div class="upload-stats">
                            <small class="text-success me-3">
                                <i class="fas fa-check-circle me-1"></i>
                                <span id="upload-success-count">0</span> archivos procesados hoy
                            </small>
                            <small class="text-info">
                                <i class="fas fa-database me-1"></i>
                                Capacidad: <span id="storage-usage">2.3GB</span> / 100GB
                            </small>
                        </div>
                    </div>
                    <div class="upload-actions d-flex gap-2 flex-wrap">
                        <button class="btn-enterprise btn-outline" onclick="showUploadHistory()"
                                aria-label="Ver historial de subidas">
                            <i class="fas fa-history me-2"></i>Historial
                        </button>
                        <button class="btn-enterprise btn-outline" onclick="showUploadHelp()"
                                aria-label="Ayuda para subir archivos">
                            <i class="fas fa-question-circle me-2"></i>Ayuda
                        </button>
                    </div>
                </div>
            </header>

            <!-- Enhanced Upload Area -->
            <section class="upload-section mb-4" role="main">
                <div class="card-enterprise">
                    <div class="card-header-enterprise">
                        <h3 class="h5 mb-0">
                            <i class="fas fa-upload me-2"></i>Área de Carga
                        </h3>
                        <div class="upload-format-info">
                            <span class="badge bg-primary me-1">SQL</span>
                            <span class="badge bg-secondary me-1">TXT</span>
                            <span class="badge bg-info me-1">PDF</span>
                            <span class="badge bg-success">Hasta 10GB</span>
                        </div>
                    </div>
                    <div class="card-body-enterprise">
                        <div class="upload-area-enterprise" id="dropzone"
                             role="button" tabindex="0" aria-label="Área de carga de archivos"
                             onkeypress="if(event.key==='Enter') document.getElementById('file-input').click()">
                            <div class="upload-icon-container">
                                <div class="upload-icon-wrapper">
                                    <i class="fas fa-cloud-upload-alt upload-main-icon"></i>
                                </div>
                            </div>
                            <div class="upload-content">
                                <h4 class="upload-title">Arrastra y suelta archivos aquí</h4>
                                <p class="upload-subtitle text-muted mb-3">
                                    o haz clic para seleccionar archivos desde tu computadora
                                </p>
                                <button type="button" class="btn-enterprise btn-primary"
                                        onclick="document.getElementById('file-input').click()"
                                        aria-label="Seleccionar archivos">
                                    <i class="fas fa-folder-open me-2"></i>Seleccionar Archivos
                                </button>
                            </div>
                            <div class="upload-info mt-4">
                                <div class="row g-3 text-center">
                                    <div class="col-md-3">
                                        <div class="info-item">
                                            <i class="fas fa-file-code text-primary"></i>
                                            <div class="info-label">Formatos</div>
                                            <div class="info-value">SQL, TXT, PDF</div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="info-item">
                                            <i class="fas fa-weight-hanging text-success"></i>
                                            <div class="info-label">Tamaño máximo</div>
                                            <div class="info-value">10 GB por archivo</div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="info-item">
                                            <i class="fas fa-layer-group text-info"></i>
                                            <div class="info-label">Múltiples archivos</div>
                                            <div class="info-value">Hasta 50 archivos</div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="info-item">
                                            <i class="fas fa-shield-alt text-warning"></i>
                                            <div class="info-label">Seguridad</div>
                                            <div class="info-value">Cifrado SSL</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <input type="file" id="file-input" multiple
                                   accept=".sql,.txt,.text,.pdf"
                                   style="display: none;"
                                   aria-label="Selector de archivos">
                        </div>
                    </div>
                </div>
            </section>

            <!-- Upload Queue Section -->
            <section class="upload-queue mb-4" id="upload-queue-section" style="display: none;"
                     role="region" aria-labelledby="queue-heading">
                <div class="card-enterprise">
                    <div class="card-header-enterprise d-flex justify-content-between align-items-center">
                        <h3 id="queue-heading" class="h5 mb-0">
                            <i class="fas fa-list me-2"></i>Cola de Subida
                        </h3>
                        <div class="queue-actions">
                            <button class="btn btn-outline-danger btn-sm" onclick="clearUploadQueue()"
                                    aria-label="Limpiar cola de subida">
                                <i class="fas fa-trash me-1"></i>Limpiar
                            </button>
                        </div>
                    </div>
                    <div class="card-body-enterprise">
                        <div id="upload-container" class="upload-container">
                            <!-- Upload items will be added here dynamically -->
                        </div>
                    </div>
                </div>
            </section>

            <!-- Analysis Progress Section -->
            <section class="analysis-progress mb-4" id="analysis-progress-section" style="display: none;"
                     role="region" aria-labelledby="analysis-heading">
                <div class="card-enterprise">
                    <div class="card-header-enterprise">
                        <h3 id="analysis-heading" class="h5 mb-0">
                            <i class="fas fa-cogs me-2"></i>Progreso de Análisis
                        </h3>
                    </div>
                    <div class="card-body-enterprise">
                        <div id="analysis-progress-container" class="analysis-progress-container">
                            <!-- Analysis progress items will be added here dynamically -->
                        </div>
                    </div>
                </div>
            </section>

            <!-- Upload Tips Section -->
            <section class="upload-tips" role="complementary" aria-labelledby="tips-heading">
                <div class="card-enterprise">
                    <div class="card-header-enterprise">
                        <h3 id="tips-heading" class="h5 mb-0">
                            <i class="fas fa-lightbulb me-2 text-warning"></i>Consejos para Mejores Resultados
                        </h3>
                    </div>
                    <div class="card-body-enterprise">
                        <div class="row g-4">
                            <div class="col-md-6">
                                <div class="tip-item">
                                    <div class="tip-icon">
                                        <i class="fas fa-file-code"></i>
                                    </div>
                                    <div class="tip-content">
                                        <h6 class="tip-title">Formato de Archivos</h6>
                                        <p class="tip-description">
                                            Los archivos .sql proporcionan los mejores resultados.
                                            Los archivos PDF se procesan con OCR para extraer el contenido SQL.
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="tip-item">
                                    <div class="tip-icon">
                                        <i class="fas fa-compress-alt"></i>
                                    </div>
                                    <div class="tip-content">
                                        <h6 class="tip-title">Optimización de Tamaño</h6>
                                        <p class="tip-description">
                                            Para archivos grandes, considera dividirlos en secciones más pequeñas
                                            para un análisis más rápido y detallado.
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="tip-item">
                                    <div class="tip-icon">
                                        <i class="fas fa-tags"></i>
                                    </div>
                                    <div class="tip-content">
                                        <h6 class="tip-title">Nombres Descriptivos</h6>
                                        <p class="tip-description">
                                            Usa nombres de archivo descriptivos para identificar fácilmente
                                            tus análisis en el historial.
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="tip-item">
                                    <div class="tip-icon">
                                        <i class="fas fa-clock"></i>
                                    </div>
                                    <div class="tip-content">
                                        <h6 class="tip-title">Tiempo de Procesamiento</h6>
                                        <p class="tip-description">
                                            El análisis típico toma 2-5 segundos por MB.
                                            Archivos más complejos pueden requerir más tiempo.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        `;
    }

    async loadHistoryContent() {
        return `
            <!-- Enhanced History Header -->
            <header class="history-header mb-4" role="banner">
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                    <div class="history-title-section">
                        <div class="d-flex align-items-center gap-3 mb-2">
                            <button class="btn btn-outline-secondary" onclick="navigateBack()"
                                    aria-label="Volver al dashboard">
                                <i class="fas fa-arrow-left me-2"></i>Volver
                            </button>
                            <h1 class="h2 mb-0 text-primary fw-bold">
                                <i class="fas fa-history me-2"></i>Historial de Análisis
                            </h1>
                        </div>
                        <p class="text-muted mb-1">
                            Gestiona y revisa todos tus análisis SQL anteriores
                        </p>
                        <div class="history-stats">
                            <small class="text-success me-3">
                                <i class="fas fa-check-circle me-1"></i>
                                <span id="history-total-count">0</span> análisis completados
                            </small>
                            <small class="text-info">
                                <i class="fas fa-calendar me-1"></i>
                                Último análisis: <span id="history-last-date">Nunca</span>
                            </small>
                        </div>
                    </div>
                    <div class="history-actions d-flex gap-2 flex-wrap">
                        <div class="dropdown">
                            <button class="btn-enterprise btn-outline dropdown-toggle" type="button"
                                    data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="fas fa-filter me-2"></i>Filtrar
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" onclick="filterHistory('all')">
                                    <i class="fas fa-list me-2"></i>Todos
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="filterHistory('completed')">
                                    <i class="fas fa-check me-2"></i>Completados
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="filterHistory('failed')">
                                    <i class="fas fa-times me-2"></i>Fallidos
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="filterHistory('recent')">
                                    <i class="fas fa-clock me-2"></i>Recientes
                                </a></li>
                            </ul>
                        </div>
                        <button class="btn-enterprise btn-outline" onclick="exportHistoryReport()"
                                aria-label="Exportar historial">
                            <i class="fas fa-download me-2"></i>Exportar
                        </button>
                        <button class="btn-enterprise btn-outline" onclick="clearHistory()"
                                aria-label="Limpiar historial">
                            <i class="fas fa-trash me-2"></i>Limpiar
                        </button>
                        <button class="btn-enterprise btn-primary" onclick="navigateToView('upload')"
                                aria-label="Nuevo análisis">
                            <i class="fas fa-plus me-2"></i>Nuevo Análisis
                        </button>
                    </div>
                </div>
            </header>

            <!-- Search and Filter Section -->
            <section class="history-controls mb-4" role="search">
                <div class="card-enterprise">
                    <div class="card-body-enterprise">
                        <div class="row g-3 align-items-end">
                            <div class="col-md-6">
                                <label for="history-search" class="form-label-enterprise">
                                    <i class="fas fa-search me-1"></i>Buscar en historial
                                </label>
                                <input type="text" class="form-control-enterprise" id="history-search"
                                       placeholder="Buscar por nombre de archivo, fecha o estado..."
                                       oninput="searchHistory(this.value)">
                            </div>
                            <div class="col-md-3">
                                <label for="history-date-filter" class="form-label-enterprise">
                                    <i class="fas fa-calendar me-1"></i>Filtrar por fecha
                                </label>
                                <select class="form-control-enterprise" id="history-date-filter"
                                        onchange="filterHistoryByDate(this.value)">
                                    <option value="all">Todas las fechas</option>
                                    <option value="today">Hoy</option>
                                    <option value="week">Esta semana</option>
                                    <option value="month">Este mes</option>
                                    <option value="custom">Personalizado...</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <button class="btn-enterprise btn-outline w-100" onclick="refreshHistory()"
                                        aria-label="Actualizar historial">
                                    <i class="fas fa-sync-alt me-2"></i>Actualizar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Enhanced History Table -->
            <section class="history-table-section" role="main">
                <div class="card-enterprise">
                    <div class="card-header-enterprise d-flex justify-content-between align-items-center">
                        <h3 class="h5 mb-0">
                            <i class="fas fa-table me-2"></i>Registro de Análisis
                        </h3>
                        <div class="table-controls">
                            <button class="btn btn-outline-secondary btn-sm" onclick="toggleTableView()"
                                    id="table-view-toggle" aria-label="Cambiar vista">
                                <i class="fas fa-th-list"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body-enterprise">
                        <div class="table-responsive">
                            <table class="table-enterprise" id="history-table" role="table">
                                <thead>
                                    <tr role="row">
                                        <th scope="col" class="sortable" onclick="sortHistory('fileName')"
                                            role="columnheader" tabindex="0">
                                            <i class="fas fa-file-alt me-1"></i>Nombre del Archivo
                                            <i class="fas fa-sort sort-icon"></i>
                                        </th>
                                        <th scope="col" class="sortable" onclick="sortHistory('date')"
                                            role="columnheader" tabindex="0">
                                            <i class="fas fa-calendar me-1"></i>Fecha y Hora
                                            <i class="fas fa-sort sort-icon"></i>
                                        </th>
                                        <th scope="col" class="sortable" onclick="sortHistory('status')"
                                            role="columnheader" tabindex="0">
                                            <i class="fas fa-info-circle me-1"></i>Estado
                                            <i class="fas fa-sort sort-icon"></i>
                                        </th>
                                        <th scope="col" class="sortable" onclick="sortHistory('processingTime')"
                                            role="columnheader" tabindex="0">
                                            <i class="fas fa-stopwatch me-1"></i>Tiempo
                                            <i class="fas fa-sort sort-icon"></i>
                                        </th>
                                        <th scope="col" class="sortable" onclick="sortHistory('fileSize')"
                                            role="columnheader" tabindex="0">
                                            <i class="fas fa-weight-hanging me-1"></i>Tamaño
                                            <i class="fas fa-sort sort-icon"></i>
                                        </th>
                                        <th scope="col" role="columnheader">
                                            <i class="fas fa-cogs me-1"></i>Acciones
                                        </th>
                                    </tr>
                                </thead>
                                <tbody id="history-table-body" role="rowgroup">
                                    <!-- Sample data for demonstration -->
                                    <tr role="row" class="history-row">
                                        <td class="file-name-cell">
                                            <div class="file-info">
                                                <div class="file-name">database_schema.sql</div>
                                                <div class="file-type">
                                                    <span class="badge bg-primary">SQL</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="date-cell">
                                            <div class="date-info">
                                                <div class="date-primary">2025-07-11 14:30:25</div>
                                                <div class="date-relative">Hace 2 minutos</div>
                                            </div>
                                        </td>
                                        <td class="status-cell">
                                            <span class="status-badge status-completed">
                                                <i class="fas fa-check-circle me-1"></i>Completado
                                            </span>
                                        </td>
                                        <td class="time-cell">
                                            <div class="time-info">
                                                <div class="time-primary">2.3s</div>
                                                <div class="time-secondary">Rápido</div>
                                            </div>
                                        </td>
                                        <td class="size-cell">
                                            <div class="size-info">
                                                <div class="size-primary">1.2 MB</div>
                                                <div class="size-secondary">245 líneas</div>
                                            </div>
                                        </td>
                                        <td class="actions-cell">
                                            <div class="action-buttons">
                                                <button class="btn btn-outline-primary btn-sm"
                                                        onclick="viewAnalysisResults('sample-1')"
                                                        aria-label="Ver resultados">
                                                    <i class="fas fa-eye"></i>
                                                </button>
                                                <button class="btn btn-outline-success btn-sm"
                                                        onclick="downloadAnalysisReport('sample-1')"
                                                        aria-label="Descargar reporte">
                                                    <i class="fas fa-download"></i>
                                                </button>
                                                <button class="btn btn-outline-info btn-sm"
                                                        onclick="rerunAnalysis('sample-1')"
                                                        aria-label="Ejecutar de nuevo">
                                                    <i class="fas fa-redo"></i>
                                                </button>
                                                <button class="btn btn-outline-danger btn-sm"
                                                        onclick="deleteAnalysis('sample-1')"
                                                        aria-label="Eliminar">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>

                                    <tr role="row" class="history-row">
                                        <td class="file-name-cell">
                                            <div class="file-info">
                                                <div class="file-name">user_queries.sql</div>
                                                <div class="file-type">
                                                    <span class="badge bg-primary">SQL</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="date-cell">
                                            <div class="date-info">
                                                <div class="date-primary">2025-07-11 14:15:10</div>
                                                <div class="date-relative">Hace 17 minutos</div>
                                            </div>
                                        </td>
                                        <td class="status-cell">
                                            <span class="status-badge status-completed">
                                                <i class="fas fa-check-circle me-1"></i>Completado
                                            </span>
                                        </td>
                                        <td class="time-cell">
                                            <div class="time-info">
                                                <div class="time-primary">4.7s</div>
                                                <div class="time-secondary">Normal</div>
                                            </div>
                                        </td>
                                        <td class="size-cell">
                                            <div class="size-info">
                                                <div class="size-primary">3.8 MB</div>
                                                <div class="size-secondary">892 líneas</div>
                                            </div>
                                        </td>
                                        <td class="actions-cell">
                                            <div class="action-buttons">
                                                <button class="btn btn-outline-primary btn-sm"
                                                        onclick="viewAnalysisResults('sample-2')"
                                                        aria-label="Ver resultados">
                                                    <i class="fas fa-eye"></i>
                                                </button>
                                                <button class="btn btn-outline-success btn-sm"
                                                        onclick="downloadAnalysisReport('sample-2')"
                                                        aria-label="Descargar reporte">
                                                    <i class="fas fa-download"></i>
                                                </button>
                                                <button class="btn btn-outline-info btn-sm"
                                                        onclick="rerunAnalysis('sample-2')"
                                                        aria-label="Ejecutar de nuevo">
                                                    <i class="fas fa-redo"></i>
                                                </button>
                                                <button class="btn btn-outline-danger btn-sm"
                                                        onclick="deleteAnalysis('sample-2')"
                                                        aria-label="Eliminar">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>

                                    <tr role="row" class="history-row">
                                        <td class="file-name-cell">
                                            <div class="file-info">
                                                <div class="file-name">security_audit.pdf</div>
                                                <div class="file-type">
                                                    <span class="badge bg-info">PDF</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="date-cell">
                                            <div class="date-info">
                                                <div class="date-primary">2025-07-11 13:45:33</div>
                                                <div class="date-relative">Hace 47 minutos</div>
                                            </div>
                                        </td>
                                        <td class="status-cell">
                                            <span class="status-badge status-failed">
                                                <i class="fas fa-exclamation-triangle me-1"></i>Error
                                            </span>
                                        </td>
                                        <td class="time-cell">
                                            <div class="time-info">
                                                <div class="time-primary">--</div>
                                                <div class="time-secondary">Falló</div>
                                            </div>
                                        </td>
                                        <td class="size-cell">
                                            <div class="size-info">
                                                <div class="size-primary">15.2 MB</div>
                                                <div class="size-secondary">OCR requerido</div>
                                            </div>
                                        </td>
                                        <td class="actions-cell">
                                            <div class="action-buttons">
                                                <button class="btn btn-outline-warning btn-sm"
                                                        onclick="viewErrorDetails('sample-3')"
                                                        aria-label="Ver error">
                                                    <i class="fas fa-exclamation-circle"></i>
                                                </button>
                                                <button class="btn btn-outline-info btn-sm"
                                                        onclick="rerunAnalysis('sample-3')"
                                                        aria-label="Reintentar">
                                                    <i class="fas fa-redo"></i>
                                                </button>
                                                <button class="btn btn-outline-danger btn-sm"
                                                        onclick="deleteAnalysis('sample-3')"
                                                        aria-label="Eliminar">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- Pagination -->
                        <div class="table-pagination mt-4">
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="pagination-info">
                                    <small class="text-muted">
                                        Mostrando <strong>1-3</strong> de <strong>3</strong> análisis
                                    </small>
                                </div>
                                <nav aria-label="Paginación del historial">
                                    <ul class="pagination pagination-sm mb-0">
                                        <li class="page-item disabled">
                                            <a class="page-link" href="#" tabindex="-1" aria-disabled="true">
                                                <i class="fas fa-chevron-left"></i>
                                            </a>
                                        </li>
                                        <li class="page-item active">
                                            <a class="page-link" href="#">1</a>
                                        </li>
                                        <li class="page-item disabled">
                                            <a class="page-link" href="#" tabindex="-1" aria-disabled="true">
                                                <i class="fas fa-chevron-right"></i>
                                            </a>
                                        </li>
                                    </ul>
                                </nav>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        `;
    }

    async loadResultsContent() {
        // Initialize results manager after content is loaded
        setTimeout(() => {
            if (window.resultsManager) {
                // Load sample results or get from URL parameter
                const urlParams = new URLSearchParams(window.location.search);
                const analysisId = urlParams.get('analysis_id');

                if (analysisId) {
                    resultsManager.loadAnalysisResults(analysisId);
                } else {
                    // Load sample results for demonstration
                    resultsManager.loadSampleResults();
                }
            }
        }, 100);

        return `
            <!-- Enhanced Results Header -->
            <header class="results-header mb-4" role="banner">
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                    <div class="results-title-section">
                        <h1 class="h2 mb-2 text-primary fw-bold">
                            <i class="fas fa-chart-line me-2"></i>Resultados de Análisis
                        </h1>
                        <p class="text-muted mb-1">
                            Resultados detallados y perspectivas del análisis SQL
                        </p>
                        <div class="results-breadcrumb">
                            <nav aria-label="breadcrumb">
                                <ol class="breadcrumb mb-0">
                                    <li class="breadcrumb-item">
                                        <a href="#" onclick="navigateToView('dashboard')">Dashboard</a>
                                    </li>
                                    <li class="breadcrumb-item">
                                        <a href="#" onclick="navigateToView('history')">Historial</a>
                                    </li>
                                    <li class="breadcrumb-item active" aria-current="page">Resultados</li>
                                </ol>
                            </nav>
                        </div>
                    </div>
                    <div class="results-actions d-flex gap-2 flex-wrap">
                        <button class="btn-enterprise btn-outline" onclick="resultsManager.exportResults('pdf')"
                                aria-label="Exportar a PDF">
                            <i class="fas fa-file-pdf me-2"></i>PDF
                        </button>
                        <button class="btn-enterprise btn-outline" onclick="resultsManager.exportResults('excel')"
                                aria-label="Exportar a Excel">
                            <i class="fas fa-file-excel me-2"></i>Excel
                        </button>
                        <button class="btn-enterprise btn-outline" onclick="resultsManager.shareResults()"
                                aria-label="Compartir resultados">
                            <i class="fas fa-share-alt me-2"></i>Compartir
                        </button>
                        <button class="btn-enterprise btn-primary" onclick="navigateToView('history')"
                                aria-label="Ver historial">
                            <i class="fas fa-history me-2"></i>Historial
                        </button>
                    </div>
                </div>
            </header>

            <!-- Sample Analysis Results -->
            <section class="results-content" role="main">
                <div class="row g-4">
                    <div class="col-lg-8">
                        <div class="card-enterprise">
                            <div class="card-header-enterprise d-flex justify-content-between align-items-center">
                                <h3 class="h5 mb-0">
                                    <i class="fas fa-file-code me-2"></i>database_schema.sql
                                </h3>
                                <span class="badge bg-success">Análisis Completado</span>
                            </div>
                            <div class="card-body-enterprise">
                                <!-- Analysis Summary -->
                                <div class="analysis-summary mb-4">
                                    <div class="row g-3">
                                        <div class="col-md-3">
                                            <div class="summary-metric">
                                                <div class="metric-icon bg-success">
                                                    <i class="fas fa-check-circle"></i>
                                                </div>
                                                <div class="metric-info">
                                                    <div class="metric-value" id="overall-score">98%</div>
                                                    <div class="metric-label">Puntuación General</div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="summary-metric">
                                                <div class="metric-icon bg-primary">
                                                    <i class="fas fa-code"></i>
                                                </div>
                                                <div class="metric-info">
                                                    <div class="metric-value" id="lines-count">245</div>
                                                    <div class="metric-label">Líneas de Código</div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="summary-metric">
                                                <div class="metric-icon bg-warning">
                                                    <i class="fas fa-exclamation-triangle"></i>
                                                </div>
                                                <div class="metric-info">
                                                    <div class="metric-value" id="warnings-count">2</div>
                                                    <div class="metric-label">Advertencias</div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="summary-metric">
                                                <div class="metric-icon bg-info">
                                                    <i class="fas fa-clock"></i>
                                                </div>
                                                <div class="metric-info">
                                                    <div class="metric-value" id="processing-time">2.3s</div>
                                                    <div class="metric-label">Tiempo de Análisis</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Detailed Results Tabs -->
                                <div class="results-tabs">
                                    <ul class="nav nav-tabs" id="resultsTab" role="tablist">
                                        <li class="nav-item" role="presentation">
                                            <button class="nav-link active" id="syntax-tab" data-bs-toggle="tab"
                                                    data-bs-target="#syntax" type="button" role="tab">
                                                <i class="fas fa-code me-1"></i>Sintaxis
                                            </button>
                                        </li>
                                        <li class="nav-item" role="presentation">
                                            <button class="nav-link" id="security-tab" data-bs-toggle="tab"
                                                    data-bs-target="#security" type="button" role="tab">
                                                <i class="fas fa-shield-alt me-1"></i>Seguridad
                                            </button>
                                        </li>
                                        <li class="nav-item" role="presentation">
                                            <button class="nav-link" id="performance-tab" data-bs-toggle="tab"
                                                    data-bs-target="#performance" type="button" role="tab">
                                                <i class="fas fa-tachometer-alt me-1"></i>Rendimiento
                                            </button>
                                        </li>
                                        <li class="nav-item" role="presentation">
                                            <button class="nav-link" id="recommendations-tab" data-bs-toggle="tab"
                                                    data-bs-target="#recommendations" type="button" role="tab">
                                                <i class="fas fa-lightbulb me-1"></i>Recomendaciones
                                            </button>
                                        </li>
                                    </ul>

                                    <div class="tab-content mt-3" id="resultsTabContent">
                                        <div class="tab-pane fade show active" id="syntax" role="tabpanel">
                                            <div class="syntax-results">
                                                <!-- Errors List Container -->
                                                <div id="errors-list" class="mb-4">
                                                    <div class="alert alert-success">
                                                        <h6><i class="fas fa-check-circle me-2"></i>Sintaxis Válida</h6>
                                                        <p>El código SQL tiene una sintaxis correcta y es ejecutable.</p>
                                                    </div>
                                                </div>

                                                <!-- Schema Information -->
                                                <div id="schema-info" class="mb-4">
                                                    <h6>Análisis de Esquema:</h6>
                                                    <div id="tables-list">
                                                        <ul class="list-unstyled">
                                                            <li class="mb-2">
                                                                <i class="fas fa-check text-success me-2"></i>
                                                                <strong>Tablas:</strong> <span id="schema-tables-count">8</span> tablas definidas correctamente
                                                            </li>
                                                            <li class="mb-2">
                                                                <i class="fas fa-check text-success me-2"></i>
                                                                <strong>Columnas:</strong> <span id="schema-columns-count">45</span> columnas totales
                                                            </li>
                                                            <li class="mb-2">
                                                                <i class="fas fa-check text-success me-2"></i>
                                                                <strong>Índices:</strong> <span id="schema-indexes-count">12</span> índices optimizados
                                                            </li>
                                                            <li class="mb-2">
                                                                <i class="fas fa-check text-success me-2"></i>
                                                                <strong>Restricciones:</strong> <span id="schema-constraints-count">8</span> restricciones válidas
                                                            </li>
                                                        </ul>
                                                    </div>
                                                </div>

                                                <!-- Schema Diagram -->
                                                <div id="schema-diagram" class="mb-4">
                                                    <h6>Diagrama de Esquema:</h6>
                                                    <div class="schema-visualization">
                                                        <!-- Schema diagram will be populated by results.js -->
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="tab-pane fade" id="security" role="tabpanel">
                                            <div class="security-results">
                                                <!-- Security Score -->
                                                <div class="security-score mb-4">
                                                    <div class="d-flex align-items-center mb-3">
                                                        <div class="security-score-circle me-3">
                                                            <span id="security-score">85</span>
                                                        </div>
                                                        <div>
                                                            <h6 class="mb-1">Puntuación de Seguridad</h6>
                                                            <p class="text-muted mb-0">Evaluación general de seguridad</p>
                                                        </div>
                                                    </div>
                                                </div>

                                                <!-- Security Issues -->
                                                <div id="security-issues" class="mb-4">
                                                    <h6>Problemas de Seguridad:</h6>
                                                    <div class="alert alert-success">
                                                        <h6><i class="fas fa-shield-check me-2"></i>Seguridad Buena</h6>
                                                        <p>No se detectaron vulnerabilidades críticas de seguridad.</p>
                                                    </div>
                                                </div>

                                                <!-- Security Recommendations -->
                                                <div id="security-recommendations" class="mb-4">
                                                    <h6>Recomendaciones de Seguridad:</h6>
                                                    <div class="security-checks">
                                                        <div class="check-item passed">
                                                            <i class="fas fa-check-circle"></i>
                                                        <span>Sin inyección SQL detectada</span>
                                                    </div>
                                                    <div class="check-item passed">
                                                        <i class="fas fa-check-circle"></i>
                                                        <span>Permisos de usuario apropiados</span>
                                                    </div>
                                                    <div class="check-item warning">
                                                        <i class="fas fa-exclamation-triangle"></i>
                                                        <span>Considerar cifrado de datos sensibles</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="tab-pane fade" id="performance" role="tabpanel">
                                            <div class="performance-results">
                                                <!-- Performance Summary -->
                                                <div class="performance-summary mb-4">
                                                    <div class="row g-3">
                                                        <div class="col-md-3">
                                                            <div class="perf-metric">
                                                                <div class="metric-value" id="perf-query-count">0</div>
                                                                <div class="metric-label">Consultas</div>
                                                            </div>
                                                        </div>
                                                        <div class="col-md-3">
                                                            <div class="perf-metric">
                                                                <div class="metric-value" id="perf-avg-time">0ms</div>
                                                                <div class="metric-label">Tiempo Promedio</div>
                                                            </div>
                                                        </div>
                                                        <div class="col-md-3">
                                                            <div class="perf-metric">
                                                                <div class="metric-value" id="perf-slow-queries">0</div>
                                                                <div class="metric-label">Consultas Lentas</div>
                                                            </div>
                                                        </div>
                                                        <div class="col-md-3">
                                                            <div class="perf-metric">
                                                                <div class="metric-value" id="perf-index-usage">0%</div>
                                                                <div class="metric-label">Uso de Índices</div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>

                                                <!-- Performance Chart -->
                                                <div id="performance-chart" class="mb-4">
                                                    <h6>Gráfico de Rendimiento:</h6>
                                                    <div class="chart-container">
                                                        <!-- Chart will be populated by results.js -->
                                                        <div class="alert alert-info">
                                                            <h6><i class="fas fa-tachometer-alt me-2"></i>Rendimiento Óptimo</h6>
                                                            <p>El esquema está bien optimizado para el rendimiento.</p>
                                                        </div>
                                                    </div>
                                                </div>

                                                <!-- Optimization Suggestions -->
                                                <div id="optimization-suggestions" class="mb-4">
                                                    <h6>Sugerencias de Optimización:</h6>
                                                    <div class="performance-metrics">
                                                        <div class="metric-bar">
                                                            <div class="metric-label">Eficiencia de Consultas</div>
                                                            <div class="progress">
                                                                <div class="progress-bar bg-success" style="width: 92%">92%</div>
                                                            </div>
                                                        </div>
                                                        <div class="metric-bar">
                                                            <div class="metric-label">Uso de Índices</div>
                                                            <div class="progress">
                                                                <div class="progress-bar bg-primary" style="width: 88%">88%</div>
                                                            </div>
                                                        </div>
                                                        <div class="metric-bar">
                                                            <div class="metric-label">Optimización de Memoria</div>
                                                            <div class="progress">
                                                                <div class="progress-bar bg-warning" style="width: 75%">75%</div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="tab-pane fade" id="recommendations" role="tabpanel">
                                            <div class="recommendations-results">
                                                <h6>Recomendaciones de Mejora:</h6>
                                                <div id="recommendations-list" class="recommendation-list">
                                                    <div class="recommendation-item priority-medium">
                                                        <div class="rec-icon">
                                                            <i class="fas fa-key"></i>
                                                        </div>
                                                        <div class="rec-content">
                                                            <h6>Agregar Claves Primarias</h6>
                                                            <p>Las tablas 'logs' y 'temp_data' necesitan claves primarias para mejor rendimiento.</p>
                                                            <span class="rec-priority">Prioridad Media</span>
                                                        </div>
                                                    </div>

                                                    <div class="recommendation-item priority-low">
                                                        <div class="rec-icon">
                                                            <i class="fas fa-database"></i>
                                                        </div>
                                                        <div class="rec-content">
                                                            <h6>Optimizar Tipos de Datos</h6>
                                                            <p>Considerar usar tipos de datos más específicos para reducir el uso de memoria.</p>
                                                            <span class="rec-priority">Prioridad Baja</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-4">
                        <div class="card-enterprise mb-4">
                            <div class="card-header-enterprise">
                                <h3 class="h5 mb-0">
                                    <i class="fas fa-chart-pie me-2"></i>Resumen Ejecutivo
                                </h3>
                            </div>
                            <div class="card-body-enterprise">
                                <div class="executive-summary">
                                    <div class="summary-score">
                                        <div class="score-circle">
                                            <div class="score-value">98</div>
                                            <div class="score-label">Puntuación</div>
                                        </div>
                                    </div>

                                    <div class="summary-stats">
                                        <div class="stat-row">
                                            <span class="stat-label">Estado</span>
                                            <span class="stat-value text-success">Excelente</span>
                                        </div>
                                        <div class="stat-row">
                                            <span class="stat-label">Errores</span>
                                            <span class="stat-value">0</span>
                                        </div>
                                        <div class="stat-row">
                                            <span class="stat-label">Advertencias</span>
                                            <span class="stat-value text-warning">2</span>
                                        </div>
                                        <div class="stat-row">
                                            <span class="stat-label">Recomendaciones</span>
                                            <span class="stat-value text-info">2</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="card-enterprise">
                            <div class="card-header-enterprise">
                                <h3 class="h5 mb-0">
                                    <i class="fas fa-cogs me-2"></i>Acciones Rápidas
                                </h3>
                            </div>
                            <div class="card-body-enterprise">
                                <div class="quick-actions">
                                    <button class="btn btn-outline-primary w-100 mb-2" onclick="rerunAnalysis('current')">
                                        <i class="fas fa-redo me-2"></i>Re-ejecutar Análisis
                                    </button>
                                    <button class="btn btn-outline-success w-100 mb-2" onclick="downloadAnalysisReport('current')">
                                        <i class="fas fa-download me-2"></i>Descargar Reporte
                                    </button>
                                    <button class="btn btn-outline-info w-100 mb-2" onclick="compareAnalysis()">
                                        <i class="fas fa-balance-scale me-2"></i>Comparar Análisis
                                    </button>
                                    <button class="btn btn-outline-warning w-100" onclick="scheduleAnalysis()">
                                        <i class="fas fa-calendar me-2"></i>Programar Análisis
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        `;
    }

    async loadAnalyzerContent() {
        return `
            <div class="analyzer-header mb-4">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h1 class="h3 mb-1">SQL Analyzer</h1>
                        <p class="text-muted">Analyze SQL syntax and structure</p>
                    </div>
                </div>
            </div>

            <!-- SQL Input -->
            <div class="card-enterprise mb-4">
                <div class="card-header-enterprise">
                    <h5 class="mb-0">SQL Input</h5>
                </div>
                <div class="card-body-enterprise">
                    <textarea class="form-control-enterprise" rows="10" placeholder="Paste your SQL code here..." id="sql-input"></textarea>
                    <div class="mt-3">
                        <button class="btn-enterprise btn-primary" onclick="analyzeSQLCode()">
                            <i class="fas fa-search me-2"></i>Analyze SQL
                        </button>
                        <button class="btn-enterprise btn-outline ms-2" onclick="clearSQLInput()">
                            <i class="fas fa-eraser me-2"></i>Clear
                        </button>
                    </div>
                </div>
            </div>

            <!-- Analysis Results -->
            <div id="sql-analysis-results" style="display: none;">
                <div class="card-enterprise">
                    <div class="card-header-enterprise">
                        <h5 class="mb-0">Analysis Results</h5>
                    </div>
                    <div class="card-body-enterprise">
                        <div id="analysis-content">
                            <!-- Results will be populated here -->
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadOptimizerContent() {
        return `
            <div class="optimizer-header mb-4">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h1 class="h3 mb-1">Performance Optimizer</h1>
                        <p class="text-muted">Optimize SQL query performance</p>
                    </div>
                </div>
            </div>

            <!-- Performance Analysis -->
            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card-enterprise">
                        <div class="card-header-enterprise">
                            <h5 class="mb-0">Query Optimization</h5>
                        </div>
                        <div class="card-body-enterprise">
                            <div class="text-center text-muted py-5">
                                <i class="fas fa-bolt fa-3x mb-3"></i>
                                <h5>Performance Optimizer</h5>
                                <p>Upload a SQL file or paste SQL code to get performance optimization suggestions</p>
                                <button class="btn-enterprise btn-primary" onclick="navigateToView('upload')">
                                    <i class="fas fa-upload me-2"></i>Upload File
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card-enterprise">
                        <div class="card-header-enterprise">
                            <h5 class="mb-0">Performance Metrics</h5>
                        </div>
                        <div class="card-body-enterprise">
                            <div class="metric-item">
                                <div class="metric-icon bg-primary">
                                    <i class="fas fa-tachometer-alt"></i>
                                </div>
                                <div class="metric-info">
                                    <div class="metric-value">--</div>
                                    <div class="metric-label">Query Speed</div>
                                </div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-icon bg-success">
                                    <i class="fas fa-database"></i>
                                </div>
                                <div class="metric-info">
                                    <div class="metric-value">--</div>
                                    <div class="metric-label">Index Usage</div>
                                </div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-icon bg-warning">
                                    <i class="fas fa-memory"></i>
                                </div>
                                <div class="metric-info">
                                    <div class="metric-value">--</div>
                                    <div class="metric-label">Memory Usage</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadSecurityContent() {
        return `
            <div class="security-header mb-4">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h1 class="h3 mb-1">Security Scanner</h1>
                        <p class="text-muted">Scan for SQL security vulnerabilities</p>
                    </div>
                </div>
            </div>

            <!-- Security Scan -->
            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card-enterprise">
                        <div class="card-header-enterprise">
                            <h5 class="mb-0">Security Analysis</h5>
                        </div>
                        <div class="card-body-enterprise">
                            <div class="text-center text-muted py-5">
                                <i class="fas fa-shield-alt fa-3x mb-3"></i>
                                <h5>Security Scanner</h5>
                                <p>Upload SQL files to scan for security vulnerabilities and best practices</p>
                                <button class="btn-enterprise btn-primary" onclick="navigateToView('upload')">
                                    <i class="fas fa-upload me-2"></i>Upload File
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card-enterprise">
                        <div class="card-header-enterprise">
                            <h5 class="mb-0">Security Score</h5>
                        </div>
                        <div class="card-body-enterprise">
                            <div class="security-score-display">
                                <div class="score-circle">
                                    <canvas id="security-score-chart" width="100" height="100"></canvas>
                                    <div class="score-text">
                                        <div class="score-number">--</div>
                                        <div class="score-label">Score</div>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-3">
                                <div class="stat-item">
                                    <span class="stat-label">Critical Issues</span>
                                    <span class="stat-value text-danger">--</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Warnings</span>
                                    <span class="stat-value text-warning">--</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Recommendations</span>
                                    <span class="stat-value text-info">--</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadProfileContent() {
        return `
            <div class="profile-header mb-4">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h1 class="h3 mb-1">Profile</h1>
                        <p class="text-muted">Manage your account settings</p>
                    </div>
                </div>
            </div>

            <!-- Profile Content -->
            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card-enterprise">
                        <div class="card-header-enterprise">
                            <h5 class="mb-0">Account Information</h5>
                        </div>
                        <div class="card-body-enterprise">
                            <form id="profile-form">
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-label-enterprise">Username</label>
                                        <input type="text" class="form-control-enterprise" value="user" readonly>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label-enterprise">Email</label>
                                        <input type="email" class="form-control-enterprise" value="user@example.com">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label-enterprise">First Name</label>
                                        <input type="text" class="form-control-enterprise" value="SQL">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label-enterprise">Last Name</label>
                                        <input type="text" class="form-control-enterprise" value="Analyzer">
                                    </div>
                                    <div class="col-12">
                                        <button type="submit" class="btn-enterprise btn-primary">
                                            <i class="fas fa-save me-2"></i>Save Changes
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card-enterprise">
                        <div class="card-header-enterprise">
                            <h5 class="mb-0">Account Stats</h5>
                        </div>
                        <div class="card-body-enterprise">
                            <div class="stat-item">
                                <span class="stat-label">Member Since</span>
                                <span class="stat-value">Today</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Files Analyzed</span>
                                <span class="stat-value" id="profile-files-count">0</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Total Analyses</span>
                                <span class="stat-value" id="profile-analyses-count">0</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Account Type</span>
                                <span class="stat-value">Enterprise</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadSettingsContent() {
        return `
            <div class="settings-header mb-4">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h1 class="h3 mb-1">Settings</h1>
                        <p class="text-muted">Configure application preferences</p>
                    </div>
                </div>
            </div>

            <!-- Settings Content -->
            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card-enterprise">
                        <div class="card-header-enterprise">
                            <h5 class="mb-0">Application Settings</h5>
                        </div>
                        <div class="card-body-enterprise">
                            <form id="settings-form">
                                <div class="mb-4">
                                    <h6>Analysis Preferences</h6>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="auto-analysis" checked>
                                        <label class="form-check-label" for="auto-analysis">
                                            Auto-start analysis after file upload
                                        </label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="detailed-reports" checked>
                                        <label class="form-check-label" for="detailed-reports">
                                            Generate detailed analysis reports
                                        </label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="security-scan" checked>
                                        <label class="form-check-label" for="security-scan">
                                            Include security vulnerability scanning
                                        </label>
                                    </div>
                                </div>

                                <div class="mb-4">
                                    <h6>Notification Settings</h6>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="email-notifications" checked>
                                        <label class="form-check-label" for="email-notifications">
                                            Email notifications for completed analyses
                                        </label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="browser-notifications" checked>
                                        <label class="form-check-label" for="browser-notifications">
                                            Browser notifications
                                        </label>
                                    </div>
                                </div>

                                <div class="mb-4">
                                    <h6>Data Retention</h6>
                                    <div class="mb-3">
                                        <label class="form-label-enterprise">Keep analysis history for</label>
                                        <select class="form-control-enterprise">
                                            <option value="30">30 days</option>
                                            <option value="90" selected>90 days</option>
                                            <option value="180">180 days</option>
                                            <option value="365">1 year</option>
                                        </select>
                                    </div>
                                </div>

                                <button type="submit" class="btn-enterprise btn-primary">
                                    <i class="fas fa-save me-2"></i>Save Settings
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card-enterprise">
                        <div class="card-header-enterprise">
                            <h5 class="mb-0">System Information</h5>
                        </div>
                        <div class="card-body-enterprise">
                            <div class="stat-item">
                                <span class="stat-label">Version</span>
                                <span class="stat-value">1.0.0</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Last Updated</span>
                                <span class="stat-value">Today</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Storage Used</span>
                                <span class="stat-value">0 MB</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">API Status</span>
                                <span class="stat-value text-success">Online</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // ========================================================================
    // VIEW INITIALIZATION
    // ========================================================================

    initializeViewFunctionality(viewName) {
        switch (viewName) {
            case 'dashboard':
                this.initializeDashboard();
                break;
            case 'upload':
                this.initializeUpload();
                break;
            case 'history':
                this.initializeHistory();
                break;
            case 'results':
                this.initializeResults();
                break;
            case 'analyzer':
                this.initializeAnalyzer();
                break;
            case 'profile':
                this.initializeProfile();
                break;
            case 'settings':
                this.initializeSettings();
                break;
        }
    }

    initializeDashboard() {
        if (window.dashboardManager) {
            dashboardManager.loadDashboardData();
            dashboardManager.updateStats();
        }
    }

    initializeUpload() {
        if (window.uploadManager) {
            uploadManager.init();
        }
    }

    initializeHistory() {
        this.loadHistoryData();
    }

    initializeResults() {
        if (window.resultsManager) {
            resultsManager.init();
        }
    }

    initializeAnalyzer() {
        // Initialize SQL analyzer functionality
    }

    initializeProfile() {
        this.loadProfileData();
    }

    initializeSettings() {
        this.loadSettingsData();
    }

    initializeAuthFunctionality() {
        // Set up auth form handler
        const authForm = document.getElementById('authForm');
        if (authForm) {
            authForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAuthSubmit(e);
            });
        }
    }

    async handleAuthSubmit(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const username = formData.get('username') || e.target.querySelector('input[type="text"]')?.value || 'user';
        const password = formData.get('password') || e.target.querySelector('input[type="password"]')?.value || 'password';

        if (window.Utils) Utils.log('🔐 Attempting authentication for:', username);

        // Show loading state
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn?.textContent;
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Iniciando sesión...';
        }

        try {
            // Simulate authentication with backend validation
            await this.validateCredentials(username, password);

            // Store auth data
            Utils.setStorage('sqlAnalyzer_sessionId', Utils.generateId('session'));
            Utils.setStorage('sqlAnalyzer_userId', Utils.generateId('user'));
            Utils.setStorage('sqlAnalyzer_username', username);
            Utils.setStorage('sqlAnalyzer_lastActivity', Date.now());

            if (window.Utils) Utils.log('✅ Authentication successful');

            // Handle successful authentication
            this.handleAuthenticationSuccess();

        } catch (error) {
            if (window.Utils) Utils.error('❌ Authentication failed:', error);

            // Show error message
            this.showAuthError('Credenciales inválidas. Por favor, intenta de nuevo.');

        } finally {
            // Restore button state
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText || 'Iniciar Sesión';
            }
        }
    }

    async validateCredentials(username, password) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Authentication failed');
            }

            if (data.success) {
                // Store additional auth data from server
                Utils.setStorage('sqlAnalyzer_sessionId', data.session_id);
                Utils.setStorage('sqlAnalyzer_userId', data.user_id);
                Utils.setStorage('sqlAnalyzer_username', data.username);
                Utils.setStorage('sqlAnalyzer_expiresAt', data.expires_at);

                return data;
            } else {
                throw new Error(data.message || 'Authentication failed');
            }

        } catch (error) {
            if (window.Utils) Utils.error('❌ API authentication error:', error);
            throw error;
        }
    }

    showAuthError(message) {
        // Find or create error display element
        let errorDiv = document.querySelector('.auth-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'auth-error alert alert-danger mt-3';
            const authForm = document.getElementById('authForm');
            if (authForm) {
                authForm.appendChild(errorDiv);
            }
        }

        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        `;

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (errorDiv) {
                errorDiv.remove();
            }
        }, 5000);
    }

    loadHistoryData() {
        const analysisHistory = Utils.getStorage('sqlAnalyzer_analysisHistory', []);
        const tableBody = document.getElementById('history-table-body');

        if (!tableBody) return;

        if (analysisHistory.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
                        <i class="fas fa-history fa-2x mb-2"></i>
                        <p>No analysis history found</p>
                        <small>Upload and analyze files to see history</small>
                    </td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = analysisHistory.map(analysis => `
            <tr>
                <td>${Utils.sanitizeHtml(analysis.fileName)}</td>
                <td>${Utils.formatRelativeTime(analysis.timestamp)}</td>
                <td><span class="status-badge status-${analysis.status}">${Utils.capitalizeFirst(analysis.status)}</span></td>
                <td>${Utils.formatTime(analysis.processingTime / 1000)}</td>
                <td>
                    ${analysis.status === 'completed' ?
                `<button class="btn-enterprise btn-sm btn-primary" onclick="viewAnalysisResults('${analysis.id}')">
                            <i class="fas fa-eye"></i>
                        </button>` : ''}
                    <button class="btn-enterprise btn-sm btn-outline ms-1" onclick="deleteAnalysis('${analysis.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    loadProfileData() {
        const filesCount = Utils.getStorage('sqlAnalyzer_uploadHistory', []).length;
        const analysesCount = Utils.getStorage('sqlAnalyzer_analysisHistory', []).length;

        const filesElement = document.getElementById('profile-files-count');
        const analysesElement = document.getElementById('profile-analyses-count');

        if (filesElement) filesElement.textContent = filesCount;
        if (analysesElement) analysesElement.textContent = analysesCount;
    }

    loadSettingsData() {
        // Load saved settings
        const settings = Utils.getStorage('sqlAnalyzer_settings', {});

        // Apply settings to form
        Object.keys(settings).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = settings[key];
                } else {
                    element.value = settings[key];
                }
            }
        });
    }
}

// Global navigation functions
function navigateToView(viewName) {
    if (window.appController) {
        appController.navigateToView(viewName);
    }
}

function navigateBack() {
    if (window.appController) {
        // Get the previous view from navigation history
        const currentView = appController.currentView;
        let targetView = 'dashboard'; // Default fallback

        // Define navigation hierarchy
        const navigationHierarchy = {
            'upload': 'dashboard',
            'history': 'dashboard',
            'results': 'history',
            'analyzer': 'dashboard',
            'optimizer': 'dashboard',
            'security': 'dashboard',
            'profile': 'dashboard',
            'settings': 'dashboard'
        };

        if (navigationHierarchy[currentView]) {
            targetView = navigationHierarchy[currentView];
        }

        if (window.Utils) Utils.log(`🔙 Navigating back from ${currentView} to ${targetView}`);
        appController.navigateToView(targetView);
    } else {
        // Fallback to browser back
        window.history.back();
    }
}

function toggleSidebar() {
    if (window.appController) {
        appController.toggleSidebar();
    }
}

function closeSidebar() {
    if (window.appController) {
        appController.closeSidebar();
    }
}

function toggleSidebarCollapse() {
    if (window.appController) {
        appController.toggleSidebarCollapse();
    }
}

function toggleUserMenu() {
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

function signOut() {
    if (window.appController) {
        appController.handleSignOut();
    }
}

// Global utility functions
function viewAnalysisResults(analysisId) {
    navigateToView('results');
    // Load specific analysis results
    if (window.resultsManager) {
        resultsManager.loadAnalysis(analysisId);
    }
}

function deleteAnalysis(analysisId) {
    if (window.confirmDialog) {
        confirmDialog('Are you sure you want to delete this analysis?', {
            title: 'Confirm Delete',
            confirmText: 'Delete',
            cancelText: 'Cancel'
        }).then(confirmed => {
            if (confirmed) {
                // Remove from history
                let history = Utils.getStorage('sqlAnalyzer_analysisHistory', []);
                history = history.filter(item => item.id !== analysisId);
                Utils.setStorage('sqlAnalyzer_analysisHistory', history);

                // Reload history view if currently active
                if (window.appController && window.appController.currentView === 'history') {
                    window.appController.loadHistoryData();
                }

                if (window.showNotification) {
                    showNotification('Analysis deleted successfully', 'success');
                }
            }
        });
    }
}

function clearHistory() {
    if (window.confirmDialog) {
        confirmDialog('Are you sure you want to clear all analysis history?', {
            title: 'Clear History',
            confirmText: 'Clear All',
            cancelText: 'Cancel'
        }).then(confirmed => {
            if (confirmed) {
                Utils.setStorage('sqlAnalyzer_analysisHistory', []);
                Utils.setStorage('sqlAnalyzer_uploadHistory', []);

                // Reload history view if currently active
                if (window.appController && window.appController.currentView === 'history') {
                    window.appController.loadHistoryData();
                }

                if (window.showNotification) {
                    showNotification('History cleared successfully', 'success');
                }
            }
        });
    }
}

function exportResults(format) {
    if (window.resultsManager) {
        resultsManager.exportResults(format);
    } else {
        if (window.showNotification) {
            showNotification('Export feature will be available soon', 'info');
        }
    }
}

function shareResults() {
    if (window.resultsManager) {
        resultsManager.shareResults();
    } else {
        if (window.showNotification) {
            showNotification('Share feature will be available soon', 'info');
        }
    }
}

function analyzeSQLCode() {
    const sqlInput = document.getElementById('sql-input');
    const resultsDiv = document.getElementById('sql-analysis-results');

    if (!sqlInput || !sqlInput.value.trim()) {
        if (window.showNotification) {
            showNotification('Please enter SQL code to analyze', 'warning');
        }
        return;
    }

    // Show results section
    if (resultsDiv) {
        resultsDiv.style.display = 'block';

        // Simulate analysis
        const analysisContent = document.getElementById('analysis-content');
        if (analysisContent) {
            analysisContent.innerHTML = `
                <div class="alert-enterprise alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    SQL analysis completed. No syntax errors found.
                </div>
                <div class="mt-3">
                    <h6>Analysis Summary:</h6>
                    <ul>
                        <li>Syntax: Valid</li>
                        <li>Tables referenced: 1</li>
                        <li>Columns selected: ${Math.floor(Math.random() * 10) + 1}</li>
                        <li>Performance score: ${Math.floor(Math.random() * 30) + 70}%</li>
                    </ul>
                </div>
            `;
        }
    }

    if (window.showNotification) {
        showNotification('SQL analysis completed', 'success');
    }
}

function clearSQLInput() {
    const sqlInput = document.getElementById('sql-input');
    const resultsDiv = document.getElementById('sql-analysis-results');

    if (sqlInput) {
        sqlInput.value = '';
    }

    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
}

// Dashboard-specific functions
function exportDashboardReport() {
    if (window.showNotification) {
        showNotification('Generando reporte del dashboard...', 'info');
    }

    // Simulate report generation
    setTimeout(() => {
        const reportData = {
            timestamp: new Date().toISOString(),
            stats: {
                filesAnalyzed: document.getElementById('files-count')?.textContent || '0',
                analysesCompleted: document.getElementById('analyses-count')?.textContent || '0',
                successRate: document.getElementById('success-rate')?.textContent || '0%',
                avgTime: document.getElementById('avg-time')?.textContent || '0s'
            }
        };

        const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dashboard-report-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        if (window.showNotification) {
            showNotification('Reporte del dashboard exportado exitosamente', 'success');
        }
    }, 1500);
}

function showDashboardHelp() {
    if (window.showModal) {
        showModal({
            title: 'Ayuda del Dashboard',
            content: `
                <div class="help-content">
                    <h6><i class="fas fa-info-circle me-2"></i>Cómo usar el Dashboard</h6>
                    <ul class="list-unstyled">
                        <li class="mb-2">
                            <strong>Estadísticas:</strong> Muestra métricas en tiempo real de tu actividad
                        </li>
                        <li class="mb-2">
                            <strong>Acciones Rápidas:</strong> Acceso directo a las herramientas principales
                        </li>
                        <li class="mb-2">
                            <strong>Actividad Reciente:</strong> Historial de las últimas operaciones
                        </li>
                        <li class="mb-2">
                            <strong>Estado del Sistema:</strong> Información sobre el estado de los servicios
                        </li>
                    </ul>

                    <h6 class="mt-4"><i class="fas fa-keyboard me-2"></i>Atajos de Teclado</h6>
                    <div class="keyboard-shortcuts">
                        <div class="shortcut-item">
                            <kbd>Ctrl</kbd> + <kbd>U</kbd> - Subir archivo
                        </div>
                        <div class="shortcut-item">
                            <kbd>Ctrl</kbd> + <kbd>H</kbd> - Ver historial
                        </div>
                        <div class="shortcut-item">
                            <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>T</kbd> - Panel de pruebas
                        </div>
                    </div>
                </div>
            `,
            size: 'lg'
        });
    } else {
        alert('Panel de ayuda del Dashboard\n\n• Estadísticas: Métricas en tiempo real\n• Acciones Rápidas: Herramientas principales\n• Actividad Reciente: Historial de operaciones\n• Estado del Sistema: Información de servicios');
    }
}

function refreshRecentActivity() {
    const activityList = document.getElementById('recent-activity-list');
    if (!activityList) return;

    // Add loading state
    const originalContent = activityList.innerHTML;
    activityList.innerHTML = `
        <div class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2 mb-0 text-muted">Actualizando actividad...</p>
        </div>
    `;

    // Simulate refresh
    setTimeout(() => {
        activityList.innerHTML = originalContent;

        if (window.showNotification) {
            showNotification('Actividad reciente actualizada', 'success');
        }
    }, 1000);
}

// Upload-specific functions
function showUploadHistory() {
    navigateToView('history');
}

function showUploadHelp() {
    if (window.showModal) {
        showModal({
            title: 'Ayuda para Subir Archivos',
            content: `
                <div class="help-content">
                    <h6><i class="fas fa-upload me-2"></i>Cómo Subir Archivos</h6>
                    <ol>
                        <li class="mb-2">Arrastra archivos al área de carga o haz clic en "Seleccionar Archivos"</li>
                        <li class="mb-2">Los archivos se añaden automáticamente a la cola de subida</li>
                        <li class="mb-2">El análisis comienza automáticamente después de la subida</li>
                        <li class="mb-2">Puedes ver el progreso en tiempo real</li>
                    </ol>

                    <h6 class="mt-4"><i class="fas fa-file-alt me-2"></i>Formatos Soportados</h6>
                    <ul class="list-unstyled">
                        <li class="mb-1"><strong>.sql</strong> - Archivos SQL nativos (recomendado)</li>
                        <li class="mb-1"><strong>.txt</strong> - Archivos de texto con contenido SQL</li>
                        <li class="mb-1"><strong>.pdf</strong> - Documentos PDF con código SQL (OCR)</li>
                    </ul>

                    <h6 class="mt-4"><i class="fas fa-exclamation-triangle me-2"></i>Limitaciones</h6>
                    <ul class="list-unstyled">
                        <li class="mb-1">• Tamaño máximo: 10GB por archivo</li>
                        <li class="mb-1">• Máximo 50 archivos simultáneos</li>
                        <li class="mb-1">• Conexión SSL requerida</li>
                    </ul>
                </div>
            `,
            size: 'lg'
        });
    } else {
        alert('Ayuda para Subir Archivos\\n\\n• Arrastra archivos o haz clic para seleccionar\\n• Formatos: SQL, TXT, PDF\\n• Máximo: 10GB por archivo\\n• Hasta 50 archivos simultáneos');
    }
}

function clearUploadQueue() {
    const uploadContainer = document.getElementById('upload-container');
    const queueSection = document.getElementById('upload-queue-section');

    if (window.confirmDialog) {
        confirmDialog('¿Estás seguro de que quieres limpiar la cola de subida?', {
            title: 'Confirmar Limpieza',
            confirmText: 'Limpiar',
            cancelText: 'Cancelar'
        }).then(confirmed => {
            if (confirmed) {
                if (uploadContainer) {
                    uploadContainer.innerHTML = '';
                }
                if (queueSection) {
                    queueSection.style.display = 'none';
                }

                if (window.showNotification) {
                    showNotification('Cola de subida limpiada', 'success');
                }
            }
        });
    } else {
        if (confirm('¿Estás seguro de que quieres limpiar la cola de subida?')) {
            if (uploadContainer) {
                uploadContainer.innerHTML = '';
            }
            if (queueSection) {
                queueSection.style.display = 'none';
            }

            if (window.showNotification) {
                showNotification('Cola de subida limpiada', 'success');
            }
        }
    }
}

// History-specific functions
function filterHistory(type) {
    const rows = document.querySelectorAll('.history-row');

    rows.forEach(row => {
        const statusBadge = row.querySelector('.status-badge');
        const status = statusBadge ? statusBadge.textContent.toLowerCase() : '';

        let show = true;

        switch (type) {
            case 'completed':
                show = status.includes('completado');
                break;
            case 'failed':
                show = status.includes('error') || status.includes('falló');
                break;
            case 'recent':
                const dateCell = row.querySelector('.date-relative');
                const dateText = dateCell ? dateCell.textContent.toLowerCase() : '';
                show = dateText.includes('minuto') || dateText.includes('hora');
                break;
            case 'all':
            default:
                show = true;
                break;
        }

        row.style.display = show ? '' : 'none';
    });

    if (window.showNotification) {
        showNotification(`Filtro aplicado: ${type}`, 'info');
    }
}

function searchHistory(query) {
    const rows = document.querySelectorAll('.history-row');
    const searchTerm = query.toLowerCase();

    rows.forEach(row => {
        const fileName = row.querySelector('.file-name')?.textContent.toLowerCase() || '';
        const date = row.querySelector('.date-primary')?.textContent.toLowerCase() || '';
        const status = row.querySelector('.status-badge')?.textContent.toLowerCase() || '';

        const matches = fileName.includes(searchTerm) ||
            date.includes(searchTerm) ||
            status.includes(searchTerm);

        row.style.display = matches ? '' : 'none';
    });
}

function filterHistoryByDate(period) {
    const rows = document.querySelectorAll('.history-row');
    const now = new Date();

    rows.forEach(row => {
        const dateCell = row.querySelector('.date-primary');
        if (!dateCell) return;

        const dateText = dateCell.textContent;
        const rowDate = new Date(dateText);

        let show = true;

        switch (period) {
            case 'today':
                show = rowDate.toDateString() === now.toDateString();
                break;
            case 'week':
                const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                show = rowDate >= weekAgo;
                break;
            case 'month':
                const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                show = rowDate >= monthAgo;
                break;
            case 'custom':
                // Would open a date picker modal
                if (window.showNotification) {
                    showNotification('Selector de fecha personalizado próximamente', 'info');
                }
                return;
            case 'all':
            default:
                show = true;
                break;
        }

        row.style.display = show ? '' : 'none';
    });
}

function sortHistory(column) {
    const table = document.getElementById('history-table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('.history-row'));

    // Toggle sort direction
    const currentSort = table.dataset.sortColumn;
    const currentDirection = table.dataset.sortDirection || 'asc';
    const newDirection = (currentSort === column && currentDirection === 'asc') ? 'desc' : 'asc';

    table.dataset.sortColumn = column;
    table.dataset.sortDirection = newDirection;

    // Update sort icons
    table.querySelectorAll('.sort-icon').forEach(icon => {
        icon.className = 'fas fa-sort sort-icon';
    });

    const activeHeader = table.querySelector(`th[onclick="sortHistory('${column}')"] .sort-icon`);
    if (activeHeader) {
        activeHeader.className = `fas fa-sort-${newDirection === 'asc' ? 'up' : 'down'} sort-icon`;
    }

    // Sort rows
    rows.sort((a, b) => {
        let aValue, bValue;

        switch (column) {
            case 'fileName':
                aValue = a.querySelector('.file-name')?.textContent || '';
                bValue = b.querySelector('.file-name')?.textContent || '';
                break;
            case 'date':
                aValue = new Date(a.querySelector('.date-primary')?.textContent || '');
                bValue = new Date(b.querySelector('.date-primary')?.textContent || '');
                break;
            case 'status':
                aValue = a.querySelector('.status-badge')?.textContent || '';
                bValue = b.querySelector('.status-badge')?.textContent || '';
                break;
            case 'processingTime':
                aValue = parseFloat(a.querySelector('.time-primary')?.textContent || '0');
                bValue = parseFloat(b.querySelector('.time-primary')?.textContent || '0');
                break;
            case 'fileSize':
                aValue = parseFloat(a.querySelector('.size-primary')?.textContent || '0');
                bValue = parseFloat(b.querySelector('.size-primary')?.textContent || '0');
                break;
            default:
                return 0;
        }

        if (aValue < bValue) return newDirection === 'asc' ? -1 : 1;
        if (aValue > bValue) return newDirection === 'asc' ? 1 : -1;
        return 0;
    });

    // Reorder rows in DOM
    rows.forEach(row => tbody.appendChild(row));

    if (window.showNotification) {
        showNotification(`Ordenado por ${column} (${newDirection === 'asc' ? 'ascendente' : 'descendente'})`, 'info');
    }
}

function refreshHistory() {
    if (window.showNotification) {
        showNotification('Actualizando historial...', 'info');
    }

    // Simulate refresh
    setTimeout(() => {
        if (window.appController && window.appController.currentView === 'history') {
            window.appController.loadHistoryData();
        }

        if (window.showNotification) {
            showNotification('Historial actualizado', 'success');
        }
    }, 1000);
}

function exportHistoryReport() {
    if (window.showNotification) {
        showNotification('Generando reporte del historial...', 'info');
    }

    // Simulate report generation
    setTimeout(() => {
        const reportData = {
            timestamp: new Date().toISOString(),
            totalAnalyses: document.querySelectorAll('.history-row').length,
            completedAnalyses: document.querySelectorAll('.status-completed').length,
            failedAnalyses: document.querySelectorAll('.status-failed').length
        };

        const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `history-report-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        if (window.showNotification) {
            showNotification('Reporte del historial exportado', 'success');
        }
    }, 1500);
}

function toggleTableView() {
    const table = document.getElementById('history-table');
    const toggle = document.getElementById('table-view-toggle');

    if (table.classList.contains('compact-view')) {
        table.classList.remove('compact-view');
        toggle.innerHTML = '<i class="fas fa-th-list"></i>';
    } else {
        table.classList.add('compact-view');
        toggle.innerHTML = '<i class="fas fa-th"></i>';
    }
}

function downloadAnalysisReport(analysisId) {
    if (window.showNotification) {
        showNotification(`Descargando reporte de análisis ${analysisId}...`, 'info');
    }

    // Simulate download
    setTimeout(() => {
        if (window.showNotification) {
            showNotification('Reporte descargado exitosamente', 'success');
        }
    }, 1000);
}

function rerunAnalysis(analysisId) {
    if (window.confirmDialog) {
        confirmDialog('¿Quieres ejecutar este análisis nuevamente?', {
            title: 'Confirmar Re-ejecución',
            confirmText: 'Ejecutar',
            cancelText: 'Cancelar'
        }).then(confirmed => {
            if (confirmed) {
                if (window.showNotification) {
                    showNotification(`Re-ejecutando análisis ${analysisId}...`, 'info');
                }

                // Simulate re-run
                setTimeout(() => {
                    if (window.showNotification) {
                        showNotification('Análisis re-ejecutado exitosamente', 'success');
                    }
                }, 2000);
            }
        });
    } else {
        if (confirm('¿Quieres ejecutar este análisis nuevamente?')) {
            if (window.showNotification) {
                showNotification(`Re-ejecutando análisis ${analysisId}...`, 'info');
            }
        }
    }
}

function viewErrorDetails(analysisId) {
    if (window.showModal) {
        showModal({
            title: 'Detalles del Error',
            content: `
                <div class="error-details">
                    <div class="alert alert-danger">
                        <h6><i class="fas fa-exclamation-triangle me-2"></i>Error de Procesamiento</h6>
                        <p>No se pudo procesar el archivo PDF. El contenido no contiene SQL válido o el OCR falló.</p>
                    </div>

                    <h6>Información del Error:</h6>
                    <ul>
                        <li><strong>Código:</strong> PDF_OCR_FAILED</li>
                        <li><strong>Archivo:</strong> security_audit.pdf</li>
                        <li><strong>Tamaño:</strong> 15.2 MB</li>
                        <li><strong>Tiempo:</strong> 2025-07-11 13:45:33</li>
                    </ul>

                    <h6>Soluciones Sugeridas:</h6>
                    <ol>
                        <li>Verifica que el PDF contenga texto SQL legible</li>
                        <li>Convierte el PDF a formato .sql o .txt</li>
                        <li>Reduce el tamaño del archivo si es muy grande</li>
                        <li>Contacta soporte si el problema persiste</li>
                    </ol>
                </div>
            `,
            size: 'lg'
        });
    } else {
        alert('Error: PDF_OCR_FAILED\\nNo se pudo procesar el archivo PDF.\\n\\nSoluciones:\\n• Convierte a formato SQL o TXT\\n• Verifica que contenga SQL válido\\n• Reduce el tamaño del archivo');
    }
}

// Results-specific functions
function compareAnalysis() {
    if (window.showModal) {
        showModal({
            title: 'Comparar Análisis',
            content: `
                <div class="compare-analysis">
                    <p>Selecciona otro análisis para comparar con el actual:</p>
                    <select class="form-control-enterprise mb-3">
                        <option>user_queries.sql (2025-07-11 14:15:10)</option>
                        <option>backup_script.sql (2025-07-11 12:30:45)</option>
                        <option>migration_v2.sql (2025-07-11 10:15:22)</option>
                    </select>
                    <div class="comparison-preview">
                        <div class="row">
                            <div class="col-6">
                                <h6>Análisis Actual</h6>
                                <ul class="list-unstyled">
                                    <li>Puntuación: 98%</li>
                                    <li>Errores: 0</li>
                                    <li>Advertencias: 2</li>
                                </ul>
                            </div>
                            <div class="col-6">
                                <h6>Análisis Seleccionado</h6>
                                <ul class="list-unstyled">
                                    <li>Puntuación: 85%</li>
                                    <li>Errores: 3</li>
                                    <li>Advertencias: 7</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            `,
            size: 'lg',
            buttons: [
                {
                    text: 'Comparar',
                    class: 'btn-primary',
                    action: () => {
                        if (window.showNotification) {
                            showNotification('Generando comparación detallada...', 'info');
                        }
                    }
                },
                {
                    text: 'Cancelar',
                    class: 'btn-outline-secondary'
                }
            ]
        });
    } else {
        if (window.showNotification) {
            showNotification('Función de comparación próximamente disponible', 'info');
        }
    }
}

function scheduleAnalysis() {
    if (window.showModal) {
        showModal({
            title: 'Programar Análisis',
            content: `
                <div class="schedule-analysis">
                    <div class="mb-3">
                        <label class="form-label-enterprise">Frecuencia</label>
                        <select class="form-control-enterprise">
                            <option>Diario</option>
                            <option>Semanal</option>
                            <option>Mensual</option>
                            <option>Personalizado</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label-enterprise">Hora de Ejecución</label>
                        <input type="time" class="form-control-enterprise" value="02:00">
                    </div>
                    <div class="mb-3">
                        <label class="form-label-enterprise">Notificaciones</label>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" checked>
                            <label class="form-check-label">Enviar email al completar</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox">
                            <label class="form-check-label">Notificar solo si hay errores</label>
                        </div>
                    </div>
                </div>
            `,
            size: 'md',
            buttons: [
                {
                    text: 'Programar',
                    class: 'btn-primary',
                    action: () => {
                        if (window.showNotification) {
                            showNotification('Análisis programado exitosamente', 'success');
                        }
                    }
                },
                {
                    text: 'Cancelar',
                    class: 'btn-outline-secondary'
                }
            ]
        });
    } else {
        if (window.showNotification) {
            showNotification('Función de programación próximamente disponible', 'info');
        }
    }
}

// Global UI functions
function toggleSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');

    if (sidebar && backdrop) {
        sidebar.classList.toggle('show');
        backdrop.classList.toggle('show');
    }
}

function closeSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');

    if (sidebar && backdrop) {
        sidebar.classList.remove('show');
        backdrop.classList.remove('show');
    }
}

function toggleSidebarCollapse() {
    const sidebar = document.getElementById('app-sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

function toggleUserMenu() {
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

function signOut() {
    if (window.appController) {
        appController.handleSignOut();
    }
}

// Global event delegation for onclick handlers
document.addEventListener('click', (e) => {
    try {
        // Handle data-action attributes
        const actionElement = e.target.closest('[data-action]');
        if (actionElement) {
            e.preventDefault();
            const action = actionElement.getAttribute('data-action');

            switch (action) {
                case 'runNavigationTests':
                    if (typeof runNavigationTests === 'function') runNavigationTests();
                    break;
                case 'exportDashboardReport':
                    if (typeof exportDashboardReport === 'function') exportDashboardReport();
                    break;
                case 'navigateToSettings':
                    if (window.navigationManager) window.navigationManager.navigateTo('settings');
                    break;
            }
        }

        // Handle onclick attributes safely (fallback for existing code)
        const onclickElement = e.target.closest('[onclick]');
        if (onclickElement) {
            const onclickValue = onclickElement.getAttribute('onclick');

            // Only allow safe, predefined functions
            const safeActions = [
                'location.reload()',
                'navigateToView(',
                'navigateBack()',
                'showUploadHistory()',
                'showUploadHelp()',
                'clearUploadQueue()',
                'filterHistory(',
                'exportHistoryReport()',
                'clearHistory()',
                'refreshHistory()',
                'toggleTableView()',
                'sortHistory(',
                'viewAnalysisResults(',
                'downloadAnalysisReport(',
                'rerunAnalysis(',
                'deleteAnalysis(',
                'viewErrorDetails(',
                'resultsManager.',
                'analyzeSQLCode()',
                'clearSQLInput()',
                'showDashboardHelp()',
                'refreshRecentActivity()',
                'compareAnalysis()',
                'scheduleAnalysis()'
            ];

            const isSafe = safeActions.some(action => onclickValue.includes(action));

            if (isSafe) {
                e.preventDefault();
                // Execute the safe function
                try {
                    eval(onclickValue);
                } catch (error) {
                    if (window.Utils) Utils.warn('Safe onclick execution failed:', error);
                }
            }
        }
    } catch (error) {
        if (window.Utils) Utils.error('Event delegation error:', error);
    }
});

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.appController = new AppController();
});
