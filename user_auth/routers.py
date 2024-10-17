import os
import uuid
from dotenv import load_dotenv
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from .schemas import (
    UserCreate,
    UserRead,
    UserLogin,
    ResetPassword,
    ForgotPassword
)
from .manager import (
    get_user_token
)
from .crud import (
    create_user,
    user_login,
    user_logout,
    password_reset,
    get_existing_user,
    create_reset_code, user_o2auth_login, google_auth, send_mail
)
from dependencies import db_dependency, user_dependency

load_dotenv()

router = APIRouter(
    tags=["auth"]
)

AUTH_URL = os.environ.get("AUTH_URL")
CLIENT_ID = os.environ.get("CLIENT_ID")
TOKEN_URL = os.environ.get("TOKEN_URL")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URL = os.environ.get("REDIRECT_URL")

MAIL_HOST = os.environ.get("MAIL_HOST")
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_PORT = os.environ.get("MAIL_HOST")


@router.post("/auth/user/", status_code=status.HTTP_201_CREATED)
async def register_user(
        db: db_dependency,
        create_user_request: UserCreate
):
    return await create_user(db, create_user_request)


@router.get("/google/login/")
async def google_login():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth"
               f"?response_type=code&client_id={CLIENT_ID}"
               f"&redirect_uri={REDIRECT_URL}"
               f"&scope=openid%20profile%20email&access_type=offline"
    }


@router.get("/auth/google/")
async def auth_google(code: str, db: db_dependency):
    return await google_auth(code, db)


@router.post("/user/token/", status_code=status.HTTP_200_OK)
async def login_user(
        form_data: UserLogin,
        db: db_dependency):
    return await user_login(form_data, db)


@router.post("/user/login/", status_code=status.HTTP_200_OK)
async def login_user_o2auth_form(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency
):
    return await user_o2auth_login(form_data, db)


@router.get("/user/me/")
async def get_actual_user(user: user_dependency):
    return UserRead(**user)


@router.post("/forgot_password/", status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPassword, db: db_dependency):
    await get_existing_user(request.email, db)
    code = str(uuid.uuid1())
    await create_reset_code(request.email, code, db)
    return await send_mail(request.email, code)


@router.patch("/reset_password/", status_code=status.HTTP_200_OK)
async def reset_password(request: ResetPassword, db: db_dependency):
    await password_reset(request.reset_password_code, request, db)
    return {"detail": "Password has been reset successfully"}


@router.get("/user/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
        token: Annotated[str, Depends(get_user_token)],
        user: user_dependency,
        db: db_dependency
):
    return await user_logout(token, user, db)
