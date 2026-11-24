from datetime import UTC, datetime, timedelta

import jwt
from app.config import settings
from pwdlib import PasswordHash

from auth_service.app.models import User

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user: User) -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(hours=1)

    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "role": getattr(user, "role", "user"),
        "iat": now,
        "exp": expire,
    }

    token = jwt.encode(
        payload=payload,
        key=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    return token
