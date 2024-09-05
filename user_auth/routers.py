from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from database.models import User
from .schemas import UserCreate, UserRead
from .manager import (
    create_access_token,
    bcrypt_context,
    authenticate_user,
    # get_user_token,
    save_blacklist_token, get_user_token
)
from dependencies import db_dependency, user_dependency

router = APIRouter(
    tags=["auth"]
)


@router.post("/auth/user/", status_code=status.HTTP_201_CREATED)
async def register_user(
        db: db_dependency,
        create_user_request: UserCreate
):
    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )
    db.add(create_user_model)
    await db.commit()
    return create_user_model


@router.post("/user/token", status_code=status.HTTP_200_OK)
async def login_user(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return "Your email address of password is incorrect"
    token = create_access_token(user.email, user.id, timedelta(days=1))
    return {"access_token": token, "type": "bearer"}


@router.get("/user/me")
async def get_actual_user(user: user_dependency):
    return UserRead(**user)


@router.get("/user/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
        token: Annotated[str, Depends(get_user_token)],
        user: user_dependency,
        db: db_dependency
):
    await save_blacklist_token(token=token, current_user=user, db=db)
    return {"info": "Successfully logged out"}
