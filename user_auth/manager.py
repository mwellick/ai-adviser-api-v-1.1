import os
from datetime import timedelta, datetime
from jose import jwt

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("JWT_ALGORITHM")


def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": email, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


