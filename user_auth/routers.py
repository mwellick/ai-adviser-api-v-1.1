from fastapi import APIRouter, Depends
from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from database.models import User
from .schemas import UserCreate
from database.engine import SessionLocal

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/user/register", status_code=status.HTTP_201_CREATED)
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
