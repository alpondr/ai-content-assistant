"""
Password hashing and JWT helpers.

- Passwords: we never store the raw password. passlib hashes it with bcrypt,
  and later only compares hashes, never the plain text.
- JWT: after login, the user gets a signed token. On every protected request,
  they send it back in the "Authorization: Bearer <token>" header, and we
  verify the signature with our secret key instead of looking up a session
  in the database. This is what makes JWT auth "stateless".
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Builds a JWT that encodes who the user is ("sub" = subject, here the
    user's email) and when it expires. jose.jwt.encode signs it with our
    secret key so nobody can forge or tamper with it without knowing the key.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Returns the email stored in the token, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
    return payload.get("sub")
