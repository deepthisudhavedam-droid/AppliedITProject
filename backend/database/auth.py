import os
from datetime import datetime, timedelta
import jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "replace_this_secret_for_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def get_password_hash(password: str) -> str:
    """Return the plaintext password for storage. WARNING: storing plain passwords is insecure."""
    return password


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Check a plaintext password against the stored password."""
    return plain_password == stored_password


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT token containing standard claim data."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and verify a JWT token, returning its payload or None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
