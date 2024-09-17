from datetime import timedelta
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import db_dependency, user_dependency
from user_auth.manager import (
    bcrypt_context,
    create_access_token,
    get_user_token,
    save_blacklist_token
)
from user_auth.schemas import UserCreate
from database.models import User
from .constraints import validate_user_create, validate_user_login


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


async def user_logout(
        token: Annotated[str, Depends(get_user_token)],
        user: user_dependency,
        db: db_dependency
):
    await save_blacklist_token(token=token, current_user=user, db=db)
    return None
