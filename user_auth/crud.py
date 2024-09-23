from datetime import datetime
from datetime import timedelta
from typing import Annotated
from starlette import status
from sqlalchemy import select
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import db_dependency, user_dependency
from user_auth.manager import (
    bcrypt_context,
    create_access_token,
    get_user_token,
    save_blacklist_token
)
from user_auth.schemas import UserCreate, ResetPassword
from database.models import User, ResetPasswordCodes
from .constraints import (
    validate_user_create,
    validate_user_login,
    validate_user_exists,
    check_code_expired,
)


async def create_user(
        db: db_dependency,
        create_user_request: UserCreate
):
    await validate_user_create(
        db,
        create_user_request.email,
        create_user_request.username
    )

    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )
    db.add(create_user_model)

    await db.commit()
    return create_user_model


async def user_login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency
):
    user = await validate_user_login(db, form_data)

    token = create_access_token(user.email, user.id, timedelta(days=1))
    return {"access_token": token, "type": "bearer"}


async def get_existing_user(email: str, db: db_dependency):
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    await validate_user_exists(email, db)
    user_email = result.scalars().first()
    return user_email


async def create_reset_code(email: str, code: str, db: db_dependency):
    expiration_time = datetime.now() + timedelta(minutes=10)
    create_code = ResetPasswordCodes(
        email=email,
        reset_code=code,
        expired_in=expiration_time
    )
    db.add(create_code)
    await db.commit()
    return create_code


async def password_reset(code: str, request: ResetPassword, db: db_dependency):
    reset_code = await check_code_expired(code, db)
    query = select(User).where(
        User.email == reset_code.email)

    result = await db.execute(query)
    await check_code_expired(code, db)

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passwords do not match."
        )
    user.hashed_password = bcrypt_context.hash(request.new_password)
    reset_code.status = False
    await db.commit()

    return {"message": "Password reset successfully"}


async def user_logout(
        token: Annotated[str, Depends(get_user_token)],
        user: user_dependency,
        db: db_dependency
):
    await save_blacklist_token(token=token, current_user=user, db=db)
    return None
