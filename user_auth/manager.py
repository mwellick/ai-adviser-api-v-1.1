import os
import jwt

from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt
from database.models import User

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("JWT_ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
o2auth_bearer = OAuth2PasswordBearer(tokenUrl="/user/token")


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
        return False
    return user
