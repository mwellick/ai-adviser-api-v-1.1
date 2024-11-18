import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    os.environ.get("SQLALCHEMY_DATABASE_URL")
    if os.environ.get("FAST_API_ENV") == "develop"
    else os.environ.get("SQLALCHEMY_PROD_DATABASE_URL")
)

engine = create_async_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine,
)

Base = declarative_base()
