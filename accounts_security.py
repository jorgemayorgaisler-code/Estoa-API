"""Security primitives for account authentication; no public routes yet."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError

_hasher = PasswordHasher()
SESSION_LIFETIME = timedelta(days=7)

def hash_password(password: str) -> str:
    if not isinstance(password, str) or not 12 <= len(password) <= 128:
        raise ValueError("Password must contain 12 to 128 characters")
    return _hasher.hash(password)

def verify_password(password: str, encoded: str) -> bool:
    if not isinstance(password, str) or not 12 <= len(password) <= 128:
        return False
    try:
        return _hasher.verify(encoded, password)
    except (VerificationError, InvalidHashError):
        return False

def session_digest(token: str) -> bytes:
    return hashlib.sha256(token.encode("ascii")).digest()

def new_session():
    token = secrets.token_urlsafe(32)
    return token, session_digest(token), datetime.now(timezone.utc) + SESSION_LIFETIME
