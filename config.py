"""
Configuration Management for NetShare Pro
Centralizes all configuration with environment variable support
"""

import os
from datetime import timedelta

class Config:
    """Base configuration with secure defaults"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # File Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'shared_files')
    VERSION_FOLDER = os.environ.get('VERSION_FOLDER', 'file_versions')
    TEMP_FOLDER = os.environ.get('TEMP_FOLDER', 'temp_uploads')
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 1 * 1024 * 1024 * 1024 * 1024))  # 1TB
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'pdf,png,jpg,jpeg,gif,zip,rar,doc,docx,xls,xlsx,ppt,pptx,txt,mp4,mp3,avi,mov').split(','))
    
    # Transfer Settings
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', 8 * 1024 * 1024))  # 8MB
    BANDWIDTH_LIMIT = int(os.environ.get('BANDWIDTH_LIMIT', 0)) or None  # 0 = unlimited
    ENABLE_COMPRESSION = os.environ.get('ENABLE_COMPRESSION', 'False') == 'True'
    
    # Server
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5001))
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    
    # SSL
    ENABLE_SSL = os.environ.get('ENABLE_SSL', 'False') == 'True'
    SSL_CERT_FILE = os.environ.get('SSL_CERT_FILE', 'cert.pem')
    SSL_KEY_FILE = os.environ.get('SSL_KEY_FILE', 'key.pem')
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True') == 'True'
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100 per hour')
    RATELIMIT_LOGIN_ATTEMPTS = os.environ.get('RATELIMIT_LOGIN_ATTEMPTS', '5 per minute')
    
    # Database (for future migration)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///netshare.db')
    
    # Redis (for caching)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')  # 'redis' for production
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'netshare.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # Email (for notifications)
    SMTP_SERVER = os.environ.get('SMTP_SERVER', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'True') == 'True'
    EMAIL_FROM = os.environ.get('EMAIL_FROM', 'noreply@netshare.local')
    
    # Security Headers
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '*').split(',')
    CSP_POLICY = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'", 'cdn.socket.io', 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com'],
        'style-src': ["'self'", "'unsafe-inline'", 'cdnjs.cloudflare.com', 'fonts.googleapis.com'],
        'font-src': ["'self'", 'cdnjs.cloudflare.com', 'fonts.gstatic.com'],
        'img-src': ["'self'", 'data:', 'blob:'],
        'connect-src': ["'self'", 'ws:', 'wss:'],
    }
    
    # Storage Quotas
    DEFAULT_USER_QUOTA = int(os.environ.get('DEFAULT_USER_QUOTA', 10 * 1024 * 1024 * 1024))  # 10GB
    ADMIN_USER_QUOTA = int(os.environ.get('ADMIN_USER_QUOTA', 100 * 1024 * 1024 * 1024))  # 100GB
    
    # File Expiration
    FILE_EXPIRATION_DAYS = int(os.environ.get('FILE_EXPIRATION_DAYS', 0))  # 0 = never expire
    
    # Monitoring
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'True') == 'True'
    METRICS_PORT = int(os.environ.get('METRICS_PORT', 9090))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    RATELIMIT_ENABLED = False  # Disable rate limiting in dev
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration with stricter security"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    RATELIMIT_ENABLED = True
    LOG_LEVEL = 'WARNING'
    CACHE_TYPE = 'redis'  # Use Redis in production


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    DATABASE_URL = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    env = env or os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
