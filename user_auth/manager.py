import os
import jwt
import requests
from fastapi import Depends, HTTPException
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt
from starlette import status

from database.models import User, BlackListToken
from dotenv import load_dotenv
from dependencies import db_dependency, user_dependency

load_dotenv()



JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("JWT_ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
o2auth_bearer = OAuth2PasswordBearer(tokenUrl="/user/login")


def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": email, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(email: str, password: str, db):
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user


async def get_user_token(token: str = Depends(o2auth_bearer)):
    return token


async def save_blacklist_token(
        db: db_dependency,
        current_user: user_dependency,
        token: str = Depends(o2auth_bearer),

):
    query = select(BlackListToken).where(BlackListToken.token == token)
    result = await db.execute(query)
    blacklist_token = result.scalars().first()
    if blacklist_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is already blacklisted"
        )

    blacklist_token = BlackListToken(
        token=token,
        email=current_user.get("email")
    )
    db.add(blacklist_token)
    await db.commit()


