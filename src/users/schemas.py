from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserBaseSchemas(BaseModel):
    username: str = Field(min_length=2)
    email: EmailStr


class UserUpdateSchemas(UserBaseSchemas):
    pass


class UserUpdatePartialSchemas(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreateSchemas(UserBaseSchemas):
    pass


class OutUserSchemas(UserBaseSchemas):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LoginSchemas(BaseModel):
    email: str
    password: str


class AuthUserSchemas(BaseModel):
    access_token: str
    token_type: str
