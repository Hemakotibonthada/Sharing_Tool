import os
import socket
import qrcode
import io
import base64
import json
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory, Response, stream_with_context, session, redirect
from werkzeug.utils import secure_filename
from datetime import datetime
import mimetypes
import threading
import time
import hashlib
from functools import wraps
import gzip
import shutil
import zipfile
from base64 import b64encode, b64decode
import subprocess
import platform

# Import auth system
from auth_system import auth_system, require_login, require_permission

# Import high-speed transfer module
from high_speed_transfer import HighSpeedTransfer

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for sessions

# Initialize high-speed transfer
high_speed = None  # Will be initialized after app config

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Range')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Range,Content-Length,Accept-Ranges')
    return response

# Configuration
UPLOAD_FOLDER = 'shared_files'
VERSION_FOLDER = 'file_versions'
TEMP_FOLDER = 'temp_uploads'
MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024 * 1024  # 1TB
CHUNK_SIZE = 8192 * 1024  # 8MB chunks for faster transfer
BANDWIDTH_LIMIT = None  # None = unlimited, or set bytes per second (e.g., 1024*1024 for 1MB/s)
ENABLE_COMPRESSION = False  # Enable auto-compression before upload
ENABLE_AUTH = True  # Set to True to enable basic authentication
AUTH_USERNAME = 'admin'  # Change this
AUTH_PASSWORD = 'password'  # Change this
ENABLE_SSL = False  # Set to True to enable HTTPS
SSL_CERT_FILE = 'cert.pem'  # Path to SSL certificate
SSL_KEY_FILE = 'key.pem'  # Path to SSL key

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for faster updates

# Create required folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VERSION_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize high-speed transfer system
high_speed = HighSpeedTransfer(app, UPLOAD_FOLDER)

# Statistics tracking with thread lock
stats = {
    'total_uploads': 0,
    'total_downloads': 0,
    'total_size': 0,
    'total_resumed': 0,
    'total_compressed': 0,
    'total_versions': 0
}
stats_lock = threading.Lock()
active_transfers = {}  # Track active uploads/downloads with speeds

# File version tracking
file_versions = {}  # {filename: [version1, version2, ...]}

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not ENABLE_AUTH:
            return f(*args, **kwargs)
        
        auth = request.authorization
        if not auth or auth.username != AUTH_USERNAME or auth.password != AUTH_PASSWORD:
            return jsonify({'error': 'Authentication required'}), 401, {
                'WWW-Authenticate': 'Basic realm="NetShare Pro"'
            }
        return f(*args, **kwargs)
    return decorated

# Bandwidth limiter decorator
def limit_bandwidth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if BANDWIDTH_LIMIT is None:
            return f(*args, **kwargs)
        
        # Wrap the response to limit bandwidth
        response = f(*args, **kwargs)
        if hasattr(response, 'direct_passthrough'):
            response.direct_passthrough = False
        return response
    return decorated

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def generate_qr_code(url):
    """Generate QR code for the URL"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create the QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"

def get_file_info(filename):
    """Get file information"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    stats = os.stat(filepath)
    
    return {
        'name': filename,
        'size': stats.st_size,
        'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        'type': mimetypes.guess_type(filename)[0] or 'unknown'
    }

@app.route('/')
def index():
    """Main page"""
    local_ip = get_local_ip()
    port = 5000
    url = f"http://{local_ip}:{port}"
    qr_code = generate_qr_code(url)
    
    # Get statistics
    total_files = len([f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                       if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))])
    total_size = sum(os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f)) 
                     for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                     if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f)))
    
    return render_template('index.html', 
                         local_ip=local_ip, 
                         port=port, 
                         qr_code=qr_code,
                         url=url,
                         total_files=total_files,
                         total_size=total_size,
                         stats=stats)

@app.route('/login')
def login_page():
    """Login/Register page"""
    return render_template('login.html')

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    display_name = data.get('display_name', '')
    role = data.get('role', 'user')  # Default to user role
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Only admins can create admin accounts
    if role == 'admin':
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_session = auth_system.validate_session(token)
        if not user_session or not auth_system.has_permission(user_session['username'], 'manage_users'):
            role = 'user'  # Force to user role if not admin
    
    success, message = auth_system.create_user(username, password, role, display_name)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'error': message}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    success, token, message = auth_system.authenticate(username, password)
    if success:
        user_session = auth_system.validate_session(token)
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'username': user_session['username'],
                'display_name': user_session['display_name'],
                'role': user_session['role']
            }
        })
    else:
        return jsonify({'error': message}), 401

@app.route('/api/auth/logout', methods=['POST'])
@require_login
def logout():
    """Logout user"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_system.logout(token)
    return jsonify({'success': True})

@app.route('/api/auth/me', methods=['GET'])
@require_login
def get_current_user():
    """Get current user info"""
    return jsonify({
        'username': request.current_user['username'],
        'display_name': request.current_user['display_name'],
        'role': request.current_user['role']
    })

@app.route('/api/users', methods=['GET'])
@require_permission('manage_users')
def get_users():
    """Get all users (admin only)"""
    users = auth_system.get_all_users()
    return jsonify({'users': users})

# ==================== ADMIN PANEL ROUTES ====================

@app.route('/admin')
def admin_panel():
    """Admin panel page (admin only)"""
    # Check if user is authenticated via session or token
    token = request.cookies.get('authToken') or request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token[7:]
    
    user_session = auth_system.validate_session(token)
    if not user_session:
        # Redirect to login page
        return redirect('/')
    
    if not auth_system.has_permission(user_session['username'], 'delete_any'):
        # Redirect to home if not admin
        return redirect('/')
    
    return render_template('admin.html')

@app.route('/settings')
def settings_page():
    """Settings page (admin only)"""
    # Check if user is authenticated via session or token
    token = request.cookies.get('authToken') or request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token[7:]
    
    user_session = auth_system.validate_session(token)
    if not user_session:
        # Redirect to login page
        return redirect('/')
    
    if not auth_system.has_permission(user_session['username'], 'delete_any'):
        # Redirect to home if not admin
        return redirect('/')
    
    return render_template('settings.html')

@app.route('/api/admin/dashboard', methods=['GET'])
@require_permission('delete_any')
def admin_dashboard():
    """Get admin dashboard data"""
    try:
        # Get all users
        users = auth_system.get_all_users()
        
        # Get all files
        files_list = []
        total_size = 0
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath)
                    total_size += file_size
                    metadata = auth_system.get_file_metadata(filename)
                    files_list.append({
                        'name': filename,
                        'size': file_size,
                        'owner': metadata.get('owner', 'Unknown') if metadata else 'Unknown',
                        'uploaded': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
                        'downloads': metadata.get('download_count', 0) if metadata else 0
                    })
        
        # Get transfer statistics
        transfer_stats = high_speed.get_stats() if high_speed else {'active_uploads': 0, 'active_downloads': 0}
        
        # Get recent activity (last 10 activities from file metadata)
        recent_activity = []
        for filename in sorted(os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else [], 
                              key=lambda x: os.path.getctime(os.path.join(UPLOAD_FOLDER, x)), 
                              reverse=True)[:10]:
            metadata = auth_system.get_file_metadata(filename)
            if metadata:
                recent_activity.append({
                    'type': 'upload',
                    'title': f'File uploaded: {filename}',
                    'user': metadata.get('owner', 'Unknown'),
                    'details': f'{format_file_size(os.path.getsize(os.path.join(UPLOAD_FOLDER, filename)))}',
                    'time': datetime.fromtimestamp(os.path.getctime(os.path.join(UPLOAD_FOLDER, filename))).strftime('%I:%M %p')
                })
        
        return jsonify({
            'stats': {
                'total_users': len(users),
                'total_files': len(files_list),
                'storage_used': total_size,
                'active_transfers': transfer_stats.get('active_uploads', 0) + transfer_stats.get('active_downloads', 0)
            },
            'users': [{
                'username': user['username'],
                'role': user['role'],
                'file_count': len([f for f in files_list if f['owner'] == user['username']]),
                'last_active': 'Recently'
            } for user in users],
            'files': files_list,
            'recent_activity': recent_activity
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<username>', methods=['DELETE'])
@require_permission('delete_any')
def admin_delete_user(username):
    """Delete a user (admin only)"""
    if username == request.current_user['username']:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    success = auth_system.delete_user(username)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/admin/files/<filename>', methods=['DELETE'])
@require_permission('delete_any')
def admin_delete_file(filename):
    """Delete a file (admin only)"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if os.path.exists(filepath):
            os.remove(filepath)
            # Remove metadata
            auth_system.delete_file_metadata(filename)
            return jsonify({'success': True})
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/settings', methods=['GET'])
@require_permission('delete_any')
def get_settings():
    """Get current settings"""
    settings = {
        'general': {
            'appName': 'Circuvent Technologies',
            'serverPort': 5000,
            'language': 'en',
            'timezone': 'UTC',
            'enableQR': True,
            'darkMode': False
        },
        'security': {
            'enableAuth': True,
            'sessionTimeout': 7,
            'passwordStrength': 'medium',
            'enable2FA': False,
            'enableIPWhitelist': False
        },
        'storage': {
            'storageLimit': 10,
            'maxFileSize': 500,
            'allowedTypes': '',
            'autoDelete': False,
            'enableVersioning': True
        },
        'transfer': {
            'transferProtocol': 'websocket',
            'chunkSize': 4,
            'parallelTransfers': 8,
            'bandwidthLimit': 0,
            'enableResume': True,
            'enableCompression': False
        },
        'notifications': {
            'enableNotifications': True,
            'notifyUpload': True,
            'notifyDownload': True,
            'notifyNewUser': True,
            'notifyDelete': True,
            'adminEmail': ''
        },
        'advanced': {
            'debugMode': False,
            'enableCORS': True,
            'corsOrigins': '*',
            'enableHTTPS': False
        }
    }
    return jsonify(settings)

@app.route('/api/admin/settings', methods=['POST'])
@require_permission('delete_any')
def save_settings():
    """Save settings"""
    try:
        settings = request.get_json()
        # Here you would save settings to a config file or database
        # For now, just return success
        return jsonify({'success': True, 'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== TEXT SHARING ENDPOINTS ====================

# In-memory storage for shared texts (you can replace with database)
shared_texts_storage = []
text_id_counter = 0

@app.route('/api/share-text', methods=['POST'])
def share_text():
    """Share a text snippet"""
    global text_id_counter
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'Text cannot be empty'}), 400
    
    # Get user info if authenticated
    author = 'Anonymous'
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token:
        user_session = auth_system.validate_session(token)
        if user_session:
            author = user_session.get('username', 'Anonymous')
    
    text_id_counter += 1
    text_entry = {
        'id': str(text_id_counter),
        'text': text,
        'author': author,
        'timestamp': datetime.now().isoformat()
    }
    
    shared_texts_storage.insert(0, text_entry)  # Add to beginning
    
    # Keep only last 100 texts
    if len(shared_texts_storage) > 100:
        shared_texts_storage.pop()
    
    return jsonify({
        'success': True,
        'id': text_entry['id'],
        'message': 'Text shared successfully'
    })

@app.route('/api/shared-texts', methods=['GET'])
def get_shared_texts():
    """Get all shared texts"""
    return jsonify({'texts': shared_texts_storage})

@app.route('/api/shared-texts/<text_id>', methods=['DELETE'])
def delete_shared_text(text_id):
    """Delete a shared text"""
    global shared_texts_storage
    
    # Find and remove the text
    for i, text in enumerate(shared_texts_storage):
        if text['id'] == text_id:
            # Check if user is author or admin
            author = text['author']
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            can_delete = False
            
            if token:
                user_session = auth_system.validate_session(token)
                if user_session:
                    username = user_session.get('username')
                    is_admin = auth_system.has_permission(username, 'delete_any')
                    can_delete = username == author or is_admin
            else:
                # Allow deletion if author is Anonymous
                can_delete = author == 'Anonymous'
            
            if not can_delete:
                return jsonify({'error': 'Permission denied'}), 403
            
            shared_texts_storage.pop(i)
            return jsonify({'success': True, 'message': 'Text deleted successfully'})
    
    return jsonify({'error': 'Text not found'}), 404

# ==================== FILE PERMISSION ENDPOINTS ====================

@app.route('/api/files/<filename>/permissions', methods=['GET'])
@require_login
def get_file_permissions(filename):
    """Get file permissions"""
    metadata = auth_system.get_file_metadata(filename)
    if not metadata:
        return jsonify({'error': 'File not found'}), 404
    
    return jsonify({
        'permission': metadata.get('permission', 'public'),
        'allowed_users': metadata.get('allowed_users', []),
        'owner': metadata.get('owner')
    })

@app.route('/api/files/<filename>/permissions', methods=['PUT'])
@require_login
def update_file_permissions(filename):
    """Update file permissions (owner only)"""
    data = request.get_json()
    permission = data.get('permission')
    allowed_users = data.get('allowed_users', [])
    
    metadata = auth_system.get_file_metadata(filename)
    if not metadata:
        return jsonify({'error': 'File not found'}), 404
    
    # Only owner or admin can change permissions
    if metadata['owner'] != request.current_user['username'] and not auth_system.has_permission(request.current_user['username'], 'delete_any'):
        return jsonify({'error': 'Only file owner can change permissions'}), 403
    
    if permission not in ['public', 'private', 'restricted']:
        return jsonify({'error': 'Invalid permission type'}), 400
    
    auth_system.update_file_permission(filename, permission, allowed_users)
    return jsonify({'success': True})

# ==================== DELETE REQUEST ENDPOINTS ====================

@app.route('/api/files/<filename>/delete-request', methods=['POST'])
@require_login
def request_file_deletion(filename):
    """Request file deletion"""
    data = request.get_json()
    reason = data.get('reason', '')
    
    # Check if user can delete directly
    if auth_system.can_delete_file(filename, request.current_user['username']):
        return jsonify({'error': 'You can delete this file directly'}), 400
    
    request_id = auth_system.request_delete(filename, request.current_user['username'], reason)
    return jsonify({'success': True, 'request_id': request_id})

@app.route('/api/delete-requests', methods=['GET'])
@require_permission('approve_delete')
def get_delete_requests():
    """Get all delete requests (admin only)"""
    status = request.args.get('status', None)
    requests = auth_system.get_delete_requests(status)
    return jsonify({'requests': requests})

@app.route('/api/delete-requests/<request_id>/approve', methods=['POST'])
@require_permission('approve_delete')
def approve_delete_request(request_id):
    """Approve delete request (admin only)"""
    success = auth_system.approve_delete_request(request_id, request.current_user['username'])
    if success:
        # Get the request details and delete the file
        requests = auth_system.get_delete_requests()
        if request_id in requests:
            filename = requests[request_id]['filename']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                auth_system.delete_file_metadata(filename)
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Request not found'}), 404

@app.route('/api/delete-requests/<request_id>/reject', methods=['POST'])
@require_permission('approve_delete')
def reject_delete_request(request_id):
    """Reject delete request (admin only)"""
    data = request.get_json()
    reason = data.get('reason', '')
    
    success = auth_system.reject_delete_request(request_id, request.current_user['username'], reason)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Request not found'}), 404

# ==================== COMMENT ENDPOINTS ====================

@app.route('/api/files/<filename>/comments', methods=['GET'])
@require_login
def get_file_comments(filename):
    """Get all comments for a file"""
    # Check access permission
    if not auth_system.can_access_file(filename, request.current_user['username']):
        return jsonify({'error': 'Access denied'}), 403
    
    comments = auth_system.get_comments(filename)
    return jsonify({'comments': comments})

@app.route('/api/files/<filename>/comments', methods=['POST'])
@require_login
def add_file_comment(filename):
    """Add comment to file"""
    # Check access permission
    if not auth_system.can_access_file(filename, request.current_user['username']):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    comment_text = data.get('comment')
    mentions = data.get('mentions', [])
    
    if not comment_text:
        return jsonify({'error': 'Comment text required'}), 400
    
    comment = auth_system.add_comment(filename, request.current_user['username'], comment_text, mentions)
    return jsonify({'success': True, 'comment': comment})

@app.route('/upload', methods=['POST'])
@require_login
def upload_file():
    """Handle file upload with chunked streaming, resumable uploads, and optional compression"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        start_time = time.time()
        filename = secure_filename(file.filename)
        
        # Get permission from request
        permission = request.form.get('permission', 'public')
        allowed_users_str = request.form.get('allowed_users', '')
        allowed_users = [u.strip() for u in allowed_users_str.split(',') if u.strip()] if allowed_users_str else []
        
        # Check for resume capability
        resume_offset = int(request.headers.get('X-Upload-Offset', 0))
        enable_compression = request.form.get('compress', 'false').lower() == 'true'
        enable_versioning = request.form.get('version', 'false').lower() == 'true'
        
        # Handle versioning
        if enable_versioning and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            version_num = len(file_versions.get(filename, [])) + 1
            version_filename = f"{os.path.splitext(filename)[0]}_v{version_num}{os.path.splitext(filename)[1]}"
            
            # Save old version
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            version_path = os.path.join(VERSION_FOLDER, version_filename)
            shutil.copy2(old_path, version_path)
            
            if filename not in file_versions:
                file_versions[filename] = []
            file_versions[filename].append({
                'version': version_num,
                'filename': version_filename,
                'timestamp': datetime.now().isoformat()
            })
            
            with stats_lock:
                stats['total_versions'] += 1
        else:
            # Handle duplicate filenames (non-versioned)
            base_name, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                filename = f"{base_name}_{counter}{extension}"
                counter += 1
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        temp_filepath = os.path.join(TEMP_FOLDER, filename + '.tmp')
        
        # Resume support: open in append mode if resuming
        mode = 'ab' if resume_offset > 0 else 'wb'
        target_file = temp_filepath if resume_offset > 0 else filepath
        
        # Stream save for better performance
        bytes_written = 0
        last_update = time.time()
        transfer_id = str(hash(filename + str(start_time)))
        
        with open(target_file, mode) as f:
            if resume_offset > 0:
                f.seek(resume_offset)
                with stats_lock:
                    stats['total_resumed'] += 1
            
            while True:
                chunk = file.stream.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                f.write(chunk)
                bytes_written += len(chunk)
                
                # Update speed every second
                current_time = time.time()
                if current_time - last_update >= 1:
                    speed = bytes_written / (current_time - start_time) if (current_time - start_time) > 0 else 0
                    active_transfers[transfer_id] = {
                        'filename': filename,
                        'type': 'upload',
                        'speed': speed,
                        'bytes': bytes_written + resume_offset,
                        'timestamp': current_time
                    }
                    last_update = current_time
                
                # Bandwidth limiting
                if BANDWIDTH_LIMIT:
                    time.sleep(len(chunk) / BANDWIDTH_LIMIT)
        
        # Move from temp to final location if resumed
        if resume_offset > 0 and os.path.exists(temp_filepath):
            shutil.move(temp_filepath, filepath)
        
        # Compression (if enabled and file is not already compressed)
        final_filepath = filepath
        if enable_compression and ENABLE_COMPRESSION:
            compressed_extensions = ['.zip', '.gz', '.7z', '.rar', '.tar']
            if not any(filename.endswith(ext) for ext in compressed_extensions):
                compressed_filepath = filepath + '.gz'
                with open(filepath, 'rb') as f_in:
                    with gzip.open(compressed_filepath, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(filepath)
                final_filepath = compressed_filepath
                filename = filename + '.gz'
                
                with stats_lock:
                    stats['total_compressed'] += 1
        
        # Calculate upload speed
        elapsed_time = time.time() - start_time
        total_bytes = bytes_written + resume_offset
        speed = total_bytes / elapsed_time if elapsed_time > 0 else 0
        
        # Update statistics
        with stats_lock:
            stats['total_uploads'] += 1
            stats['total_size'] += total_bytes
            stats['upload_speed'] = speed
        
        # Clean up transfer tracking
        if transfer_id in active_transfers:
            del active_transfers[transfer_id]
        
        # Add file metadata for auth system
        auth_system.add_file_metadata(
            filename,
            request.current_user['username'],
            permission,
            allowed_users
        )
        
        # Update file size and type in metadata
        metadata = auth_system.get_file_metadata(filename)
        if metadata:
            metadata['size'] = total_bytes
            metadata['type'] = file.content_type or ''
            auth_system._save_json(auth_system.FILE_METADATA_DB, auth_system.file_metadata)
        
        file_info = get_file_info(filename)
        file_info['upload_speed'] = format_speed(speed)
        file_info['resumed'] = resume_offset > 0
        file_info['compressed'] = enable_compression and ENABLE_COMPRESSION
        file_info['versioned'] = enable_versioning
        file_info['owner'] = request.current_user['username']
        file_info['permission'] = permission
        
        return jsonify({
            'success': True,
            'message': f'File {filename} uploaded successfully',
            'file': file_info,
            'speed': format_speed(speed),
            'resumed_from': resume_offset if resume_offset > 0 else None
        })
    
    return jsonify({'error': 'Upload failed'}), 500

@app.route('/files')
def list_files():
    """List all shared files with metadata"""
    # Get current user if authenticated
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_session = auth_system.validate_session(token)
    current_username = user_session['username'] if user_session else None
    
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filepath):
            # Check if user can access this file
            if current_username and not auth_system.can_access_file(filename, current_username):
                continue  # Skip files user can't access
            
            file_info = get_file_info(filename)
            
            # Add metadata
            metadata = auth_system.get_file_metadata(filename)
            if metadata:
                file_info['owner'] = metadata.get('owner', 'Unknown')
                file_info['owner_display'] = metadata.get('owner', 'Unknown')
                file_info['permission'] = metadata.get('permission', 'public')
                file_info['created_at'] = metadata.get('created_at', file_info['modified'])
            else:
                file_info['owner'] = 'Unknown'
                file_info['owner_display'] = 'Unknown'
                file_info['permission'] = 'public'
                file_info['created_at'] = file_info['modified']
            
            # Add delete permission check
            if current_username:
                file_info['can_delete'] = auth_system.can_delete_file(filename, current_username)
                file_info['can_edit_permissions'] = (metadata and metadata.get('owner') == current_username) or auth_system.has_permission(current_username, 'delete_any')
            else:
                file_info['can_delete'] = False
                file_info['can_edit_permissions'] = False
            
            files.append(file_info)
    
    # Sort by modified time (newest first)
    files.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify(files)

@app.route('/download/<filename>')
def download_file(filename):
    """Download a file with optimized streaming"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        with stats_lock:
            stats['total_downloads'] += 1
        
        # Use send_file with optimized settings
        return send_from_directory(
            app.config['UPLOAD_FOLDER'], 
            filename, 
            as_attachment=True,
            max_age=0,
            conditional=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/delete/<filename>', methods=['DELETE'])
@require_login
def delete_file(filename):
    """Delete a file (owner or admin only)"""
    try:
        # Check if user can delete this file
        if not auth_system.can_delete_file(filename, request.current_user['username']):
            return jsonify({'error': 'You do not have permission to delete this file. You can request deletion instead.'}), 403
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            os.remove(filepath)
            stats['total_size'] -= file_size
            
            # Delete metadata
            auth_system.delete_file_metadata(filename)
            
            return jsonify({'success': True, 'message': f'File {filename} deleted'})
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    """Get server statistics"""
    total_files = len([f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                       if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))])
    total_size = sum(os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f)) 
                     for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                     if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f)))
    
    return jsonify({
        'total_files': total_files,
        'total_size': total_size,
        'total_uploads': stats.get('total_uploads', 0),
        'total_downloads': stats.get('total_downloads', 0),
        'total_resumed': stats.get('total_resumed', 0),
        'total_compressed': stats.get('total_compressed', 0),
        'total_versions': stats.get('total_versions', 0)
    })

@app.route('/search')
def search_files():
    """Search files by name"""
    query = request.args.get('q', '').lower()
    files = []
    
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filepath) and query in filename.lower():
            files.append(get_file_info(filename))
    
    files.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify(files)

@app.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    """Delete multiple files"""
    try:
        data = request.get_json()
        filenames = data.get('filenames', [])
        deleted = []
        errors = []
        
        for filename in filenames:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                os.remove(filepath)
                stats['total_size'] -= file_size
                deleted.append(filename)
            else:
                errors.append(filename)
        
        return jsonify({
            'success': True,
            'deleted': deleted,
            'errors': errors,
            'message': f'Deleted {len(deleted)} files'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<filename>')
@require_auth
def preview_file_enhanced(filename):
    """Preview file (PDF, audio, video, images, text) in browser"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    # Determine if file is previewable
    mime_type = mimetypes.guess_type(filename)[0]
    previewable_types = [
        'image/', 'video/', 'audio/', 'application/pdf',
        'text/', 'application/json', 'application/javascript'
    ]
    
    is_previewable = any(mime_type and mime_type.startswith(t) for t in previewable_types)
    
    if not is_previewable:
        # Try to serve it anyway
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    return send_file(filepath, mimetype=mime_type, as_attachment=False)

@app.route('/bulk-upload', methods=['POST'])
def bulk_upload():
    """Handle multiple file uploads simultaneously"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    results = []
    
    for file in files:
        if file.filename != '':
            try:
                filename = secure_filename(file.filename)
                
                # Handle duplicate filenames
                base_name, extension = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                    filename = f"{base_name}_{counter}{extension}"
                    counter += 1
                
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                with stats_lock:
                    stats['total_uploads'] += 1
                    stats['total_size'] += os.path.getsize(filepath)
                
                results.append({
                    'success': True,
                    'filename': filename,
                    'size': os.path.getsize(filepath)
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'filename': file.filename,
                    'error': str(e)
                })
    
    return jsonify({
        'success': True,
        'message': f'Uploaded {len(results)} files',
        'results': results
    })

@app.route('/bulk-download', methods=['POST'])
def bulk_download():
    """Download multiple files as a zip"""
    try:
        import zipfile
        from io import BytesIO
        
        data = request.get_json()
        filenames = data.get('filenames', [])
        
        if not filenames:
            return jsonify({'error': 'No files specified'}), 400
        
        # Create zip file in memory
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename in filenames:
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.exists(filepath):
                    zf.write(filepath, filename)
        
        memory_file.seek(0)
        
        with stats_lock:
            stats['total_downloads'] += len(filenames)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='files.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/file-info/<filename>')
def file_info_endpoint(filename):
    """Get detailed file information"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        stats_info = os.stat(filepath)
        file_hash = calculate_file_hash(filepath)
        
        return jsonify({
            'name': filename,
            'size': stats_info.st_size,
            'created': datetime.fromtimestamp(stats_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.fromtimestamp(stats_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'type': mimetypes.guess_type(filename)[0] or 'unknown',
            'hash': file_hash
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/transfer-status')
def transfer_status():
    """Get current transfer status"""
    # Count active transfers by type
    upload_count = sum(1 for t in active_transfers.values() if t.get('type') == 'upload')
    download_count = sum(1 for t in active_transfers.values() if t.get('type') == 'download')
    
    # Calculate average speeds
    upload_speeds = [t['speed'] for t in active_transfers.values() if t.get('type') == 'upload' and 'speed' in t]
    download_speeds = [t['speed'] for t in active_transfers.values() if t.get('type') == 'download' and 'speed' in t]
    
    avg_upload_speed = sum(upload_speeds) / len(upload_speeds) if upload_speeds else 0
    avg_download_speed = sum(download_speeds) / len(download_speeds) if download_speeds else 0
    
    return jsonify({
        'active_uploads': upload_count,
        'active_downloads': download_count,
        'upload_speed': format_speed(avg_upload_speed),
        'download_speed': format_speed(avg_download_speed),
        'total_active': len(active_transfers)
    })

@app.route('/clear-all', methods=['POST'])
def clear_all_files():
    """Clear all files (with confirmation)"""
    try:
        import shutil
        
        # Get file count before clearing
        file_count = len([f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                         if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))])
        
        # Remove all files
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        
        with stats_lock:
            stats['total_size'] = 0
        
        return jsonify({
            'success': True,
            'message': f'Cleared {file_count} files'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_file_hash(filepath, algorithm='md5'):
    """Calculate file hash for integrity verification"""
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def format_file_size(bytes_size):
    """Format file size in human-readable format"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"

def format_speed(bytes_per_second):
    """Format transfer speed in human-readable format"""
    if bytes_per_second < 1024:
        return f"{bytes_per_second:.2f} B/s"
    elif bytes_per_second < 1024 * 1024:
        return f"{bytes_per_second / 1024:.2f} KB/s"
    elif bytes_per_second < 1024 * 1024 * 1024:
        return f"{bytes_per_second / (1024 * 1024):.2f} MB/s"
    else:
        return f"{bytes_per_second / (1024 * 1024 * 1024):.2f} GB/s"

# New endpoints for advanced features

@app.route('/file-versions/<filename>', methods=['GET'])
@require_auth
def get_file_versions(filename):
    """Get all versions of a file"""
    versions = file_versions.get(filename, [])
    
    version_list = []
    for v in versions:
        version_path = os.path.join(VERSION_FOLDER, v['filename'])
        if os.path.exists(version_path):
            size = os.path.getsize(version_path)
            version_list.append({
                'version': v['version'],
                'filename': v['filename'],
                'timestamp': v['timestamp'],
                'size': size
            })
    
    return jsonify({
        'filename': filename,
        'versions': version_list,
        'current_version': len(version_list) + 1
    })

@app.route('/restore-version', methods=['POST'])
@require_auth
def restore_version():
    """Restore a previous version of a file"""
    data = request.json
    filename = data.get('filename')
    version_num = data.get('version')
    
    if not filename or version_num is None:
        return jsonify({'error': 'Missing filename or version'}), 400
    
    versions = file_versions.get(filename, [])
    version_info = next((v for v in versions if v['version'] == version_num), None)
    
    if not version_info:
        return jsonify({'error': 'Version not found'}), 404
    
    version_path = os.path.join(VERSION_FOLDER, version_info['filename'])
    current_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(version_path):
        return jsonify({'error': 'Version file not found'}), 404
    
    # Backup current version before restoring
    if os.path.exists(current_path):
        backup_version = len(versions) + 1
        backup_filename = f"{os.path.splitext(filename)[0]}_v{backup_version}{os.path.splitext(filename)[1]}"
        backup_path = os.path.join(VERSION_FOLDER, backup_filename)
        shutil.copy2(current_path, backup_path)
        
        file_versions[filename].append({
            'version': backup_version,
            'filename': backup_filename,
            'timestamp': datetime.now().isoformat()
        })
    shutil.copy2(version_path, current_path)
    
    return jsonify({
        'success': True,
        'message': f'Restored {filename} to version {version_num}'
    })

@app.route('/upload-folder', methods=['POST'])
@require_auth
def upload_folder():
    """Handle folder upload with multiple files"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    paths = request.form.getlist('paths')  # Relative paths to maintain folder structure
    
    uploaded_files = []
    failed_files = []
    
    for file, relative_path in zip(files, paths):
        try:
            # Secure the relative path
            safe_path = secure_filename(relative_path)
            full_path = os.path.join(UPLOAD_FOLDER, safe_path)
            
            # Create subdirectories if needed
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Save the file
            file.save(full_path)
            uploaded_files.append(safe_path)
            
            with stats_lock:
                stats['total_uploads'] += 1
                stats['total_size'] += os.path.getsize(full_path)
                
        except Exception as e:
            failed_files.append({'file': relative_path, 'error': str(e)})
    
    return jsonify({
        'success': True,
        'uploaded': len(uploaded_files),
        'failed': len(failed_files),
        'files': uploaded_files,
        'errors': failed_files
    })

@app.route('/download-progress/<filename>', methods=['GET'])
@require_auth
@limit_bandwidth
def download_with_progress(filename):
    """Download file with progress tracking and bandwidth limiting"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    # Support range requests for resume
    range_header = request.headers.get('Range', None)
    
    # Validate range header - ignore if it's malformed or 'undefined'
    if range_header and (range_header == 'undefined' or not range_header.startswith('bytes=')):
        range_header = None
    
    file_size = os.path.getsize(filepath)
    
    def generate():
        nonlocal filename
        start = 0
        end = file_size - 1
        
        if range_header:
            # Parse range header: bytes=start-end
            byte_range = range_header.replace('bytes=', '').split('-')
            try:
                start = int(byte_range[0]) if byte_range[0] and byte_range[0] != 'undefined' else 0
                end = int(byte_range[1]) if byte_range[1] and byte_range[1] != 'undefined' else file_size - 1
            except ValueError:
                # If parsing fails, download full file
                start = 0
                end = file_size - 1
        
        transfer_id = str(hash(filename + str(time.time())))
        bytes_sent = 0
        start_time = time.time()
        
        with open(filepath, 'rb') as f:
            f.seek(start)
            remaining = end - start + 1;
            
            while remaining > 0:
                chunk_size = min(CHUNK_SIZE, remaining)
                chunk = f.read(chunk_size)
                
                if not chunk:
                    break
                
                yield chunk
                bytes_sent += len(chunk)
                remaining -= len(chunk)
                
                # Update speed tracking
                elapsed = time.time() - start_time
                if elapsed > 0:
                    speed = bytes_sent / elapsed
                    active_transfers[transfer_id] = {
                        'filename': filename,
                        'type': 'download',
                        'speed': speed,
                        'bytes': bytes_sent + start,
                        'total': file_size,
                        'progress': ((bytes_sent + start) / file_size) * 100,
                        'timestamp': time.time()
                    }
                
                # Bandwidth limiting
                if BANDWIDTH_LIMIT:
                    time.sleep(len(chunk) / BANDWIDTH_LIMIT)
        
        # Clean up
        if transfer_id in active_transfers:
            del active_transfers[transfer_id]
        
        with stats_lock:
            stats['total_downloads'] += 1
    
    # Build response
    status_code = 206 if range_header else 200
    response = Response(stream_with_context(generate()), status=status_code)
    response.headers['Content-Type'] = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Accept-Ranges'] = 'bytes'
    
    if range_header:
        start = 0
        end = file_size - 1
        byte_range = range_header.replace('bytes=', '').split('-')
        start = int(byte_range[0]) if byte_range[0] else 0
        end = int(byte_range[1]) if byte_range[1] else file_size - 1
        
        response.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response.headers['Content-Length'] = str(end - start + 1)
    else:
        response.headers['Content-Length'] = str(file_size)
    
    return response

@app.route('/compress-files', methods=['POST'])
@require_auth
def compress_files():
    """Compress selected files before downloading"""
    data = request.json
    filenames = data.get('filenames', [])
    
    if not filenames:
        return jsonify({'error': 'No files selected'}), 400
    
    # Create a zip file in memory
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for filename in filenames:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                zf.write(filepath, filename)
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='compressed_files.zip'
    )

@app.route('/api/legacy/settings', methods=['GET', 'POST'])
@require_auth
def manage_legacy_settings():
    """Get or update server settings (legacy endpoint)"""
    global BANDWIDTH_LIMIT, ENABLE_COMPRESSION, ENABLE_AUTH
    
    if request.method == 'GET':
        return jsonify({
            'bandwidth_limit': BANDWIDTH_LIMIT,
            'enable_compression': ENABLE_COMPRESSION,
            'enable_auth': ENABLE_AUTH,
            'enable_ssl': ENABLE_SSL,
            'max_file_size': MAX_FILE_SIZE,
            'chunk_size': CHUNK_SIZE
        })
    
    # POST - update settings
    data = request.json
    
    if 'bandwidth_limit' in data:
        BANDWIDTH_LIMIT = data['bandwidth_limit']
    
    if 'enable_compression' in data:
        ENABLE_COMPRESSION = data['enable_compression']
    
    return jsonify({'success': True, 'message': 'Settings updated'})

# ==================== NETWORK DEVICES ENDPOINT ====================

@app.route('/api/network/devices', methods=['GET'])
def get_network_devices():
    """Scan local subnet for active devices (ping sweep)"""
    import ipaddress
    import threading

    local_ip = get_local_ip()
    net = ipaddress.ip_network(local_ip + '/24', strict=False)
    devices = []
    threads = []
    lock = threading.Lock()

    def ping(ip):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', '-w', '500', str(ip)]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                with lock:
                    devices.append(str(ip))
        except Exception:
            pass

    # Only scan first 50 IPs for speed
    for ip in list(net.hosts())[:50]:
        t = threading.Thread(target=ping, args=(ip,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    return jsonify({'devices': devices, 'local_ip': local_ip})

# ==================== USER ROLE ASSIGNMENT ENDPOINT ====================

@app.route('/api/admin/users/<username>/role', methods=['PUT'])
@require_login
def update_user_role(username):
    """Update a user's role (admin only)"""
    data = request.get_json()
    new_role = data.get('role')
    if new_role not in ['admin', 'user', 'viewer']:
        return jsonify({'error': 'Invalid role'}), 400
    # Only admin can change roles
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_session = auth_system.validate_session(token)
    if not user_session or user_session.get('role') != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    if not auth_system.user_exists(username):
        return jsonify({'error': 'User not found'}), 404
    auth_system.set_user_role(username, new_role)
    return jsonify({'success': True, 'role': new_role})

if __name__ == '__main__':
    # Print startup information
    local_ip = get_local_ip()
    port = 5000
    
    print("\n" + "=" * 60)
    print("🚀 Circuvent Technologies - NetShare Pro v2.0")
    print("   Advanced File Sharing Server")
    print("=" * 60)
    print(f"\n📱 Access from this device: http://localhost:{port}")
    print(f"🌐 Access from network: http://{local_ip}:{port}")
    print(f"\n💡 Scan the QR code on the webpage to access from mobile devices")
    print(f"\n📁 Files are stored in: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"📦 File versions stored in: {os.path.abspath(VERSION_FOLDER)}")
    
    if ENABLE_AUTH:
        print(f"\n🔐 Authentication: ENABLED")
        print(f"   Username: {AUTH_USERNAME}")
        print(f"   Password: {'*' * len(AUTH_PASSWORD)}")
    else:
        print(f"\n🔓 Authentication: DISABLED (use trusted networks only)")
    
    if BANDWIDTH_LIMIT:
        print(f"\n⚡ Bandwidth limit: {format_speed(BANDWIDTH_LIMIT)}")
    else:
        print(f"\n⚡ Bandwidth limit: UNLIMITED")
    
    if ENABLE_SSL:
        print(f"\n🔒 HTTPS: ENABLED")
        print(f"   Certificate: {SSL_CERT_FILE}")
        print(f"   Key: {SSL_KEY_FILE}")
    else:
        print(f"\n🔓 HTTPS: DISABLED")
    
    print("\n" + "=" * 60)
    print()
    
    # Run server with high-speed WebSocket support
    # Note: use_reloader=False is required to prevent port conflicts with SocketIO
    if ENABLE_SSL and os.path.exists(SSL_CERT_FILE) and os.path.exists(SSL_KEY_FILE):
        high_speed.socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=False,  # Disable reloader to prevent port conflicts
            ssl_context=(SSL_CERT_FILE, SSL_KEY_FILE)
        )
    else:
        high_speed.socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=False  # Disable reloader to prevent port conflicts
        )
