/**
 * High-Speed File Transfer Client
 * Using WebSocket with Binary Streaming
 * Target: 500+ Mbps
 */

class HighSpeedTransfer {
    constructor() {
        this.socket = null;
        this.CHUNK_SIZE = 2 * 1024 * 1024; // 2MB chunks (increased for speed)
        this.PARALLEL_CHUNKS = 8; // 8 parallel transfers (increased for speed)
        this.activeUploads = new Map();
        this.activeDownloads = new Map();
        this.init();
    }

    init() {
        // Connect to WebSocket server with optimized settings
        this.socket = io({
            transports: ['websocket', 'polling'], // Prefer WebSocket
            upgrade: true,
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5,
            timeout: 60000,  // 60 second connection timeout
            perMessageDeflate: false, // Disable compression for maximum speed
            maxHttpBufferSize: 200 * 1024 * 1024,  // 200MB buffer
            forceNew: false,
            multiplex: false,  // Dedicated connection for better performance
        });

        this.setupEventHandlers();
    }

    setupEventHandlers() {
        this.socket.on('connect', () => {
            console.log('Socket connected successfully');
        });

        this.socket.on('connect_error', (error) => {
            console.error('Socket connection error:', error);
        });

        this.socket.on('disconnect', (reason) => {
            console.log('Socket disconnected:', reason);
        });

        this.socket.on('connected', (data) => {
            console.log('High-speed transfer connected:', data);
        });

        this.socket.on('chunk_received', (data) => {
            // Find upload by checking all uploads for matching chunk
            let upload = null;
            for (const [key, up] of this.activeUploads.entries()) {
                if (!key.startsWith('temp_')) {
                    upload = up;
                    break;
                }
            }
            
            if (upload) {
                upload.progress = data.progress;
                this.updateUploadProgress(upload, data);
                
                // Update transfer monitor if available
                if (typeof updateTransferProgress === 'function' && data.progress !== undefined) {
                    const elapsed = (Date.now() - upload.start_time) / 1000;
                    const speedMbps = elapsed > 0 ? (data.received * this.CHUNK_SIZE * 8) / (elapsed * 1000000) : 0;
                    updateTransferProgress(data.progress, speedMbps);
                }
                
                // Continue sending next chunks
                this.sendNextChunks(upload);
            }
        });

        this.socket.on('upload_complete', (data) => {
            console.log(`Upload complete: ${data.filename} at ${data.speed_mbps.toFixed(2)} Mbps`);
            // Find and remove the upload
            for (const [key, upload] of this.activeUploads.entries()) {
                if (upload.filename === data.filename) {
                    if (upload.onComplete) {
                        upload.onComplete(data);
                    }
                    this.activeUploads.delete(key);
                    break;
                }
            }
        });

        this.socket.on('download_ready', (data) => {
            const download = this.activeDownloads.get(this.socket.id);
            if (download) {
                download.chunk_count = data.chunk_count;
                download.filesize = data.filesize;
                download.chunks = new Array(data.chunk_count);
                download.receivedChunks = 0;
                console.log(`Download ready: ${data.filesize} bytes in ${data.chunk_count} chunks`);
                this.requestParallelChunks(download);
            } else {
                console.error('Download not found for session:', this.socket.id);
            }
        });

        this.socket.on('download_chunk', (data) => {
            const download = this.activeDownloads.get(this.socket.id);
            if (download) {
                download.chunks[data.chunk_index] = data.data;
                download.receivedChunks++;
                
                const progress = (download.receivedChunks / download.chunk_count) * 100;
                console.log(`Received chunk ${data.chunk_index}, progress: ${progress.toFixed(1)}%`);
                this.updateDownloadProgress(download, progress);
                
                // Request next chunk
                if (download.receivedChunks < download.chunk_count) {
                    this.requestNextChunk(download);
                } else {
                    console.log('All chunks received, finalizing download');
                    this.finalizeDownload(download);
                }
            } else {
                console.error('Download not found for chunk:', data.chunk_index);
            }
        });

        this.socket.on('error', (data) => {
            console.error('Transfer error:', data.message);
            const download = this.activeDownloads.get(this.socket.id);
            const upload = this.activeUploads.get(this.socket.id);
            
            if (download && download.onError) {
                download.onError(new Error(data.message));
            }
            
            if (upload && upload.onError) {
                upload.onError(new Error(data.message));
            }
        });
    }

    /**
     * Upload file with high speed
     */
    uploadFile(file, options = {}) {
        return new Promise((resolve, reject) => {
            if (!this.socket.connected) {
                console.error('Socket not connected');
                reject(new Error('Socket not connected'));
                return;
            }

            console.log(`Starting upload: ${file.name} (${file.size} bytes)`);
            const chunk_count = Math.ceil(file.size / this.CHUNK_SIZE);
            
            const upload = {
                file: file,
                filename: file.name,
                filesize: file.size,
                chunk_count: chunk_count,
                current_chunk: 0,
                chunks_sent: new Set(),
                chunks_in_flight: new Set(), // Track chunks currently being processed
                progress: 0,
                start_time: Date.now(),
                session_id: null,  // Will be set when upload_ready is received
                onProgress: options.onProgress || (() => {}),
                onComplete: (data) => {
                    resolve(data);
                },
                onError: (error) => {
                    console.error('Upload error:', error);
                    reject(error);
                }
            };

            // Store upload temporarily with a temp key, will be updated when upload_ready arrives
            const tempKey = 'temp_' + Date.now();
            this.activeUploads.set(tempKey, upload);

            // Start upload
            console.log('Emitting start_upload event');
            
            // Get permission settings from options or fallback to UI
            const permission = options.permission || document.getElementById('filePermission')?.value || 'public';
            const allowedUsers = options.allowedUsers || document.getElementById('restrictedUsers')?.value || '';
            
            // Listen for upload_ready to get session_id (BEFORE emitting start_upload)
            const uploadReadyHandler = (data) => {
                console.log('✅ Received upload_ready with session_id:', data.session_id);
                // Move upload from temp key to session_id key
                const tempUpload = this.activeUploads.get(tempKey);
                console.log('Temp upload found:', !!tempUpload);
                if (tempUpload && tempUpload.filename === file.name) {
                    tempUpload.session_id = data.session_id;
                    this.activeUploads.delete(tempKey);
                    this.activeUploads.set(data.session_id, tempUpload);
                    console.log('✅ Upload moved to session key:', data.session_id);
                    this.socket.off('upload_ready', uploadReadyHandler); // Remove this specific listener
                    console.log('🚀 Starting chunked upload...');
                    this.startChunkedUpload(tempUpload);
                } else {
                    console.error('❌ Upload not found or filename mismatch');
                }
            };
            
            this.socket.on('upload_ready', uploadReadyHandler);
            console.log('📡 Registered upload_ready listener, emitting start_upload...');
            
            this.socket.emit('start_upload', {
                filename: file.name,
                filesize: file.size,
                chunk_count: chunk_count,
                permission: permission,
                allowed_users: allowedUsers
            });
            console.log('📤 start_upload event emitted');
        });
    }

    startChunkedUpload(upload) {
        console.log(`🚀 Starting chunked upload: ${upload.chunk_count} chunks`);
        // Send first batch of chunks in parallel
        for (let i = 0; i < Math.min(this.PARALLEL_CHUNKS, upload.chunk_count); i++) {
            console.log(`📤 Queueing chunk ${i} for sending`);
            this.sendChunk(upload, i);
        }
    }

    sendChunk(upload, chunkIndex) {
        // Mark as being processed to avoid duplicate sends
        if (upload.chunks_in_flight.has(chunkIndex)) {
            console.log(`⚠️ Chunk ${chunkIndex} already in flight, skipping`);
            return;
        }
        upload.chunks_in_flight.add(chunkIndex);
        
        const start = chunkIndex * this.CHUNK_SIZE;
        const end = Math.min(start + this.CHUNK_SIZE, upload.filesize);
        const blob = upload.file.slice(start, end);
        
        console.log(`📦 Reading chunk ${chunkIndex} (${blob.size} bytes)`);

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                console.log(`📤 Emitting chunk ${chunkIndex}`);
                this.socket.emit('upload_chunk', {
                    chunk_index: chunkIndex,
                    data: e.target.result
                });
                upload.chunks_sent.add(chunkIndex);
                
                // Calculate total bytes sent (not just chunk_count * CHUNK_SIZE)
                let totalBytesSent = 0;
                for (let i = 0; i < upload.chunk_count; i++) {
                    if (upload.chunks_sent.has(i)) {
                        const chunkStart = i * this.CHUNK_SIZE;
                        const chunkEnd = Math.min(chunkStart + this.CHUNK_SIZE, upload.filesize);
                        totalBytesSent += (chunkEnd - chunkStart);
                    }
                }
                
                // Immediate progress update (optimistic)
                const progress = (upload.chunks_sent.size / upload.chunk_count) * 100;
                const elapsed = (Date.now() - upload.start_time) / 1000;
                // Convert bytes to Mbps: (bytes * 8 bits/byte) / (seconds * 1,000,000 bits/Mbps)
                const speed_mbps = elapsed > 0 ? (totalBytesSent * 8) / (elapsed * 1000000) : 0;
                
                if (upload.onProgress) {
                    upload.onProgress({
                        progress: progress,
                        received: upload.chunks_sent.size,
                        total: upload.chunk_count,
                        speed_mbps: speed_mbps
                    });
                }
                
                // CRITICAL FIX: Send next chunk immediately to maintain parallel pipeline
                // Find next unsent chunk and send it
                for (let i = 0; i < upload.chunk_count; i++) {
                    if (!upload.chunks_sent.has(i) && !upload.chunks_in_flight.has(i)) {
                        this.sendChunk(upload, i);
                        break; // Only send one replacement chunk
                    }
                }
            } catch (error) {
                console.error(`Error sending chunk ${chunkIndex}:`, error);
                upload.chunks_in_flight.delete(chunkIndex);
                if (upload.onError) {
                    upload.onError(error);
                }
            }
        };
        reader.onerror = (error) => {
            console.error(`Error reading chunk ${chunkIndex}:`, error);
            upload.chunks_in_flight.delete(chunkIndex);
            if (upload.onError) {
                upload.onError(error);
            }
        };
        reader.readAsArrayBuffer(blob);
    }

    sendNextChunks(upload) {
        // This is now only called from chunk_received acknowledgment
        // Just continue the pipeline if needed
        for (let i = 0; i < upload.chunk_count; i++) {
            if (!upload.chunks_sent.has(i) && !upload.chunks_in_flight.has(i)) {
                this.sendChunk(upload, i);
                break; // Only send one at a time when called from acknowledgment
            }
        }
    }

    updateUploadProgress(upload, data) {
        // Calculate total bytes received
        let totalBytesReceived = 0;
        for (let i = 0; i < data.received; i++) {
            const chunkStart = i * this.CHUNK_SIZE;
            const chunkEnd = Math.min(chunkStart + this.CHUNK_SIZE, upload.filesize);
            totalBytesReceived += (chunkEnd - chunkStart);
        }
        
        const elapsed = (Date.now() - upload.start_time) / 1000;
        const speed_mbps = elapsed > 0 ? (totalBytesReceived * 8) / (elapsed * 1000000) : 0;
        
        if (upload.onProgress) {
            upload.onProgress({
                progress: data.progress,
                received: data.received,
                total: data.total,
                speed_mbps: speed_mbps
            });
        }
    }

    /**
     * Download file with high speed
     */
    downloadFile(filename, options = {}) {
        return new Promise((resolve, reject) => {
            const download = {
                filename: filename,
                chunks: [],
                chunk_count: 0,
                receivedChunks: 0,
                current_chunk: 0,
                start_time: Date.now(),
                onProgress: options.onProgress || (() => {}),
                onComplete: (blob) => {
                    resolve(blob);
                },
                onError: (error) => {
                    reject(error);
                }
            };

            this.activeDownloads.set(this.socket.id, download);

            // Request download
            this.socket.emit('request_download', {
                filename: filename
            });
        });
    }

    requestParallelChunks(download) {
        // Request first batch of chunks in parallel
        for (let i = 0; i < Math.min(this.PARALLEL_CHUNKS, download.chunk_count); i++) {
            this.socket.emit('request_chunk', {
                chunk_index: i
            });
            download.current_chunk = i + 1;
        }
    }

    requestNextChunk(download) {
        if (download.current_chunk < download.chunk_count) {
            this.socket.emit('request_chunk', {
                chunk_index: download.current_chunk
            });
            download.current_chunk++;
        }
    }

    updateDownloadProgress(download, progress) {
        const bytesReceived = Math.floor(download.filesize * (progress / 100));
        const speed_mbps = this.calculateSpeed(bytesReceived, download.start_time);
        
        if (download.onProgress) {
            download.onProgress({
                progress: progress,
                received: bytesReceived,
                total: download.filesize,
                speed_mbps: speed_mbps
            });
        }
    }

    finalizeDownload(download) {
        // Combine all chunks into a blob
        const blob = new Blob(download.chunks);
        
        const elapsed = (Date.now() - download.start_time) / 1000;
        const speed_mbps = (download.filesize * 8) / (elapsed * 1000000);
        
        console.log(`Download complete: ${download.filename} at ${speed_mbps.toFixed(2)} Mbps`);
        
        if (download.onComplete) {
            download.onComplete(blob);
        }
        
        this.activeDownloads.delete(this.socket.id);
    }

    calculateSpeed(bytes, startTime) {
        const elapsed = (Date.now() - startTime) / 1000; // seconds
        if (elapsed === 0) return 0;
        return (bytes * 8) / (elapsed * 1000000); // Mbps
    }

    cancelTransfer(session_id) {
        this.socket.emit('cancel_transfer');
        this.activeUploads.delete(session_id);
        this.activeDownloads.delete(session_id);
    }
}

// Don't auto-create instance - let script.js handle it
// const highSpeedTransfer = new HighSpeedTransfer();
