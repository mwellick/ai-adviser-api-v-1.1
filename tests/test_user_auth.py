import json

import pytest
from httpx import AsyncClient
from starlette import status
from tests.conftest import TestSessionLocal
from user_auth.manager import bcrypt_context
from database.models import User


@pytest.fixture
async def create_user():
    user = User(
        email="user@example.com",
        hashed_password=bcrypt_context.hash("String123")
    )
    db = TestSessionLocal()
    db.add(user)
    await db.commit()
    return user.id


async def test_register_user(ac: AsyncClient):
    response = await ac.post(
        "/auth/user/", json={
            "email": "user@example.com",
            "password": "String123"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_login_user(ac: AsyncClient):
    await ac.post(
        "/auth/user/", json={
            "email": "user@example.com",
            "password": "String123"
        }
    )
    form_data = {
        "email": "user@example.com",
        "password": "String123"
    }
    response = await ac.post(
        "/user/token", json=form_data
    )
    assert response.status_code == status.HTTP_200_OK


async def test_forgot_password(create_user, ac: AsyncClient):
    response = await ac.post(
        "/forgot_password",
        json={
            "email": "user@example.com"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "detail" in response.json()


async def test_reset_password(create_user, ac: AsyncClient):
    response = await ac.post(
        "/forgot_password",
        json={
            "email": "user@example.com"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    decode_to_dict = json.load(response)
    code = ""
    for i in decode_to_dict.values():
        split = i.split(" ")
        code += split[3]
        break

    reset_password = await ac.patch(
        "/reset_password",
        json={
            "reset_password_code": f"{code}",
            "new_password": "Qwerty12345",
            "confirm_password": "Qwerty12345"
        }
    )
    assert reset_password.status_code == status.HTTP_200_OK
    assert reset_password.json() == {"detail": "Password has been reset successfully"}


async def test_logout_user(ac: AsyncClient):
    await ac.post(
        "/auth/user/", json={
            "email": "user@example.com",
            "password": "String123"
        }
    )
    form_data = {
        "email": "user@example.com",
        "password": "String123"
    }
    token = await ac.post(
        "/user/token", data=form_data
    )
    token = token.json().get("access_token")
    response = await ac.get(
        "/user/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
