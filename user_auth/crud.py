import os
from aiosmtplib import SMTP
import requests
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta
from typing import Annotated
from starlette import status
from sqlalchemy import select
from email.message import EmailMessage
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import db_dependency, user_dependency
from user_auth.manager import (
    bcrypt_context,
    create_access_token,
    get_user_token,
    save_blacklist_token,
)
from user_auth.schemas import UserCreate, ResetPassword, UserLogin
from database.models import User, ResetPasswordCodes
from .constraints import (
    validate_user_create,
    validate_user_login,
    validate_user_o2auth_login,
    validate_user_exists,
    check_code_expired,
)

load_dotenv()

AUTH_URL = os.environ.get("AUTH_URL")
CLIENT_ID = os.environ.get("CLIENT_ID")
TOKEN_URL = os.environ.get("TOKEN_URL")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URL = os.environ.get("REDIRECT_URL")

MAIL_HOST = os.environ.get("MAIL_HOST")
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_PORT = int(os.environ.get("MAIL_PORT"))


async def create_user(db: db_dependency, create_user_request: UserCreate):
    await validate_user_create(
        db,
        create_user_request.email,
    )

    create_user_model = User(
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
    )
    db.add(create_user_model)

    await db.commit()
    return create_user_model


async def user_login(form_data: UserLogin, db: db_dependency):
    user = await validate_user_login(db, form_data)

    token = create_access_token(user.email, user.id, timedelta(days=1))
    return {"access_token": token, "type": "bearer"}


async def user_o2auth_login(form_data: OAuth2PasswordRequestForm, db: db_dependency):
    user = await validate_user_o2auth_login(db, form_data)

    token = create_access_token(user.email, user.id, timedelta(days=1))
    return {"access_token": token, "type": "bearer"}


async def get_existing_user(email: str, db: db_dependency):
    user_email = await validate_user_exists(email, db)
    return user_email


async def send_mail(email: str, code: str):
    smtp_email = MAIL_USERNAME
    message = EmailMessage()
    message["From"] = smtp_email
    message["To"] = email
    message["Subject"] = "Password reset code"

    body = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>You requested a password reset. Use the following code to reset your password:</p>
            <h3 style="color: black; font-weight: bold;">{code}</h3>  
            <p>This code will expire in 10 minutes. Please do not share this code with anyone.</p>
            <p>You can reset your password by visiting the following link:</p>
            <a href="http://127.0.0.1:8000/docs#/auth/reset_password_reset_password__patch"
               style="color: #3498db; text-decoration: none; font-weight: bold;">
               http://127.0.0.1:8000/docs#/auth/reset_password_reset_password__patch
            </a>
            <br><br>
            <p>Best regards,
            <br>Elli.Ai Team</p>
        </body>
    </html>
    """
    message.set_content(body, subtype="html")

    try:
        async with SMTP(hostname=MAIL_HOST, port=MAIL_PORT) as smtp:
            await smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
            await smtp.send_message(message)
        return {
            "detail": "A list with detailed information was sent into your email address"
        }
    except Exception as e:
        raise HTTPException(
            detail=f"An error occurred while sending you a message.{e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def create_reset_code(email: str, code: str, db: db_dependency):
    expiration_time = datetime.now() + timedelta(minutes=10)
    create_code = ResetPasswordCodes(
        email=email, reset_code=code, expired_in=expiration_time
    )
    db.add(create_code)
    await db.commit()
    return create_code


async def password_reset(code: str, request: ResetPassword, db: db_dependency):
    reset_code = await check_code_expired(code, db)
    query = select(User).where(User.email == reset_code.email)

    result = await db.execute(query)

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.hashed_password = bcrypt_context.hash(request.new_password)
    reset_code.status = False
    await db.commit()

    return {"message": "Password reset successfully"}


async def user_logout(
        token: Annotated[str, Depends(get_user_token)],
        user: user_dependency,
        db: db_dependency,
):
    await save_blacklist_token(db, user, token)
    return None


async def google_auth(code: str, db: db_dependency):
    token_url = TOKEN_URL
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URL,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info = user_info_response.json()
    email = user_info.get("email")

    query = select(User).where(User.email == email)
    result = await db.execute(query)

    user = result.scalars().first()

    if not user:
        user_create = User(email=email, hashed_password=None)
        db.add(user_create)
        await db.commit()
        await db.refresh(user_create)

        token = create_access_token(
            user_create.email, user_create.id, timedelta(days=1)
        )
        return {"access_token": token, "type": "bearer"}

    token = create_access_token(user.email, user.id, timedelta(days=1))
    return {"access_token": token, "type": "bearer"}
