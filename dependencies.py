import os
from fastapi import  HTTPException
from sqlalchemy import select

from starlette import status
from jose import jwt, JWTError
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from database.models import User
from database.engine import SessionLocal
from user_auth.manager import  o2auth_bearer


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


db_dependency = Annotated[Session, Depends(get_db)]


async def get_current_user(token: Annotated[str, Depends(o2auth_bearer)], db: db_dependency):
    try:
        payload = jwt.decode(
            token,
            os.environ.get("JWT_SECRET_KEY"),
            algorithms=[os.environ.get("JWT_ALGORITHM")]
        )
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user.")
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not find user"
                                )

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active

        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user.")


user_dependency = Annotated[dict, Depends(get_current_user)]
