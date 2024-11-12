from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator
)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("email")
    def validate_email_format(cls, value: str) -> str:
        allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789."

        if not all(char in allowed_chars for char in value):
            raise ValueError("Email must contain only Latin letters, digits, and a dot (.)")

        return value

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
