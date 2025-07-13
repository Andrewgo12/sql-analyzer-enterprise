/* ============================================================================
   SQL ANALYZER ENTERPRISE - DASHBOARD MANAGER MODULE
   Integrates with the new modular JavaScript architecture
   ============================================================================ */

class DashboardManager {
    constructor() {
        this.stats = {
            totalFiles: 0,
            totalAnalyses: 0,
            successRate: 0,
            avgProcessingTime: 0
        };
        
        this.init();
    }
    
    // ========================================================================
    // INITIALIZATION
    // ========================================================================
    
    init() {
        this.loadDashboardData();
        this.setupEventListeners();
        this.updateStats();
        this.checkAuthentication();
        this.setupRealTimeUpdates();
    }
    
    checkAuthentication() {
        if (window.authManager && !authManager.isAuthenticated()) {
            window.location.href = '/';
            return;
        }
    }
    
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-stats');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshStats());
        }
        
        // Quick actions
        const quickActions = document.querySelectorAll('.quick-action');
        quickActions.forEach(action => {
            action.addEventListener('click', (e) => {
                const actionType = e.currentTarget.dataset.action;
                this.handleQuickAction(actionType);
            });
        });
        
        // Listen for upload and analysis events
        if (window.eventManager) {
            eventManager.on('upload-complete', () => this.handleUploadComplete());
            eventManager.on('analysis-complete', () => this.handleAnalysisComplete());
        }
    }
    
    setupRealTimeUpdates() {
        // Update stats every 30 seconds
        setInterval(() => {
            this.loadDashboardData();
            this.updateStats();
        }, 30000);
    }
    
    // ========================================================================
    // DATA LOADING
    // ========================================================================
    
    loadDashboardData() {
        // Load from localStorage for demo
        const uploadHistory = Utils.getStorage('sqlAnalyzer_uploadHistory', []);
        const analysisHistory = Utils.getStorage('sqlAnalyzer_analysisHistory', []);
        
        this.stats.totalFiles = uploadHistory.length;
        this.stats.totalAnalyses = analysisHistory.length;
        
        // Calculate success rate
        const successfulAnalyses = analysisHistory.filter(a => a.status === 'completed').length;
        this.stats.successRate = analysisHistory.length > 0 ? 
            Math.round((successfulAnalyses / analysisHistory.length) * 100) : 0;
        
        // Calculate average processing time
        const completedAnalyses = analysisHistory.filter(a => a.processingTime);
        if (completedAnalyses.length > 0) {
            const totalTime = completedAnalyses.reduce((sum, a) => sum + a.processingTime, 0);
            this.stats.avgProcessingTime = Math.round(totalTime / completedAnalyses.length / 1000); // Convert to seconds
        }
    }
    
    // ========================================================================
    // UI UPDATES
    // ========================================================================
    
    updateStats() {
        // Update stat cards with animation
        this.animateStatUpdate('files-count', this.stats.totalFiles);
        this.animateStatUpdate('analyses-count', this.stats.totalAnalyses);
        this.updateElement('success-rate', `${this.stats.successRate}%`);
        this.updateElement('avg-time', `${this.stats.avgProcessingTime}s`);
        
        // Update recent activity
        this.updateRecentActivity();
        
        // Update quick stats
        this.updateQuickStats();
        
        // Update system health
        this.updateSystemHealth();
    }
    
    animateStatUpdate(elementId, newValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const currentValue = parseInt(element.textContent) || 0;
        if (currentValue === newValue) return;
        
        const duration = 1000;
        const steps = 20;
        const stepValue = (newValue - currentValue) / steps;
        const stepDuration = duration / steps;
        
        let currentStep = 0;
        const timer = setInterval(() => {
            currentStep++;
            const value = Math.round(currentValue + (stepValue * currentStep));
            element.textContent = value;
            
            if (currentStep >= steps) {
                clearInterval(timer);
                element.textContent = newValue;
            }
        }, stepDuration);
    }
    
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    updateRecentActivity() {
        const analysisHistory = Utils.getStorage('sqlAnalyzer_analysisHistory', []);
        const recentAnalyses = analysisHistory.slice(0, 5);
        
        const activityList = document.getElementById('recent-activity-list');
        if (!activityList) return;
        
        if (recentAnalyses.length === 0) {
            activityList.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-2"></i>
                    <p>No recent activity</p>
                    <small>Upload a SQL file to get started</small>
                </div>
            `;
            return;
        }
        
        activityList.innerHTML = recentAnalyses.map(analysis => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas fa-${this.getStatusIcon(analysis.status)} ${this.getStatusColor(analysis.status)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${Utils.sanitizeHtml(analysis.fileName)}</div>
                    <div class="activity-meta">
                        <span class="status-badge status-${analysis.status}">${Utils.capitalizeFirst(analysis.status)}</span>
                        <span class="activity-time">${Utils.formatRelativeTime(analysis.timestamp)}</span>
                    </div>
                </div>
                <div class="activity-actions">
                    ${analysis.status === 'completed' ? 
                        `<button class="btn-sm btn-outline-primary" onclick="viewResults('${analysis.id}')" title="View Results">
                            <i class="fas fa-eye"></i>
                        </button>` : ''}
                    <button class="btn-sm btn-outline-secondary" onclick="downloadAnalysis('${analysis.id}')" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    updateQuickStats() {
        // Update progress indicators
        const successRateProgress = document.getElementById('success-rate-progress');
        if (successRateProgress) {
            successRateProgress.style.width = `${this.stats.successRate}%`;
            successRateProgress.setAttribute('aria-valuenow', this.stats.successRate);
        }
        
        // Update performance indicators
        this.updatePerformanceIndicators();
    }
    
    updateSystemHealth() {
        const statusIndicator = document.getElementById('system-status');
        if (statusIndicator) {
            // Simulate system health check
            const isHealthy = this.checkSystemHealth();
            
            if (isHealthy) {
                statusIndicator.textContent = 'Operational';
                statusIndicator.className = 'badge bg-success';
            } else {
                statusIndicator.textContent = 'Degraded';
                statusIndicator.className = 'badge bg-warning';
            }
        }
    }
    
    updatePerformanceIndicators() {
        // Update memory usage indicator
        const memoryUsage = Math.random() * 100; // Simulated
        const memoryElement = document.getElementById('memory-usage');
        if (memoryElement) {
            memoryElement.style.width = `${memoryUsage}%`;
            memoryElement.setAttribute('aria-valuenow', Math.round(memoryUsage));
        }
        
        // Update CPU usage indicator
        const cpuUsage = Math.random() * 100; // Simulated
        const cpuElement = document.getElementById('cpu-usage');
        if (cpuElement) {
            cpuElement.style.width = `${cpuUsage}%`;
            cpuElement.setAttribute('aria-valuenow', Math.round(cpuUsage));
        }
    }
    
    // ========================================================================
    // EVENT HANDLERS
    // ========================================================================
    
    handleUploadComplete() {
        this.loadDashboardData();
        this.updateStats();
        
        // Show success notification
        if (window.showNotification) {
            showNotification('File uploaded successfully! Analysis will begin shortly.', 'success');
        }
    }
    
    handleAnalysisComplete() {
        this.loadDashboardData();
        this.updateStats();
        
        // Update recent activity
        this.updateRecentActivity();
    }
    
    // ========================================================================
    // ACTIONS
    // ========================================================================
    
    handleQuickAction(actionType) {
        switch (actionType) {
            case 'new-analysis':
                this.triggerFileUpload();
                break;
            case 'view-history':
                if (window.navigationManager) {
                    navigationManager.navigateTo('/history');
                } else {
                    window.location.href = '/history';
                }
                break;
            case 'settings':
                if (window.navigationManager) {
                    navigationManager.navigateTo('/settings');
                } else {
                    window.location.href = '/settings';
                }
                break;
            case 'help':
                this.showHelp();
                break;
            case 'profile':
                if (window.navigationManager) {
                    navigationManager.navigateTo('/profile');
                } else {
                    window.location.href = '/profile';
                }
                break;
            default:
                if (window.Utils) Utils.log('Unknown action:', actionType);
        }
    }
    
    triggerFileUpload() {
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.click();
        } else {
            // Focus on dropzone
            const dropzone = document.getElementById('dropzone');
            if (dropzone) {
                dropzone.scrollIntoView({ behavior: 'smooth' });
                dropzone.classList.add('highlight');
                setTimeout(() => {
                    dropzone.classList.remove('highlight');
                }, 2000);
            }
        }
    }
    
    showHelp() {
        if (window.showModal) {
            showModal('helpModal');
        } else {
            // Fallback help content
            const helpContent = `
                <h5>SQL Analyzer Enterprise Help</h5>
                <p><strong>Getting Started:</strong></p>
                <ul>
                    <li>Drag and drop SQL files or click to browse</li>
                    <li>Supported formats: .sql, .txt, .text, .pdf</li>
                    <li>Maximum file size: 10GB</li>
                </ul>
                <p><strong>Features:</strong></p>
                <ul>
                    <li>SQL syntax analysis</li>
                    <li>Schema visualization</li>
                    <li>Security assessment</li>
                    <li>Performance optimization</li>
                    <li>PDF document analysis</li>
                </ul>
            `;
            
            if (window.alertDialog) {
                alertDialog(helpContent, { title: 'Help' });
            } else {
                alert('Help: Drag and drop SQL files to analyze them. Supported formats: .sql, .txt, .text, .pdf');
            }
        }
    }
    
    async refreshStats() {
        const refreshBtn = document.getElementById('refresh-stats');
        if (refreshBtn) {
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            refreshBtn.disabled = true;
        }
        
        try {
            // Check API health
            if (window.apiManager) {
                const isHealthy = await apiManager.healthCheck();
                if (!isHealthy) {
                    throw new Error('API health check failed');
                }
            }
            
            // Simulate API call delay
            await Utils.delay(1000);
            
            this.loadDashboardData();
            this.updateStats();
            
            if (window.showNotification) {
                showNotification('Dashboard statistics updated', 'success');
            }
            
        } catch (error) {
            Utils.logError(error, 'Dashboard refresh failed');
            
            if (window.showNotification) {
                showNotification('Failed to refresh dashboard statistics', 'error');
            }
        } finally {
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
                refreshBtn.disabled = false;
            }
        }
    }
    
    // ========================================================================
    // UTILITY METHODS
    // ========================================================================
    
    getStatusIcon(status) {
        const icons = {
            completed: 'check-circle',
            failed: 'times-circle',
            cancelled: 'ban',
            running: 'spinner fa-spin',
            pending: 'clock'
        };
        return icons[status] || 'question-circle';
    }
    
    getStatusColor(status) {
        const colors = {
            completed: 'text-success',
            failed: 'text-danger',
            cancelled: 'text-warning',
            running: 'text-primary',
            pending: 'text-info'
        };
        return colors[status] || 'text-muted';
    }
    
    checkSystemHealth() {
        // Simulate system health check
        const factors = [
            this.stats.successRate > 80,
            this.stats.avgProcessingTime < 60,
            navigator.onLine,
            !document.hidden
        ];
        
        return factors.filter(Boolean).length >= 3;
    }
}

// Global functions for dashboard
function viewResults(analysisId) {
    if (window.navigationManager) {
        navigationManager.navigateTo(`/results?id=${analysisId}`);
    } else {
        window.location.href = `/results?id=${analysisId}`;
    }
}

function downloadAnalysis(analysisId) {
    if (window.resultsManager) {
        resultsManager.exportResults('json');
    } else {
        if (window.Utils) Utils.log('Download analysis:', analysisId);
        if (window.showNotification) {
            showNotification('Download feature will be available soon', 'info');
        }
    }
}

function signOut() {
    if (window.authManager) {
        authManager.signOut().then(() => {
            if (window.navigationManager) {
                navigationManager.navigateTo('/');
            } else {
                window.location.href = '/';
            }
        }).catch(error => {
            Utils.logError(error, 'Sign out failed');
            // Force logout anyway
            localStorage.clear();
            window.location.href = '/';
        });
    } else {
        localStorage.clear();
        window.location.href = '/';
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});
