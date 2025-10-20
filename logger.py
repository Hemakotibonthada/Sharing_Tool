"""
Logging Module for NetShare Pro
Provides structured logging with rotation, security event tracking, and audit logs
"""

import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, g


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user'):
            log_data['user'] = record.user
        if hasattr(record, 'ip'):
            log_data['ip'] = record.ip
        if hasattr(record, 'action'):
            log_data['action'] = record.action
        if hasattr(record, 'resource'):
            log_data['resource'] = record.resource
        
        return json.dumps(log_data)


class SecurityLogger:
    """Security event logger"""
    
    def __init__(self, log_dir='logs'):
        os.makedirs(log_dir, exist_ok=True)
        
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Security log file with rotation
        security_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'security.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        security_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(security_handler)
    
    def _log_event(self, level: str, event_type: str, message: str, **kwargs):
        """Log security event with context"""
        extra = {
            'action': event_type,
            'ip': kwargs.get('ip', self._get_client_ip()),
            'user': kwargs.get('user', self._get_current_user()),
            'resource': kwargs.get('resource'),
        }
        
        # Add any additional context
        for key, value in kwargs.items():
            if key not in ['ip', 'user', 'resource']:
                extra[key] = value
        
        log_func = getattr(self.logger, level.lower())
        log_func(message, extra=extra)
    
    def _get_client_ip(self) -> Optional[str]:
        """Get client IP address"""
        try:
            return request.headers.get('X-Forwarded-For', request.remote_addr)
        except:
            return None
    
    def _get_current_user(self) -> Optional[str]:
        """Get current username"""
        try:
            return getattr(g, 'current_user', {}).get('username')
        except:
            return None
    
    # Authentication Events
    def log_login_success(self, username: str, **kwargs):
        """Log successful login"""
        self._log_event('info', 'login_success', 
                       f"User {username} logged in successfully",
                       user=username, **kwargs)
    
    def log_login_failure(self, username: str, reason: str, **kwargs):
        """Log failed login attempt"""
        self._log_event('warning', 'login_failure',
                       f"Failed login attempt for {username}: {reason}",
                       user=username, reason=reason, **kwargs)
    
    def log_logout(self, username: str, **kwargs):
        """Log logout"""
        self._log_event('info', 'logout',
                       f"User {username} logged out",
                       user=username, **kwargs)
    
    def log_session_expired(self, username: str, **kwargs):
        """Log session expiration"""
        self._log_event('info', 'session_expired',
                       f"Session expired for {username}",
                       user=username, **kwargs)
    
    # User Management Events
    def log_user_created(self, username: str, role: str, created_by: str, **kwargs):
        """Log user creation"""
        self._log_event('info', 'user_created',
                       f"User {username} created with role {role} by {created_by}",
                       user=created_by, target_user=username, role=role, **kwargs)
    
    def log_user_deleted(self, username: str, deleted_by: str, **kwargs):
        """Log user deletion"""
        self._log_event('warning', 'user_deleted',
                       f"User {username} deleted by {deleted_by}",
                       user=deleted_by, target_user=username, **kwargs)
    
    def log_password_changed(self, username: str, **kwargs):
        """Log password change"""
        self._log_event('info', 'password_changed',
                       f"Password changed for {username}",
                       user=username, **kwargs)
    
    def log_role_changed(self, username: str, old_role: str, new_role: str, changed_by: str, **kwargs):
        """Log role change"""
        self._log_event('warning', 'role_changed',
                       f"Role changed for {username} from {old_role} to {new_role} by {changed_by}",
                       user=changed_by, target_user=username, 
                       old_role=old_role, new_role=new_role, **kwargs)
    
    # File Events
    def log_file_upload(self, filename: str, size: int, username: str, **kwargs):
        """Log file upload"""
        self._log_event('info', 'file_upload',
                       f"File {filename} ({size} bytes) uploaded by {username}",
                       user=username, resource=filename, size=size, **kwargs)
    
    def log_file_download(self, filename: str, username: str, **kwargs):
        """Log file download"""
        self._log_event('info', 'file_download',
                       f"File {filename} downloaded by {username}",
                       user=username, resource=filename, **kwargs)
    
    def log_file_deleted(self, filename: str, username: str, **kwargs):
        """Log file deletion"""
        self._log_event('warning', 'file_deleted',
                       f"File {filename} deleted by {username}",
                       user=username, resource=filename, **kwargs)
    
    def log_file_permission_changed(self, filename: str, old_perm: str, new_perm: str, username: str, **kwargs):
        """Log file permission change"""
        self._log_event('info', 'permission_changed',
                       f"Permission for {filename} changed from {old_perm} to {new_perm} by {username}",
                       user=username, resource=filename,
                       old_permission=old_perm, new_permission=new_perm, **kwargs)
    
    # Security Events
    def log_unauthorized_access(self, resource: str, username: Optional[str] = None, **kwargs):
        """Log unauthorized access attempt"""
        user_info = username or "anonymous"
        self._log_event('warning', 'unauthorized_access',
                       f"Unauthorized access attempt to {resource} by {user_info}",
                       user=username, resource=resource, **kwargs)
    
    def log_rate_limit_exceeded(self, identifier: str, **kwargs):
        """Log rate limit exceeded"""
        self._log_event('warning', 'rate_limit_exceeded',
                       f"Rate limit exceeded for {identifier}",
                       user=identifier, **kwargs)
    
    def log_suspicious_activity(self, activity: str, details: str, **kwargs):
        """Log suspicious activity"""
        self._log_event('error', 'suspicious_activity',
                       f"Suspicious activity detected: {activity} - {details}",
                       activity=activity, details=details, **kwargs)
    
    def log_csrf_failure(self, **kwargs):
        """Log CSRF token validation failure"""
        self._log_event('warning', 'csrf_failure',
                       "CSRF token validation failed",
                       **kwargs)
    
    def log_path_traversal_attempt(self, path: str, **kwargs):
        """Log path traversal attempt"""
        self._log_event('error', 'path_traversal',
                       f"Path traversal attempt detected: {path}",
                       path=path, **kwargs)


class ApplicationLogger:
    """Application logger for general events"""
    
    def __init__(self, name='netshare', log_dir='logs', log_level='INFO'):
        os.makedirs(log_dir, exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'netshare.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        # Error log
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'errors.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)


class AuditLogger:
    """Audit logger for compliance and tracking"""
    
    def __init__(self, log_dir='logs'):
        os.makedirs(log_dir, exist_ok=True)
        
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # Daily rotating audit log
        audit_handler = logging.handlers.TimedRotatingFileHandler(
            os.path.join(log_dir, 'audit.log'),
            when='midnight',
            interval=1,
            backupCount=365  # Keep 1 year of audit logs
        )
        audit_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(audit_handler)
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log audit event"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'user': getattr(g, 'current_user', {}).get('username', 'anonymous'),
            'ip': request.headers.get('X-Forwarded-For', request.remote_addr) if hasattr(request, 'remote_addr') else None,
            **details
        }
        self.logger.info(json.dumps(audit_entry))


# Performance logger
class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self, log_dir='logs'):
        os.makedirs(log_dir, exist_ok=True)
        
        self.logger = logging.getLogger('performance')
        self.logger.setLevel(logging.INFO)
        
        # Performance log with rotation
        perf_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'performance.log'),
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=5
        )
        perf_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(perf_handler)
    
    def log_request(self, endpoint: str, method: str, duration_ms: float, status_code: int, **kwargs):
        """Log HTTP request performance"""
        extra = {
            'endpoint': endpoint,
            'method': method,
            'duration_ms': round(duration_ms, 2),
            'status_code': status_code,
            **kwargs
        }
        self.logger.info(f"{method} {endpoint} {status_code} {duration_ms:.2f}ms", extra=extra)
    
    def log_file_transfer(self, filename: str, operation: str, size: int, duration_s: float, speed_mbps: float):
        """Log file transfer performance"""
        extra = {
            'filename': filename,
            'operation': operation,
            'size_bytes': size,
            'duration_s': round(duration_s, 2),
            'speed_mbps': round(speed_mbps, 2)
        }
        self.logger.info(f"Transfer {operation}: {filename} at {speed_mbps:.2f} Mbps", extra=extra)


# Decorator for logging function calls
def log_function_call(logger):
    """Decorator to log function calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args} kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned successfully")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {str(e)}")
                raise
        return wrapper
    return decorator


# Initialize global loggers
security_logger = SecurityLogger()
app_logger = ApplicationLogger()
audit_logger = AuditLogger()
perf_logger = PerformanceLogger()
