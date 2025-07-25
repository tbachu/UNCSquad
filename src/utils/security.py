import logging
import os
import hashlib
import secrets
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Manages security and privacy for health data.
    Handles encryption, decryption, and secure storage of sensitive information.
    """
    
    def __init__(self, storage_path: str = "data/security"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Key storage paths
        self.master_key_path = self.storage_path / ".master_key"
        self.salt_path = self.storage_path / ".salt"
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Session management
        self.sessions = {}
        self.session_timeout = timedelta(hours=1)
    
    def _initialize_encryption(self):
        """Initializes or loads encryption keys."""
        if self.master_key_path.exists() and self.salt_path.exists():
            # Load existing keys
            self._load_keys()
        else:
            # Generate new keys
            self._generate_keys()
    
    def _generate_keys(self):
        """Generates new encryption keys."""
        # Generate salt
        self.salt = secrets.token_bytes(32)
        
        # Generate master password (in production, this should be user-provided)
        master_password = os.getenv('HIA_MASTER_PASSWORD', secrets.token_urlsafe(32))
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.cipher_suite = Fernet(key)
        
        # Save keys securely
        self._save_keys(key)
        
        logger.info("Generated new encryption keys")
    
    def _load_keys(self):
        """Loads existing encryption keys."""
        try:
            with open(self.salt_path, 'rb') as f:
                self.salt = f.read()
            
            with open(self.master_key_path, 'rb') as f:
                key = f.read()
            
            self.cipher_suite = Fernet(key)
            logger.info("Loaded existing encryption keys")
            
        except Exception as e:
            logger.error(f"Error loading keys: {str(e)}")
            # Regenerate if loading fails
            self._generate_keys()
    
    def _save_keys(self, key: bytes):
        """Saves encryption keys securely."""
        # Set restrictive permissions
        os.umask(0o077)
        
        with open(self.salt_path, 'wb') as f:
            f.write(self.salt)
        
        with open(self.master_key_path, 'wb') as f:
            f.write(key)
        
        # Set file permissions (Unix-like systems)
        try:
            os.chmod(self.salt_path, 0o600)
            os.chmod(self.master_key_path, 0o600)
        except:
            pass  # Windows doesn't support chmod
    
    def encrypt_data(self, data: Union[str, Dict, bytes]) -> str:
        """
        Encrypts data using Fernet symmetric encryption.
        
        Args:
            data: Data to encrypt (string, dict, or bytes)
            
        Returns:
            Base64 encoded encrypted data
        """
        try:
            # Convert data to bytes
            if isinstance(data, dict):
                data_bytes = json.dumps(data).encode()
            elif isinstance(data, str):
                data_bytes = data.encode()
            else:
                data_bytes = data
            
            # Encrypt
            encrypted = self.cipher_suite.encrypt(data_bytes)
            
            # Return as base64 string for storage
            return base64.urlsafe_b64encode(encrypted).decode()
            
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> Union[str, Dict]:
        """
        Decrypts data encrypted with encrypt_data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted data (string or dict)
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Decrypt
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            
            # Try to parse as JSON first
            try:
                return json.loads(decrypted_bytes.decode())
            except:
                # Return as string if not JSON
                return decrypted_bytes.decode()
                
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise
    
    def hash_sensitive_data(self, data: str) -> str:
        """
        Creates a one-way hash of sensitive data for comparison.
        
        Args:
            data: Sensitive data to hash
            
        Returns:
            SHA-256 hash of the data
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def create_session(self, user_id: str) -> str:
        """
        Creates a new secure session for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session token
        """
        session_token = secrets.token_urlsafe(32)
        
        self.sessions[session_token] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_accessed': datetime.now()
        }
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[str]:
        """
        Validates a session token and returns user ID if valid.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            User ID if valid, None otherwise
        """
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        # Check timeout
        if datetime.now() - session['last_accessed'] > self.session_timeout:
            del self.sessions[session_token]
            return None
        
        # Update last accessed
        session['last_accessed'] = datetime.now()
        
        return session['user_id']
    
    def end_session(self, session_token: str):
        """Ends a user session."""
        if session_token in self.sessions:
            del self.sessions[session_token]
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes a filename to prevent path traversal attacks.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path separators and special characters
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_')
        sanitized = ''.join(c for c in filename if c in safe_chars)
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = 'unnamed_file'
        
        return sanitized
    
    def generate_secure_filename(self, original_filename: str) -> str:
        """
        Generates a secure filename with random component.
        
        Args:
            original_filename: Original filename
            
        Returns:
            Secure filename with random prefix
        """
        sanitized = self.sanitize_filename(original_filename)
        random_prefix = secrets.token_hex(8)
        
        # Extract extension
        parts = sanitized.rsplit('.', 1)
        if len(parts) == 2:
            name, ext = parts
            return f"{random_prefix}_{name}.{ext}"
        else:
            return f"{random_prefix}_{sanitized}"
    
    def encrypt_file(self, file_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Encrypts a file.
        
        Args:
            file_path: Path to file to encrypt
            output_path: Optional output path (defaults to .enc extension)
            
        Returns:
            Path to encrypted file
        """
        if not output_path:
            output_path = file_path.with_suffix(file_path.suffix + '.enc')
        
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.cipher_suite.encrypt(file_data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return output_path
            
        except Exception as e:
            logger.error(f"File encryption error: {str(e)}")
            raise
    
    def decrypt_file(self, encrypted_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Decrypts a file.
        
        Args:
            encrypted_path: Path to encrypted file
            output_path: Optional output path
            
        Returns:
            Path to decrypted file
        """
        if not output_path:
            # Remove .enc extension if present
            if encrypted_path.suffix == '.enc':
                output_path = encrypted_path.with_suffix('')
            else:
                output_path = encrypted_path.with_suffix('.decrypted')
        
        try:
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return output_path
            
        except Exception as e:
            logger.error(f"File decryption error: {str(e)}")
            raise
    
    def create_audit_log(self, action: str, user_id: str, details: Dict[str, Any]):
        """
        Creates an audit log entry for security tracking.
        
        Args:
            action: Action performed
            user_id: User who performed the action
            details: Additional details about the action
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'details': details
        }
        
        # Encrypt log entry
        encrypted_log = self.encrypt_data(log_entry)
        
        # Append to audit log file
        audit_log_path = self.storage_path / "audit.log"
        with open(audit_log_path, 'a') as f:
            f.write(encrypted_log + '\n')
    
    def check_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Checks password strength and provides feedback.
        
        Args:
            password: Password to check
            
        Returns:
            Dictionary with strength score and suggestions
        """
        score = 0
        suggestions = []
        
        # Length check
        if len(password) >= 8:
            score += 1
        else:
            suggestions.append("Use at least 8 characters")
        
        if len(password) >= 12:
            score += 1
        
        # Character variety checks
        if any(c.isupper() for c in password):
            score += 1
        else:
            suggestions.append("Include uppercase letters")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            suggestions.append("Include lowercase letters")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            suggestions.append("Include numbers")
        
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            score += 1
        else:
            suggestions.append("Include special characters")
        
        # Common patterns check
        common_patterns = ['123', 'abc', 'password', 'qwerty']
        if any(pattern in password.lower() for pattern in common_patterns):
            score -= 1
            suggestions.append("Avoid common patterns")
        
        # Determine strength level
        if score >= 5:
            strength = "Strong"
        elif score >= 3:
            strength = "Moderate"
        else:
            strength = "Weak"
        
        return {
            'score': score,
            'strength': strength,
            'suggestions': suggestions
        }