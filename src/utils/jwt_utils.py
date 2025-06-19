import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from src.core.config import setting, setting_conn


async def create_hash_password(password: str) -> bytes:
    """
    Создание хеш пароля
    """
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    await asyncio.sleep(0)
    return bcrypt.hashpw(pwd_bytes, salt)


async def validate_password(
    password: str,
    hashed_password: str,
) -> bool:
    """
    Проверка валидности пароля. Сверяет пароль с хеш-значением правильного пароля
    """
    await asyncio.sleep(0)
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password.encode(),
    )


async def encode_jwt(
    payload: dict,
    key: str = setting_conn.SECRET_KEY,
    algorithm: str = setting.auth_jwt.algorithm,
) -> str:
    """
     Создает jwt-токена по алгоритму RS256 (с использованием ассиметричных ключей)
    """
    encoded = jwt.encode(payload, key, algorithm=algorithm)
    await asyncio.sleep(0)
    return encoded


async def decode_jwt(
    token: str | bytes,
    key: str = setting_conn.SECRET_KEY,
    algorithm: str = setting.auth_jwt.algorithm,
):
    """
    Раскодирует jwt-токен, возвращает содержание токена (payload)
    """
    decoded = jwt.decode(token, key, algorithms=[algorithm])
    await asyncio.sleep(0)
    return decoded


async def create_jwt(
    user_id: str,
    expire_minutes: Optional[int] = None,
) -> str:
    """
    Создание jwt-токен
    """
    payload = dict()
    payload["sub"] = user_id
    if expire_minutes is None:
        expire_minutes = setting.auth_jwt.access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload["exp"] = expire
    return await encode_jwt(payload)
