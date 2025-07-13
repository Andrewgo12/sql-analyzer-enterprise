/* ============================================================================
   SQL ANALYZER ENTERPRISE - UPLOAD MODULE
   File upload functionality, drag-and-drop, progress tracking, PDF support
   ============================================================================ */

class UploadManager {
    constructor() {
        this.maxFileSize = 10 * 1024 * 1024 * 1024; // 10GB
        this.allowedTypes = ['.sql', '.txt', '.text', '.pdf'];
        this.uploadQueue = [];
        this.activeUploads = new Map();
        this.maxConcurrentUploads = 3;
        
        this.init();
    }
    
    // ========================================================================
    // INITIALIZATION
    // ========================================================================
    
    init() {
        this.setupDropZone();
        this.setupFileInput();
        this.setupEventListeners();
    }
    
    setupDropZone() {
        const dropZone = document.getElementById('dropzone');
        if (!dropZone) return;
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => this.highlight(dropZone), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => this.unhighlight(dropZone), false);
        });
        
        // Handle dropped files
        dropZone.addEventListener('drop', (e) => this.handleDrop(e), false);
        
        // Handle click to browse
        dropZone.addEventListener('click', () => this.triggerFileInput());
    }
    
    setupFileInput() {
        const fileInput = document.getElementById('file-input');
        if (!fileInput) return;
        
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
    }
    
    setupEventListeners() {
        // Listen for paste events (for future enhancement)
        document.addEventListener('paste', (e) => this.handlePaste(e));
    }
    
    // ========================================================================
    // DRAG AND DROP HANDLERS
    // ========================================================================
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    highlight(element) {
        element.classList.add('dragover');
    }
    
    unhighlight(element) {
        element.classList.remove('dragover');
    }
    
    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        this.handleFiles(files);
    }
    
    handleFileSelect(e) {
        const files = e.target.files;
        this.handleFiles(files);
        
        // Clear the input so the same file can be selected again
        e.target.value = '';
    }
    
    handlePaste(e) {
        const items = e.clipboardData.items;
        
        for (let item of items) {
            if (item.kind === 'file') {
                const file = item.getAsFile();
                if (file) {
                    this.handleFiles([file]);
                }
            }
        }
    }
    
    triggerFileInput() {
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.click();
        }
    }
    
    // ========================================================================
    // FILE PROCESSING
    // ========================================================================
    
    handleFiles(files) {
        const fileArray = Array.from(files);
        
        // Validate each file
        const validFiles = [];
        const errors = [];
        
        fileArray.forEach(file => {
            const validation = this.validateFile(file);
            if (validation.isValid) {
                validFiles.push(file);
            } else {
                errors.push({
                    fileName: file.name,
                    errors: validation.errors
                });
            }
        });
        
        // Show validation errors
        if (errors.length > 0) {
            this.showValidationErrors(errors);
        }
        
        // Process valid files
        if (validFiles.length > 0) {
            validFiles.forEach(file => this.queueUpload(file));
            this.processUploadQueue();
        }
    }
    
    validateFile(file) {
        const errors = [];
        let isValid = true;
        
        // Check file type
        if (!Utils.validateFileType(file, this.allowedTypes)) {
            errors.push(`File type not supported. Allowed types: ${this.allowedTypes.join(', ')}`);
            isValid = false;
        }
        
        // Check file size
        if (!Utils.validateFileSize(file, this.maxFileSize)) {
            errors.push(`File too large. Maximum size: ${Utils.formatFileSize(this.maxFileSize)}`);
            isValid = false;
        }
        
        // Check if file is empty
        if (file.size === 0) {
            errors.push('File is empty');
            isValid = false;
        }
        
        return { isValid, errors };
    }
    
    showValidationErrors(errors) {
        const errorMessages = errors.map(error => 
            `${error.fileName}: ${error.errors.join(', ')}`
        ).join('\n');
        
        if (window.showNotification) {
            showNotification(`Upload validation failed:\n${errorMessages}`, 'error');
        } else {
            alert(`Upload validation failed:\n${errorMessages}`);
        }
    }
    
    // ========================================================================
    // UPLOAD QUEUE MANAGEMENT
    // ========================================================================
    
    queueUpload(file) {
        const uploadId = Utils.generateId('upload');
        const uploadItem = {
            id: uploadId,
            file: file,
            status: 'queued',
            progress: 0,
            startTime: null,
            endTime: null,
            error: null,
            result: null
        };
        
        this.uploadQueue.push(uploadItem);
        this.showUploadItem(uploadItem);
        
        return uploadId;
    }
    
    processUploadQueue() {
        // Start uploads up to the concurrent limit
        while (this.activeUploads.size < this.maxConcurrentUploads && this.uploadQueue.length > 0) {
            const uploadItem = this.uploadQueue.shift();
            this.startUpload(uploadItem);
        }
    }
    
    async startUpload(uploadItem) {
        try {
            uploadItem.status = 'uploading';
            uploadItem.startTime = Date.now();
            this.activeUploads.set(uploadItem.id, uploadItem);
            
            this.updateUploadItem(uploadItem);
            
            // Ensure we have a valid session
            if (!authManager.isAuthenticated()) {
                await authManager.refreshSession();
            }
            
            // Start the upload
            const result = await apiManager.uploadFile(
                uploadItem.file,
                (progress, loaded, total) => {
                    uploadItem.progress = Math.round(progress);
                    this.updateUploadProgress(uploadItem, loaded, total);
                }
            );
            
            // Upload completed successfully
            uploadItem.status = 'completed';
            uploadItem.endTime = Date.now();
            uploadItem.result = result;
            
            this.updateUploadItem(uploadItem);
            this.onUploadComplete(uploadItem);
            
        } catch (error) {
            // Upload failed
            uploadItem.status = 'failed';
            uploadItem.endTime = Date.now();
            uploadItem.error = error;
            
            this.updateUploadItem(uploadItem);
            this.onUploadError(uploadItem, error);
            
        } finally {
            // Remove from active uploads and process next in queue
            this.activeUploads.delete(uploadItem.id);
            this.processUploadQueue();
        }
    }
    
    cancelUpload(uploadId) {
        const uploadItem = this.activeUploads.get(uploadId);
        if (uploadItem) {
            uploadItem.status = 'cancelled';
            uploadItem.endTime = Date.now();
            
            // Remove from active uploads
            this.activeUploads.delete(uploadId);
            
            this.updateUploadItem(uploadItem);
            this.processUploadQueue();
        }
        
        // Also remove from queue if it's still there
        const queueIndex = this.uploadQueue.findIndex(item => item.id === uploadId);
        if (queueIndex !== -1) {
            this.uploadQueue.splice(queueIndex, 1);
        }
    }
    
    // ========================================================================
    // UI UPDATES
    // ========================================================================
    
    showUploadItem(uploadItem) {
        const uploadContainer = this.getOrCreateUploadContainer();
        
        const uploadElement = Utils.createElement('div', {
            className: 'upload-item',
            id: `upload-${uploadItem.id}`
        });
        
        uploadElement.innerHTML = `
            <div class="upload-info">
                <div class="upload-filename">
                    <i class="fas fa-file-${this.getFileIcon(uploadItem.file)} me-2"></i>
                    ${Utils.sanitizeHtml(uploadItem.file.name)}
                </div>
                <div class="upload-size">${Utils.formatFileSize(uploadItem.file.size)}</div>
            </div>
            <div class="upload-progress">
                <div class="progress-bar" style="width: 0%"></div>
            </div>
            <div class="upload-status">
                <span class="status-text">Queued</span>
                <button class="btn-cancel" onclick="uploadManager.cancelUpload('${uploadItem.id}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        uploadContainer.appendChild(uploadElement);
        this.showUploadContainer();
    }
    
    updateUploadItem(uploadItem) {
        const uploadElement = document.getElementById(`upload-${uploadItem.id}`);
        if (!uploadElement) return;
        
        const statusText = uploadElement.querySelector('.status-text');
        const progressBar = uploadElement.querySelector('.progress-bar');
        const cancelButton = uploadElement.querySelector('.btn-cancel');
        
        // Update status text
        switch (uploadItem.status) {
            case 'queued':
                statusText.textContent = 'Queued';
                statusText.className = 'status-text status-queued';
                break;
            case 'uploading':
                statusText.textContent = `${uploadItem.progress}%`;
                statusText.className = 'status-text status-uploading';
                break;
            case 'completed':
                statusText.textContent = 'Completed';
                statusText.className = 'status-text status-completed';
                cancelButton.style.display = 'none';
                break;
            case 'failed':
                statusText.textContent = 'Failed';
                statusText.className = 'status-text status-failed';
                cancelButton.innerHTML = '<i class="fas fa-redo"></i>';
                cancelButton.onclick = () => this.retryUpload(uploadItem.id);
                break;
            case 'cancelled':
                statusText.textContent = 'Cancelled';
                statusText.className = 'status-text status-cancelled';
                break;
        }
        
        // Update progress bar
        progressBar.style.width = `${uploadItem.progress}%`;
        
        // Update progress bar color based on status
        progressBar.className = `progress-bar progress-${uploadItem.status}`;
    }
    
    updateUploadProgress(uploadItem, loaded, total) {
        const uploadElement = document.getElementById(`upload-${uploadItem.id}`);
        if (!uploadElement) return;
        
        const statusText = uploadElement.querySelector('.status-text');
        const progressBar = uploadElement.querySelector('.progress-bar');
        
        // Calculate upload speed
        const elapsed = (Date.now() - uploadItem.startTime) / 1000;
        const speed = loaded / elapsed;
        const remaining = (total - loaded) / speed;
        
        // Update status with progress and speed info
        statusText.innerHTML = `
            ${uploadItem.progress}%<br>
            <small>${Utils.formatFileSize(speed)}/s - ${Utils.formatTime(Math.round(remaining))} remaining</small>
        `;
        
        progressBar.style.width = `${uploadItem.progress}%`;
    }
    
    getOrCreateUploadContainer() {
        let container = document.getElementById('upload-container');
        if (!container) {
            container = Utils.createElement('div', {
                id: 'upload-container',
                className: 'upload-container'
            });
            
            // Insert after the upload area
            const uploadArea = document.getElementById('upload-area');
            if (uploadArea) {
                uploadArea.parentNode.insertBefore(container, uploadArea.nextSibling);
            } else {
                document.body.appendChild(container);
            }
        }
        return container;
    }
    
    showUploadContainer() {
        const container = document.getElementById('upload-container');
        if (container) {
            container.style.display = 'block';
        }
    }
    
    hideUploadContainer() {
        const container = document.getElementById('upload-container');
        if (container && container.children.length === 0) {
            container.style.display = 'none';
        }
    }
    
    getFileIcon(file) {
        const extension = file.name.split('.').pop().toLowerCase();
        switch (extension) {
            case 'sql': return 'code';
            case 'txt': case 'text': return 'alt';
            case 'pdf': return 'pdf';
            default: return 'file';
        }
    }
    
    // ========================================================================
    // EVENT HANDLERS
    // ========================================================================
    
    onUploadComplete(uploadItem) {
        // Store upload result
        this.storeUploadResult(uploadItem);
        
        // Show success notification
        if (window.showNotification) {
            showNotification(`File "${uploadItem.file.name}" uploaded successfully!`, 'success');
        }
        
        // Trigger analysis if auto-analysis is enabled
        if (this.shouldAutoStartAnalysis()) {
            this.startAnalysisForUpload(uploadItem);
        }
        
        // Update file history
        this.updateFileHistory(uploadItem);
        
        // Remove upload item after delay
        setTimeout(() => {
            this.removeUploadItem(uploadItem.id);
        }, 5000);
    }
    
    onUploadError(uploadItem, error) {
        Utils.logError(error, `Upload failed: ${uploadItem.file.name}`);
        
        // Show error notification
        if (window.showNotification) {
            showNotification(`Upload failed: ${error.message}`, 'error');
        }
    }
    
    retryUpload(uploadId) {
        // Find the upload item (it might be in completed/failed state)
        const uploadElement = document.getElementById(`upload-${uploadId}`);
        if (!uploadElement) return;
        
        // Reset the upload item and add back to queue
        const uploadItem = {
            id: uploadId,
            file: this.getFileFromUploadElement(uploadElement),
            status: 'queued',
            progress: 0,
            startTime: null,
            endTime: null,
            error: null,
            result: null
        };
        
        this.uploadQueue.push(uploadItem);
        this.updateUploadItem(uploadItem);
        this.processUploadQueue();
    }
    
    removeUploadItem(uploadId) {
        const uploadElement = document.getElementById(`upload-${uploadId}`);
        if (uploadElement) {
            uploadElement.remove();
        }
        
        this.hideUploadContainer();
    }
    
    // ========================================================================
    // INTEGRATION METHODS
    // ========================================================================
    
    storeUploadResult(uploadItem) {
        const uploadHistory = Utils.getStorage('sqlAnalyzer_uploadHistory', []);
        
        uploadHistory.unshift({
            id: uploadItem.id,
            fileName: uploadItem.file.name,
            fileSize: uploadItem.file.size,
            uploadTime: uploadItem.endTime,
            processingTime: uploadItem.endTime - uploadItem.startTime,
            result: uploadItem.result
        });
        
        // Keep only last 50 uploads
        if (uploadHistory.length > 50) {
            uploadHistory.splice(50);
        }
        
        Utils.setStorage('sqlAnalyzer_uploadHistory', uploadHistory);
    }
    
    shouldAutoStartAnalysis() {
        const settings = Utils.getStorage('sqlAnalyzer_settings', {});
        return settings.autoStartAnalysis !== false; // Default to true
    }
    
    async startAnalysisForUpload(uploadItem) {
        if (!uploadItem.result || !uploadItem.result.file_id) {
            return;
        }
        
        try {
            if (window.analysisManager) {
                await analysisManager.startAnalysis(uploadItem.result.file_id);
            }
        } catch (error) {
            Utils.logError(error, 'Auto-start analysis failed');
        }
    }
    
    updateFileHistory(uploadItem) {
        // Update the global file count
        const currentCount = parseInt(document.getElementById('files-count')?.textContent || '0');
        const filesCountElement = document.getElementById('files-count');
        if (filesCountElement) {
            filesCountElement.textContent = currentCount + 1;
        }
    }
    
    // ========================================================================
    // PUBLIC API
    // ========================================================================
    
    getActiveUploads() {
        return Array.from(this.activeUploads.values());
    }
    
    getUploadQueue() {
        return [...this.uploadQueue];
    }
    
    clearCompletedUploads() {
        const completedElements = document.querySelectorAll('.upload-item .status-completed, .upload-item .status-failed');
        completedElements.forEach(element => {
            const uploadItem = element.closest('.upload-item');
            if (uploadItem) {
                uploadItem.remove();
            }
        });
        
        this.hideUploadContainer();
    }
    
    cancelAllUploads() {
        // Cancel active uploads
        for (const uploadId of this.activeUploads.keys()) {
            this.cancelUpload(uploadId);
        }
        
        // Clear queue
        this.uploadQueue.length = 0;
    }
}

// Create global instance
window.uploadManager = new UploadManager();
window.UploadManager = UploadManager;
