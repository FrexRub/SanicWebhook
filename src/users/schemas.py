import re
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

PATTERN_PASSWORD = (
    r'^(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[0-9])(?=.*?[!"#\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_'
    r"`\{\|}~])[a-zA-Z0-9!\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_`\{\|}~]{8,}$"
)


class UserBaseSchemas(BaseModel):
    full_name: str = Field(min_length=2)
    email: EmailStr


class UserUpdateSchemas(UserBaseSchemas):
    pass


class UserUpdatePartialSchemas(BaseModel):
    username: Optional[str] = None
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

    model_config = ConfigDict(from_attributes=True)


class LoginSchemas(BaseModel):
    email: str
    password: str


class AuthUserSchemas(BaseModel):
    access_token: str
    token_type: str
