/**
 * PERFORMANCE OPTIMIZATION JAVASCRIPT
 * Interactive performance analysis and optimization suggestions
 */

class PerformanceOptimization {
    constructor() {
        this.currentAnalysisId = null;
        this.performanceIssues = [];
        this.performanceChart = null;
        this.initializeEventListeners();
        this.initializeUpload();
    }

    initializeEventListeners() {
        // File upload events
        const uploadArea = document.getElementById('performance-upload-area');
        const fileInput = document.getElementById('performance-file-input');
        const removeBtn = document.getElementById('performance-remove-file');
        const startBtn = document.getElementById('start-performance-analysis');

        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => fileInput.click());
            uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
            uploadArea.addEventListener('drop', this.handleDrop.bind(this));
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }

        if (removeBtn) {
            removeBtn.addEventListener('click', this.removeFile.bind(this));
        }

        if (startBtn) {
            startBtn.addEventListener('click', this.startPerformanceAnalysis.bind(this));
        }

        // Filter events
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', this.filterIssues.bind(this));
        });
    }

    initializeUpload() {
        const uploadArea = document.getElementById('performance-upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('dragenter', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                if (!uploadArea.contains(e.relatedTarget)) {
                    uploadArea.classList.remove('dragover');
                }
            });
        }
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    }

    handleDrop(e) {
        e.preventDefault();
        const uploadArea = document.getElementById('performance-upload-area');
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    processFile(file) {
        // Validate file
        if (!this.validateFile(file)) {
            return;
        }

        // Show file info
        this.showFileInfo(file);
        
        // Enable analysis button
        const startBtn = document.getElementById('start-performance-analysis');
        if (startBtn) {
            startBtn.disabled = false;
        }
    }

    validateFile(file) {
        const maxSize = 100 * 1024 * 1024; // 100MB
        const allowedTypes = ['.sql', '.txt', '.ddl', '.dml'];
        
        if (file.size > maxSize) {
            this.showError('File size exceeds 100MB limit');
            return false;
        }

        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(extension)) {
            this.showError('Invalid file type. Please upload SQL files only.');
            return false;
        }

        return true;
    }

    showFileInfo(file) {
        const uploadArea = document.getElementById('performance-upload-area');
        const fileInfo = document.getElementById('performance-file-info');
        
        if (uploadArea && fileInfo) {
            uploadArea.style.display = 'none';
            fileInfo.style.display = 'flex';
            
            const fileName = fileInfo.querySelector('.file-name');
            const fileSize = fileInfo.querySelector('.file-size');
            
            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = this.formatFileSize(file.size);
        }
    }

    removeFile() {
        const uploadArea = document.getElementById('performance-upload-area');
        const fileInfo = document.getElementById('performance-file-info');
        const fileInput = document.getElementById('performance-file-input');
        const startBtn = document.getElementById('start-performance-analysis');
        
        if (uploadArea) uploadArea.style.display = 'block';
        if (fileInfo) fileInfo.style.display = 'none';
        if (fileInput) fileInput.value = '';
        if (startBtn) startBtn.disabled = true;
        
        this.hideResults();
    }

    async startPerformanceAnalysis() {
        const fileInput = document.getElementById('performance-file-input');
        if (!fileInput || !fileInput.files[0]) {
            this.showError('Please select a file first');
            return;
        }

        // Show progress
        this.showProgress();
        
        // Get analysis options
        const options = this.getAnalysisOptions();
        
        try {
            // Create form data
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('options', JSON.stringify(options));

            // Start analysis
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.currentAnalysisId = result.data.analysis_result.id;
                await this.loadPerformanceResults();
            } else {
                this.showError(result.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Performance analysis error:', error);
            this.showError('Network error occurred');
        } finally {
            this.hideProgress();
        }
    }

    getAnalysisOptions() {
        return {
            query_optimization: document.getElementById('query-optimization')?.checked || false,
            index_analysis: document.getElementById('index-analysis')?.checked || false,
            bottleneck_detection: document.getElementById('bottleneck-detection')?.checked || false,
            execution_plan: document.getElementById('execution-plan')?.checked || false,
            resource_estimation: document.getElementById('resource-estimation')?.checked || false,
            database_type: document.getElementById('performance-db-type')?.value || 'auto'
        };
    }

    async loadPerformanceResults() {
        if (!this.currentAnalysisId) return;

        try {
            const response = await fetch(`/api/analysis/${this.currentAnalysisId}/performance`);
            const result = await response.json();
            
            if (result.success) {
                this.displayPerformanceResults(result.data);
            } else {
                this.showError(result.error || 'Failed to load performance results');
            }
        } catch (error) {
            console.error('Load performance results error:', error);
            this.showError('Failed to load performance results');
        }
    }

    displayPerformanceResults(data) {
        this.performanceIssues = data.issues || [];
        
        // Hide empty state and show results
        this.hideEmptyState();
        this.showResults();
        
        // Update overview
        this.updatePerformanceOverview(data);
        
        // Create performance chart
        this.createPerformanceChart(data);
        
        // Display performance issues
        this.displayPerformanceIssues();
        
        // Show optimization suggestions
        this.displayOptimizationSuggestions(data.optimization_suggestions || []);
        
        // Show index recommendations
        this.displayIndexRecommendations(data.index_recommendations || []);
        
        // Show execution plan
        this.displayExecutionPlan(data.execution_plan || []);
    }

    updatePerformanceOverview(data) {
        // Update overview cards
        document.getElementById('processing-time').textContent = 
            (data.processing_time || 0).toFixed(3) + 's';
        document.getElementById('memory-usage').textContent = 
            Math.round(data.memory_usage || 0) + 'MB';
        document.getElementById('query-complexity').textContent = 
            data.complexity_level || 'Low';
        document.getElementById('optimization-score').textContent = 
            data.optimization_score || 100;
        
        // Update header metrics
        document.getElementById('avg-processing-time').textContent = 
            (data.processing_time || 0).toFixed(1) + 's';
        document.getElementById('optimization-potential').textContent = 
            Math.round(data.optimization_potential || 0) + '%';
        document.getElementById('performance-score').textContent = 
            data.performance_score || 100;
    }

    createPerformanceChart(data) {
        const ctx = document.getElementById('performance-chart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.performanceChart) {
            this.performanceChart.destroy();
        }

        const chartData = {
            labels: ['Query Time', 'Memory Usage', 'CPU Usage', 'I/O Operations', 'Network'],
            datasets: [{
                label: 'Current Performance',
                data: [
                    data.query_time || 0,
                    data.memory_usage || 0,
                    data.cpu_usage || 0,
                    data.io_operations || 0,
                    data.network_usage || 0
                ],
                backgroundColor: 'rgba(40, 167, 69, 0.2)',
                borderColor: 'rgba(40, 167, 69, 1)',
                borderWidth: 2,
                fill: true
            }, {
                label: 'Optimal Performance',
                data: [100, 100, 100, 100, 100],
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                borderColor: 'rgba(255, 193, 7, 1)',
                borderWidth: 1,
                borderDash: [5, 5],
                fill: false
            }]
        };

        this.performanceChart = new Chart(ctx, {
            type: 'radar',
            data: chartData,
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
                        position: 'bottom'
                    }
                }
            }
        });
    }

    displayPerformanceIssues() {
        const issuesList = document.getElementById('performance-issues-list');
        if (!issuesList) return;

        if (this.performanceIssues.length === 0) {
            issuesList.innerHTML = `
                <div class="no-issues">
                    <i class="fas fa-tachometer-alt"></i>
                    <h4>No Performance Issues Found</h4>
                    <p>Your SQL queries are well optimized!</p>
                </div>
            `;
            return;
        }

        issuesList.innerHTML = this.performanceIssues.map(issue => `
            <div class="issue-item" data-impact="${issue.impact}">
                <div class="issue-header">
                    <h4 class="issue-title">${issue.issue_type.replace(/_/g, ' ').toUpperCase()}</h4>
                    <span class="issue-impact impact-${issue.impact}">${issue.impact}</span>
                </div>
                <div class="issue-description">
                    ${issue.description}
                </div>
                <div class="issue-meta">
                    <span>Line: ${issue.line_number}</span>
                    <span>Impact: ${issue.impact}</span>
                    ${issue.estimated_improvement ? `<span>Improvement: ${issue.estimated_improvement}</span>` : ''}
                </div>
                <div class="issue-actions">
                    <button class="btn btn-sm btn-secondary" onclick="viewIssueDetails('${issue.id}')">
                        <i class="fas fa-eye"></i> Details
                    </button>
                    ${issue.suggestion ? `
                        <button class="btn btn-sm btn-primary" onclick="applyOptimization('${issue.id}')">
                            <i class="fas fa-magic"></i> Optimize
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    displayOptimizationSuggestions(suggestions) {
        const suggestionsList = document.getElementById('optimization-suggestions-list');
        if (!suggestionsList) return;

        if (suggestions.length === 0) {
            suggestionsList.innerHTML = `
                <div class="no-suggestions">
                    <p>No specific optimization suggestions at this time.</p>
                </div>
            `;
            return;
        }

        suggestionsList.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item">
                <h5 class="suggestion-title">${suggestion.title || 'Optimization Suggestion'}</h5>
                <div class="suggestion-description">
                    ${suggestion.description}
                </div>
                ${suggestion.benefit ? `
                    <div class="suggestion-benefit">
                        <strong>Expected Benefit:</strong> ${suggestion.benefit}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    displayIndexRecommendations(recommendations) {
        const recommendationsList = document.getElementById('index-recommendations-list');
        if (!recommendationsList) return;

        if (recommendations.length === 0) {
            recommendationsList.innerHTML = `
                <div class="no-recommendations">
                    <p>No index recommendations at this time.</p>
                </div>
            `;
            return;
        }

        recommendationsList.innerHTML = recommendations.map(rec => `
            <div class="recommendation-item">
                <h5 class="recommendation-title">${rec.table_name} - ${rec.index_type} Index</h5>
                <div class="recommendation-code">
                    ${rec.sql_statement}
                </div>
                <div class="recommendation-impact">
                    <strong>Expected Impact:</strong> ${rec.impact_description}
                </div>
            </div>
        `).join('');
    }

    displayExecutionPlan(executionPlan) {
        const planContainer = document.getElementById('execution-plan-container');
        if (!planContainer) return;

        if (executionPlan.length === 0) {
            planContainer.innerHTML = `
                <div class="no-execution-plan">
                    <p>No execution plan available.</p>
                </div>
            `;
            return;
        }

        planContainer.innerHTML = executionPlan.map((step, index) => `
            <div class="execution-step">
                <div class="step-number">${index + 1}</div>
                <div class="step-details">
                    <div class="step-operation">${step.operation}</div>
                    <div class="step-cost">Cost: ${step.cost || 'N/A'}</div>
                </div>
            </div>
        `).join('');
    }

    filterIssues(e) {
        const filter = e.target.dataset.filter;
        const issueItems = document.querySelectorAll('.issue-item');
        
        // Update active filter button
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        
        // Filter issues
        issueItems.forEach(item => {
            if (filter === 'all' || item.dataset.impact === filter) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    showProgress() {
        const progress = document.getElementById('performance-analysis-progress');
        const startBtn = document.getElementById('start-performance-analysis');
        
        if (progress) progress.style.display = 'block';
        if (startBtn) startBtn.disabled = true;
        
        this.animateProgress();
    }

    hideProgress() {
        const progress = document.getElementById('performance-analysis-progress');
        const startBtn = document.getElementById('start-performance-analysis');
        
        if (progress) progress.style.display = 'none';
        if (startBtn) startBtn.disabled = false;
    }

    animateProgress() {
        const progressFill = document.getElementById('performance-progress-fill');
        const progressText = document.getElementById('performance-progress-text');
        const progressPercent = document.getElementById('performance-progress-percent');
        
        const steps = [
            { percent: 20, text: 'Parsing SQL queries...' },
            { percent: 40, text: 'Analyzing query structure...' },
            { percent: 60, text: 'Detecting performance issues...' },
            { percent: 80, text: 'Generating optimization suggestions...' },
            { percent: 100, text: 'Finalizing analysis...' }
        ];
        
        let currentStep = 0;
        
        const updateProgress = () => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                if (progressFill) progressFill.style.width = step.percent + '%';
                if (progressText) progressText.textContent = step.text;
                if (progressPercent) progressPercent.textContent = step.percent + '%';
                currentStep++;
                setTimeout(updateProgress, 800);
            }
        };
        
        updateProgress();
    }

    showResults() {
        const results = document.getElementById('performance-results');
        if (results) results.style.display = 'block';
    }

    hideResults() {
        const results = document.getElementById('performance-results');
        if (results) results.style.display = 'none';
    }

    showEmptyState() {
        const emptyState = document.getElementById('performance-empty-state');
        if (emptyState) emptyState.style.display = 'flex';
    }

    hideEmptyState() {
        const emptyState = document.getElementById('performance-empty-state');
        if (emptyState) emptyState.style.display = 'none';
    }

    showError(message) {
        // Create or update error notification
        let errorDiv = document.getElementById('performance-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'performance-error';
            errorDiv.className = 'error-notification';
            document.querySelector('.performance-optimization-container').appendChild(errorDiv);
        }
        
        errorDiv.innerHTML = `
            <div class="error-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        errorDiv.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (errorDiv) errorDiv.remove();
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Global functions for modal interactions
function viewIssueDetails(issueId) {
    const modal = document.getElementById('performance-issue-modal');
    const modalBody = document.getElementById('issue-modal-body');
    
    // Find issue data
    const issue = performanceOptimization.performanceIssues.find(i => i.id === issueId);
    if (!issue) return;
    
    modalBody.innerHTML = `
        <div class="issue-detail">
            <h4>${issue.issue_type.replace(/_/g, ' ').toUpperCase()}</h4>
            <div class="detail-section">
                <h5>Description</h5>
                <p>${issue.description}</p>
            </div>
            <div class="detail-section">
                <h5>Location</h5>
                <p>Line ${issue.line_number}</p>
            </div>
            <div class="detail-section">
                <h5>Impact Level</h5>
                <span class="issue-impact impact-${issue.impact}">${issue.impact}</span>
            </div>
            ${issue.suggestion ? `
                <div class="detail-section">
                    <h5>Optimization Suggestion</h5>
                    <p>${issue.suggestion}</p>
                </div>
            ` : ''}
            ${issue.estimated_improvement ? `
                <div class="detail-section">
                    <h5>Expected Improvement</h5>
                    <p>${issue.estimated_improvement}</p>
                </div>
            ` : ''}
        </div>
    `;
    
    modal.classList.add('show');
}

function closePerformanceIssueModal() {
    const modal = document.getElementById('performance-issue-modal');
    modal.classList.remove('show');
}

function applyOptimization() {
    // Implement optimization application logic
    console.log('Applying performance optimization...');
    closePerformanceIssueModal();
}

function exportPerformanceReport(format) {
    if (!performanceOptimization.currentAnalysisId) {
        performanceOptimization.showError('No analysis available for export');
        return;
    }
    
    const url = `/api/export/${performanceOptimization.currentAnalysisId}/${format}`;
    window.open(url, '_blank');
}

// Initialize performance optimization when DOM is loaded
let performanceOptimization;
document.addEventListener('DOMContentLoaded', () => {
    performanceOptimization = new PerformanceOptimization();
});
