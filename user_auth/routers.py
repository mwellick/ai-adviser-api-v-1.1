from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status
from database.models import User
from .schemas import UserCreate
from .manager import create_access_token
from database.engine import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
o2auth_bearer = OAuth2PasswordBearer(tokenUrl="token")


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


db_dependency = Annotated[Session, Depends(get_db)]


async def authenticate_user(email: str, password: str, db):
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


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


@router.post("/user/login", status_code=status.HTTP_200_OK)
async def login_user(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return "Your email address of password is incorrect"
    token = create_access_token(user.email, user.id, timedelta(hours=1))
    return {"access_token": token, "type": "bearer"}



