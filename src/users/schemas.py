import re
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

from src.payments.schemas import ScoreBaseSchemas

PATTERN_PASSWORD = (
    r'^(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[0-9])(?=.*?[!"#\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_'
    r"`\{\|}~])[a-zA-Z0-9!\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_`\{\|}~]{8,}$"
)


class UserProtectedSchemas(BaseModel):
    id: int
    full_name: str
    email: EmailStr


class UserSuperSchemas(UserProtectedSchemas):
    is_superuser: bool


class UserBaseSchemas(BaseModel):
    full_name: str = Field(min_length=2)
    email: EmailStr


class UserUpdateSchemas(UserBaseSchemas):
    pass


class UserUpdatePartialSchemas(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreateSchemasIn(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserCreateSchemas(BaseModel):
    full_name: str
    email: EmailStr
    hashed_password: str

    @field_validator("hashed_password")
    def validate_password(cls, value: str) -> str:
        if not re.match(PATTERN_PASSWORD, value):
            raise ValueError("Invalid password")
        return value


class OutUserSchemas(UserBaseSchemas):
    id: int
    score: list[ScoreBaseSchemas]


class LoginSchemas(BaseModel):
    email: str
    password: str
