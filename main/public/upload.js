(function () {
    const uploadForm = document.getElementById('upload-form');
    if (!uploadForm) return;

    const uploadFile = document.getElementById('upload-file');
    const uploadFolder = document.getElementById('upload-folder');
    const folderSelectBtn = document.getElementById('folder-select-btn');
    const dropZone = document.getElementById('drop-zone');
    const dropLabel = document.getElementById('drop-label');
    const uploadBtn = document.getElementById('upload-btn');
    const uploadStatus = document.getElementById('upload-status');
    const uploadProgress = document.getElementById('upload-progress');
    const uploadProgressLabel = document.getElementById('upload-progress-label');
    const uploadProgressPercent = document.getElementById('upload-progress-percent');
    const uploadProgressTrack = document.querySelector('.upload-progress-track');
    const uploadProgressBar = document.getElementById('upload-progress-bar');

    let selectedUploadFiles = [];
    let processingProgressTimer = null;
    const SUPPORTED_UPLOAD_EXTENSIONS = ['.pdf', '.docx', '.pptx'];
    const MAX_UPLOAD_FILES = 8;
    const MAX_UPLOAD_FILE_BYTES = 15 * 1024 * 1024;
    const MAX_UPLOAD_BATCH_BYTES = 60 * 1024 * 1024;

    function isSupportedUpload(file) {
        const name = file.name.toLowerCase();
        return SUPPORTED_UPLOAD_EXTENSIONS.some(ext => name.endsWith(ext));
    }

    function getDisplayName(file) {
        return file.webkitRelativePath || file.relativePath || file.name;
    }

    function escapeHtml(str) {
        return String(str ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function updateDropLabel(files) {
        if (!files.length) {
            dropLabel.innerHTML = `<span class="drop-icon">DOC</span><span>Click to browse files or drag &amp; drop</span>`;
            return;
        }

        const supported = files.filter(isSupportedUpload).length;
        const skipped = files.length - supported;
        const label = files.length === 1
            ? escapeHtml(getDisplayName(files[0]))
            : `${supported} supported file${supported === 1 ? '' : 's'} selected${skipped ? `, ${skipped} skipped` : ''}`;
        dropLabel.innerHTML = `<span class="drop-icon">OK</span><span>${label}</span>`;
    }

    function setSelectedUploadFiles(files) {
        selectedUploadFiles = Array.from(files || []);
        updateDropLabel(selectedUploadFiles);
        resetUploadProgress();
    }

    async function collectDroppedFiles(dataTransfer) {
        const items = Array.from(dataTransfer.items || []);
        const entries = items
            .map(item => item.webkitGetAsEntry ? item.webkitGetAsEntry() : null)
            .filter(Boolean);

        if (!entries.length) return Array.from(dataTransfer.files || []);

        const files = [];
        for (const entry of entries) {
            files.push(...await readEntryFiles(entry));
        }
        return files;
    }

    function readEntryFiles(entry, prefix = '') {
        return new Promise((resolve, reject) => {
            if (entry.isFile) {
                entry.file(file => {
                    file.relativePath = prefix + file.name;
                    resolve([file]);
                }, reject);
                return;
            }

            if (!entry.isDirectory) {
                resolve([]);
                return;
            }

            const reader = entry.createReader();
            const children = [];
            const readBatch = () => {
                reader.readEntries(async batch => {
                    if (!batch.length) {
                        const nested = await Promise.all(children.map(child => readEntryFiles(child, `${prefix}${entry.name}/`)));
                        resolve(nested.flat());
                        return;
                    }
                    children.push(...batch);
                    readBatch();
                }, reject);
            };
            readBatch();
        });
    }

    uploadFile.addEventListener('change', () => {
        setSelectedUploadFiles(uploadFile.files);
        uploadFolder.value = '';
    });

    uploadFolder.addEventListener('change', () => {
        setSelectedUploadFiles(uploadFolder.files);
        uploadFile.value = '';
    });

    folderSelectBtn.addEventListener('click', () => {
        uploadFolder.click();
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', async (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        setSelectedUploadFiles(await collectDroppedFiles(e.dataTransfer));
        uploadFile.value = '';
        uploadFolder.value = '';
    });

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const files = selectedUploadFiles;
        const tag = document.getElementById('equipment-tag').value.trim();
        const uploadedBy = document.getElementById('uploaded-by').value.trim();

        if (!files.length || !tag || !uploadedBy) return;

        const supportedFiles = files.filter(isSupportedUpload);
        if (!supportedFiles.length) {
            setUploadStatus('error', `No supported files found. Accepted: ${SUPPORTED_UPLOAD_EXTENSIONS.join(', ')}`);
            return;
        }
        const uploadLimitError = getUploadLimitError(supportedFiles);
        if (uploadLimitError) {
            setUploadStatus('error', uploadLimitError);
            return;
        }

        setUploadStatus('loading', `Processing ${supportedFiles.length} document${supportedFiles.length === 1 ? '' : 's'}...`);
        setUploadProgress(2, 'Preparing upload');
        uploadBtn.disabled = true;

        const formData = new FormData();
        supportedFiles.forEach(file => {
            formData.append('files', file, getDisplayName(file));
        });
        if (supportedFiles.length === 1) {
            formData.append('file', supportedFiles[0], getDisplayName(supportedFiles[0]));
        }
        formData.append('equipment_tag', tag);
        formData.append('uploaded_by', uploadedBy);

        try {
            const uploadResult = await uploadWithProgress(formData);
            const data = parseUploadResponse(uploadResult.body);

            if (!uploadResult.ok) {
                stopProcessingProgress();
                setUploadProgress(100, 'Upload failed');
                setUploadStatus('error', formatUploadError(data, uploadResult.status));
            } else {
                stopProcessingProgress();
                setUploadProgress(100, 'Ingestion complete');
                setUploadStatus(data.files_skipped ? 'partial' : 'success', buildUploadSummary(data));
                uploadForm.reset();
                selectedUploadFiles = [];
                updateDropLabel(selectedUploadFiles);
            }
        } catch (err) {
            stopProcessingProgress();
            setUploadProgress(100, 'Upload failed');
            setUploadStatus('error', 'Upload failed. Check that the server is running.');
            console.error(err);
        } finally {
            uploadBtn.disabled = false;
        }
    });

    function setUploadStatus(type, html) {
        uploadStatus.className = `upload-status upload-status--${type}`;
        uploadStatus.innerHTML = html;
    }

    function uploadWithProgress(formData) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/documents/upload');

            xhr.upload.addEventListener('progress', (event) => {
                if (!event.lengthComputable) {
                    setUploadProgress(12, 'Uploading documents');
                    return;
                }
                const uploadPercent = Math.round((event.loaded / event.total) * 70);
                setUploadProgress(Math.max(2, Math.min(uploadPercent, 70)), 'Uploading documents');
            });

            xhr.upload.addEventListener('load', () => {
                setUploadProgress(72, 'Upload complete. Ingesting documents');
                startProcessingProgress();
            });

            xhr.addEventListener('load', () => {
                resolve({
                    ok: xhr.status >= 200 && xhr.status < 300,
                    status: xhr.status,
                    body: xhr.responseText,
                });
            });

            xhr.addEventListener('error', () => reject(new Error('Upload request failed.')));
            xhr.addEventListener('abort', () => reject(new Error('Upload request aborted.')));
            xhr.send(formData);
        });
    }

    function parseUploadResponse(text) {
        if (!text) return {};
        try {
            return JSON.parse(text);
        } catch (error) {
            return { detail: text };
        }
    }

    function setUploadProgress(percent, label) {
        const safePercent = Math.max(0, Math.min(100, Math.round(percent)));
        uploadProgress.classList.remove('hidden');
        uploadProgressLabel.textContent = label;
        uploadProgressPercent.textContent = `${safePercent}%`;
        uploadProgressTrack.setAttribute('aria-valuenow', String(safePercent));
        uploadProgressBar.style.width = `${safePercent}%`;
    }

    function resetUploadProgress() {
        stopProcessingProgress();
        uploadProgress.classList.add('hidden');
        uploadProgressLabel.textContent = 'Preparing upload';
        uploadProgressPercent.textContent = '0%';
        uploadProgressTrack.setAttribute('aria-valuenow', '0');
        uploadProgressBar.style.width = '0%';
    }

    function startProcessingProgress() {
        stopProcessingProgress();
        let progress = 72;
        processingProgressTimer = window.setInterval(() => {
            progress = Math.min(96, progress + Math.max(1, Math.round((96 - progress) * 0.12)));
            setUploadProgress(progress, 'Ingesting and embedding documents');
            if (progress >= 96) stopProcessingProgress();
        }, 900);
    }

    function stopProcessingProgress() {
        if (processingProgressTimer) {
            window.clearInterval(processingProgressTimer);
            processingProgressTimer = null;
        }
    }

    function formatUploadError(data, status) {
        const detail = data.detail || data.message || 'Upload failed.';
        if (Array.isArray(detail)) {
            return `Upload failed (${status}): ${detail.map(item => item.msg || JSON.stringify(item)).join('; ')}`;
        }
        return `Upload failed (${status}): ${escapeHtml(String(detail))}`;
    }

    function getUploadLimitError(files) {
        if (files.length > MAX_UPLOAD_FILES) {
            return `Too many files selected. Upload at most ${MAX_UPLOAD_FILES} files per batch.`;
        }

        const oversized = files.find(file => file.size > MAX_UPLOAD_FILE_BYTES);
        if (oversized) {
            return `${escapeHtml(getDisplayName(oversized))} is larger than ${formatBytes(MAX_UPLOAD_FILE_BYTES)}. Split or compress it before uploading.`;
        }

        const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
        if (totalBytes > MAX_UPLOAD_BATCH_BYTES) {
            return `Selected files total ${formatBytes(totalBytes)}. Upload at most ${formatBytes(MAX_UPLOAD_BATCH_BYTES)} per batch.`;
        }

        return '';
    }

    function formatBytes(bytes) {
        if (bytes >= 1024 * 1024) return `${Math.round(bytes / 1024 / 1024)} MB`;
        if (bytes >= 1024) return `${Math.round(bytes / 1024)} KB`;
        return `${bytes} B`;
    }

    function buildUploadSummary(data) {
        if (!data.results) {
            return `<strong>${escapeHtml(data.filename || 'Document')}</strong> ingested - ${data.chunks_stored || 0} chunks stored.`;
        }

        const skipped = data.files_skipped
            ? ` ${data.files_skipped} skipped.`
            : '';
        const failedChunks = data.chunks_failed
            ? ` ${data.chunks_failed} chunks failed.`
            : '';
        const truncated = data.results.some(result => result.truncated)
            ? ' Some large files were capped to prevent memory overload.'
            : '';
        return `<strong>${data.files_processed}</strong> of <strong>${data.files_received}</strong> files ingested - ${data.chunks_stored} chunks stored.${skipped}${failedChunks}${truncated}`;
    }
})();
