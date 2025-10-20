# 🚀 NetShare Pro - Implementation Guide
**Post-Audit Enhancement Implementation**

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Security Enhancements](#security-enhancements)
3. [New Modules](#new-modules)
4. [Database Migration](#database-migration)
5. [Deployment Guide](#deployment-guide)
6. [Testing](#testing)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### 1. Install New Dependencies

```bash
# Install all new dependencies
pip install -r requirements.txt

# For bcrypt on Windows, you might need:
# pip install bcrypt --only-binary :all:
```

### 2. Configure Environment

```bash
# Copy example environment file
copy .env.example .env

# Edit .env with your settings
notepad .env
```

### 3. Generate Secure Secret Key

```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

Copy the output to your `.env` file.

### 4. Run Server

```bash
python app.py
```

---

## 🔒 Security Enhancements

### New Security Module (`security.py`)

The new security module provides:

#### 1. **Secure Password Hashing**

**Old (Insecure):**
```python
# SHA-256 - NO SALT! ❌
password_hash = hashlib.sha256(password.encode()).hexdigest()
```

**New (Secure):**
```python
from security import PasswordHasher

# bcrypt with salt ✅
hashed = PasswordHasher.hash_password(password)
is_valid = PasswordHasher.verify_password(password, hashed)
```

**Features:**
- bcrypt with 12 rounds (preferred)
- PBKDF2-SHA256 with 600,000 iterations (fallback)
- Automatic password hash migration
- Timing-attack resistant verification

#### 2. **Password Validation**

```python
from security import PasswordValidator

# Validate password strength
is_valid, message = PasswordValidator.validate_password(password)

if not is_valid:
    return jsonify({'error': message}), 400
```

**Enforces:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Checks against common passwords

#### 3. **Username Validation**

```python
from security import UsernameValidator

is_valid, message = UsernameValidator.validate_username(username)
```

**Rules:**
- 3-30 characters
- Alphanumeric, hyphens, underscores only
- No reserved names (admin, root, system, etc.)

#### 4. **File Validation**

```python
from security import FileValidator

# Validate filename
is_valid, msg = FileValidator.validate_filename(filename)

# Validate extension
is_valid, msg = FileValidator.validate_file_extension(filename, allowed_extensions)

# Check for dangerous files
if FileValidator.is_dangerous_file(filename):
    return jsonify({'error': 'Dangerous file type'}), 400
```

#### 5. **Security Headers**

```python
from security import SecurityHeaders

headers = SecurityHeaders.get_security_headers()
csp = SecurityHeaders.get_csp_header()

@app.after_request
def add_security_headers(response):
    for key, value in headers.items():
        response.headers[key] = value
    response.headers['Content-Security-Policy'] = csp
    return response
```

#### 6. **Rate Limiting**

```python
from security import rate_limiter

# Check rate limit
is_allowed, seconds_remaining = rate_limiter.check_rate_limit(
    identifier=request.remote_addr,
    max_attempts=5,
    window_seconds=60
)

if not is_allowed:
    return jsonify({'error': f'Rate limit exceeded. Try again in {seconds_remaining}s'}), 429
```

#### 7. **Input Sanitization**

```python
from security import sanitize_input

# Sanitize user input
clean_text = sanitize_input(user_input, max_length=1000)
```

---

## 📝 New Modules

### 1. Configuration Module (`config.py`)

Centralizes all configuration with environment variable support:

```python
from config import get_config

# Load configuration
app.config.from_object(get_config())

# Or specific environment
app.config.from_object(get_config('production'))
```

**Environments:**
- `development` - Debug mode, no rate limits
- `production` - Strict security, HTTPS required
- `testing` - In-memory DB, CSRF disabled

**Key Features:**
- Environment-based configuration
- Secure defaults
- All settings from environment variables
- Validation of required settings

### 2. Logging Module (`logger.py`)

Comprehensive logging system with multiple specialized loggers:

#### Application Logger

```python
from logger import app_logger

app_logger.info("Server started successfully")
app_logger.error("Database connection failed", error=str(e))
app_logger.debug("Processing file upload", filename=filename)
```

#### Security Logger

```python
from logger import security_logger

# Authentication events
security_logger.log_login_success(username)
security_logger.log_login_failure(username, reason="Invalid password")
security_logger.log_logout(username)

# File events
security_logger.log_file_upload(filename, size, username)
security_logger.log_file_download(filename, username)
security_logger.log_file_deleted(filename, username)

# Security events
security_logger.log_unauthorized_access(resource, username)
security_logger.log_rate_limit_exceeded(identifier)
security_logger.log_suspicious_activity(activity, details)
```

#### Audit Logger

```python
from logger import audit_logger

# Log compliance events
audit_logger.log_event('user_created', {
    'username': username,
    'role': role,
    'created_by': current_user
})
```

#### Performance Logger

```python
from logger import perf_logger

# Log request performance
perf_logger.log_request(endpoint, method, duration_ms, status_code)

# Log file transfer performance
perf_logger.log_file_transfer(filename, 'upload', size, duration, speed_mbps)
```

**Log Files Created:**
- `logs/netshare.log` - Application logs (10MB rotation)
- `logs/errors.log` - Error logs only
- `logs/security.log` - Security events (10MB rotation)
- `logs/audit.log` - Audit trail (daily rotation, 365 days retention)
- `logs/performance.log` - Performance metrics (50MB rotation)

**Log Format:**
- JSON structured logging for easy parsing
- Timestamp (UTC)
- Log level
- Message
- Context (user, IP, resource, etc.)
- Exception traceback if applicable

---

## 🔄 Database Migration

### Current State
- JSON files (`data/users.json`, `data/sessions.json`, etc.)
- File I/O on every request
- No transactions
- Race conditions possible

### Migration Plan

#### Phase 1: Add SQLAlchemy Models

Create `models.py`:

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    display_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    storage_used = db.Column(db.BigInteger, default=0)
    storage_quota = db.Column(db.BigInteger, default=10*1024*1024*1024)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45))

class FileMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    mime_type = db.Column(db.String(100))
    permission = db.Column(db.String(20), default='public')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)
```

#### Phase 2: Migration Script

```python
# migrate_to_db.py
import json
from app import app, db
from models import User, FileMetadata

def migrate():
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Migrate users
        with open('data/users.json') as f:
            users = json.load(f)
        
        for username, data in users.items():
            user = User(
                username=username,
                password_hash=data['password'],
                role=data['role'],
                display_name=data['display_name'],
                created_at=datetime.fromisoformat(data['created_at'])
            )
            db.session.add(user)
        
        # Migrate file metadata
        with open('data/file_metadata.json') as f:
            files = json.load(f)
        
        for filename, data in files.items():
            file_meta = FileMetadata(
                filename=filename,
                owner_id=User.query.filter_by(username=data['owner']).first().id,
                size=data.get('size', 0),
                permission=data.get('permission', 'public')
            )
            db.session.add(file_meta)
        
        db.session.commit()
        print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
```

#### Phase 3: Update Code

Replace JSON operations with database queries:

**Old:**
```python
users = json.load(open('users.json'))
if username in users:
    ...
```

**New:**
```python
user = User.query.filter_by(username=username).first()
if user:
    ...
```

---

## 🚢 Deployment Guide

### Production Deployment Checklist

#### 1. Security

- [ ] Change `SECRET_KEY` to secure random value
- [ ] Set `SESSION_COOKIE_SECURE=True` (requires HTTPS)
- [ ] Set `DEBUG=False`
- [ ] Set `FLASK_ENV=production`
- [ ] Update `CORS_ALLOWED_ORIGINS` to specific domains
- [ ] Generate SSL certificates or use Let's Encrypt
- [ ] Change default admin password
- [ ] Set up firewall rules (allow only 80, 443)
- [ ] Enable rate limiting with Redis
- [ ] Set up fail2ban for IP blocking

#### 2. Performance

- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up Redis for caching and sessions
- [ ] Configure Nginx as reverse proxy
- [ ] Enable gzip compression
- [ ] Set up CDN for static files
- [ ] Configure Celery for background tasks

#### 3. Reliability

- [ ] Set up process manager (systemd or supervisor)
- [ ] Configure automatic restart on crash
- [ ] Set up log rotation
- [ ] Configure database backups
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure health checks
- [ ] Set up alerting

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/netshare
upstream netshare {
    server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name netshare.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name netshare.example.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/netshare.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/netshare.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Max upload size
    client_max_body_size 1024M;
    
    # Static files
    location /static {
        alias /var/www/netshare/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # WebSocket support
    location /socket.io {
        proxy_pass http://netshare;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
    
    # Application
    location / {
        proxy_pass http://netshare;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

### Systemd Service

```ini
# /etc/systemd/system/netshare.service
[Unit]
Description=NetShare Pro File Sharing Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=netshare
Group=netshare
WorkingDirectory=/opt/netshare
Environment="PATH=/opt/netshare/venv/bin"
EnvironmentFile=/opt/netshare/.env
ExecStart=/opt/netshare/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=netshare

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/netshare/shared_files /opt/netshare/logs

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable netshare
sudo systemctl start netshare
sudo systemctl status netshare
```

---

## 🧪 Testing

### Unit Tests

Create `tests/test_security.py`:

```python
import pytest
from security import PasswordHasher, PasswordValidator, FileValidator

def test_password_hashing():
    password = "SecurePass123!"
    hashed = PasswordHasher.hash_password(password)
    
    assert PasswordHasher.verify_password(password, hashed)
    assert not PasswordHasher.verify_password("wrong", hashed)

def test_password_validation():
    # Valid password
    valid, msg = PasswordValidator.validate_password("SecurePass123!")
    assert valid
    
    # Too short
    valid, msg = PasswordValidator.validate_password("Short1!")
    assert not valid
    
    # No uppercase
    valid, msg = PasswordValidator.validate_password("securepass123!")
    assert not valid

def test_file_validation():
    # Valid filename
    valid, msg = FileValidator.validate_filename("document.pdf")
    assert valid
    
    # Path traversal
    valid, msg = FileValidator.validate_filename("../etc/passwd")
    assert not valid
    
    # Dangerous file
    assert FileValidator.is_dangerous_file("malware.exe")
```

Run tests:
```bash
pytest tests/ --cov=. --cov-report=html
```

---

## 📊 Monitoring

### Prometheus Metrics

Add to `app.py`:

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Custom metrics
metrics.info('app_info', 'NetShare Pro', version='2.1')

# Add custom metrics
upload_counter = metrics.counter(
    'file_uploads_total', 'Total file uploads',
    labels={'status': lambda r: r.status_code}
)

@app.route('/upload', methods=['POST'])
@upload_counter
def upload_file():
    ...
```

### Health Check Endpoint

```python
@app.route('/health')
def health_check():
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'disk_space': check_disk_space(),
        'memory': check_memory()
    }
    
    status = 'healthy' if all(checks.values()) else 'unhealthy'
    code = 200 if status == 'healthy' else 503
    
    return jsonify({
        'status': status,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }), code
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "bcrypt not available"

**Solution:**
```bash
pip install bcrypt --only-binary :all:
```

#### 2. "Rate limit storage connection failed"

**Solution:** Install and start Redis:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Windows
# Download Redis from https://github.com/microsoftarchive/redis/releases
```

#### 3. "Database locked" (SQLite)

**Solution:** Migrate to PostgreSQL for production or use WAL mode:
```python
db.engine.execute('PRAGMA journal_mode=WAL')
```

#### 4. "Permission denied" on upload

**Solution:** Check folder permissions:
```bash
chmod -R 755 shared_files/
chown -R netshare:netshare shared_files/
```

#### 5. "WebSocket connection failed"

**Solution:** Check Nginx WebSocket configuration and firewall rules.

---

## 📚 Next Steps

1. **Immediate:**
   - Run security audit
   - Change default credentials
   - Configure .env file
   - Test all endpoints

2. **Short-term:**
   - Migrate to database
   - Set up monitoring
   - Configure backups
   - Write unit tests

3. **Long-term:**
   - Implement 2FA
   - Add OAuth login
   - Create mobile app
   - Develop desktop client

---

## 📞 Support

For issues or questions:
- Check the logs in `logs/` directory
- Review AUDIT_REPORT.md for known issues
- Check GitHub issues
- Contact: [Your Support Email]

---

**Made with ❤️ for Circuvent Technologies**
