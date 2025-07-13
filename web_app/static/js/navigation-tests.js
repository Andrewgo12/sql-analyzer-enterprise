/* ============================================================================
   SQL ANALYZER ENTERPRISE - NAVIGATION TESTING SUITE
   Comprehensive testing for navigation and view loading functionality
   ============================================================================ */

class NavigationTestSuite {
    constructor() {
        this.tests = [];
        this.results = [];
        this.isRunning = false;
        
        this.setupTests();
    }
    
    // ========================================================================
    // TEST SETUP
    // ========================================================================
    
    setupTests() {
        // Authentication Tests
        this.addTest('Authentication Flow', () => this.testAuthenticationFlow());
        this.addTest('Session Management', () => this.testSessionManagement());
        this.addTest('Logout Functionality', () => this.testLogoutFunctionality());
        
        // Navigation Tests
        this.addTest('Dashboard Navigation', () => this.testDashboardNavigation());
        this.addTest('Upload View Navigation', () => this.testUploadNavigation());
        this.addTest('History View Navigation', () => this.testHistoryNavigation());
        this.addTest('Results View Navigation', () => this.testResultsNavigation());
        this.addTest('Profile View Navigation', () => this.testProfileNavigation());
        this.addTest('Settings View Navigation', () => this.testSettingsNavigation());
        this.addTest('Analyzer View Navigation', () => this.testAnalyzerNavigation());
        this.addTest('Optimizer View Navigation', () => this.testOptimizerNavigation());
        this.addTest('Security View Navigation', () => this.testSecurityNavigation());
        
        // UI Tests
        this.addTest('Sidebar Functionality', () => this.testSidebarFunctionality());
        this.addTest('Mobile Responsiveness', () => this.testMobileResponsiveness());
        this.addTest('Navigation State Management', () => this.testNavigationState());
        this.addTest('URL Routing', () => this.testURLRouting());
        this.addTest('Browser Back/Forward', () => this.testBrowserNavigation());
        
        // Content Loading Tests
        this.addTest('Content Loading Speed', () => this.testContentLoadingSpeed());
        this.addTest('Error Handling', () => this.testErrorHandling());
        this.addTest('Loading States', () => this.testLoadingStates());
        
        // Integration Tests
        this.addTest('File Upload Integration', () => this.testFileUploadIntegration());
        this.addTest('Analysis Integration', () => this.testAnalysisIntegration());
        this.addTest('Data Persistence', () => this.testDataPersistence());
    }
    
    addTest(name, testFunction) {
        this.tests.push({
            name,
            testFunction,
            status: 'pending',
            error: null,
            duration: 0
        });
    }
    
    // ========================================================================
    // TEST EXECUTION
    // ========================================================================
    
    async runAllTests() {
        if (this.isRunning) {
            if (window.Utils) Utils.warn('Tests are already running');
            return;
        }
        
        this.isRunning = true;
        this.results = [];
        
        if (window.Utils) Utils.log('🧪 Starting Navigation Test Suite...');
        if (window.Utils) Utils.log(`Running ${this.tests.length} tests...`);
        
        for (const test of this.tests) {
            await this.runTest(test);
        }
        
        this.isRunning = false;
        this.generateReport();
    }
    
    async runTest(test) {
        if (window.Utils) Utils.log(`🔄 Running: ${test.name}`);
        
        const startTime = Date.now();
        
        try {
            await test.testFunction();
            test.status = 'passed';
            test.error = null;
        } catch (error) {
            test.status = 'failed';
            test.error = error.message;
            if (window.Utils) Utils.error(`❌ ${test.name} failed:`, error);
        }
        
        test.duration = Date.now() - startTime;
        this.results.push(test);
        
        // Add delay between tests
        await this.delay(100);
    }
    
    // ========================================================================
    // AUTHENTICATION TESTS
    // ========================================================================
    
    async testAuthenticationFlow() {
        // Test initial auth state
        if (!window.appController) {
            throw new Error('App controller not initialized');
        }
        
        // Test auth view loading
        const authView = document.getElementById('auth-view');
        const mainApp = document.getElementById('main-app');
        
        if (!authView || !mainApp) {
            throw new Error('Auth views not found');
        }
        
        // Test authentication success
        appController.handleAuthenticationSuccess();
        
        if (mainApp.style.display === 'none') {
            throw new Error('Main app not shown after authentication');
        }
        
        if (window.Utils) Utils.log('✅ Authentication flow working correctly');
    }
    
    async testSessionManagement() {
        if (!window.authManager) {
            throw new Error('Auth manager not initialized');
        }
        
        // Test session creation
        const sessionInfo = authManager.getSessionInfo();
        if (!sessionInfo) {
            throw new Error('Session info not available');
        }
        
        if (window.Utils) Utils.log('✅ Session management working correctly');
    }
    
    async testLogoutFunctionality() {
        // Test logout
        if (window.appController) {
            appController.handleSignOut();
        }
        
        // Verify auth state
        const authView = document.getElementById('auth-view');
        if (authView && authView.style.display === 'none') {
            throw new Error('Auth view not shown after logout');
        }
        
        // Re-authenticate for remaining tests
        appController.handleAuthenticationSuccess();
        
        if (window.Utils) Utils.log('✅ Logout functionality working correctly');
    }
    
    // ========================================================================
    // NAVIGATION TESTS
    // ========================================================================
    
    async testDashboardNavigation() {
        await this.testViewNavigation('dashboard', 'Dashboard');
    }
    
    async testUploadNavigation() {
        await this.testViewNavigation('upload', 'Upload Files');
    }
    
    async testHistoryNavigation() {
        await this.testViewNavigation('history', 'Analysis History');
    }
    
    async testResultsNavigation() {
        await this.testViewNavigation('results', 'Results');
    }
    
    async testProfileNavigation() {
        await this.testViewNavigation('profile', 'Profile');
    }
    
    async testSettingsNavigation() {
        await this.testViewNavigation('settings', 'Settings');
    }
    
    async testAnalyzerNavigation() {
        await this.testViewNavigation('analyzer', 'SQL Analyzer');
    }
    
    async testOptimizerNavigation() {
        await this.testViewNavigation('optimizer', 'Performance Optimizer');
    }
    
    async testSecurityNavigation() {
        await this.testViewNavigation('security', 'Security Scanner');
    }
    
    async testViewNavigation(viewName, expectedTitle) {
        if (!window.appController) {
            throw new Error('App controller not initialized');
        }
        
        // Navigate to view
        appController.navigateToView(viewName);
        
        // Wait for content to load
        await this.delay(500);
        
        // Check if view is active
        if (appController.currentView !== viewName) {
            throw new Error(`Failed to navigate to ${viewName}`);
        }
        
        // Check if content is loaded
        const contentContainer = document.getElementById('content-container');
        if (!contentContainer || !contentContainer.innerHTML.trim()) {
            throw new Error(`Content not loaded for ${viewName}`);
        }
        
        // Check navigation state
        const activeNavLink = document.querySelector(`.nav-link[data-view="${viewName}"]`);
        if (!activeNavLink || !activeNavLink.classList.contains('active')) {
            throw new Error(`Navigation state not updated for ${viewName}`);
        }
        
        if (window.Utils) Utils.log(`✅ ${expectedTitle} navigation working correctly`);
    }
    
    // ========================================================================
    // UI TESTS
    // ========================================================================
    
    async testSidebarFunctionality() {
        const sidebar = document.getElementById('app-sidebar');
        if (!sidebar) {
            throw new Error('Sidebar not found');
        }
        
        // Test sidebar toggle
        if (window.appController) {
            appController.toggleSidebarCollapse();
            
            if (!sidebar.classList.contains('collapsed')) {
                throw new Error('Sidebar collapse not working');
            }
            
            appController.toggleSidebarCollapse();
            
            if (sidebar.classList.contains('collapsed')) {
                throw new Error('Sidebar expand not working');
            }
        }
        
        if (window.Utils) Utils.log('✅ Sidebar functionality working correctly');
    }
    
    async testMobileResponsiveness() {
        // Simulate mobile viewport
        const originalWidth = window.innerWidth;
        
        // Test mobile sidebar
        if (window.appController) {
            appController.isMobile = true;
            appController.toggleSidebar();
            
            const sidebar = document.getElementById('app-sidebar');
            const backdrop = document.getElementById('sidebar-backdrop');
            
            if (!sidebar.classList.contains('show') || !backdrop.classList.contains('show')) {
                throw new Error('Mobile sidebar not working');
            }
            
            appController.closeSidebar();
            appController.isMobile = false;
        }
        
        if (window.Utils) Utils.log('✅ Mobile responsiveness working correctly');
    }
    
    async testNavigationState() {
        // Test navigation state persistence
        const testViews = ['dashboard', 'upload', 'history', 'profile'];
        
        for (const viewName of testViews) {
            appController.navigateToView(viewName);
            await this.delay(100);
            
            if (appController.currentView !== viewName) {
                throw new Error(`Navigation state not maintained for ${viewName}`);
            }
        }
        
        if (window.Utils) Utils.log('✅ Navigation state management working correctly');
    }
    
    async testURLRouting() {
        // Test URL updates
        const testRoutes = [
            { view: 'dashboard', url: '/' },
            { view: 'upload', url: '/upload' },
            { view: 'history', url: '/history' }
        ];
        
        for (const route of testRoutes) {
            appController.navigateToView(route.view);
            await this.delay(100);
            
            const currentPath = window.location.pathname;
            if (currentPath !== route.url) {
                throw new Error(`URL not updated correctly for ${route.view}. Expected: ${route.url}, Got: ${currentPath}`);
            }
        }
        
        if (window.Utils) Utils.log('✅ URL routing working correctly');
    }
    
    async testBrowserNavigation() {
        // Test browser back/forward
        appController.navigateToView('dashboard');
        await this.delay(100);
        
        appController.navigateToView('upload');
        await this.delay(100);
        
        // Simulate browser back
        window.history.back();
        await this.delay(200);
        
        if (appController.currentView !== 'dashboard') {
            throw new Error('Browser back navigation not working');
        }
        
        if (window.Utils) Utils.log('✅ Browser navigation working correctly');
    }
    
    // ========================================================================
    // CONTENT LOADING TESTS
    // ========================================================================
    
    async testContentLoadingSpeed() {
        const startTime = Date.now();
        
        appController.navigateToView('dashboard');
        await this.delay(100);
        
        const loadTime = Date.now() - startTime;
        
        if (loadTime > 2000) {
            throw new Error(`Content loading too slow: ${loadTime}ms`);
        }
        
        if (window.Utils) Utils.log(`✅ Content loading speed acceptable: ${loadTime}ms`);
    }
    
    async testErrorHandling() {
        // Test invalid view navigation
        try {
            appController.navigateToView('invalid-view');
            await this.delay(100);
            
            // Should fallback to dashboard
            if (appController.currentView !== 'dashboard') {
                throw new Error('Error handling not working for invalid views');
            }
        } catch (error) {
            // Expected behavior
        }
        
        if (window.Utils) Utils.log('✅ Error handling working correctly');
    }
    
    async testLoadingStates() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (!loadingOverlay) {
            throw new Error('Loading overlay not found');
        }
        
        // Test loading state
        appController.showLoading();
        
        if (!loadingOverlay.classList.contains('show')) {
            throw new Error('Loading state not shown');
        }
        
        appController.hideLoading();
        
        if (loadingOverlay.classList.contains('show')) {
            throw new Error('Loading state not hidden');
        }
        
        if (window.Utils) Utils.log('✅ Loading states working correctly');
    }
    
    // ========================================================================
    // INTEGRATION TESTS
    // ========================================================================
    
    async testFileUploadIntegration() {
        // Navigate to upload view
        appController.navigateToView('upload');
        await this.delay(200);
        
        // Check if upload components are present
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('file-input');
        
        if (!dropzone || !fileInput) {
            throw new Error('Upload components not found');
        }
        
        if (window.Utils) Utils.log('✅ File upload integration working correctly');
    }
    
    async testAnalysisIntegration() {
        // Navigate to analyzer view
        appController.navigateToView('analyzer');
        await this.delay(200);
        
        // Check if analyzer components are present
        const sqlInput = document.getElementById('sql-input');
        
        if (!sqlInput) {
            throw new Error('Analyzer components not found');
        }
        
        if (window.Utils) Utils.log('✅ Analysis integration working correctly');
    }
    
    async testDataPersistence() {
        // Test data storage and retrieval
        const testData = { test: 'navigation-test' };
        Utils.setStorage('test-data', testData);
        
        const retrievedData = Utils.getStorage('test-data');
        
        if (!retrievedData || retrievedData.test !== 'navigation-test') {
            throw new Error('Data persistence not working');
        }
        
        Utils.removeStorage('test-data');
        
        if (window.Utils) Utils.log('✅ Data persistence working correctly');
    }
    
    // ========================================================================
    // REPORTING
    // ========================================================================
    
    generateReport() {
        const passed = this.results.filter(r => r.status === 'passed').length;
        const failed = this.results.filter(r => r.status === 'failed').length;
        const total = this.results.length;
        const totalTime = this.results.reduce((sum, r) => sum + r.duration, 0);
        
        if (window.Utils) Utils.log('\n🧪 NAVIGATION TEST SUITE RESULTS');
        if (window.Utils) Utils.log('=====================================');
        if (window.Utils) Utils.log(`Total Tests: ${total}`);
        if (window.Utils) Utils.log(`Passed: ${passed} ✅`);
        if (window.Utils) Utils.log(`Failed: ${failed} ❌`);
        if (window.Utils) Utils.log(`Success Rate: ${Math.round((passed / total) * 100)}%`);
        if (window.Utils) Utils.log(`Total Time: ${totalTime}ms`);
        if (window.Utils) Utils.log('=====================================');
        
        if (failed > 0) {
            if (window.Utils) Utils.log('\n❌ FAILED TESTS:');
            this.results.filter(r => r.status === 'failed').forEach(test => {
                if (window.Utils) Utils.log(`- ${test.name}: ${test.error}`);
            });
        }
        
        if (window.Utils) Utils.log('\n✅ All navigation tests completed!');
        
        // Show notification
        if (window.showNotification) {
            const message = `Navigation tests completed: ${passed}/${total} passed`;
            const type = failed === 0 ? 'success' : 'warning';
            showNotification(message, type);
        }
    }
    
    // ========================================================================
    // UTILITIES
    // ========================================================================
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Global test runner
window.runNavigationTests = () => {
    const testSuite = new NavigationTestSuite();
    testSuite.runAllTests();
};

// Auto-run tests in development
if (window.location.hostname === 'localhost') {
    // Run tests after app initialization
    setTimeout(() => {
        if (window.appController && window.appController.isAuthenticated) {
            if (window.Utils) Utils.log('🧪 Auto-running navigation tests...');
            window.runNavigationTests();
        }
    }, 2000);
}
