from datetime import datetime, timedelta, timezone

from django.contrib.auth.hashers import check_password
from jose import JWTError, jwt

from app.core import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return check_password(plain_password, hashed_password)


def create_access_token(username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": username, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        username = payload.get("sub")
        return username if isinstance(username, str) and username else None
    except JWTError:
        return None
