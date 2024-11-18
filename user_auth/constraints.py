from fastapi import HTTPException
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, or_, desc
from starlette import status
from dependencies import db_dependency
from database.models import User, ResetPasswordCodes
from user_auth.manager import authenticate_user
from .schemas import UserLogin


async def validate_user_create(db: db_dependency, email: str):
    query = select(User).where(or_(User.email == email))
    result = await db.execute(query)
    user = result.scalars().first()

    if user:
        if user.email == email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address is already exists.",
            )

    return user


async def validate_user_login(db: db_dependency, form_data: UserLogin):
    user = await authenticate_user(form_data.email, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The email address or password you entered is incorrect, or the user does not exist.",
        )
    return user


async def validate_user_o2auth_login(
    db: db_dependency,
    form_data: OAuth2PasswordRequestForm,
):
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your email address or password is incorrect",
        )
    return user


async def validate_user_exists(email: str, db: db_dependency):
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email address does not exist",
        )
    return user


async def check_code_expired(code: str, db: db_dependency):
    query = (
        select(ResetPasswordCodes)
        .where(ResetPasswordCodes.reset_code == code)
        .order_by(desc(ResetPasswordCodes.expired_in))
        .limit(1)
    )

    result = await db.execute(query)
    reset_code = result.scalar_one_or_none()
    if not reset_code or reset_code.expired_in < datetime.now():
        reset_code.status = False
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your reset code is expired or does not exist",
        )

    return reset_code
