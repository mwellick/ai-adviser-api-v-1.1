import uuid
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from .schemas import UserCreate, UserRead, UserLogin, ResetPassword, ForgotPassword
from .manager import (
    get_user_token
)
from .crud import (
    create_user,
    user_login,
    user_logout,
    password_reset,
    get_existing_user,
    create_reset_code, user_o2auth_login
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
    return await create_user(db, create_user_request)


@router.post("/user/token", status_code=status.HTTP_200_OK)
async def login_user(
        form_data: UserLogin,
        db: db_dependency):
    return await user_login(form_data, db)


@router.post("/user/login", status_code=status.HTTP_200_OK)
async def login_user_o2auth_form(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency
):
    return await user_o2auth_login(form_data,db)


@router.get("/user/me")
async def get_actual_user(user: user_dependency):
    return UserRead(**user)


@router.post("/forgot_password", status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPassword, db: db_dependency):
    await get_existing_user(request.email, db)
    code = str(uuid.uuid1())
    await create_reset_code(request.email, code, db)
    return {
        "detail": f"Reset password code: {code} \n"
                  f"This code will be available for 10 minutes."
                  f"Please,don't share it to anyone."
    }


@router.patch("/reset_password")
async def reset_password(request: ResetPassword, db: db_dependency):
    await password_reset(request.reset_password_code, request, db)
    return {"detail": "Password has been reset successfully"}


@router.get("/user/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
        token: Annotated[str, Depends(get_user_token)],
        user: user_dependency,
        db: db_dependency
):
    return await user_logout(token, user, db)
