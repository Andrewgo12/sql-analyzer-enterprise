#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - SECURITY MANAGER
Comprehensive security system with logging, audit trails, and access control
"""

import os
import json
import hashlib
import secrets
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
from cryptography.fernet import Fernet

class UserRole(Enum):
    """User role definitions."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"

class SecurityLevel(Enum):
    """Security level definitions."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class User:
    """User data structure."""
    user_id: str
    username: str
    email: str
    role: UserRole
    created_at: datetime.datetime
    last_login: Optional[datetime.datetime] = None
    is_active: bool = True
    failed_login_attempts: int = 0
    password_hash: str = ""

@dataclass
class AuditEvent:
    """Audit event data structure."""
    event_id: str
    user_id: str
    action: str
    resource: str
    timestamp: datetime.datetime
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any]

class SecurityManager:
    """Comprehensive security management system."""
    
    def __init__(self, config_dir: str = "web_app/security"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Security configuration
        self.max_login_attempts = 5
        self.session_timeout = 3600  # 1 hour
        self.password_min_length = 8
        self.jwt_secret = self._get_or_create_jwt_secret()
        self.encryption_key = self._get_or_create_encryption_key()
        
        # Initialize components
        self.setup_logging()
        self.users_db = self._load_users_database()
        self.audit_log = []
        
    def setup_logging(self):
        """Setup comprehensive security logging."""
        log_dir = self.config_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Security log
        security_log = log_dir / f"security_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        
        # Audit log
        audit_log = log_dir / f"audit_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure loggers
        self.security_logger = logging.getLogger('security')
        self.audit_logger = logging.getLogger('audit')
        
        # Security logger setup
        security_handler = logging.FileHandler(security_log)
        security_formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        self.security_logger.addHandler(security_handler)
        self.security_logger.setLevel(logging.INFO)
        
        # Audit logger setup
        audit_handler = logging.FileHandler(audit_log)
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        self.audit_logger.addHandler(audit_handler)
        self.audit_logger.setLevel(logging.INFO)
    
    def _get_or_create_jwt_secret(self) -> str:
        """Get or create JWT secret key."""
        secret_file = self.config_dir / "jwt_secret.key"
        
        if secret_file.exists():
            with open(secret_file, 'r') as f:
                return f.read().strip()
        else:
            secret = secrets.token_urlsafe(32)
            with open(secret_file, 'w') as f:
                f.write(secret)
            os.chmod(secret_file, 0o600)  # Restrict permissions
            return secret
    
    def _get_or_create_encryption_key(self) -> Fernet:
        """Get or create encryption key."""
        key_file = self.config_dir / "encryption.key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
        
        return Fernet(key)
    
    def _load_users_database(self) -> Dict[str, User]:
        """Load users database."""
        users_file = self.config_dir / "users.json"
        
        if users_file.exists():
            with open(users_file, 'r') as f:
                users_data = json.load(f)
                users = {}
                for user_id, user_data in users_data.items():
                    user_data['created_at'] = datetime.datetime.fromisoformat(user_data['created_at'])
                    if user_data.get('last_login'):
                        user_data['last_login'] = datetime.datetime.fromisoformat(user_data['last_login'])
                    user_data['role'] = UserRole(user_data['role'])
                    users[user_id] = User(**user_data)
                return users
        else:
            # Create default admin user
            admin_user = self.create_user(
                username="admin",
                email="admin@sqlanalyzer.com",
                password="admin123",
                role=UserRole.ADMIN
            )
            return {"admin": admin_user}
    
    def _save_users_database(self):
        """Save users database."""
        users_file = self.config_dir / "users.json"
        
        users_data = {}
        for user_id, user in self.users_db.items():
            user_dict = asdict(user)
            user_dict['created_at'] = user.created_at.isoformat()
            if user.last_login:
                user_dict['last_login'] = user.last_login.isoformat()
            user_dict['role'] = user.role.value
            users_data[user_id] = user_dict
        
        with open(users_file, 'w') as f:
            json.dump(users_data, f, indent=2)
        
        os.chmod(users_file, 0o600)  # Restrict permissions
    
    def hash_password(self, password: str) -> str:
        """Hash password securely."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            salt, hash_hex = password_hash.split(':')
            password_hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash_bytes.hex() == hash_hex
        except ValueError:
            return False
    
    def create_user(self, username: str, email: str, password: str, role: UserRole) -> User:
        """Create new user."""
        user_id = secrets.token_urlsafe(16)
        password_hash = self.hash_password(password)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            created_at=datetime.datetime.now(),
            password_hash=password_hash
        )
        
        self.users_db[user_id] = user
        self._save_users_database()
        
        self.security_logger.info(f"User created: {username} ({user_id}) with role {role.value}")
        return user
    
    def authenticate_user(self,
        username: str,
        password: str,
        ip_address: str = "",
        user_agent: str = "") -> Tuple[bool, Optional[str]]:
        """Authenticate user credentials."""
        user = None
        for u in self.users_db.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            self.log_audit_event("LOGIN_FAILED", "", "authentication", ip_address, user_agent, False, 
                               {"reason": "user_not_found", "username": username})
            return False, None
        
        if not user.is_active:
            self.log_audit_event("LOGIN_FAILED", user.user_id, "authentication", ip_address, user_agent, False,
                               {"reason": "account_disabled", "username": username})
            return False, None
        
        if user.failed_login_attempts >= self.max_login_attempts:
            self.log_audit_event("LOGIN_FAILED", user.user_id, "authentication", ip_address, user_agent, False,
                               {"reason": "account_locked", "username": username})
            return False, None
        
        if self.verify_password(password, user.password_hash):
            # Successful login
            user.last_login = datetime.datetime.now()
            user.failed_login_attempts = 0
            self._save_users_database()
            
            # Generate JWT token
            token = self.generate_jwt_token(user)
            
            self.log_audit_event("LOGIN_SUCCESS", user.user_id, "authentication", ip_address, user_agent, True,
                               {"username": username})
            
            return True, token
        else:
            # Failed login
            user.failed_login_attempts += 1
            self._save_users_database()
            
            self.log_audit_event("LOGIN_FAILED", user.user_id, "authentication", ip_address, user_agent, False,
                               {"reason": "invalid_password",
                                   "username": username,
                                   "attempts": user.failed_login_attempts})            
            return False, None
    
    def generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for user."""
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.value,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.session_timeout),
            'iat': datetime.datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {"error": "token_expired"}
        except jwt.InvalidTokenError:
            return False, {"error": "invalid_token"}
    
    def log_audit_event(self, action: str, user_id: str, resource: str, ip_address: str, 
                       user_agent: str, success: bool, details: Dict[str, Any]):
        """Log audit event."""
        event = AuditEvent(
            event_id=secrets.token_urlsafe(16),
            user_id=user_id,
            action=action,
            resource=resource,
            timestamp=datetime.datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details
        )
        
        self.audit_log.append(event)
        
        # Log to file
        audit_message = json.dumps({
            'event_id': event.event_id,
            'user_id': event.user_id,
            'action': event.action,
            'resource': event.resource,
            'timestamp': event.timestamp.isoformat(),
            'ip_address': event.ip_address,
            'user_agent': event.user_agent,
            'success': event.success,
            'details': event.details
        })
        
        self.audit_logger.info(audit_message)
    
    def check_permission(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Check if user has required permission."""
        role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.VIEWER: 1,
            UserRole.ANALYST: 2,
            UserRole.ADMIN: 3
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.encryption_key.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.encryption_key.decrypt(encrypted_data.encode()).decode()

if __name__ == "__main__":
    # Example usage
    security_manager = SecurityManager()
    
    # Test authentication
    success, token = security_manager.authenticate_user("admin", "admin123", "127.0.0.1", "Test Agent")
    
    if success:
        logger.info("✅ Authentication successful. Token: {token[:50]}...")
        
        # Verify token
        valid, payload = security_manager.verify_jwt_token(token)
        if valid:
            logger.info("✅ Token valid. User: {payload['username']}, Role: {payload['role']}")
        else:
            logger.info("❌ Token invalid: {payload}")
    else:
        logger.info("❌ Authentication failed")
    
    logger.info("✅ Security system initialized with {len(security_manager.users_db)} users")
