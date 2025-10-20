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
            max_size=1024 * 1024 * 200,  # 200MB max message size (increased for speed)
            ping_timeout=300,  # 5 minutes timeout for very large files
            ping_interval=25,
            async_mode='eventlet',  # Use eventlet for best performance
            logger=False,
            engineio_logger=False,
            async_handlers=True,  # Enable async handling for better throughput
        )
        self.upload_folder = upload_folder
        self.active_transfers = {}
        self.transfer_lock = Lock()
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Clean up any orphaned temp files from previous sessions
        self.cleanup_temp_files()
        
        # Optimized chunk size for network transfer (2MB for balance of speed and reliability)
        self.CHUNK_SIZE = 2 * 1024 * 1024  # 2MB chunks
        self.PARALLEL_CHUNKS = 8  # 8 parallel chunks for faster transfers
        
        self.setup_handlers()
        self.start_monitoring()
    
    def cleanup_temp_files(self):
        """Remove orphaned temporary upload files"""
        try:
            for filename in os.listdir(self.upload_folder):
                if filename.startswith('.upload_'):
                    temp_path = os.path.join(self.upload_folder, filename)
                    print(f"Cleaning up orphaned temp file: {filename}")
                    os.remove(temp_path)
        except Exception as e:
            print(f"Error cleaning temp files: {e}")
    
    def start_monitoring(self):
        """Start background monitoring for admin panel"""
        def broadcast_stats():
            while True:
                time.sleep(5)  # Update every 5 seconds (reduced from 2)
                transfers = self.get_active_transfers()
                if transfers:
                    self.socketio.emit('active_transfers', {
                        'transfers': transfers
                    })
        
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
            # Clean up any active transfers and temp files
            with self.transfer_lock:
                if request.sid in self.active_transfers:
                    transfer = self.active_transfers[request.sid]
                    # Clean up temp file if it exists
                    if 'temp_filepath' in transfer:
                        try:
                            if os.path.exists(transfer['temp_filepath']):
                                print(f"Cleaning up temp file: {transfer['temp_filepath']}")
                                os.remove(transfer['temp_filepath'])
                        except Exception as e:
                            print(f"Error cleaning up temp file: {e}")
                    del self.active_transfers[request.sid]
        
        @self.socketio.on('start_upload')
        def handle_start_upload(data):
            print(f"[DEBUG] Received start_upload event: {data}")
            """Initialize upload session"""
            filename = data['filename']
            filesize = data['filesize']
            chunk_count = data['chunk_count']
            permission = data.get('permission', 'public')
            allowed_users = data.get('allowed_users', '')
            session_id = request.sid
            
            print(f"Starting upload: {filename} ({filesize} bytes, {chunk_count} chunks, permission: {permission})")
            
            with self.transfer_lock:
                self.active_transfers[session_id] = {
                    'filename': filename,
                    'filesize': filesize,
                    'chunk_count': chunk_count,
                    'received_chunks': set(),
                    'temp_filepath': os.path.join(self.upload_folder, f'.upload_{filename}_{session_id}'),
                    'start_time': time.time(),
                    'type': 'upload',
                    'permission': permission,
                    'allowed_users': allowed_users
                }
                
                # Create temporary file for streaming chunks
                temp_file = self.active_transfers[session_id]['temp_filepath']
                with open(temp_file, 'wb') as f:
                    # Pre-allocate file size if supported (helps with large files)
                    try:
                        f.truncate(filesize)
                    except:
                        pass  # Not all filesystems support truncate
            
            emit('upload_ready', {
                'session_id': session_id,
                'chunk_size': self.CHUNK_SIZE,
                'status': 'ready'
            })
        
        @self.socketio.on('upload_chunk')
        def handle_upload_chunk(data):
            """Receive file chunk and write directly to disk (optimized)"""
            try:
                session_id = request.sid
                chunk_index = data['chunk_index']
                chunk_data = data['data']  # Binary data
                
                if session_id not in self.active_transfers:
                    emit('error', {'message': 'Invalid session'})
                    return
                
                transfer = self.active_transfers[session_id]
                
                # Write chunk directly to disk at correct offset (optimized buffered write)
                temp_filepath = transfer['temp_filepath']
                offset = chunk_index * self.CHUNK_SIZE
                
                # Use buffered writes for better performance
                with open(temp_filepath, 'r+b', buffering=8192*16) as f:  # 128KB buffer
                    f.seek(offset)
                    f.write(chunk_data)
                
                transfer['received_chunks'].add(chunk_index)
                
            except Exception as e:
                print(f"Error in upload_chunk: {e}")
                emit('error', {'message': f'Upload error: {str(e)}'})
                return
            
            # Calculate progress and speed (using actual bytes, not chunk_count * CHUNK_SIZE)
            progress = (len(transfer['received_chunks']) / transfer['chunk_count']) * 100
            elapsed = time.time() - transfer['start_time']
            
            # Calculate actual bytes received (accounting for last chunk being smaller)
            total_bytes_received = 0
            for chunk_idx in sorted(transfer['received_chunks']):
                chunk_start = chunk_idx * self.CHUNK_SIZE
                chunk_end = min(chunk_start + self.CHUNK_SIZE, transfer['filesize'])
                total_bytes_received += (chunk_end - chunk_start)
            
            if elapsed > 0:
                # Convert bytes to Mbps: (bytes * 8 bits/byte) / (seconds * 1,000,000 bits/Mbps)
                speed_mbps = (total_bytes_received * 8) / (elapsed * 1000000)
            else:
                speed_mbps = 0
            
            # Send acknowledgment (batch updates - only send every 4 chunks or if significant progress)
            should_send_update = (
                chunk_index % 4 == 0 or  # Every 4th chunk
                progress >= 99 or  # Near completion
                len(transfer['received_chunks']) == 1  # First chunk
            )
            
            if should_send_update:
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
                })
            
            # ALWAYS check if upload is complete (not just when sending updates)
            if len(transfer['received_chunks']) == transfer['chunk_count']:
                print(f"All chunks received ({len(transfer['received_chunks'])}/{transfer['chunk_count']}), finalizing upload...")
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
            
            # Calculate actual progress and speed
            progress = ((chunk_index + 1) / transfer['chunk_count']) * 100
            elapsed = time.time() - transfer['start_time']
            
            # Calculate bytes sent so far (account for smaller last chunk)
            total_bytes_sent = 0
            for i in range(chunk_index + 1):
                chunk_start = i * self.CHUNK_SIZE
                chunk_end = min(chunk_start + self.CHUNK_SIZE, transfer['filesize'])
                total_bytes_sent += (chunk_end - chunk_start)
            
            if elapsed > 0:
                speed_mbps = (total_bytes_sent * 8) / (elapsed * 1000000)
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
            })
            
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
        """Finalize upload by renaming temp file"""
        try:
            transfer = self.active_transfers[session_id]
            filename = transfer['filename']
            temp_filepath = transfer['temp_filepath']
            final_filepath = os.path.join(self.upload_folder, filename)
            permission = transfer.get('permission', 'public')
            allowed_users = transfer.get('allowed_users', '')
            
            # Rename temp file to final filename
            if os.path.exists(final_filepath):
                os.remove(final_filepath)
            os.rename(temp_filepath, final_filepath)
            
        except Exception as e:
            print(f"Error finalizing upload: {e}")
            # Clean up temp file on error
            try:
                if os.path.exists(transfer.get('temp_filepath', '')):
                    os.remove(transfer['temp_filepath'])
            except:
                pass
            return
        
        # Calculate statistics
        elapsed = time.time() - transfer['start_time']
        speed_mbps = (transfer['filesize'] * 8) / (elapsed * 1000000)  # Mbps
        
        print(f"Upload complete: {filename} - {speed_mbps:.2f} Mbps (Permission: {permission})")
        
        # Save file metadata with permissions
        # Import auth_system here to avoid circular import
        try:
            from auth_system import auth_system
            from flask import request as flask_request
            
            # Try to get current user
            username = 'Anonymous'
            token = flask_request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                token = flask_request.cookies.get('authToken')
            if token:
                user_session = auth_system.validate_session(token)
                if user_session:
                    username = user_session.get('username', 'Anonymous')
            
            # Parse allowed users
            allowed_users_list = [u.strip() for u in allowed_users.split(',') if u.strip()] if allowed_users else []
            
            # Add file metadata
            auth_system.add_file_metadata(
                filename,
                username,
                permission,
                allowed_users_list
            )
        except Exception as e:
            print(f"Error saving file metadata: {e}")
        
        # Send completion notification to the specific client
        print(f"Sending upload_complete to session {session_id}")
        self.socketio.emit('upload_complete', {
            'filename': filename,
            'filesize': transfer['filesize'],
            'elapsed': elapsed,
            'speed_mbps': speed_mbps
        }, room=session_id)  # Use room instead of to
        
        # Clean up
        with self.transfer_lock:
            if session_id in self.active_transfers:
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
