from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, or_
from starlette import status
from dependencies import db_dependency
from database.models import User
from user_auth.manager import authenticate_user


async def validate_user_create(db: db_dependency, email: str, username: str):
    query = select(User).where(
        or_(User.email == email, User.username == username)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if user:
        if user.email == email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email is already exists"
            )
        if user.username == username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username is already exists"
            )
    return user


async def validate_user_login(
        db: db_dependency,
        form_data: OAuth2PasswordRequestForm
):
    user = await authenticate_user(
        form_data.username,
        form_data.password,
        db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your email address or password is incorrect"
        )
    return user
