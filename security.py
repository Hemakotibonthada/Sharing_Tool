"""
Enhanced Security Module
Provides secure password hashing, validation, and security utilities
"""

import re
import secrets
import hashlib
from typing import Tuple, Optional
from datetime import datetime, timedelta

# Try to import bcrypt, fallback to pbkdf2 if not available
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    import hashlib
    import base64


class PasswordHasher:
    """Secure password hashing with bcrypt or PBKDF2"""
    
    BCRYPT_ROUNDS = 12
    PBKDF2_ITERATIONS = 600000  # OWASP recommendation
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password securely using bcrypt (preferred) or PBKDF2
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        if BCRYPT_AVAILABLE:
            # Use bcrypt (best practice)
            salt = bcrypt.gensalt(rounds=PasswordHasher.BCRYPT_ROUNDS)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return f"bcrypt${hashed.decode('utf-8')}"
        else:
            # Fallback to PBKDF2-SHA256 with salt
            salt = secrets.token_bytes(32)
            key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                PasswordHasher.PBKDF2_ITERATIONS
            )
            salt_b64 = base64.b64encode(salt).decode('utf-8')
            key_b64 = base64.b64encode(key).decode('utf-8')
            return f"pbkdf2${salt_b64}${key_b64}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against a hash
        
        Args:
            password: Plain text password to verify
            hashed: Stored hash
            
        Returns:
            True if password matches, False otherwise
        """
        if hashed.startswith('bcrypt$'):
            # bcrypt hash
            if not BCRYPT_AVAILABLE:
                raise RuntimeError("bcrypt not available but bcrypt hash detected")
            stored_hash = hashed[7:].encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        
        elif hashed.startswith('pbkdf2$'):
            # PBKDF2 hash
            parts = hashed.split('$')
            if len(parts) != 3:
                return False
            salt = base64.b64decode(parts[1])
            stored_key = base64.b64decode(parts[2])
            
            key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                PasswordHasher.PBKDF2_ITERATIONS
            )
            return secrets.compare_digest(key, stored_key)
        
        else:
            # Legacy SHA-256 (insecure, for migration only)
            legacy_hash = hashlib.sha256(password.encode()).hexdigest()
            return secrets.compare_digest(legacy_hash, hashed)
    
    @staticmethod
    def needs_rehash(hashed: str) -> bool:
        """Check if password hash needs to be updated"""
        # Rehash if it's not bcrypt or PBKDF2
        return not (hashed.startswith('bcrypt$') or hashed.startswith('pbkdf2$'))


class PasswordValidator:
    """Password strength validation"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < PasswordValidator.MIN_LENGTH:
            return False, f"Password must be at least {PasswordValidator.MIN_LENGTH} characters"
        
        if len(password) > PasswordValidator.MAX_LENGTH:
            return False, f"Password must be at most {PasswordValidator.MAX_LENGTH} characters"
        
        # Check for at least one uppercase
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for at least one lowercase
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
    
    @staticmethod
    def is_common_password(password: str) -> bool:
        """Check against common passwords"""
        # Top 20 most common passwords
        common_passwords = {
            'password', '123456', '12345678', 'qwerty', 'abc123',
            'monkey', '1234567', 'letmein', 'trustno1', 'dragon',
            'baseball', '111111', 'iloveyou', 'master', 'sunshine',
            'ashley', 'bailey', 'passw0rd', 'shadow', '123123'
        }
        return password.lower() in common_passwords


class UsernameValidator:
    """Username validation"""
    
    MIN_LENGTH = 3
    MAX_LENGTH = 30
    PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(username) < UsernameValidator.MIN_LENGTH:
            return False, f"Username must be at least {UsernameValidator.MIN_LENGTH} characters"
        
        if len(username) > UsernameValidator.MAX_LENGTH:
            return False, f"Username must be at most {UsernameValidator.MAX_LENGTH} characters"
        
        if not UsernameValidator.PATTERN.match(username):
            return False, "Username can only contain letters, numbers, hyphens, and underscores"
        
        # Reserved usernames
        reserved = {'admin', 'root', 'system', 'administrator', 'guest', 'anonymous'}
        if username.lower() in reserved:
            return False, "Username is reserved"
        
        return True, "Username is valid"


class TokenGenerator:
    """Secure token generation"""
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(48)
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate a password reset token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_share_token() -> str:
        """Generate a file sharing token"""
        return secrets.token_urlsafe(16)


class FileValidator:
    """File upload validation"""
    
    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, str]:
        """
        Validate filename for security
        
        Args:
            filename: Filename to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "Filename cannot be empty"
        
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Invalid filename (path traversal detected)"
        
        # Check for null bytes
        if '\x00' in filename:
            return False, "Invalid filename (null byte detected)"
        
        # Check for control characters
        if any(ord(c) < 32 for c in filename):
            return False, "Invalid filename (control characters detected)"
        
        return True, "Filename is valid"
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: set) -> Tuple[bool, str]:
        """
        Validate file extension
        
        Args:
            filename: Filename to check
            allowed_extensions: Set of allowed extensions (e.g., {'pdf', 'jpg'})
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if '.' not in filename:
            return False, "File must have an extension"
        
        extension = filename.rsplit('.', 1)[1].lower()
        
        if extension not in allowed_extensions:
            return False, f"File type .{extension} not allowed"
        
        return True, "File extension is valid"
    
    @staticmethod
    def is_dangerous_file(filename: str) -> bool:
        """Check for potentially dangerous files"""
        dangerous_extensions = {
            'exe', 'bat', 'cmd', 'sh', 'bash', 'ps1', 'vbs', 'js',
            'jar', 'app', 'dmg', 'pkg', 'deb', 'rpm', 'msi'
        }
        
        if '.' in filename:
            extension = filename.rsplit('.', 1)[1].lower()
            return extension in dangerous_extensions
        
        return False


class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_security_headers() -> dict:
        """Get recommended security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
    
    @staticmethod
    def get_csp_header(nonce: Optional[str] = None) -> str:
        """Generate Content Security Policy header"""
        csp_directives = [
            "default-src 'self'",
            f"script-src 'self' {'nonce-' + nonce if nonce else ''} cdn.socket.io cdn.jsdelivr.net cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' cdnjs.cloudflare.com fonts.googleapis.com",
            "font-src 'self' cdnjs.cloudflare.com fonts.gstatic.com",
            "img-src 'self' data: blob:",
            "connect-src 'self' ws: wss:",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests"
        ]
        return "; ".join(csp_directives)


class RateLimitTracker:
    """Simple in-memory rate limit tracker"""
    
    def __init__(self):
        self.attempts = {}
        self.lockouts = {}
    
    def check_rate_limit(self, identifier: str, max_attempts: int, window_seconds: int) -> Tuple[bool, Optional[int]]:
        """
        Check if identifier is rate limited
        
        Args:
            identifier: IP address or username
            max_attempts: Maximum attempts allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, seconds_until_reset)
        """
        now = datetime.now()
        
        # Check if currently locked out
        if identifier in self.lockouts:
            lockout_until = self.lockouts[identifier]
            if now < lockout_until:
                seconds_remaining = int((lockout_until - now).total_seconds())
                return False, seconds_remaining
            else:
                # Lockout expired
                del self.lockouts[identifier]
                if identifier in self.attempts:
                    del self.attempts[identifier]
        
        # Clean old attempts
        if identifier in self.attempts:
            self.attempts[identifier] = [
                timestamp for timestamp in self.attempts[identifier]
                if (now - timestamp).total_seconds() < window_seconds
            ]
        else:
            self.attempts[identifier] = []
        
        # Check if limit exceeded
        if len(self.attempts[identifier]) >= max_attempts:
            # Lock out for window_seconds
            self.lockouts[identifier] = now + timedelta(seconds=window_seconds)
            return False, window_seconds
        
        # Record attempt
        self.attempts[identifier].append(now)
        return True, None


# Global rate limiter instance
rate_limiter = RateLimitTracker()


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent XSS"""
    if not text:
        return ""
    
    # Truncate
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters except newline and tab
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text.strip()


def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, session_token: str) -> bool:
    """Verify CSRF token"""
    return secrets.compare_digest(token, session_token)
