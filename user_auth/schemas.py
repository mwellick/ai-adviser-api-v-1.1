import string
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=8)



    @field_validator("password")
    def validate_password_startswith_upper(cls, value: str) -> str:
        if not value[0].isupper():
            raise ValueError("Password must start with an uppercase letter")
        return value

    @field_validator("username")
    def validate_username_with_ascii_letters(cls, value: str) -> str:
        for i in range(len(value)):
            if value[i] not in string.ascii_letters:
                raise ValueError("Username must contain only ASCII letters")
        return value


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool

    class Config:
        from_attributes = True
