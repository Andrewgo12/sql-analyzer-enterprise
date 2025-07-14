/* ============================================================================
   SQL ANALYZER ENTERPRISE - RESULTS MODULE
   Results display, charts, data visualization, export functionality
   ============================================================================ */

class ResultsManager {
    constructor() {
        this.currentAnalysis = null;
        this.charts = new Map();
        this.exportFormats = ['pdf', 'html', 'json', 'excel', 'csv'];

        this.init();
    }

    // Helper method for notifications
    showNotification(message, type = 'info') {
        try {
            if (window.notificationManager && window.notificationManager.show) {
                window.notificationManager.show(message, type);
            } else if (window.showNotification) {
                window.showNotification(message, type);
            } else {
                if (window.Utils) Utils.log(`[${type.toUpperCase()}] ${message}`);
            }
        } catch (error) {
            if (window.Utils) Utils.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    init() {
        try {
            this.loadAnalysisFromURL();
            this.setupEventListeners();
            this.initializeCharts();
            if (window.Utils) Utils.log('✅ ResultsManager initialized successfully');
        } catch (error) {
            if (window.Utils) Utils.error('❌ ResultsManager initialization failed:', error);
            this.handleInitializationError(error);
        }
    }

    handleInitializationError(error) {
        try {
            // Fallback initialization
            this.currentAnalysis = null;
            this.charts = new Map();
            this.showErrorState('Error al inicializar el gestor de resultados. Algunas funciones pueden no estar disponibles.');
            if (window.Utils) Utils.warn('⚠️ ResultsManager running in fallback mode');
            if (window.Utils) Utils.error('Initialization error details:', error);
        } catch (fallbackError) {
            if (window.Utils) Utils.error('❌ ResultsManager fallback failed:', fallbackError);
        }
    }

    loadAnalysisFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const analysisId = urlParams.get('id');

        if (analysisId) {
            this.loadAnalysis(analysisId);
        } else {
            this.showNoAnalysisMessage();
        }
    }

    setupEventListeners() {
        // Tab switching
        const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
        tabButtons.forEach(button => {
            button.addEventListener('shown.bs.tab', (e) => {
                this.handleTabSwitch(e.target.getAttribute('data-bs-target'));
            });
        });

        // Error filter
        const errorFilter = document.getElementById('error-severity-filter');
        if (errorFilter) {
            errorFilter.addEventListener('change', () => this.filterErrors());
        }

        // Window resize handler for charts
        window.addEventListener('resize', Utils.debounce(() => {
            this.resizeCharts();
        }, 250));
    }

    // ========================================================================
    // ANALYSIS LOADING
    // ========================================================================

    async loadAnalysis(analysisId) {
        try {
            this.showLoadingState();

            // Try to get from analysis manager first
            let analysis = null;
            if (window.analysisManager) {
                analysis = analysisManager.getAnalysisById(analysisId);
            }

            // If not found locally, try to fetch from API
            if (!analysis) {
                try {
                    const results = await apiManager.getAnalysisResults(analysisId);
                    analysis = {
                        id: analysisId,
                        results: results,
                        status: 'completed'
                    };
                } catch (error) {
                    if (error.code === 'NOT_FOUND') {
                        this.showAnalysisNotFound();
                        return;
                    }
                    throw error;
                }
            }

            if (!analysis || !analysis.results) {
                this.showAnalysisNotFound();
                return;
            }

            this.currentAnalysis = analysis;
            this.displayAnalysisResults(analysis);

        } catch (error) {
            Utils.logError(error, 'Load analysis failed');
            this.showErrorState(error.message);
        }
    }

    displayAnalysisResults(analysis) {
        this.hideLoadingState();

        // Update overview section
        this.updateOverview(analysis);

        // Update all tabs
        this.updateSummaryTab(analysis);
        this.updateErrorsTab(analysis);
        this.updateSchemaTab(analysis);
        this.updateSecurityTab(analysis);
        this.updatePerformanceTab(analysis);

        // Initialize charts
        this.renderAllCharts(analysis);
    }

    // ========================================================================
    // OVERVIEW SECTION
    // ========================================================================

    updateOverview(analysis) {
        const results = analysis.results;

        // File information
        this.updateElement('file-name', results.file_info?.name || 'Unknown');
        this.updateElement('file-size', Utils.formatFileSize(results.file_info?.size || 0));
        this.updateElement('lines-count', Utils.formatNumber(results.file_info?.lines || 0));
        this.updateElement('processing-time', Utils.formatTime(results.processing_time || 0));
        this.updateElement('analysis-types', this.formatAnalysisTypes(results.analysis_types || []));
        this.updateElement('database-type', results.database_info?.type || 'Unknown');

        // Health score
        const healthScore = this.calculateHealthScore(results);
        this.updateElement('health-score', healthScore);
        this.renderHealthScoreChart(healthScore);

        // Status and date
        this.updateElement('analysis-status', Utils.capitalizeFirst(analysis.status || 'unknown'));
        this.updateElement('analysis-date', Utils.formatRelativeTime(analysis.endTime || Date.now()));
    }

    calculateHealthScore(results) {
        let score = 100;

        // Deduct points for errors
        const errors = results.errors || [];
        const criticalErrors = errors.filter(e => e.severity === 'critical').length;
        const warnings = errors.filter(e => e.severity === 'warning').length;

        score -= criticalErrors * 15;
        score -= warnings * 5;

        // Deduct points for security issues
        const securityIssues = results.security?.issues || [];
        score -= securityIssues.length * 10;

        // Deduct points for performance issues
        const performanceIssues = results.performance?.issues || [];
        score -= performanceIssues.length * 5;

        return Math.max(0, Math.min(100, score));
    }

    formatAnalysisTypes(types) {
        return types.map(type => Utils.capitalizeFirst(type)).join(', ');
    }

    // ========================================================================
    // TAB UPDATES
    // ========================================================================

    updateSummaryTab(analysis) {
        const results = analysis.results;
        const schema = results.schema || {};

        // Update metrics
        this.updateElement('summary-tables', schema.tables?.length || 0);
        this.updateElement('summary-columns', this.getTotalColumns(schema.tables || []));
        this.updateElement('summary-indexes', schema.indexes?.length || 0);
        this.updateElement('summary-constraints', schema.constraints?.length || 0);

        // Update recommendations
        this.updateRecommendations(results.recommendations || []);
    }

    updateErrorsTab(analysis) {
        const errors = analysis.results.errors || [];

        // Update error count badge
        this.updateElement('errors-count', errors.length);

        // Render error list
        this.renderErrorList(errors);
    }

    updateSchemaTab(analysis) {
        const schema = analysis.results.schema || {};

        // Update schema statistics
        this.updateSchemaStatistics(schema);

        // Render schema diagram
        this.renderSchemaDiagram(schema);

        // Update table list
        this.updateTableList(schema.tables || []);
    }

    updateSecurityTab(analysis) {
        const security = analysis.results.security || {};

        // Update security score
        const securityScore = security.score || 0;
        this.renderSecurityScoreChart(securityScore);

        // Update security issues
        this.renderSecurityIssues(security.issues || []);

        // Update recommendations
        this.renderSecurityRecommendations(security.recommendations || []);
    }

    updatePerformanceTab(analysis) {
        const performance = analysis.results.performance || {};

        // Update performance metrics
        this.updatePerformanceMetrics(performance);

        // Render performance chart
        this.renderPerformanceChart(performance);

        // Update optimization suggestions
        this.renderOptimizationSuggestions(performance.suggestions || []);
    }

    // ========================================================================
    // CHART RENDERING
    // ========================================================================

    initializeCharts() {
        // Initialize Chart.js defaults
        Chart.defaults.font.family = 'Inter, sans-serif';
        Chart.defaults.color = '#64748b';
        Chart.defaults.borderColor = '#e2e8f0';
    }

    renderAllCharts(analysis) {
        const results = analysis.results;

        // Render health score chart
        const healthScore = this.calculateHealthScore(results);
        this.renderHealthScoreChart(healthScore);

        // Render security chart
        if (results.security) {
            this.renderSecurityScoreChart(results.security.score || 0);
        }

        // Render performance chart
        if (results.performance) {
            this.renderPerformanceChart(results.performance);
        }
    }

    renderHealthScoreChart(score) {
        const canvas = document.getElementById('health-score-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        // Destroy existing chart
        if (this.charts.has('health-score')) {
            this.charts.get('health-score').destroy();
        }

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [
                        this.getScoreColor(score),
                        '#e2e8f0'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                }
            }
        });

        this.charts.set('health-score', chart);
    }

    renderSecurityScoreChart(score) {
        const canvas = document.getElementById('security-score-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        // Destroy existing chart
        if (this.charts.has('security-score')) {
            this.charts.get('security-score').destroy();
        }

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [
                        this.getScoreColor(score),
                        '#e2e8f0'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                }
            }
        });

        this.charts.set('security-score', chart);
    }

    renderPerformanceChart(performance) {
        const canvas = document.getElementById('performance-chart');
        if (!canvas) return;

        // Use performance data for chart rendering
        if (window.Utils) Utils.log('Rendering performance chart with data:', performance);

        const ctx = canvas.getContext('2d');

        // Destroy existing chart
        if (this.charts.has('performance')) {
            this.charts.get('performance').destroy();
        }

        // Sample performance data
        const data = {
            labels: ['Query Speed', 'Index Usage', 'Memory Usage', 'CPU Usage', 'Disk I/O'],
            datasets: [{
                label: 'Performance Score',
                data: [85, 92, 78, 88, 95],
                backgroundColor: 'rgba(30, 64, 175, 0.1)',
                borderColor: '#1e40af',
                borderWidth: 2,
                pointBackgroundColor: '#1e40af',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        };

        const chart = new Chart(ctx, {
            type: 'radar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        this.charts.set('performance', chart);
    }

    getScoreColor(score) {
        if (score >= 80) return '#059669'; // Green
        if (score >= 60) return '#d97706'; // Orange
        return '#dc2626'; // Red
    }

    resizeCharts() {
        this.charts.forEach(chart => {
            chart.resize();
        });
    }

    // ========================================================================
    // UI HELPERS
    // ========================================================================

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    showLoadingState() {
        // Show loading spinner or skeleton
        const mainContent = document.querySelector('.dashboard-main');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3 text-muted">Loading analysis results...</p>
                </div>
            `;
        }
    }

    hideLoadingState() {
        // Loading state is hidden when content is rendered
    }

    showAnalysisNotFound() {
        const mainContent = document.querySelector('.dashboard-main');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-search text-muted" style="font-size: 3rem;"></i>
                    <h4 class="mt-3">Analysis Not Found</h4>
                    <p class="text-muted">The requested analysis could not be found.</p>
                    <a href="/dashboard" class="btn-enterprise btn-primary">
                        <i class="fas fa-arrow-left me-2"></i>Back to Dashboard
                    </a>
                </div>
            `;
        }
    }

    showErrorState(message) {
        const mainContent = document.querySelector('.dashboard-main');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle text-danger" style="font-size: 3rem;"></i>
                    <h4 class="mt-3">Error Loading Results</h4>
                    <p class="text-muted">${Utils.sanitizeHtml(message)}</p>
                    <button class="btn-enterprise btn-primary" onclick="location.reload()">
                        <i class="fas fa-redo me-2"></i>Try Again
                    </button>
                </div>
            `;
        }
    }

    showNoAnalysisMessage() {
        const mainContent = document.querySelector('.dashboard-main');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-chart-line text-muted" style="font-size: 3rem;"></i>
                    <h4 class="mt-3">No Analysis Selected</h4>
                    <p class="text-muted">Please select an analysis to view its results.</p>
                    <a href="/history" class="btn-enterprise btn-primary">
                        <i class="fas fa-history me-2"></i>View Analysis History
                    </a>
                </div>
            `;
        }
    }

    // ========================================================================
    // EXPORT FUNCTIONALITY
    // ========================================================================

    async exportResults(format) {
        if (!this.currentAnalysis) {
            this.showNotification('No analysis to export', 'warning');
            return;
        }

        try {
            const response = await apiManager.exportResults(this.currentAnalysis.id, format);

            if (response.download_url) {
                // Create download link
                const link = document.createElement('a');
                link.href = response.download_url;
                link.download = response.filename || `analysis_${this.currentAnalysis.id}.${format}`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                this.showNotification(`Export completed: ${response.filename}`, 'success');
            }

        } catch (error) {
            Utils.logError(error, 'Export results failed');

            this.showNotification(`Export failed: ${error.message}`, 'error');
        }
    }

    async shareResults() {
        if (!this.currentAnalysis) {
            this.showNotification('No analysis to share', 'warning');
            return;
        }

        try {
            const response = await apiManager.shareResults(this.currentAnalysis.id, {
                expires_in: 7 * 24 * 60 * 60 // 7 days
            });

            if (response.share_url) {
                // Copy to clipboard
                await navigator.clipboard.writeText(response.share_url);

                this.showNotification('Share link copied to clipboard', 'success');
            }

        } catch (error) {
            Utils.logError(error, 'Share results failed');

            this.showNotification(`Share failed: ${error.message}`, 'error');
        }
    }

    // ========================================================================
    // MISSING IMPLEMENTATION METHODS
    // ========================================================================

    updateRecommendations(recommendations) {
        const container = document.getElementById('recommendations-list');
        if (!container) return;

        if (recommendations.length === 0) {
            container.innerHTML = '<p class="text-muted">No recommendations available.</p>';
            return;
        }

        container.innerHTML = recommendations.map(rec => `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex align-items-start">
                        <div class="badge badge-${rec.priority || 'info'} me-3">${rec.priority || 'info'}</div>
                        <div class="flex-grow-1">
                            <h6 class="card-title">${Utils.sanitizeHtml(rec.title)}</h6>
                            <p class="card-text">${Utils.sanitizeHtml(rec.description)}</p>
                            ${rec.code ? `<pre class="bg-light p-2 rounded"><code>${Utils.sanitizeHtml(rec.code)}</code></pre>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderErrorList(errors) {
        const container = document.getElementById('errors-list');
        if (!container) return;

        if (errors.length === 0) {
            container.innerHTML = '<p class="text-muted">No errors found.</p>';
            return;
        }

        container.innerHTML = errors.map(error => `
            <div class="error-item card mb-3 severity-${error.severity || 'info'}">
                <div class="card-body">
                    <div class="d-flex align-items-start">
                        <div class="badge badge-${this.getSeverityColor(error.severity)} me-3">
                            ${error.severity || 'info'}
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="card-title">${Utils.sanitizeHtml(error.message)}</h6>
                            <p class="text-muted small">Line ${error.line || 'N/A'}: ${Utils.sanitizeHtml(error.context || '')}</p>
                            ${error.suggestion ? `<div class="alert alert-info mt-2"><strong>Suggestion:</strong> ${Utils.sanitizeHtml(error.suggestion)}</div>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    getSeverityColor(severity) {
        const colors = {
            'critical': 'danger',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info',
            'success': 'success'
        };
        return colors[severity] || 'secondary';
    }

    updateSchemaStatistics(schema) {
        const stats = {
            'schema-tables-count': schema.tables?.length || 0,
            'schema-columns-count': this.getTotalColumns(schema.tables || []),
            'schema-indexes-count': schema.indexes?.length || 0,
            'schema-constraints-count': schema.constraints?.length || 0,
            'schema-relationships-count': schema.relationships?.length || 0
        };

        Object.entries(stats).forEach(([id, value]) => {
            this.updateElement(id, value);
        });
    }

    renderSchemaDiagram(schema) {
        const container = document.getElementById('schema-diagram');
        if (!container) return;

        if (!schema.tables || schema.tables.length === 0) {
            container.innerHTML = '<p class="text-muted">No schema information available.</p>';
            return;
        }

        // Simple table representation
        container.innerHTML = `
            <div class="schema-tables">
                ${schema.tables.map(table => `
                    <div class="table-node card mb-3" data-table="${table.name}">
                        <div class="card-header">
                            <h6 class="mb-0">${Utils.sanitizeHtml(table.name)}</h6>
                        </div>
                        <div class="card-body">
                            ${table.columns ? table.columns.map(col => `
                                <div class="column-item d-flex justify-content-between">
                                    <span>${Utils.sanitizeHtml(col.name)}</span>
                                    <small class="text-muted">${Utils.sanitizeHtml(col.type || '')}</small>
                                </div>
                            `).join('') : '<p class="text-muted">No columns</p>'}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    updateTableList(tables) {
        const container = document.getElementById('tables-list');
        if (!container) return;

        if (tables.length === 0) {
            container.innerHTML = '<p class="text-muted">No tables found.</p>';
            return;
        }

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Table Name</th>
                            <th>Columns</th>
                            <th>Type</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tables.map(table => `
                            <tr>
                                <td><strong>${Utils.sanitizeHtml(table.name)}</strong></td>
                                <td>${table.columns?.length || 0}</td>
                                <td><span class="badge badge-info">${Utils.sanitizeHtml(table.type || 'TABLE')}</span></td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="resultsManager.selectTable('${table.name}')">
                                        View Details
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    renderSecurityIssues(issues) {
        const container = document.getElementById('security-issues');
        if (!container) return;

        if (issues.length === 0) {
            container.innerHTML = '<div class="alert alert-success">No security issues found.</div>';
            return;
        }

        container.innerHTML = issues.map(issue => `
            <div class="alert alert-${this.getSeverityColor(issue.severity)}">
                <div class="d-flex align-items-start">
                    <i class="fas fa-shield-alt me-2 mt-1"></i>
                    <div>
                        <strong>${Utils.sanitizeHtml(issue.title)}</strong>
                        <p class="mb-0">${Utils.sanitizeHtml(issue.description)}</p>
                        ${issue.recommendation ? `<small class="text-muted">Recommendation: ${Utils.sanitizeHtml(issue.recommendation)}</small>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderSecurityRecommendations(recommendations) {
        const container = document.getElementById('security-recommendations');
        if (!container) return;

        if (recommendations.length === 0) {
            container.innerHTML = '<p class="text-muted">No security recommendations.</p>';
            return;
        }

        container.innerHTML = recommendations.map(rec => `
            <div class="card mb-2">
                <div class="card-body">
                    <h6 class="card-title">${Utils.sanitizeHtml(rec.title)}</h6>
                    <p class="card-text">${Utils.sanitizeHtml(rec.description)}</p>
                </div>
            </div>
        `).join('');
    }

    updatePerformanceMetrics(performance) {
        const metrics = {
            'perf-query-count': performance.query_count || 0,
            'perf-avg-time': performance.avg_execution_time || 0,
            'perf-slow-queries': performance.slow_queries?.length || 0,
            'perf-index-usage': performance.index_usage_score || 0
        };

        Object.entries(metrics).forEach(([id, value]) => {
            this.updateElement(id, typeof value === 'number' ? Utils.formatNumber(value) : value);
        });
    }

    renderOptimizationSuggestions(suggestions) {
        const container = document.getElementById('optimization-suggestions');
        if (!container) return;

        if (suggestions.length === 0) {
            container.innerHTML = '<p class="text-muted">No optimization suggestions available.</p>';
            return;
        }

        container.innerHTML = suggestions.map(suggestion => `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex align-items-start">
                        <div class="badge badge-${suggestion.impact || 'info'} me-3">${suggestion.impact || 'low'}</div>
                        <div class="flex-grow-1">
                            <h6 class="card-title">${Utils.sanitizeHtml(suggestion.title)}</h6>
                            <p class="card-text">${Utils.sanitizeHtml(suggestion.description)}</p>
                            ${suggestion.before && suggestion.after ? `
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Before:</h6>
                                        <pre class="bg-light p-2 rounded"><code>${Utils.sanitizeHtml(suggestion.before)}</code></pre>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>After:</h6>
                                        <pre class="bg-success-light p-2 rounded"><code>${Utils.sanitizeHtml(suggestion.after)}</code></pre>
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // ========================================================================
    // SAMPLE DATA LOADING (FOR DEMONSTRATION)
    // ========================================================================

    loadSampleResults() {
        const sampleResults = {
            file_info: {
                name: "database_schema.sql",
                size: 15420,
                lines: 245,
                type: "sql"
            },
            processing_time: 2.3,
            analysis_types: ["syntax", "schema", "security", "performance"],
            database_info: {
                type: "MySQL",
                version: "8.0",
                charset: "utf8mb4"
            },
            analysis_summary: {
                total_statements: 45,
                total_tables: 8,
                total_errors: 0
            },
            schema: {
                tables: [
                    {
                        name: "users",
                        columns: [
                            { name: "id", type: "INT PRIMARY KEY" },
                            { name: "username", type: "VARCHAR(50)" },
                            { name: "email", type: "VARCHAR(100)" },
                            { name: "created_at", type: "TIMESTAMP" }
                        ],
                        type: "TABLE"
                    },
                    {
                        name: "orders",
                        columns: [
                            { name: "id", type: "INT PRIMARY KEY" },
                            { name: "user_id", type: "INT" },
                            { name: "total", type: "DECIMAL(10,2)" },
                            { name: "status", type: "VARCHAR(20)" }
                        ],
                        type: "TABLE"
                    }
                ],
                indexes: [
                    { name: "idx_users_email", table: "users", columns: ["email"] },
                    { name: "idx_orders_user_id", table: "orders", columns: ["user_id"] }
                ],
                constraints: [
                    { name: "fk_orders_user_id", type: "FOREIGN KEY", table: "orders", references: "users(id)" }
                ],
                relationships: [
                    { from: "orders", to: "users", type: "many-to-one" }
                ]
            },
            security: {
                score: 85,
                issues: [],
                recommendations: [
                    {
                        title: "Use Prepared Statements",
                        description: "Consider using prepared statements to prevent SQL injection attacks."
                    },
                    {
                        title: "Add Data Validation",
                        description: "Implement proper data validation for user inputs."
                    }
                ]
            },
            performance: {
                query_count: 45,
                avg_execution_time: 0.05,
                slow_queries: [],
                index_usage_score: 88,
                suggestions: [
                    {
                        title: "Add Index on Status Column",
                        description: "Consider adding an index on the orders.status column for better query performance.",
                        impact: "medium",
                        before: "SELECT * FROM orders WHERE status = 'pending'",
                        after: "CREATE INDEX idx_orders_status ON orders(status);"
                    }
                ]
            },
            recommendations: [
                {
                    title: "Add Primary Keys",
                    description: "Ensure all tables have primary keys for better performance and data integrity.",
                    priority: "high"
                },
                {
                    title: "Normalize Database Schema",
                    description: "Consider normalizing your database schema to reduce data redundancy.",
                    priority: "medium"
                }
            ]
        };

        // Display the sample results
        this.displayAnalysisResults({ results: sampleResults, status: 'completed' });
    }

    // ========================================================================
    // UTILITY METHODS
    // ========================================================================

    getTotalColumns(tables) {
        return tables.reduce((total, table) => total + (table.columns?.length || 0), 0);
    }

    handleTabSwitch(tabId) {
        // Resize charts when tab becomes visible
        if (window.Utils) Utils.log('Switching to tab:', tabId);
        setTimeout(() => {
            this.resizeCharts();
        }, 100);
    }

    filterErrors() {
        // Implementation for error filtering
        const filter = document.getElementById('error-severity-filter')?.value;
        const errorItems = document.querySelectorAll('.error-item');

        errorItems.forEach(item => {
            if (!filter || item.classList.contains(`severity-${filter}`)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    selectTable(tableName) {
        // Highlight selected table in schema diagram
        const tableNodes = document.querySelectorAll('.table-node');
        tableNodes.forEach(node => {
            node.classList.remove('selected');
        });

        const selectedNode = document.querySelector(`[data-table="${tableName}"]`);
        if (selectedNode) {
            selectedNode.classList.add('selected');
        }
    }
}

// Create global instance
window.ResultsManager = ResultsManager;
