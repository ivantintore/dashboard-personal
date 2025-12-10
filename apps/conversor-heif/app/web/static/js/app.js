// Conversor HEIC + PDF a JPG - Frontend JavaScript
// Maneja la interfaz de usuario, upload de archivos, conversión y descarga

class FileConverter {
    constructor() {
        this.files = [];
        this.isProcessing = false;
        this.initializeEventListeners();
        this.updateUI();
    }

    initializeEventListeners() {
        // File input change
        const fileInput = document.getElementById('fileInput');
        fileInput.addEventListener('change', (e) => this.handleFileSelection(e));

        // Select files button
        const selectFilesBtn = document.getElementById('selectFilesBtn');
        selectFilesBtn.addEventListener('click', () => fileInput.click());

        // Drag and drop
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        uploadArea.addEventListener('click', (e) => {
            // Only trigger file selection if not clicking on the button
            if (!e.target.closest('.select-files-btn')) {
                fileInput.click();
            }
        });

        // Quality and compression sliders
        const qualitySlider = document.getElementById('qualitySlider');
        const compressionSlider = document.getElementById('compressionSlider');
        
        qualitySlider.addEventListener('input', (e) => {
            document.getElementById('qualityValue').textContent = e.target.value;
            this.updateUI();
        });
        
        compressionSlider.addEventListener('input', (e) => {
            document.getElementById('compressionValue').textContent = e.target.value;
            this.updateUI();
        });

        // Convert button
        const convertBtn = document.getElementById('convertBtn');
        convertBtn.addEventListener('click', () => this.convertFiles());
    }

    handleFileSelection(event) {
        const selectedFiles = Array.from(event.target.files);
        this.addFiles(selectedFiles);
    }

    handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        event.currentTarget.classList.add('drag-over');
    }

    handleDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        event.currentTarget.classList.remove('drag-over');
        
        const droppedFiles = Array.from(event.dataTransfer.files);
        this.addFiles(droppedFiles);
    }

    addFiles(newFiles) {
        // Filter valid files
        const validFiles = newFiles.filter(file => {
            const extension = file.name.toLowerCase().split('.').pop();
            const validExtensions = ['heic', 'heif', 'pdf', 'png', 'jpg', 'jpeg'];
            return validExtensions.includes(extension);
        });

        if (validFiles.length === 0) {
            this.showNotification('No se encontraron archivos válidos', 'error');
            return;
        }

        // Add files to the list
        this.files = [...this.files, ...validFiles];
        this.updateFileList();
        this.updateUI();
        
        this.showNotification(`${validFiles.length} archivo(s) agregado(s)`, 'success');
    }

    removeFile(index) {
        this.files.splice(index, 1);
        this.updateFileList();
        this.updateUI();
    }

    updateFileList() {
        const fileList = document.getElementById('fileList');
        const filesContainer = document.getElementById('files');
        
        if (this.files.length === 0) {
            fileList.style.display = 'none';
            return;
        }

        fileList.style.display = 'block';
        filesContainer.innerHTML = '';

        this.files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const fileIcon = this.getFileIcon(file.name);
            const fileSize = this.formatFileSize(file.size);
            
            fileItem.innerHTML = `
                <div class="file-info">
                    <i class="${fileIcon}"></i>
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${fileSize}</span>
                </div>
                <button class="remove-file-btn" onclick="fileConverter.removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            filesContainer.appendChild(fileItem);
        });
    }

    getFileIcon(filename) {
        const extension = filename.toLowerCase().split('.').pop();
        const iconMap = {
            'heic': 'fas fa-image',
            'heif': 'fas fa-image',
            'pdf': 'fas fa-file-pdf',
            'png': 'fas fa-image',
            'jpg': 'fas fa-image',
            'jpeg': 'fas fa-image'
        };
        return iconMap[extension] || 'fas fa-file';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    updateUI() {
        const convertBtn = document.getElementById('convertBtn');
        const hasFiles = this.files.length > 0;
        const isProcessing = this.isProcessing;
        
        convertBtn.disabled = !hasFiles || isProcessing;
        
        if (hasFiles && !isProcessing) {
            convertBtn.innerHTML = '<i class="fas fa-cog"></i> Convertir Archivos';
            convertBtn.classList.remove('processing');
        } else if (isProcessing) {
            convertBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            convertBtn.classList.add('processing');
        }
    }

    async convertFiles() {
        if (this.files.length === 0 || this.isProcessing) return;

        this.isProcessing = true;
        this.updateUI();
        this.showProgress();

        try {
            // Prepare form data
            const formData = new FormData();
            this.files.forEach(file => {
                formData.append('files', file);
            });

            const quality = document.getElementById('qualitySlider').value;
            const compression = document.getElementById('compressionSlider').value;
            
            formData.append('quality', quality);
            formData.append('compression', compression);

            // Send conversion request
            const response = await fetch('api/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.showResults(result);
                this.showNotification('Conversión completada exitosamente', 'success');
            } else {
                throw new Error(result.message || 'Error en la conversión');
            }

        } catch (error) {
            console.error('Error during conversion:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
        } finally {
            this.isProcessing = false;
            this.hideProgress();
            this.updateUI();
        }
    }

    showProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.style.display = 'block';
        
        // Simulate progress
        let progress = 0;
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            
            progressFill.style.width = `${progress}%`;
            progressText.textContent = `Procesando archivos... ${Math.round(progress)}%`;
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 200);
    }

    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.style.display = 'none';
    }

    showResults(result) {
        console.log('🔍 showResults called with:', result);
        
        const resultsSection = document.getElementById('resultsSection');
        const processedCount = document.getElementById('processedCount');
        const totalSize = document.getElementById('totalSize');
        
        // Fix data structure: result.results.results is the actual array
        const actualResults = result.results?.results || [];
        console.log('📊 Actual results array:', actualResults);
        
        processedCount.textContent = actualResults.length;
        totalSize.textContent = this.calculateTotalSize(actualResults);
        
        resultsSection.style.display = 'block';
        
        // Add download button if available
        this.addDownloadButton(result);
    }

    calculateTotalSize(results) {
        if (!results || !Array.isArray(results)) return '0 MB';
        
        const totalBytes = results.reduce((sum, result) => {
            return sum + (result.output_size || 0);
        }, 0);
        
        return this.formatFileSize(totalBytes);
    }

    addDownloadButton(result) {
        console.log('🎯 addDownloadButton called with:', result);
        
        const resultsContent = document.getElementById('downloadButtonContainer') || document.querySelector('.results-content');
        if (!resultsContent) {
            console.error('❌ .results-content not found');
            return;
        }
        
        // Remove existing download button
        const existingBtn = resultsContent.querySelector('.download-btn');
        if (existingBtn) {
            existingBtn.remove();
            console.log('🗑️ Removed existing download button');
        }
        
        // Check if we have actual results and download_url
        const actualResults = result.results?.results || [];
        const downloadUrl = result.results?.download_url;
        
        console.log('📦 Download URL:', downloadUrl);
        console.log('📊 Results count:', actualResults.length);
        
        if (actualResults.length > 0 && downloadUrl) {
            const downloadBtn = document.createElement('button');
            downloadBtn.className = 'download-btn';
            downloadBtn.innerHTML = '<i class="fas fa-download"></i> Descargar ZIP con Todas las Imágenes';
            downloadBtn.onclick = () => this.downloadResults(result);
            
            resultsContent.appendChild(downloadBtn);
            console.log('✅ Download button created and added');
        } else {
            console.log('⚠️ No download button created - missing results or download_url');
        }
    }

    async downloadResults(result) {
        try {
            console.log('💾 downloadResults called with:', result);
            
            // Use the download_url from the correct location in API response
            const downloadUrl = result.results?.download_url;
            const taskId = result.results?.task_id;
            
            console.log('📦 Download URL:', downloadUrl);
            console.log('🆔 Task ID:', taskId);
            
            if (downloadUrl) {
                console.log('🚀 Starting download directly (no URL verification)...');
                
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = `converted_images_${taskId || 'unknown'}.zip`;
                link.style.display = 'none';
                document.body.appendChild(link);
                
                // Add small delay to ensure link is ready
                setTimeout(() => {
                    link.click();
                    document.body.removeChild(link);
                }, 100);
                
                console.log('✅ Download initiated');
                this.showNotification('Descargando archivo ZIP...', 'success');
            } else {
                throw new Error('URL de descarga no disponible');
            }
        } catch (error) {
            console.error('❌ Error downloading files:', error);
            this.showNotification(`Error en la descarga: ${error.message}`, 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const iconMap = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return iconMap[type] || 'info-circle';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.fileConverter = new FileConverter();
    
    // Add some CSS for notifications
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease-out;
        }
        
        .notification-success { background: #28a745; }
        .notification-error { background: #dc3545; }
        .notification-warning { background: #ffc107; color: #333; }
        .notification-info { background: #17a2b8; }
        
        .notification button {
            background: none;
            border: none;
            color: inherit;
            cursor: pointer;
            margin-left: 10px;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .drag-over {
            border-color: var(--primary-color) !important;
            background-color: rgba(102, 126, 234, 0.1) !important;
        }
        
        .processing {
            background: var(--secondary-color) !important;
            cursor: not-allowed !important;
        }
    `;
    document.head.appendChild(style);
});

// Update version information dynamically
async function updateVersionInfo() {
    try {
        const response = await fetch('health');
        const data = await response.json();
        
        if (data.version) {
            const versionText = document.getElementById('versionText');
            const buildTime = document.getElementById('buildTime');
            
            // Update version
            versionText.textContent = `v${data.version}`;
            
            // Extract timestamp from version and convert to readable time
            const timestamp = data.version.split('.')[2];
            if (timestamp) {
                const date = new Date(parseInt(timestamp) * 1000);
                const timeStr = date.toLocaleTimeString('es-ES', { 
                    hour: '2-digit', 
                    minute: '2-digit',
                    second: '2-digit'
                });
                buildTime.textContent = ` (${timeStr})`;
                buildTime.style.fontSize = '0.8em';
                buildTime.style.opacity = '0.8';
            }
        }
    } catch (error) {
        console.log('Could not update version info:', error);
    }
}

// Initialize the converter when page loads
document.addEventListener('DOMContentLoaded', function() {
    new FileConverter();
    updateVersionInfo();
});
