import os
import socket
import qrcode
import io
import base64
import json
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory, Response, stream_with_context
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

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'shared_files'
VERSION_FOLDER = 'file_versions'
TEMP_FOLDER = 'temp_uploads'
MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024 * 1024  # 1TB
CHUNK_SIZE = 8192 * 1024  # 8MB chunks for faster transfer
BANDWIDTH_LIMIT = None  # None = unlimited, or set bytes per second (e.g., 1024*1024 for 1MB/s)
ENABLE_COMPRESSION = False  # Enable auto-compression before upload
ENABLE_AUTH = False  # Set to True to enable basic authentication
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

@app.route('/upload', methods=['POST'])
@require_auth
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
        
        file_info = get_file_info(filename)
        file_info['upload_speed'] = format_speed(speed)
        file_info['resumed'] = resume_offset > 0
        file_info['compressed'] = enable_compression and ENABLE_COMPRESSION
        file_info['versioned'] = enable_versioning
        
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
    """List all shared files"""
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filepath):
            files.append(get_file_info(filename))
    
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
def delete_file(filename):
    """Delete a file"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            os.remove(filepath)
            stats['total_size'] -= file_size
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
        'total_uploads': stats['total_uploads'],
        'total_downloads': stats['total_downloads'],
        'active_connections': stats['active_connections']
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
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
    return jsonify({
        'active_uploads': len(active_transfers['uploads']),
        'active_downloads': len(active_transfers['downloads']),
        'upload_speed': format_speed(stats.get('upload_speed', 0)),
        'download_speed': format_speed(stats.get('download_speed', 0))
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
    file_size = os.path.getsize(filepath)
    
    def generate():
        nonlocal filename
        start = 0
        end = file_size - 1
        
        if range_header:
            # Parse range header: bytes=start-end
            byte_range = range_header.replace('bytes=', '').split('-')
            start = int(byte_range[0]) if byte_range[0] else 0
            end = int(byte_range[1]) if byte_range[1] else file_size - 1
        
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

@app.route('/settings', methods=['GET', 'POST'])
@require_auth
def manage_settings():
    """Get or update server settings"""
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

if __name__ == '__main__':
    # Print startup information
    local_ip = get_local_ip()
    port = 5000
    
    print("\n" + "=" * 60)
    print("🚀 NetShare Pro v2.0 - Advanced File Sharing Server")
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
    
    # Run server with SSL if enabled
    if ENABLE_SSL and os.path.exists(SSL_CERT_FILE) and os.path.exists(SSL_KEY_FILE):
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            ssl_context=(SSL_CERT_FILE, SSL_KEY_FILE)
        )
    else:
        app.run(host='0.0.0.0', port=port, debug=True)
