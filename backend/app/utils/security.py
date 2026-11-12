from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.config import settings

# Khởi tạo công cụ băm mật khẩu chuẩn Argon2id
password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """Băm mật khẩu người dùng an toàn trước khi lưu vào CSDL."""
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So khớp mật khẩu người dùng nhập với mật khẩu đã băm trong CSDL."""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """Tạo JWT access token chứa định danh người dùng (sub)."""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
