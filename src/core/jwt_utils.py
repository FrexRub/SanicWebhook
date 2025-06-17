from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Response

from src.core.config import COOKIE_NAME, setting, setting_conn


def create_hash_password(password: str) -> bytes:
    """
    Создание хеш пароля
    :param password: str
        пароль
    :return: bytes
        хеш значение пароля
    """
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    """
    Проверка валидности пароля. Проверяет пароль с хеш-значением правильного пароля
    :param password: str
        переданный пароль
    :param hashed_password: bytes
        хеш-значение правильного пароля
    :return: bool
        возвращает True, если пароль верный иначе - False
    """
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def encode_jwt(
    payload: dict,
    key: str = setting_conn.SECRET_KEY,
    algorithm: str = setting.auth_jwt.algorithm,
):
    """
     Создает jwt-токена по алгоритму RS256 (с использованием ассиметричных ключей)
    :param payload: dict
        содержание jwt-токена
    :param key: str
        секретный ключ
    :param algorithm: str
        задается алгоритм
    :return:
        возвращает jwt-токен
    """
    encoded = jwt.encode(payload, key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    key: str = setting_conn.SECRET_KEY,
    algorithm: str = setting.auth_jwt.algorithm,
):
    """
        Раскодирует jwt-токен
    :param token: str | bytes
        jwt-токен
    :param key: str
        секретный ключ шифрования
    :param algorithm: str
        алгоритм шифрования
    :return:
        ?? содержание токена (payload)
    """
    decoded = jwt.decode(token, key, algorithms=[algorithm])
    return decoded


def create_jwt(user: str) -> str:
    payload = dict()
    payload["sub"] = user
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=setting.auth_jwt.access_token_expire_minutes
    )
    payload["exp"] = expire
    return encode_jwt(payload)
