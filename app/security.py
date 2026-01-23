"""Security utilities for password hashing and token signing using built-in libraries."""
import os
import hmac
import hashlib
import base64
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2 with a random salt.
    Returns a string in format 'salt:hash' (both base64 encoded).
    """
    salt = os.urandom(32)  # 32 bytes = 256 bits
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,  # 100k iterations
        dklen=32  # 32 bytes = 256 bits
    )
    # Encode both salt and key as base64 for storage
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    key_b64 = base64.b64encode(key).decode('utf-8')
    return f"{salt_b64}:{key_b64}"


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a stored hash.
    password_hash should be in format 'salt:hash' (both base64 encoded).
    """
    try:
        salt_b64, key_b64 = password_hash.split(':')
        salt = base64.b64decode(salt_b64)
        stored_key = base64.b64decode(key_b64)
        
        # Compute hash with the same salt
        computed_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000,
            dklen=32
        )
        
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(stored_key, computed_key)
    except (ValueError, TypeError):
        return False


def get_secret_key() -> bytes:
    """Get the secret key for token signing from environment variable."""
    secret = os.getenv("ADMIN_SECRET_KEY")
    if not secret:
        raise ValueError(
            "ADMIN_SECRET_KEY environment variable must be set. "
            "Generate a secure random key (e.g., 32+ bytes)."
        )
    # If it's a hex string, decode it; otherwise use as-is
    if len(secret) == 64 and all(c in '0123456789abcdefABCDEF' for c in secret):
        return bytes.fromhex(secret)
    return secret.encode('utf-8') if isinstance(secret, str) else secret


def create_admin_token(admin_id: int, username: str, expires_in_hours: int = 2) -> str:
    """
    Create a signed token for admin authentication.
    Returns a base64-encoded string containing the payload and signature.
    """
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    payload = {
        "admin_id": admin_id,
        "username": username,
        "expires_at": expires_at.isoformat(),
        "iat": datetime.utcnow().isoformat()
    }
    
    # Encode payload as JSON, then base64
    payload_json = json.dumps(payload, sort_keys=True)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8')
    
    # Create HMAC signature
    secret_key = get_secret_key()
    signature = hmac.new(
        secret_key,
        payload_b64.encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode('utf-8')
    
    # Return token as 'payload.signature'
    return f"{payload_b64}.{signature_b64}"


def verify_admin_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode an admin token.
    Returns the payload dict if valid, None otherwise.
    """
    try:
        payload_b64, signature_b64 = token.split('.')
        
        # Verify signature
        secret_key = get_secret_key()
        expected_signature = hmac.new(
            secret_key,
            payload_b64.encode('utf-8'),
            hashlib.sha256
        ).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).decode('utf-8')
        
        # Constant-time comparison
        if not hmac.compare_digest(signature_b64, expected_signature_b64):
            return None
        
        # Decode payload
        payload_json = base64.urlsafe_b64decode(payload_b64).decode('utf-8')
        payload = json.loads(payload_json)
        
        # Check expiration
        expires_at_str = payload.get('expires_at')
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            if datetime.utcnow() > expires_at:
                return None
        
        return payload
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None
