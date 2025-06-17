from datetime import datetime, timedelta, timezone
import asyncio
from typing import Optional

import bcrypt
import jwt

from src.core.config import setting, setting_conn


async def create_hash_password(password: str) -> bytes:
    """
    Создание хеш пароля
    :param password: пароль
    :type password: str
    :rtype: bytes
    :return: хеш значение пароля
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
    Проверка валидности пароля. Проверяет пароль с хеш-значением правильного пароля
    :param password: переданный пароль
    :type password: str
    :param hashed_password: хеш-значение правильного пароля
    :type hashed_password: str
    :rtype: bool
    :return: возвращает True, если пароль верный иначе - False
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
    :param payload: содержание jwt-токена
    :type payload: dict
    :param key: секретный ключ
    :type key: str
    :param algorithm: задается алгоритм
    :type algorithm: str
    :rtype: str
    :return: возвращает jwt-токен

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
    Раскодирует jwt-токен
    :param token: jwt-токен
    :type token: str | bytes
    :param key: секретный ключ шифрования
    :type key: str
    :param algorithm: алгоритм шифрования
    :type algorithm: str
    :rtype: dict
    :return: содержание токена (payload)
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
    :param user_id: id пользователя
    :type user_id: str
    :param expire_minutes: время экспирации токена
    :type expire_minutes: Optional[int]
    :rtype: str
    :return: jwt-токен
    """
    payload = dict()
    payload["sub"] = user_id
    if expire_minutes is None:
        expire_minutes = setting.auth_jwt.access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload["exp"] = expire
    return await encode_jwt(payload)
