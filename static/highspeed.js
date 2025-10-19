/**
 * High-Speed File Transfer Client
 * Using WebSocket with Binary Streaming
 * Target: 500+ Mbps
 */

class HighSpeedTransfer {
    constructor() {
        this.socket = null;
        this.CHUNK_SIZE = 4 * 1024 * 1024; // 4MB chunks
        this.PARALLEL_CHUNKS = 8; // Parallel transfers
        this.activeUploads = new Map();
        this.activeDownloads = new Map();
        this.init();
    }

    init() {
        // Connect to WebSocket server
        this.socket = io({
            transports: ['websocket'], // Force WebSocket (no polling)
            upgrade: false,
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5,
            perMessageDeflate: false, // Disable compression for speed
            maxHttpBufferSize: 1e8 // 100MB buffer
        });

        this.setupEventHandlers();
    }

    setupEventHandlers() {
        this.socket.on('connected', (data) => {
            console.log('High-speed transfer connected:', data);
        });

        this.socket.on('upload_ready', (data) => {
            const upload = this.activeUploads.get(data.session_id);
            if (upload) {
                this.startChunkedUpload(upload);
            }
        });

        this.socket.on('chunk_received', (data) => {
            const upload = this.activeUploads.get(this.socket.id);
            if (upload) {
                upload.progress = data.progress;
                this.updateUploadProgress(upload, data);
                
                // Continue sending next chunks
                this.sendNextChunks(upload);
            }
        });

        this.socket.on('upload_complete', (data) => {
            console.log(`Upload complete: ${data.filename} at ${data.speed_mbps.toFixed(2)} Mbps`);
            const upload = this.activeUploads.get(this.socket.id);
            if (upload && upload.onComplete) {
                upload.onComplete(data);
            }
            this.activeUploads.delete(this.socket.id);
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
            if (download && download.onError) {
                download.onError(new Error(data.message));
            }
        });
    }

    /**
     * Upload file with high speed
     */
    uploadFile(file, options = {}) {
        return new Promise((resolve, reject) => {
            const chunk_count = Math.ceil(file.size / this.CHUNK_SIZE);
            
            const upload = {
                file: file,
                filename: file.name,
                filesize: file.size,
                chunk_count: chunk_count,
                current_chunk: 0,
                chunks_sent: new Set(),
                progress: 0,
                start_time: Date.now(),
                onProgress: options.onProgress || (() => {}),
                onComplete: (data) => {
                    resolve(data);
                },
                onError: (error) => {
                    reject(error);
                }
            };

            this.activeUploads.set(this.socket.id, upload);

            // Start upload
            this.socket.emit('start_upload', {
                filename: file.name,
                filesize: file.size,
                chunk_count: chunk_count
            });
        });
    }

    startChunkedUpload(upload) {
        // Send first batch of chunks in parallel
        for (let i = 0; i < Math.min(this.PARALLEL_CHUNKS, upload.chunk_count); i++) {
            this.sendChunk(upload, i);
        }
    }

    sendChunk(upload, chunkIndex) {
        const start = chunkIndex * this.CHUNK_SIZE;
        const end = Math.min(start + this.CHUNK_SIZE, upload.filesize);
        const blob = upload.file.slice(start, end);

        const reader = new FileReader();
        reader.onload = (e) => {
            this.socket.emit('upload_chunk', {
                chunk_index: chunkIndex,
                data: e.target.result
            });
            upload.chunks_sent.add(chunkIndex);
        };
        reader.readAsArrayBuffer(blob);
    }

    sendNextChunks(upload) {
        // Send next parallel chunks
        const chunks_to_send = [];
        for (let i = 0; i < upload.chunk_count; i++) {
            if (!upload.chunks_sent.has(i)) {
                chunks_to_send.push(i);
                if (chunks_to_send.length >= this.PARALLEL_CHUNKS) break;
            }
        }

        chunks_to_send.forEach(index => this.sendChunk(upload, index));
    }

    updateUploadProgress(upload, data) {
        const speed_mbps = this.calculateSpeed(upload.filesize * (data.progress / 100), upload.start_time);
        
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
