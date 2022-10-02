# pylint: disable=E0213
from typing import Optional
from pydantic.fields import Field
from pydantic.main import BaseModel
from app.internal.security.danger import generate_password_hash
from app.internal.helpers import sanitize

from app.exceptions import AppException
from app.models.base import CustomBase
from pydantic import validator, constr


class UserSession(BaseModel):
    user_id: Optional[str]
    user: Optional[str]
    is_admin: bool


PasswordType = constr(min_length=4)


class AuthModel(BaseModel):
    user: constr(strip_whitespace=True, to_lower=True, min_length=3, max_length=50)


class LoginModel(AuthModel):
    password: PasswordType


class _UserBase(AuthModel):
    name: constr(strip_whitespace=True, max_length=100)

    @validator("user")
    def validate_user(cls, user: str):
        sanitized = sanitize(user)
        if sanitized != user.lower():
            raise AppException("User cannot contain invalid characters")
        return sanitized


class UserEditable(_UserBase):
    pass


class UserIn(_UserBase):
    is_admin: bool
    password_hash: PasswordType

    @validator("password_hash")
    def validate_pw_hash(cls, password: str):
        return generate_password_hash(password)


class UserOut(CustomBase):
    id_ = str
    user: str
    name: str
    is_admin: bool


class UserOutSecure(UserOut):
    secure: dict = Field(alias="_secure_")