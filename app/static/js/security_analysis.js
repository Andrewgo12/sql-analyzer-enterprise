/**
 * SECURITY ANALYSIS JAVASCRIPT
 * Interactive security vulnerability scanning and risk assessment
 */

class SecurityAnalysis {
    constructor() {
        this.currentAnalysisId = null;
        this.vulnerabilities = [];
        this.securityScore = 100;
        this.initializeEventListeners();
        this.initializeUpload();
    }

    initializeEventListeners() {
        // File upload events
        const uploadArea = document.getElementById('security-upload-area');
        const fileInput = document.getElementById('security-file-input');
        const removeBtn = document.getElementById('security-remove-file');
        const startBtn = document.getElementById('start-security-scan');

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
            startBtn.addEventListener('click', this.startSecurityScan.bind(this));
        }

        // Filter events
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', this.filterVulnerabilities.bind(this));
        });
    }

    initializeUpload() {
        const uploadArea = document.getElementById('security-upload-area');
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
        const uploadArea = document.getElementById('security-upload-area');
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
        
        // Enable scan button
        const startBtn = document.getElementById('start-security-scan');
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
        const uploadArea = document.getElementById('security-upload-area');
        const fileInfo = document.getElementById('security-file-info');
        
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
        const uploadArea = document.getElementById('security-upload-area');
        const fileInfo = document.getElementById('security-file-info');
        const fileInput = document.getElementById('security-file-input');
        const startBtn = document.getElementById('start-security-scan');
        
        if (uploadArea) uploadArea.style.display = 'block';
        if (fileInfo) fileInfo.style.display = 'none';
        if (fileInput) fileInput.value = '';
        if (startBtn) startBtn.disabled = true;
        
        this.hideResults();
    }

    async startSecurityScan() {
        const fileInput = document.getElementById('security-file-input');
        if (!fileInput || !fileInput.files[0]) {
            this.showError('Please select a file first');
            return;
        }

        // Show progress
        this.showProgress();
        
        // Get scan options
        const options = this.getScanOptions();
        
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
                await this.loadSecurityResults();
            } else {
                this.showError(result.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Security scan error:', error);
            this.showError('Network error occurred');
        } finally {
            this.hideProgress();
        }
    }

    getScanOptions() {
        return {
            sql_injection_scan: document.getElementById('sql-injection-scan')?.checked || false,
            hardcoded_credentials: document.getElementById('hardcoded-credentials')?.checked || false,
            information_disclosure: document.getElementById('information-disclosure')?.checked || false,
            privilege_escalation: document.getElementById('privilege-escalation')?.checked || false,
            owasp_compliance: document.getElementById('owasp-compliance')?.checked || false
        };
    }

    async loadSecurityResults() {
        if (!this.currentAnalysisId) return;

        try {
            const response = await fetch(`/api/analysis/${this.currentAnalysisId}/security`);
            const result = await response.json();
            
            if (result.success) {
                this.displaySecurityResults(result.data);
            } else {
                this.showError(result.error || 'Failed to load security results');
            }
        } catch (error) {
            console.error('Load security results error:', error);
            this.showError('Failed to load security results');
        }
    }

    displaySecurityResults(data) {
        this.vulnerabilities = data.vulnerabilities || [];
        this.securityScore = data.security_score || 100;
        
        // Hide empty state and show results
        this.hideEmptyState();
        this.showResults();
        
        // Update overview
        this.updateSecurityOverview(data);
        
        // Update security score
        this.updateSecurityScore(data);
        
        // Display vulnerabilities
        this.displayVulnerabilities();
        
        // Update OWASP compliance
        this.updateOWASPCompliance(data);
        
        // Show recommendations
        this.displayRecommendations(data.recommendations || []);
    }

    updateSecurityOverview(data) {
        const severityCounts = data.severity_breakdown || {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
        };

        // Update counts
        document.getElementById('critical-count').textContent = severityCounts.critical;
        document.getElementById('high-count').textContent = severityCounts.high;
        document.getElementById('medium-count').textContent = severityCounts.medium;
        document.getElementById('low-count').textContent = severityCounts.low;
        
        // Update header stats
        document.getElementById('vulnerabilities-found').textContent = data.total_vulnerabilities || 0;
        document.getElementById('security-score').textContent = data.security_score || 100;
    }

    updateSecurityScore(data) {
        const scoreValue = document.getElementById('security-score-value');
        const scoreLevel = document.getElementById('security-score-level');
        const scoreDescription = document.getElementById('security-score-description');
        const scoreCircle = document.getElementById('security-score-circle');
        
        const score = data.security_score || 100;
        
        if (scoreValue) scoreValue.textContent = score;
        
        // Determine level and description
        let level, description, color;
        if (score >= 90) {
            level = 'Excellent';
            description = 'No significant security vulnerabilities detected';
            color = '#28a745';
        } else if (score >= 75) {
            level = 'Good';
            description = 'Minor security issues that should be addressed';
            color = '#ffc107';
        } else if (score >= 50) {
            level = 'Fair';
            description = 'Several security vulnerabilities need attention';
            color = '#fd7e14';
        } else {
            level = 'Poor';
            description = 'Critical security vulnerabilities require immediate action';
            color = '#dc3545';
        }
        
        if (scoreLevel) scoreLevel.textContent = level;
        if (scoreDescription) scoreDescription.textContent = description;
        
        // Animate score circle
        if (scoreCircle) {
            const circumference = 314; // 2 * π * 50
            const offset = circumference - (score / 100) * circumference;
            scoreCircle.style.strokeDashoffset = offset;
            scoreCircle.style.stroke = color;
        }
    }

    displayVulnerabilities() {
        const vulnerabilityList = document.getElementById('vulnerability-list');
        if (!vulnerabilityList) return;

        if (this.vulnerabilities.length === 0) {
            vulnerabilityList.innerHTML = `
                <div class="no-vulnerabilities">
                    <i class="fas fa-shield-alt"></i>
                    <h4>No Vulnerabilities Found</h4>
                    <p>Your SQL code appears to be secure!</p>
                </div>
            `;
            return;
        }

        vulnerabilityList.innerHTML = this.vulnerabilities.map(vuln => `
            <div class="vulnerability-item" data-severity="${vuln.risk_level}">
                <div class="vulnerability-header">
                    <h4 class="vulnerability-title">${vuln.vulnerability_type.replace(/_/g, ' ').toUpperCase()}</h4>
                    <span class="vulnerability-risk risk-${vuln.risk_level}">${vuln.risk_level}</span>
                </div>
                <div class="vulnerability-description">
                    ${vuln.description}
                </div>
                <div class="vulnerability-meta">
                    <span>Line: ${vuln.line_number}</span>
                    ${vuln.owasp_category ? `<span>OWASP: ${vuln.owasp_category}</span>` : ''}
                    ${vuln.cwe_id ? `<span>CWE: ${vuln.cwe_id}</span>` : ''}
                </div>
                <div class="vulnerability-actions">
                    <button class="btn btn-sm btn-secondary" onclick="viewVulnerabilityDetails('${vuln.id}')">
                        <i class="fas fa-eye"></i> Details
                    </button>
                    ${vuln.mitigation ? `
                        <button class="btn btn-sm btn-primary" onclick="applyMitigation('${vuln.id}')">
                            <i class="fas fa-wrench"></i> Fix
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    updateOWASPCompliance(data) {
        const complianceGrid = document.getElementById('owasp-compliance-grid');
        if (!complianceGrid) return;

        const owaspCategories = [
            'A01:2021 – Broken Access Control',
            'A02:2021 – Cryptographic Failures',
            'A03:2021 – Injection',
            'A04:2021 – Insecure Design',
            'A05:2021 – Security Misconfiguration',
            'A06:2021 – Vulnerable Components',
            'A07:2021 – Identification and Authentication Failures',
            'A08:2021 – Software and Data Integrity Failures',
            'A09:2021 – Security Logging and Monitoring Failures',
            'A10:2021 – Server-Side Request Forgery'
        ];

        const affectedCategories = data.compliance_status?.affected_categories || [];

        complianceGrid.innerHTML = owaspCategories.map(category => {
            const isAffected = affectedCategories.some(affected => 
                category.toLowerCase().includes(affected.toLowerCase())
            );
            
            return `
                <div class="compliance-item">
                    <div class="compliance-status ${isAffected ? 'compliance-fail' : 'compliance-pass'}"></div>
                    <div class="compliance-info">
                        <h4>${category}</h4>
                        <p>${isAffected ? 'Issues detected' : 'Compliant'}</p>
                    </div>
                </div>
            `;
        }).join('');
    }

    displayRecommendations(recommendations) {
        const recommendationsList = document.getElementById('security-recommendations');
        if (!recommendationsList) return;

        if (recommendations.length === 0) {
            recommendationsList.innerHTML = `
                <div class="no-recommendations">
                    <p>No specific security recommendations at this time.</p>
                </div>
            `;
            return;
        }

        recommendationsList.innerHTML = recommendations.map(rec => `
            <div class="recommendation-item">
                <div class="recommendation-icon">
                    <i class="fas fa-lightbulb"></i>
                </div>
                <div class="recommendation-content">
                    <h5>${rec.title || 'Security Recommendation'}</h5>
                    <p>${rec.description || rec}</p>
                </div>
            </div>
        `).join('');
    }

    filterVulnerabilities(e) {
        const filter = e.target.dataset.filter;
        const vulnerabilityItems = document.querySelectorAll('.vulnerability-item');
        
        // Update active filter button
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        
        // Filter vulnerabilities
        vulnerabilityItems.forEach(item => {
            if (filter === 'all' || item.dataset.severity === filter) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    showProgress() {
        const progress = document.getElementById('security-scan-progress');
        const startBtn = document.getElementById('start-security-scan');
        
        if (progress) progress.style.display = 'block';
        if (startBtn) startBtn.disabled = true;
        
        this.animateProgress();
    }

    hideProgress() {
        const progress = document.getElementById('security-scan-progress');
        const startBtn = document.getElementById('start-security-scan');
        
        if (progress) progress.style.display = 'none';
        if (startBtn) startBtn.disabled = false;
    }

    animateProgress() {
        const progressFill = document.getElementById('security-progress-fill');
        const progressText = document.getElementById('security-progress-text');
        const progressPercent = document.getElementById('security-progress-percent');
        
        const steps = [
            { percent: 20, text: 'Validating file...' },
            { percent: 40, text: 'Parsing SQL structure...' },
            { percent: 60, text: 'Scanning for vulnerabilities...' },
            { percent: 80, text: 'Analyzing security patterns...' },
            { percent: 100, text: 'Generating report...' }
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
        const results = document.getElementById('security-results');
        if (results) results.style.display = 'block';
    }

    hideResults() {
        const results = document.getElementById('security-results');
        if (results) results.style.display = 'none';
    }

    showEmptyState() {
        const emptyState = document.getElementById('security-empty-state');
        if (emptyState) emptyState.style.display = 'flex';
    }

    hideEmptyState() {
        const emptyState = document.getElementById('security-empty-state');
        if (emptyState) emptyState.style.display = 'none';
    }

    showError(message) {
        // Create or update error notification
        let errorDiv = document.getElementById('security-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'security-error';
            errorDiv.className = 'error-notification';
            document.querySelector('.security-analysis-container').appendChild(errorDiv);
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
function viewVulnerabilityDetails(vulnId) {
    const modal = document.getElementById('vulnerability-detail-modal');
    const modalBody = document.getElementById('vuln-modal-body');
    
    // Find vulnerability data
    const vuln = securityAnalysis.vulnerabilities.find(v => v.id === vulnId);
    if (!vuln) return;
    
    modalBody.innerHTML = `
        <div class="vulnerability-detail">
            <h4>${vuln.vulnerability_type.replace(/_/g, ' ').toUpperCase()}</h4>
            <div class="detail-section">
                <h5>Description</h5>
                <p>${vuln.description}</p>
            </div>
            <div class="detail-section">
                <h5>Location</h5>
                <p>Line ${vuln.line_number}</p>
            </div>
            <div class="detail-section">
                <h5>Risk Level</h5>
                <span class="vulnerability-risk risk-${vuln.risk_level}">${vuln.risk_level}</span>
            </div>
            ${vuln.mitigation ? `
                <div class="detail-section">
                    <h5>Mitigation</h5>
                    <p>${vuln.mitigation}</p>
                </div>
            ` : ''}
            ${vuln.owasp_category ? `
                <div class="detail-section">
                    <h5>OWASP Category</h5>
                    <p>${vuln.owasp_category}</p>
                </div>
            ` : ''}
        </div>
    `;
    
    modal.classList.add('show');
}

function closeVulnerabilityModal() {
    const modal = document.getElementById('vulnerability-detail-modal');
    modal.classList.remove('show');
}

function fixVulnerability() {
    // Implement vulnerability fixing logic
    console.log('Applying vulnerability fix...');
    closeVulnerabilityModal();
}

function exportSecurityReport(format) {
    if (!securityAnalysis.currentAnalysisId) {
        securityAnalysis.showError('No analysis available for export');
        return;
    }
    
    const url = `/api/export/${securityAnalysis.currentAnalysisId}/${format}`;
    window.open(url, '_blank');
}

// Initialize security analysis when DOM is loaded
let securityAnalysis;
document.addEventListener('DOMContentLoaded', () => {
    securityAnalysis = new SecurityAnalysis();
});
