"""
High-Performance File Transfer Module
Using WebSocket with Binary Streaming and Parallel Chunks
Target Speed: 500+ Mbps
"""

from flask_socketio import SocketIO, emit
from flask import request
import os
import hashlib
import time
from threading import Lock
import struct

class HighSpeedTransfer:
    def __init__(self, app, upload_folder):
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            max_size=1024 * 1024 * 1024 * 10,  # 10GB max message size
            ping_timeout=120,
            ping_interval=25,
            async_mode='eventlet',  # Use eventlet for best performance
            logger=False,
            engineio_logger=False
        )
        self.upload_folder = upload_folder
        self.active_transfers = {}
        self.transfer_lock = Lock()
        
        # Optimized chunk size for network transfer (4MB - optimal for most networks)
        self.CHUNK_SIZE = 4 * 1024 * 1024  # 4MB chunks
        self.PARALLEL_CHUNKS = 8  # Number of parallel chunks
        
        self.setup_handlers()
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background monitoring for admin panel"""
        def broadcast_stats():
            while True:
                time.sleep(2)  # Update every 2 seconds
                transfers = self.get_active_transfers()
                if transfers:
                    self.socketio.emit('active_transfers', {
                        'transfers': transfers
                    }, broadcast=True)
        
        import threading
        monitor_thread = threading.Thread(target=broadcast_stats, daemon=True)
        monitor_thread.start()
    
    def setup_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print(f"Client connected: {request.sid}")
            emit('connected', {'status': 'ready'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"Client disconnected: {request.sid}")
            # Clean up any active transfers
            with self.transfer_lock:
                if request.sid in self.active_transfers:
                    del self.active_transfers[request.sid]
        
        @self.socketio.on('start_upload')
        def handle_start_upload(data):
            """Initialize upload session"""
            filename = data['filename']
            filesize = data['filesize']
            chunk_count = data['chunk_count']
            session_id = request.sid
            
            print(f"Starting upload: {filename} ({filesize} bytes, {chunk_count} chunks)")
            
            with self.transfer_lock:
                self.active_transfers[session_id] = {
                    'filename': filename,
                    'filesize': filesize,
                    'chunk_count': chunk_count,
                    'received_chunks': set(),
                    'chunks_data': {},
                    'start_time': time.time(),
                    'type': 'upload'
                }
            
            emit('upload_ready', {
                'session_id': session_id,
                'chunk_size': self.CHUNK_SIZE,
                'status': 'ready'
            })
        
        @self.socketio.on('upload_chunk')
        def handle_upload_chunk(data):
            """Receive file chunk"""
            session_id = request.sid
            chunk_index = data['chunk_index']
            chunk_data = data['data']  # Binary data
            
            if session_id not in self.active_transfers:
                emit('error', {'message': 'Invalid session'})
                return
            
            transfer = self.active_transfers[session_id]
            
            # Store chunk
            transfer['chunks_data'][chunk_index] = chunk_data
            transfer['received_chunks'].add(chunk_index)
            
            # Calculate progress and speed
            progress = (len(transfer['received_chunks']) / transfer['chunk_count']) * 100
            elapsed = time.time() - transfer['start_time']
            if elapsed > 0:
                speed_mbps = (len(transfer['received_chunks']) * self.CHUNK_SIZE * 8) / (elapsed * 1000000)
            else:
                speed_mbps = 0
            
            # Send acknowledgment
            emit('chunk_received', {
                'chunk_index': chunk_index,
                'progress': progress,
                'received': len(transfer['received_chunks']),
                'total': transfer['chunk_count']
            })
            
            # Broadcast transfer update to admin panel
            self.socketio.emit('transfer_update', {
                'filename': transfer['filename'],
                'type': 'upload',
                'progress': progress,
                'speed_mbps': speed_mbps,
                'upload_speed': speed_mbps,
                'download_speed': 0
            }, broadcast=True)
            
            # Check if upload is complete
            if len(transfer['received_chunks']) == transfer['chunk_count']:
                self.finalize_upload(session_id)
        
        @self.socketio.on('request_download')
        def handle_download_request(data):
            """Initialize download session"""
            filename = data['filename']
            session_id = request.sid
            
            filepath = os.path.join(self.upload_folder, filename)
            
            if not os.path.exists(filepath):
                emit('error', {'message': 'File not found'})
                return
            
            filesize = os.path.getsize(filepath)
            chunk_count = (filesize + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
            
            print(f"Starting download: {filename} ({filesize} bytes, {chunk_count} chunks)")
            
            with self.transfer_lock:
                self.active_transfers[session_id] = {
                    'filename': filename,
                    'filepath': filepath,
                    'filesize': filesize,
                    'chunk_count': chunk_count,
                    'start_time': time.time(),
                    'type': 'download'
                }
            
            emit('download_ready', {
                'session_id': session_id,
                'filesize': filesize,
                'chunk_count': chunk_count,
                'chunk_size': self.CHUNK_SIZE
            })
        
        @self.socketio.on('request_chunk')
        def handle_chunk_request(data):
            """Send requested chunk to client"""
            session_id = request.sid
            chunk_index = data['chunk_index']
            
            if session_id not in self.active_transfers:
                emit('error', {'message': 'Invalid session'})
                return
            
            transfer = self.active_transfers[session_id]
            filepath = transfer['filepath']
            
            # Read chunk from file
            offset = chunk_index * self.CHUNK_SIZE
            
            with open(filepath, 'rb') as f:
                f.seek(offset)
                chunk_data = f.read(self.CHUNK_SIZE)
            
            # Calculate progress and speed
            progress = ((chunk_index + 1) / transfer['chunk_count']) * 100
            elapsed = time.time() - transfer['start_time']
            if elapsed > 0:
                speed_mbps = ((chunk_index + 1) * self.CHUNK_SIZE * 8) / (elapsed * 1000000)
            else:
                speed_mbps = 0
            
            # Broadcast transfer update to admin panel
            self.socketio.emit('transfer_update', {
                'filename': transfer['filename'],
                'type': 'download',
                'progress': progress,
                'speed_mbps': speed_mbps,
                'upload_speed': 0,
                'download_speed': speed_mbps
            }, broadcast=True)
            
            # Send chunk
            emit('download_chunk', {
                'chunk_index': chunk_index,
                'data': chunk_data,
                'size': len(chunk_data)
            })
        
        @self.socketio.on('cancel_transfer')
        def handle_cancel_transfer():
            """Cancel active transfer"""
            session_id = request.sid
            
            with self.transfer_lock:
                if session_id in self.active_transfers:
                    del self.active_transfers[session_id]
            
            emit('transfer_cancelled', {'status': 'cancelled'})
    
    def finalize_upload(self, session_id):
        """Finalize upload by combining chunks"""
        transfer = self.active_transfers[session_id]
        filename = transfer['filename']
        filepath = os.path.join(self.upload_folder, filename)
        
        # Sort chunks by index and write to file
        with open(filepath, 'wb') as f:
            for i in range(transfer['chunk_count']):
                if i in transfer['chunks_data']:
                    f.write(transfer['chunks_data'][i])
        
        # Calculate statistics
        elapsed = time.time() - transfer['start_time']
        speed_mbps = (transfer['filesize'] * 8) / (elapsed * 1000000)  # Mbps
        
        print(f"Upload complete: {filename} - {speed_mbps:.2f} Mbps")
        
        # Send completion notification
        self.socketio.emit('upload_complete', {
            'filename': filename,
            'filesize': transfer['filesize'],
            'elapsed': elapsed,
            'speed_mbps': speed_mbps
        }, room=session_id)
        
        # Clean up
        with self.transfer_lock:
            del self.active_transfers[session_id]
    
    def get_stats(self):
        """Get transfer statistics"""
        with self.transfer_lock:
            return {
                'active_uploads': sum(1 for t in self.active_transfers.values() if t['type'] == 'upload'),
                'active_downloads': sum(1 for t in self.active_transfers.values() if t['type'] == 'download'),
                'total_active': len(self.active_transfers)
            }
    
    def get_active_transfers(self):
        """Get detailed list of active transfers"""
        with self.transfer_lock:
            transfers = []
            for session_id, transfer in self.active_transfers.items():
                elapsed = time.time() - transfer['start_time']
                if transfer['type'] == 'upload':
                    progress = (len(transfer['received_chunks']) / transfer['chunk_count']) * 100
                    bytes_transferred = len(transfer['received_chunks']) * self.CHUNK_SIZE
                else:
                    progress = 0
                    bytes_transferred = 0
                
                speed_mbps = (bytes_transferred * 8) / (elapsed * 1000000) if elapsed > 0 else 0
                
                transfers.append({
                    'filename': transfer['filename'],
                    'type': transfer['type'],
                    'progress': progress,
                    'speed_mbps': speed_mbps,
                    'elapsed': elapsed
                })
            return transfers
