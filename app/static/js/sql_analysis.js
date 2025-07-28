/**
 * SQL ANALYSIS JAVASCRIPT
 * Interactive SQL analysis and correction functionality
 */

class SQLAnalysis {
    constructor() {
        this.currentAnalysisId = null;
        this.originalCode = '';
        this.correctedCode = '';
        this.issues = [];
        this.initializeEventListeners();
        this.initializeUpload();
    }

    initializeEventListeners() {
        // File upload events
        const uploadArea = document.getElementById('sql-upload-area');
        const fileInput = document.getElementById('sql-file-input');
        const removeBtn = document.getElementById('sql-remove-file');
        const startBtn = document.getElementById('start-sql-analysis');

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
            startBtn.addEventListener('click', this.startAnalysis.bind(this));
        }

        // Tab switching
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', this.switchTab.bind(this));
        });
    }

    initializeUpload() {
        const uploadArea = document.getElementById('sql-upload-area');
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
        const uploadArea = document.getElementById('sql-upload-area');
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

        // Read file content
        const reader = new FileReader();
        reader.onload = (e) => {
            this.originalCode = e.target.result;
            this.showFileInfo(file);
            this.enableAnalysis();
        };
        reader.readAsText(file);
    }

    validateFile(file) {
        const maxSize = 100 * 1024 * 1024; // 100MB
        const allowedTypes = ['.sql', '.txt', '.ddl', '.dml'];
        
        if (file.size > maxSize) {
            this.showError('El archivo excede el límite de 100MB');
            return false;
        }

        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(extension)) {
            this.showError('Tipo de archivo inválido. Por favor sube archivos SQL únicamente.');
            return false;
        }

        return true;
    }

    showFileInfo(file) {
        const uploadArea = document.getElementById('sql-upload-area');
        const fileInfo = document.getElementById('sql-file-info');
        
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
        const uploadArea = document.getElementById('sql-upload-area');
        const fileInfo = document.getElementById('sql-file-info');
        const fileInput = document.getElementById('sql-file-input');
        const startBtn = document.getElementById('start-sql-analysis');
        
        if (uploadArea) uploadArea.style.display = 'block';
        if (fileInfo) fileInfo.style.display = 'none';
        if (fileInput) fileInput.value = '';
        if (startBtn) startBtn.disabled = true;
        
        this.originalCode = '';
        this.hideResults();
    }

    enableAnalysis() {
        const startBtn = document.getElementById('start-sql-analysis');
        if (startBtn) {
            startBtn.disabled = false;
        }
    }

    async startAnalysis() {
        if (!this.originalCode) {
            this.showError('Por favor selecciona un archivo primero');
            return;
        }

        // Show progress
        this.showProgress();
        
        // Get analysis options
        const options = this.getAnalysisOptions();
        
        try {
            // Create form data
            const formData = new FormData();
            const blob = new Blob([this.originalCode], { type: 'text/plain' });
            formData.append('file', blob, 'analysis.sql');
            formData.append('options', JSON.stringify(options));

            // Start analysis
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.currentAnalysisId = result.data.analysis_result.id;
                await this.loadAnalysisResults();
            } else {
                this.showError(result.error || 'El análisis falló');
            }
        } catch (error) {
            console.error('Error en el análisis:', error);
            this.showError('Ocurrió un error de red');
        } finally {
            this.hideProgress();
        }
    }

    getAnalysisOptions() {
        return {
            syntax_check: document.getElementById('syntax-check')?.checked || false,
            auto_correction: document.getElementById('auto-correction')?.checked || false,
            spanish_comments: document.getElementById('spanish-comments')?.checked || false,
            optimization_suggestions: document.getElementById('optimization-suggestions')?.checked || false,
            format_beautify: document.getElementById('format-beautify')?.checked || false,
            database_type: document.getElementById('sql-db-type')?.value || 'auto'
        };
    }

    async loadAnalysisResults() {
        // Simulate analysis results
        const mockResults = {
            errors_found: 2,
            corrections_made: 1,
            code_quality: 95,
            total_lines: this.originalCode.split('\n').length,
            corrected_code: this.generateCorrectedCode(),
            issues: this.generateMockIssues(),
            suggestions: this.generateMockSuggestions()
        };

        this.displayResults(mockResults);
    }

    generateCorrectedCode() {
        // Simple mock correction - add comments in Spanish
        let corrected = this.originalCode;
        
        // Add header comment
        corrected = `-- Análisis SQL Enterprise - Código Corregido\n-- Fecha: ${new Date().toLocaleDateString()}\n\n` + corrected;
        
        // Add comments for CREATE TABLE statements
        corrected = corrected.replace(/CREATE TABLE (\w+)/gi, (match, tableName) => {
            return `-- Tabla: ${tableName} - Estructura de datos\n${match}`;
        });
        
        // Add comments for FOREIGN KEY constraints
        corrected = corrected.replace(/FOREIGN KEY/gi, '-- Clave foránea para mantener integridad referencial\n    FOREIGN KEY');
        
        return corrected;
    }

    generateMockIssues() {
        return [
            {
                id: 'issue_1',
                title: 'Falta índice en clave foránea',
                severity: 'warning',
                description: 'La columna sector_id debería tener un índice para mejorar el rendimiento de las consultas.',
                line: 12,
                suggestion: 'Agregar: CREATE INDEX idx_equipos_sector ON equipos_biomedicos(sector_id);'
            },
            {
                id: 'issue_2',
                title: 'Comentarios faltantes',
                severity: 'info',
                description: 'Se recomienda agregar comentarios descriptivos a las tablas y columnas importantes.',
                line: 1,
                suggestion: 'Agregar comentarios COMMENT en las definiciones de tabla'
            }
        ];
    }

    generateMockSuggestions() {
        return [
            {
                title: 'Optimización de Índices',
                description: 'Considera agregar índices en las columnas que se usan frecuentemente en WHERE y JOIN.'
            },
            {
                title: 'Nomenclatura Consistente',
                description: 'Mantén una nomenclatura consistente para nombres de tablas y columnas.'
            },
            {
                title: 'Documentación',
                description: 'Agrega comentarios descriptivos para mejorar la mantenibilidad del código.'
            }
        ];
    }

    displayResults(results) {
        // Hide empty state and show results
        this.hideEmptyState();
        this.showResults();
        
        // Update overview cards
        this.updateOverview(results);
        
        // Update code tabs
        this.updateCodeTabs(results);
        
        // Display issues
        this.displayIssues(results.issues);
        
        // Display suggestions
        this.displaySuggestions(results.suggestions);
        
        // Store corrected code
        this.correctedCode = results.corrected_code;
        this.issues = results.issues;
    }

    updateOverview(results) {
        document.getElementById('errors-found').textContent = results.errors_found;
        document.getElementById('corrections-made').textContent = results.corrections_made;
        document.getElementById('code-quality').textContent = results.code_quality + '%';
        document.getElementById('total-lines').textContent = results.total_lines;
        
        // Update header stats
        document.getElementById('files-analyzed').textContent = '1';
        document.getElementById('errors-corrected').textContent = results.corrections_made;
        document.getElementById('quality-score').textContent = results.code_quality + '%';
    }

    updateCodeTabs(results) {
        const originalCode = document.getElementById('original-code');
        const correctedCode = document.getElementById('corrected-code');
        const codeDiff = document.getElementById('code-diff');
        
        if (originalCode) {
            originalCode.textContent = this.originalCode;
        }
        
        if (correctedCode) {
            correctedCode.textContent = results.corrected_code;
        }
        
        if (codeDiff) {
            this.generateDiff(codeDiff);
        }
    }

    generateDiff(container) {
        const originalLines = this.originalCode.split('\n');
        const correctedLines = this.correctedCode.split('\n');
        
        let diffHtml = '';
        let correctedIndex = 0;
        
        for (let i = 0; i < originalLines.length; i++) {
            const originalLine = originalLines[i];
            
            // Find corresponding line in corrected code
            while (correctedIndex < correctedLines.length && 
                   correctedLines[correctedIndex].startsWith('--') && 
                   !originalLines[i].startsWith('--')) {
                diffHtml += `<div class="diff-line added">+ ${correctedLines[correctedIndex]}</div>`;
                correctedIndex++;
            }
            
            if (correctedIndex < correctedLines.length) {
                const correctedLine = correctedLines[correctedIndex];
                if (originalLine === correctedLine) {
                    diffHtml += `<div class="diff-line">  ${originalLine}</div>`;
                } else {
                    diffHtml += `<div class="diff-line removed">- ${originalLine}</div>`;
                    diffHtml += `<div class="diff-line added">+ ${correctedLine}</div>`;
                }
                correctedIndex++;
            } else {
                diffHtml += `<div class="diff-line">  ${originalLine}</div>`;
            }
        }
        
        // Add any remaining corrected lines
        while (correctedIndex < correctedLines.length) {
            diffHtml += `<div class="diff-line added">+ ${correctedLines[correctedIndex]}</div>`;
            correctedIndex++;
        }
        
        container.innerHTML = diffHtml;
    }

    displayIssues(issues) {
        const issuesList = document.getElementById('issues-list');
        if (!issuesList) return;

        if (issues.length === 0) {
            issuesList.innerHTML = `
                <div class="no-issues">
                    <i class="fas fa-check-circle"></i>
                    <h4>¡No se encontraron problemas!</h4>
                    <p>Tu código SQL está bien estructurado.</p>
                </div>
            `;
            return;
        }

        issuesList.innerHTML = issues.map(issue => `
            <div class="issue-item ${issue.severity}">
                <div class="issue-header">
                    <h4 class="issue-title">${issue.title}</h4>
                    <span class="issue-severity ${issue.severity}">${issue.severity}</span>
                </div>
                <div class="issue-description">
                    ${issue.description}
                </div>
                <div class="issue-actions">
                    <button class="btn btn-sm btn-secondary" onclick="viewIssueDetails('${issue.id}')">
                        <i class="fas fa-eye"></i> Ver Detalles
                    </button>
                    ${issue.suggestion ? `
                        <button class="btn btn-sm btn-primary" onclick="applySuggestion('${issue.id}')">
                            <i class="fas fa-magic"></i> Aplicar Sugerencia
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    displaySuggestions(suggestions) {
        const suggestionsList = document.getElementById('suggestions-list');
        if (!suggestionsList) return;

        if (suggestions.length === 0) {
            suggestionsList.innerHTML = `
                <div class="no-suggestions">
                    <p>No hay sugerencias adicionales en este momento.</p>
                </div>
            `;
            return;
        }

        suggestionsList.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item">
                <h5 class="suggestion-title">${suggestion.title}</h5>
                <div class="suggestion-description">
                    ${suggestion.description}
                </div>
            </div>
        `).join('');
    }

    switchTab(e) {
        const tabName = e.target.dataset.tab;
        
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    showProgress() {
        const progress = document.getElementById('sql-analysis-progress');
        const startBtn = document.getElementById('start-sql-analysis');
        
        if (progress) progress.style.display = 'block';
        if (startBtn) startBtn.disabled = true;
        
        this.animateProgress();
    }

    hideProgress() {
        const progress = document.getElementById('sql-analysis-progress');
        const startBtn = document.getElementById('start-sql-analysis');
        
        if (progress) progress.style.display = 'none';
        if (startBtn) startBtn.disabled = false;
    }

    animateProgress() {
        const progressFill = document.getElementById('sql-progress-fill');
        const progressText = document.getElementById('sql-progress-text');
        const progressPercent = document.getElementById('sql-progress-percent');
        
        const steps = [
            { percent: 20, text: 'Validando archivo...' },
            { percent: 40, text: 'Analizando sintaxis...' },
            { percent: 60, text: 'Detectando errores...' },
            { percent: 80, text: 'Aplicando correcciones...' },
            { percent: 100, text: 'Generando reporte...' }
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
        const results = document.getElementById('sql-results');
        if (results) results.style.display = 'block';
    }

    hideResults() {
        const results = document.getElementById('sql-results');
        if (results) results.style.display = 'none';
    }

    showEmptyState() {
        const emptyState = document.getElementById('sql-empty-state');
        if (emptyState) emptyState.style.display = 'flex';
    }

    hideEmptyState() {
        const emptyState = document.getElementById('sql-empty-state');
        if (emptyState) emptyState.style.display = 'none';
    }

    showError(message) {
        // Create or update error notification
        let errorDiv = document.getElementById('sql-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'sql-error';
            errorDiv.className = 'error-notification';
            document.querySelector('.sql-analysis-container').appendChild(errorDiv);
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
    const modal = document.getElementById('issue-detail-modal');
    const modalTitle = document.getElementById('issue-modal-title');
    const modalBody = document.getElementById('issue-modal-body');
    
    // Find issue data
    const issue = sqlAnalysis.issues.find(i => i.id === issueId);
    if (!issue) return;
    
    modalTitle.textContent = issue.title;
    modalBody.innerHTML = `
        <div class="issue-detail">
            <p><strong>Descripción:</strong> ${issue.description}</p>
            <p><strong>Línea:</strong> ${issue.line}</p>
            <p><strong>Severidad:</strong> ${issue.severity}</p>
            ${issue.suggestion ? `<p><strong>Sugerencia:</strong> ${issue.suggestion}</p>` : ''}
        </div>
    `;
    
    modal.classList.add('show');
}

function closeIssueModal() {
    const modal = document.getElementById('issue-detail-modal');
    modal.classList.remove('show');
}

function applyCorrection() {
    // Implement correction application logic
    console.log('Aplicando corrección...');
    closeIssueModal();
}

function applySuggestion(issueId) {
    // Implement suggestion application logic
    console.log('Aplicando sugerencia para:', issueId);
}

function exportSQLResults(format) {
    if (!sqlAnalysis.currentAnalysisId) {
        sqlAnalysis.showError('No hay análisis disponible para exportar');
        return;
    }
    
    const url = `/api/export/${sqlAnalysis.currentAnalysisId}/${format}`;
    window.open(url, '_blank');
}

// Initialize SQL analysis when DOM is loaded
let sqlAnalysis;
document.addEventListener('DOMContentLoaded', () => {
    sqlAnalysis = new SQLAnalysis();
});
