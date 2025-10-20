"""
Authentication and Authorization System
Handles user management, sessions, roles, and permissions
"""

import json
import os
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, jsonify

# Database files
USERS_DB = 'data/users.json'
SESSIONS_DB = 'data/sessions.json'
FILE_METADATA_DB = 'data/file_metadata.json'
COMMENTS_DB = 'data/comments.json'
DELETE_REQUESTS_DB = 'data/delete_requests.json'

# Create data directory
os.makedirs('data', exist_ok=True)

# User roles
ROLES = {
    'admin': ['upload', 'download', 'delete', 'delete_any', 'manage_users', 'approve_delete'],
    'user': ['upload', 'download', 'delete_own', 'request_delete'],
    'viewer': ['download']
}

# File permissions
PERMISSIONS = {
    'public': 'Anyone can view and download',
    'private': 'Only owner can access',
    'restricted': 'Only specific users can access'
}

class AuthSystem:
    def __init__(self):
        self.load_databases()
    
    def load_databases(self):
        """Load all databases from JSON files"""
        self.users = self._load_json(USERS_DB, {})
        self.sessions = self._load_json(SESSIONS_DB, {})
        self.file_metadata = self._load_json(FILE_METADATA_DB, {})
        self.comments = self._load_json(COMMENTS_DB, {})
        self.delete_requests = self._load_json(DELETE_REQUESTS_DB, {})
        
        # Create default admin user if no users exist
        if not self.users:
            self.create_user('admin', 'admin123', 'admin', 'Admin User')
    
    def _load_json(self, filepath, default=None):
        """Load JSON file or return default"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except:
            pass
        return default if default is not None else {}
    
    def _save_json(self, filepath, data):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, role='user', display_name=''):
        """Create a new user"""
        if username in self.users:
            return False, "Username already exists"
        
        if role not in ROLES:
            return False, "Invalid role"
        
        self.users[username] = {
            'password': self.hash_password(password),
            'role': role,
            'display_name': display_name or username,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        self._save_json(USERS_DB, self.users)
        return True, "User created successfully"
    
    def authenticate(self, username, password):
        """Authenticate user and create session"""
        if username not in self.users:
            return False, None, "Invalid username or password"
        
        user = self.users[username]
        if user['password'] != self.hash_password(password):
            return False, None, "Invalid username or password"
        
        # Create session token
        session_token = secrets.token_urlsafe(32)
        session_data = {
            'username': username,
            'role': user['role'],
            'display_name': user['display_name'],
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        self.sessions[session_token] = session_data
        self._save_json(SESSIONS_DB, self.sessions)
        
        # Update last login
        self.users[username]['last_login'] = datetime.now().isoformat()
        self._save_json(USERS_DB, self.users)
        
        return True, session_token, "Login successful"
    
    def validate_session(self, token):
        """Validate session token and return user info"""
        if not token:
            return None
            
        if token not in self.sessions:
            return None
        
        session_data = self.sessions[token]
        expires_at = datetime.fromisoformat(session_data['expires_at'])
        
        if datetime.now() > expires_at:
            del self.sessions[token]
            self._save_json(SESSIONS_DB, self.sessions)
            return None
        
        return session_data
    
    def logout(self, token):
        """Logout user by removing session"""
        if token in self.sessions:
            del self.sessions[token]
            self._save_json(SESSIONS_DB, self.sessions)
        return True
    
    def has_permission(self, username, permission):
        """Check if user has specific permission"""
        if username not in self.users:
            return False
        
        role = self.users[username]['role']
        return permission in ROLES.get(role, [])
    
    def add_file_metadata(self, filename, owner, permission='public', allowed_users=None):
        """Add metadata for uploaded file"""
        self.file_metadata[filename] = {
            'owner': owner,
            'created_at': datetime.now().isoformat(),
            'permission': permission,
            'allowed_users': allowed_users or [],
            'size': 0,
            'type': ''
        }
        self._save_json(FILE_METADATA_DB, self.file_metadata)
    
    def get_file_metadata(self, filename):
        """Get file metadata"""
        return self.file_metadata.get(filename, None)
    
    def update_file_permission(self, filename, permission, allowed_users=None):
        """Update file permission"""
        if filename in self.file_metadata:
            self.file_metadata[filename]['permission'] = permission
            if allowed_users is not None:
                self.file_metadata[filename]['allowed_users'] = allowed_users
            self._save_json(FILE_METADATA_DB, self.file_metadata)
            return True
        return False
    
    def can_access_file(self, filename, username):
        """Check if user can access file"""
        metadata = self.get_file_metadata(filename)
        if not metadata:
            return True  # Legacy files without metadata are public
        
        permission = metadata.get('permission', 'public')
        
        if permission == 'public':
            return True
        elif permission == 'private':
            return metadata['owner'] == username
        elif permission == 'restricted':
            return username in metadata.get('allowed_users', []) or metadata['owner'] == username
        
        return False
    
    def can_delete_file(self, filename, username):
        """Check if user can delete file"""
        metadata = self.get_file_metadata(filename)
        
        # Admin can delete anything
        if self.has_permission(username, 'delete_any'):
            return True
        
        # Owner can delete their own files
        if metadata and metadata['owner'] == username:
            return True
        
        return False
    
    def request_delete(self, filename, username, reason=''):
        """Request file deletion"""
        request_id = f"{filename}_{username}_{int(time.time())}"
        self.delete_requests[request_id] = {
            'filename': filename,
            'requester': username,
            'reason': reason,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        self._save_json(DELETE_REQUESTS_DB, self.delete_requests)
        return request_id
    
    def get_delete_requests(self, status=None):
        """Get delete requests, optionally filtered by status"""
        if status:
            return {k: v for k, v in self.delete_requests.items() if v['status'] == status}
        return self.delete_requests
    
    def approve_delete_request(self, request_id, approver):
        """Approve delete request"""
        if request_id in self.delete_requests:
            self.delete_requests[request_id]['status'] = 'approved'
            self.delete_requests[request_id]['approver'] = approver
            self.delete_requests[request_id]['approved_at'] = datetime.now().isoformat()
            self._save_json(DELETE_REQUESTS_DB, self.delete_requests)
            return True
        return False
    
    def reject_delete_request(self, request_id, approver, reason=''):
        """Reject delete request"""
        if request_id in self.delete_requests:
            self.delete_requests[request_id]['status'] = 'rejected'
            self.delete_requests[request_id]['approver'] = approver
            self.delete_requests[request_id]['rejection_reason'] = reason
            self.delete_requests[request_id]['rejected_at'] = datetime.now().isoformat()
            self._save_json(DELETE_REQUESTS_DB, self.delete_requests)
            return True
        return False
    
    def add_comment(self, filename, username, comment, mentions=None):
        """Add comment to file"""
        if filename not in self.comments:
            self.comments[filename] = []
        
        comment_data = {
            'id': len(self.comments[filename]) + 1,
            'username': username,
            'comment': comment,
            'mentions': mentions or [],
            'created_at': datetime.now().isoformat()
        }
        
        self.comments[filename].append(comment_data)
        self._save_json(COMMENTS_DB, self.comments)
        return comment_data
    
    def get_comments(self, filename):
        """Get all comments for a file"""
        return self.comments.get(filename, [])
    
    def get_all_users(self):
        """Get all users (excluding passwords)"""
        users_list = []
        for username, data in self.users.items():
            users_list.append({
                'username': username,
                'display_name': data['display_name'],
                'role': data['role'],
                'created_at': data['created_at'],
                'last_login': data.get('last_login')
            })
        return users_list
    
    def delete_file_metadata(self, filename):
        """Delete file metadata when file is deleted"""
        if filename in self.file_metadata:
            del self.file_metadata[filename]
            self._save_json(FILE_METADATA_DB, self.file_metadata)
        
        if filename in self.comments:
            del self.comments[filename]
            self._save_json(COMMENTS_DB, self.comments)
    
    def delete_user(self, username):
        """Delete a user from the system"""
        if username in self.users:
            del self.users[username]
            self._save_json(USERS_DB, self.users)
            
            # Delete all sessions for this user
            sessions_to_delete = [sid for sid, session in self.sessions.items() 
                                 if session.get('username') == username]
            for sid in sessions_to_delete:
                del self.sessions[sid]
            self._save_json(SESSIONS_DB, self.sessions)
            
            return True
        return False

# Global auth system instance
auth_system = AuthSystem()

def require_login(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for token in Authorization header
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        # Also check for token in cookies
        if not token:
            token = request.cookies.get('authToken')
        
        user_session = auth_system.validate_session(token)
        
        if not user_session:
            # If it's an HTML request, redirect to login
            if request.accept_mimetypes.accept_html:
                from flask import redirect, url_for
                return redirect(url_for('login_page'))
            # If it's an API request, return JSON error
            return jsonify({'error': 'Authentication required'}), 401
        
        # Add user info to request
        request.current_user = user_session
        return f(*args, **kwargs)
    
    return decorated_function

def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if token and token.startswith('Bearer '):
                token = token[7:]
            
            user_session = auth_system.validate_session(token)
            if not user_session:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not auth_system.has_permission(user_session['username'], permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            request.current_user = user_session
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
