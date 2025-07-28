/**
 * SCHEMA ANALYSIS JAVASCRIPT
 * Interactive database schema analysis and visualization
 */

class SchemaAnalysis {
    constructor() {
        this.currentAnalysisId = null;
        this.tables = [];
        this.relationships = [];
        this.diagram = null;
        this.initializeEventListeners();
        this.initializeUpload();
    }

    initializeEventListeners() {
        // File upload events
        const uploadArea = document.getElementById('schema-upload-area');
        const fileInput = document.getElementById('schema-file-input');
        const removeBtn = document.getElementById('schema-remove-file');
        const startBtn = document.getElementById('start-schema-analysis');

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
            startBtn.addEventListener('click', this.startSchemaAnalysis.bind(this));
        }

        // Search and sort events
        const tableSearch = document.getElementById('table-search');
        const tableSort = document.getElementById('table-sort');

        if (tableSearch) {
            tableSearch.addEventListener('input', this.filterTables.bind(this));
        }

        if (tableSort) {
            tableSort.addEventListener('change', this.sortTables.bind(this));
        }
    }

    initializeUpload() {
        const uploadArea = document.getElementById('schema-upload-area');
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
        const uploadArea = document.getElementById('schema-upload-area');
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
        const startBtn = document.getElementById('start-schema-analysis');
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
        const uploadArea = document.getElementById('schema-upload-area');
        const fileInfo = document.getElementById('schema-file-info');
        
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
        const uploadArea = document.getElementById('schema-upload-area');
        const fileInfo = document.getElementById('schema-file-info');
        const fileInput = document.getElementById('schema-file-input');
        const startBtn = document.getElementById('start-schema-analysis');
        
        if (uploadArea) uploadArea.style.display = 'block';
        if (fileInfo) fileInfo.style.display = 'none';
        if (fileInput) fileInput.value = '';
        if (startBtn) startBtn.disabled = true;
        
        this.hideResults();
    }

    async startSchemaAnalysis() {
        const fileInput = document.getElementById('schema-file-input');
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
                await this.loadSchemaResults();
            } else {
                this.showError(result.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Schema analysis error:', error);
            this.showError('Network error occurred');
        } finally {
            this.hideProgress();
        }
    }

    getAnalysisOptions() {
        return {
            table_detection: document.getElementById('table-detection')?.checked || false,
            relationship_mapping: document.getElementById('relationship-mapping')?.checked || false,
            constraint_analysis: document.getElementById('constraint-analysis')?.checked || false,
            index_detection: document.getElementById('index-detection')?.checked || false,
            documentation_generation: document.getElementById('documentation-generation')?.checked || false,
            diagram_type: document.querySelector('input[name="diagram-type"]:checked')?.value || 'erd'
        };
    }

    async loadSchemaResults() {
        if (!this.currentAnalysisId) return;

        try {
            const response = await fetch(`/api/analysis/${this.currentAnalysisId}/schema`);
            const result = await response.json();
            
            if (result.success) {
                this.displaySchemaResults(result.data);
            } else {
                this.showError(result.error || 'Failed to load schema results');
            }
        } catch (error) {
            console.error('Load schema results error:', error);
            this.showError('Failed to load schema results');
        }
    }

    displaySchemaResults(data) {
        this.tables = data.tables || [];
        this.relationships = data.relationships || [];
        
        // Hide empty state and show results
        this.hideEmptyState();
        this.showResults();
        
        // Update overview
        this.updateSchemaOverview(data);
        
        // Create schema diagram
        this.createSchemaDiagram(data);
        
        // Display tables
        this.displayTables();
        
        // Display relationships
        this.displayRelationships();
        
        // Display constraints
        this.displayConstraints(data.constraints || []);
        
        // Generate documentation
        this.generateDocumentation(data);
    }

    updateSchemaOverview(data) {
        // Update overview cards
        document.getElementById('tables-count').textContent = data.total_tables || 0;
        document.getElementById('columns-count').textContent = data.total_columns || 0;
        document.getElementById('relationships-count').textContent = data.total_relationships || 0;
        document.getElementById('indexes-count').textContent = data.total_indexes || 0;
        
        // Update header stats
        document.getElementById('total-tables').textContent = data.total_tables || 0;
        document.getElementById('total-relationships').textContent = data.total_relationships || 0;
        document.getElementById('schema-complexity').textContent = data.complexity_level || 'Low';
    }

    createSchemaDiagram(data) {
        const diagramContainer = document.getElementById('schema-diagram');
        if (!diagramContainer) return;

        // Clear existing diagram
        diagramContainer.innerHTML = '';

        // Create simple diagram representation
        if (this.tables.length === 0) {
            diagramContainer.innerHTML = `
                <div class="no-diagram">
                    <i class="fas fa-sitemap"></i>
                    <p>No tables found to visualize</p>
                </div>
            `;
            return;
        }

        // Create basic table nodes
        this.tables.forEach((table, index) => {
            const node = document.createElement('div');
            node.className = 'diagram-node';
            node.style.left = `${50 + (index % 3) * 200}px`;
            node.style.top = `${50 + Math.floor(index / 3) * 150}px`;
            
            node.innerHTML = `
                <div class="node-title">${table.name}</div>
                ${table.columns.slice(0, 5).map(col => `
                    <div class="node-field">
                        ${col.is_primary_key ? '<i class="fas fa-key field-key"></i>' : ''}
                        ${col.is_foreign_key ? '<i class="fas fa-link field-foreign"></i>' : ''}
                        ${col.name} (${col.data_type})
                    </div>
                `).join('')}
                ${table.columns.length > 5 ? `<div class="node-field">... ${table.columns.length - 5} more</div>` : ''}
            `;
            
            diagramContainer.appendChild(node);
        });

        // Make nodes draggable
        this.makeDraggable();
    }

    makeDraggable() {
        const nodes = document.querySelectorAll('.diagram-node');
        nodes.forEach(node => {
            let isDragging = false;
            let startX, startY, startLeft, startTop;

            node.addEventListener('mousedown', (e) => {
                isDragging = true;
                startX = e.clientX;
                startY = e.clientY;
                startLeft = parseInt(node.style.left);
                startTop = parseInt(node.style.top);
                node.style.zIndex = 1000;
            });

            document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                
                const deltaX = e.clientX - startX;
                const deltaY = e.clientY - startY;
                
                node.style.left = `${startLeft + deltaX}px`;
                node.style.top = `${startTop + deltaY}px`;
            });

            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    node.style.zIndex = 'auto';
                }
            });
        });
    }

    displayTables() {
        const tablesList = document.getElementById('tables-list');
        if (!tablesList) return;

        if (this.tables.length === 0) {
            tablesList.innerHTML = `
                <div class="no-tables">
                    <i class="fas fa-table"></i>
                    <h4>No Tables Found</h4>
                    <p>No database tables were detected in the SQL file.</p>
                </div>
            `;
            return;
        }

        tablesList.innerHTML = this.tables.map(table => `
            <div class="table-item" onclick="viewTableDetails('${table.name}')">
                <div class="table-header">
                    <h4 class="table-name">${table.name}</h4>
                    <div class="table-stats">
                        <span>${table.columns.length} columns</span>
                        <span>${table.relationships?.length || 0} relationships</span>
                        <span>${table.indexes?.length || 0} indexes</span>
                    </div>
                </div>
                <div class="table-columns">
                    ${table.columns.slice(0, 6).map(col => `
                        <div class="column-item">
                            ${col.is_primary_key ? '<i class="fas fa-key" style="color: #ffc107;"></i>' : ''}
                            ${col.is_foreign_key ? '<i class="fas fa-link" style="color: #28a745;"></i>' : ''}
                            <span class="column-name">${col.name}</span>
                            <span class="column-type">${col.data_type}</span>
                        </div>
                    `).join('')}
                    ${table.columns.length > 6 ? `
                        <div class="column-item">
                            <span>... ${table.columns.length - 6} more columns</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    displayRelationships() {
        const relationshipsList = document.getElementById('relationships-list');
        if (!relationshipsList) return;

        if (this.relationships.length === 0) {
            relationshipsList.innerHTML = `
                <div class="no-relationships">
                    <p>No relationships found between tables.</p>
                </div>
            `;
            return;
        }

        relationshipsList.innerHTML = this.relationships.map(rel => `
            <div class="relationship-item">
                <h5 class="relationship-title">${rel.from_table} → ${rel.to_table}</h5>
                <div class="relationship-details">
                    Foreign Key: ${rel.foreign_key}<br>
                    References: ${rel.referenced_key}<br>
                    Type: ${rel.relationship_type || 'Foreign Key'}
                </div>
                <span class="relationship-type">${rel.relationship_type || 'FK'}</span>
            </div>
        `).join('');
    }

    displayConstraints(constraints) {
        const constraintsList = document.getElementById('constraints-list');
        if (!constraintsList) return;

        if (constraints.length === 0) {
            constraintsList.innerHTML = `
                <div class="no-constraints">
                    <p>No constraints found.</p>
                </div>
            `;
            return;
        }

        constraintsList.innerHTML = constraints.map(constraint => `
            <div class="constraint-item">
                <h5 class="constraint-title">${constraint.name || 'Unnamed Constraint'}</h5>
                <div class="constraint-description">
                    Table: ${constraint.table_name}<br>
                    Column: ${constraint.column_name}<br>
                    ${constraint.description || 'No description available'}
                </div>
                <span class="constraint-type">${constraint.constraint_type || 'UNKNOWN'}</span>
            </div>
        `).join('');
    }

    generateDocumentation(data) {
        const documentationContent = document.getElementById('documentation-content');
        if (!documentationContent) return;

        const documentation = `
            <h1>Database Schema Documentation</h1>
            
            <h2>Overview</h2>
            <p>This database contains ${data.total_tables || 0} tables with ${data.total_relationships || 0} relationships.</p>
            
            <h2>Tables</h2>
            ${this.tables.map(table => `
                <h3>${table.name}</h3>
                <p>Columns: ${table.columns.length}</p>
                <ul>
                    ${table.columns.map(col => `
                        <li><strong>${col.name}</strong> (${col.data_type})
                            ${col.is_primary_key ? ' - Primary Key' : ''}
                            ${col.is_foreign_key ? ' - Foreign Key' : ''}
                        </li>
                    `).join('')}
                </ul>
            `).join('')}
            
            <h2>Relationships</h2>
            ${this.relationships.length > 0 ? `
                <ul>
                    ${this.relationships.map(rel => `
                        <li><strong>${rel.from_table}</strong> → <strong>${rel.to_table}</strong> 
                            (${rel.foreign_key} → ${rel.referenced_key})</li>
                    `).join('')}
                </ul>
            ` : '<p>No relationships found.</p>'}
        `;

        documentationContent.innerHTML = documentation;
    }

    filterTables() {
        const searchTerm = document.getElementById('table-search').value.toLowerCase();
        const tableItems = document.querySelectorAll('.table-item');
        
        tableItems.forEach(item => {
            const tableName = item.querySelector('.table-name').textContent.toLowerCase();
            if (tableName.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    sortTables() {
        const sortBy = document.getElementById('table-sort').value;
        const tablesList = document.getElementById('tables-list');
        const tableItems = Array.from(tablesList.querySelectorAll('.table-item'));
        
        tableItems.sort((a, b) => {
            switch (sortBy) {
                case 'name':
                    return a.querySelector('.table-name').textContent.localeCompare(
                        b.querySelector('.table-name').textContent
                    );
                case 'columns':
                    const aColumns = parseInt(a.querySelector('.table-stats span').textContent);
                    const bColumns = parseInt(b.querySelector('.table-stats span').textContent);
                    return bColumns - aColumns;
                case 'relationships':
                    const aRels = parseInt(a.querySelector('.table-stats span:nth-child(2)').textContent);
                    const bRels = parseInt(b.querySelector('.table-stats span:nth-child(2)').textContent);
                    return bRels - aRels;
                default:
                    return 0;
            }
        });
        
        // Re-append sorted items
        tableItems.forEach(item => tablesList.appendChild(item));
    }

    showProgress() {
        const progress = document.getElementById('schema-analysis-progress');
        const startBtn = document.getElementById('start-schema-analysis');
        
        if (progress) progress.style.display = 'block';
        if (startBtn) startBtn.disabled = true;
        
        this.animateProgress();
    }

    hideProgress() {
        const progress = document.getElementById('schema-analysis-progress');
        const startBtn = document.getElementById('start-schema-analysis');
        
        if (progress) progress.style.display = 'none';
        if (startBtn) startBtn.disabled = false;
    }

    animateProgress() {
        const progressFill = document.getElementById('schema-progress-fill');
        const progressText = document.getElementById('schema-progress-text');
        const progressPercent = document.getElementById('schema-progress-percent');
        
        const steps = [
            { percent: 20, text: 'Parsing SQL structure...' },
            { percent: 40, text: 'Detecting tables...' },
            { percent: 60, text: 'Analyzing relationships...' },
            { percent: 80, text: 'Processing constraints...' },
            { percent: 100, text: 'Generating documentation...' }
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
        const results = document.getElementById('schema-results');
        if (results) results.style.display = 'block';
    }

    hideResults() {
        const results = document.getElementById('schema-results');
        if (results) results.style.display = 'none';
    }

    showEmptyState() {
        const emptyState = document.getElementById('schema-empty-state');
        if (emptyState) emptyState.style.display = 'flex';
    }

    hideEmptyState() {
        const emptyState = document.getElementById('schema-empty-state');
        if (emptyState) emptyState.style.display = 'none';
    }

    showError(message) {
        // Create or update error notification
        let errorDiv = document.getElementById('schema-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'schema-error';
            errorDiv.className = 'error-notification';
            document.querySelector('.schema-analysis-container').appendChild(errorDiv);
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

// Global functions for interactions
function viewTableDetails(tableName) {
    const modal = document.getElementById('table-detail-modal');
    const modalTitle = document.getElementById('table-modal-title');
    const modalBody = document.getElementById('table-modal-body');
    
    // Find table data
    const table = schemaAnalysis.tables.find(t => t.name === tableName);
    if (!table) return;
    
    modalTitle.textContent = `Table: ${table.name}`;
    modalBody.innerHTML = `
        <div class="table-detail">
            <h4>Columns (${table.columns.length})</h4>
            <div class="columns-detail">
                ${table.columns.map(col => `
                    <div class="column-detail">
                        <strong>${col.name}</strong> - ${col.data_type}
                        ${col.is_primary_key ? '<span class="badge badge-warning">PK</span>' : ''}
                        ${col.is_foreign_key ? '<span class="badge badge-success">FK</span>' : ''}
                        ${col.is_nullable ? '<span class="badge badge-secondary">NULL</span>' : '<span class="badge badge-primary">NOT NULL</span>'}
                    </div>
                `).join('')}
            </div>
            ${table.indexes && table.indexes.length > 0 ? `
                <h4>Indexes (${table.indexes.length})</h4>
                <div class="indexes-detail">
                    ${table.indexes.map(idx => `
                        <div class="index-detail">
                            <strong>${idx.name}</strong> - ${idx.type || 'INDEX'}
                            <br><small>Columns: ${idx.columns.join(', ')}</small>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
    
    modal.classList.add('show');
}

function closeTableModal() {
    const modal = document.getElementById('table-detail-modal');
    modal.classList.remove('show');
}

function exportTableStructure() {
    // Implement table structure export
    console.log('Exporting table structure...');
    closeTableModal();
}

function zoomIn() {
    const diagram = document.getElementById('schema-diagram');
    const currentScale = parseFloat(diagram.style.transform?.match(/scale\(([^)]+)\)/)?.[1] || 1);
    diagram.style.transform = `scale(${Math.min(currentScale * 1.2, 3)})`;
}

function zoomOut() {
    const diagram = document.getElementById('schema-diagram');
    const currentScale = parseFloat(diagram.style.transform?.match(/scale\(([^)]+)\)/)?.[1] || 1);
    diagram.style.transform = `scale(${Math.max(currentScale / 1.2, 0.3)})`;
}

function resetZoom() {
    const diagram = document.getElementById('schema-diagram');
    diagram.style.transform = 'scale(1)';
}

function exportDiagram() {
    // Implement diagram export
    console.log('Exporting diagram...');
}

function generateDocumentation() {
    // Trigger documentation generation
    if (schemaAnalysis.currentAnalysisId) {
        schemaAnalysis.generateDocumentation({
            total_tables: schemaAnalysis.tables.length,
            total_relationships: schemaAnalysis.relationships.length
        });
    }
}

function exportDocumentation() {
    // Export documentation
    console.log('Exporting documentation...');
}

function exportSchemaReport(format) {
    if (!schemaAnalysis.currentAnalysisId) {
        schemaAnalysis.showError('No analysis available for export');
        return;
    }
    
    const url = `/api/export/${schemaAnalysis.currentAnalysisId}/${format}`;
    window.open(url, '_blank');
}

// Initialize schema analysis when DOM is loaded
let schemaAnalysis;
document.addEventListener('DOMContentLoaded', () => {
    schemaAnalysis = new SchemaAnalysis();
});
