import os
import pytest
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from database.models import Base
from dependencies import get_db, get_current_user
from main import app

load_dotenv()

SQLALCHEMY_TEST_DATABASE_URL = os.environ.get("SQLALCHEMY_TEST_DATABASE_URL")

engine_test = create_async_engine(
    url=SQLALCHEMY_TEST_DATABASE_URL,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine_test
)

client = TestClient(app)


async def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        await db.close()


app.dependency_overrides[get_db] = override_get_db


async def override_get_current_user():
    return {
        "id": 1,
        "email": "user@example.com",
        "username": "testuser123",
        "is_active": True
    }


app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture(scope="function")
async def async_db_engine():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine_test

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def ac(async_db_engine):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
