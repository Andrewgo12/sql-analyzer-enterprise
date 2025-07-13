/* ============================================================================
   SQL ANALYZER ENTERPRISE - TESTING DASHBOARD
   Real-time testing and monitoring dashboard
   ============================================================================ */

class TestDashboard {
    constructor() {
        this.isVisible = false;
        this.testResults = [];
        this.performanceMetrics = [];
        
        this.init();
    }
    
    init() {
        this.createDashboard();
        this.setupEventListeners();
        this.startPerformanceMonitoring();
    }
    
    createDashboard() {
        const dashboard = document.createElement('div');
        dashboard.id = 'test-dashboard';
        dashboard.innerHTML = `
            <div class="test-dashboard-container">
                <div class="test-dashboard-header">
                    <h5><i class="fas fa-vial me-2"></i>Navigation Test Dashboard</h5>
                    <div class="test-dashboard-controls">
                        <button class="btn-test btn-sm" onclick="testDashboard.runQuickTest()">
                            <i class="fas fa-play me-1"></i>Quick Test
                        </button>
                        <button class="btn-test btn-sm" onclick="testDashboard.runFullTest()">
                            <i class="fas fa-cogs me-1"></i>Full Test
                        </button>
                        <button class="btn-test btn-sm" onclick="testDashboard.clearResults()">
                            <i class="fas fa-trash me-1"></i>Clear
                        </button>
                        <button class="btn-test btn-sm" onclick="testDashboard.toggle()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="test-dashboard-content">
                    <div class="test-metrics">
                        <div class="metric-card">
                            <div class="metric-value" id="test-success-rate">--</div>
                            <div class="metric-label">Success Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value" id="test-avg-load-time">--</div>
                            <div class="metric-label">Avg Load Time</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value" id="test-total-tests">--</div>
                            <div class="metric-label">Total Tests</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value" id="test-errors">--</div>
                            <div class="metric-label">Errors</div>
                        </div>
                    </div>
                    <div class="test-results" id="test-results-container">
                        <div class="test-placeholder">
                            <i class="fas fa-flask fa-2x mb-2"></i>
                            <p>Run tests to see results</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add styles
        const styles = document.createElement('style');
        styles.textContent = `
            #test-dashboard {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 400px;
                max-height: 600px;
                background: var(--bg-primary);
                border: 1px solid var(--border-color);
                border-radius: var(--border-radius-lg);
                box-shadow: var(--shadow-2xl);
                z-index: 2000;
                display: none;
                font-family: 'Inter', sans-serif;
            }
            
            .test-dashboard-container {
                display: flex;
                flex-direction: column;
                height: 100%;
            }
            
            .test-dashboard-header {
                padding: 1rem;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: between;
                align-items: center;
                background: var(--bg-secondary);
                border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
            }
            
            .test-dashboard-header h5 {
                margin: 0;
                color: var(--text-primary);
                font-size: 0.875rem;
                font-weight: 600;
            }
            
            .test-dashboard-controls {
                display: flex;
                gap: 0.5rem;
            }
            
            .btn-test {
                padding: 0.25rem 0.5rem;
                font-size: 0.75rem;
                border: 1px solid var(--border-color);
                background: var(--bg-primary);
                color: var(--text-secondary);
                border-radius: var(--border-radius);
                cursor: pointer;
                transition: var(--transition);
            }
            
            .btn-test:hover {
                background: var(--bg-hover);
                color: var(--text-primary);
            }
            
            .test-dashboard-content {
                flex: 1;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }
            
            .test-metrics {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0.5rem;
                padding: 1rem;
                border-bottom: 1px solid var(--border-color);
            }
            
            .metric-card {
                text-align: center;
                padding: 0.75rem;
                background: var(--bg-secondary);
                border-radius: var(--border-radius);
            }
            
            .metric-value {
                font-size: 1.25rem;
                font-weight: 700;
                color: var(--primary-color);
                line-height: 1;
            }
            
            .metric-label {
                font-size: 0.75rem;
                color: var(--text-muted);
                margin-top: 0.25rem;
            }
            
            .test-results {
                flex: 1;
                overflow-y: auto;
                padding: 1rem;
            }
            
            .test-placeholder {
                text-align: center;
                color: var(--text-muted);
                padding: 2rem 0;
            }
            
            .test-item {
                display: flex;
                justify-content: between;
                align-items: center;
                padding: 0.5rem;
                margin-bottom: 0.5rem;
                border-radius: var(--border-radius);
                font-size: 0.8125rem;
            }
            
            .test-item.passed {
                background: rgba(16, 185, 129, 0.1);
                color: var(--success-color);
            }
            
            .test-item.failed {
                background: rgba(239, 68, 68, 0.1);
                color: var(--danger-color);
            }
            
            .test-item.running {
                background: rgba(59, 130, 246, 0.1);
                color: var(--primary-color);
            }
            
            .test-name {
                flex: 1;
            }
            
            .test-duration {
                font-size: 0.75rem;
                opacity: 0.7;
            }
            
            @media (max-width: 768px) {
                #test-dashboard {
                    width: calc(100vw - 40px);
                    max-width: 400px;
                }
            }
        `;
        
        document.head.appendChild(styles);
        document.body.appendChild(dashboard);
    }
    
    setupEventListeners() {
        // Keyboard shortcut to toggle dashboard (Ctrl+Shift+T)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggle();
            }
        });
    }
    
    startPerformanceMonitoring() {
        // Monitor navigation performance
        setInterval(() => {
            this.updatePerformanceMetrics();
        }, 5000);
    }
    
    toggle() {
        const dashboard = document.getElementById('test-dashboard');
        this.isVisible = !this.isVisible;
        dashboard.style.display = this.isVisible ? 'block' : 'none';
    }
    
    show() {
        const dashboard = document.getElementById('test-dashboard');
        this.isVisible = true;
        dashboard.style.display = 'block';
    }
    
    hide() {
        const dashboard = document.getElementById('test-dashboard');
        this.isVisible = false;
        dashboard.style.display = 'none';
    }
    
    async runQuickTest() {
        this.show();
        
        const quickTests = [
            { name: 'Dashboard Load', test: () => this.testViewLoad('dashboard') },
            { name: 'Upload Load', test: () => this.testViewLoad('upload') },
            { name: 'Navigation State', test: () => this.testNavigationState() },
            { name: 'Sidebar Toggle', test: () => this.testSidebarToggle() }
        ];
        
        await this.runTests(quickTests);
    }
    
    async runFullTest() {
        this.show();
        
        if (window.runNavigationTests) {
            // Use the comprehensive test suite
            runNavigationTests();
        } else {
            // Fallback to basic tests
            await this.runQuickTest();
        }
    }
    
    async runTests(tests) {
        const resultsContainer = document.getElementById('test-results-container');
        resultsContainer.innerHTML = '';
        
        this.testResults = [];
        
        for (const testConfig of tests) {
            const testItem = this.createTestItem(testConfig.name, 'running');
            resultsContainer.appendChild(testItem);
            
            const startTime = Date.now();
            
            try {
                await testConfig.test();
                const duration = Date.now() - startTime;
                
                this.updateTestItem(testItem, 'passed', duration);
                this.testResults.push({ name: testConfig.name, status: 'passed', duration });
                
            } catch (error) {
                const duration = Date.now() - startTime;
                
                this.updateTestItem(testItem, 'failed', duration, error.message);
                this.testResults.push({ name: testConfig.name, status: 'failed', duration, error: error.message });
            }
            
            // Small delay between tests
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        this.updateMetrics();
    }
    
    createTestItem(name, status) {
        const item = document.createElement('div');
        item.className = `test-item ${status}`;
        item.innerHTML = `
            <div class="test-name">${name}</div>
            <div class="test-duration">
                ${status === 'running' ? '<i class="fas fa-spinner fa-spin"></i>' : ''}
            </div>
        `;
        return item;
    }
    
    updateTestItem(item, status, duration, error = null) {
        item.className = `test-item ${status}`;
        
        const durationElement = item.querySelector('.test-duration');
        const icon = status === 'passed' ? '✅' : '❌';
        const time = `${duration}ms`;
        
        durationElement.innerHTML = `${icon} ${time}`;
        
        if (error) {
            item.title = error;
        }
    }
    
    updateMetrics() {
        const passed = this.testResults.filter(r => r.status === 'passed').length;
        const total = this.testResults.length;
        const avgTime = total > 0 ? Math.round(this.testResults.reduce((sum, r) => sum + r.duration, 0) / total) : 0;
        const errors = this.testResults.filter(r => r.status === 'failed').length;
        
        document.getElementById('test-success-rate').textContent = total > 0 ? `${Math.round((passed / total) * 100)}%` : '--';
        document.getElementById('test-avg-load-time').textContent = total > 0 ? `${avgTime}ms` : '--';
        document.getElementById('test-total-tests').textContent = total;
        document.getElementById('test-errors').textContent = errors;
    }
    
    updatePerformanceMetrics() {
        // Update real-time performance metrics
        const navigationErrors = Utils.getStorage('sqlAnalyzer_navigationErrors', []);
        const recentErrors = navigationErrors.filter(e => Date.now() - e.timestamp < 300000); // Last 5 minutes
        
        document.getElementById('test-errors').textContent = recentErrors.length;
    }
    
    clearResults() {
        const resultsContainer = document.getElementById('test-results-container');
        resultsContainer.innerHTML = `
            <div class="test-placeholder">
                <i class="fas fa-flask fa-2x mb-2"></i>
                <p>Run tests to see results</p>
            </div>
        `;
        
        this.testResults = [];
        this.updateMetrics();
        
        // Clear stored errors
        Utils.removeStorage('sqlAnalyzer_navigationErrors');
    }
    
    // Test Methods
    async testViewLoad(viewName) {
        if (!window.appController) {
            throw new Error('App controller not available');
        }
        
        const startTime = Date.now();
        appController.navigateToView(viewName);
        
        // Wait for content to load
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const loadTime = Date.now() - startTime;
        
        if (appController.currentView !== viewName) {
            throw new Error(`Failed to load ${viewName}`);
        }
        
        if (loadTime > 2000) {
            throw new Error(`Load time too slow: ${loadTime}ms`);
        }
    }
    
    async testNavigationState() {
        if (!window.appController) {
            throw new Error('App controller not available');
        }
        
        const originalView = appController.currentView;
        
        // Test navigation to different view
        appController.navigateToView('upload');
        await new Promise(resolve => setTimeout(resolve, 200));
        
        if (appController.currentView !== 'upload') {
            throw new Error('Navigation state not updated');
        }
        
        // Return to original view
        appController.navigateToView(originalView);
        await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    async testSidebarToggle() {
        if (!window.appController) {
            throw new Error('App controller not available');
        }
        
        const sidebar = document.getElementById('app-sidebar');
        if (!sidebar) {
            throw new Error('Sidebar not found');
        }
        
        // Test collapse
        appController.toggleSidebarCollapse();
        
        if (!sidebar.classList.contains('collapsed')) {
            throw new Error('Sidebar collapse failed');
        }
        
        // Test expand
        appController.toggleSidebarCollapse();
        
        if (sidebar.classList.contains('collapsed')) {
            throw new Error('Sidebar expand failed');
        }
    }
}

// Initialize test dashboard
window.testDashboard = new TestDashboard();

// Global shortcut info
if (window.Utils) Utils.log('🧪 Test Dashboard initialized');
if (window.Utils) Utils.log('Press Ctrl+Shift+T to toggle test dashboard');
if (window.Utils) Utils.log('Or call testDashboard.show() from console');
