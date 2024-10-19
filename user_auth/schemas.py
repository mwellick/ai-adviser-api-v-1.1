import string
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator
)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    def validate_password_startswith_upper(cls, value: str) -> str:
        if not value[0].isupper():
            raise ValueError("Password must start with an uppercase letter")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    reset_password_code: str
    new_password: str
