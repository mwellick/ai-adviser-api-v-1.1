import pytest
from httpx import AsyncClient
from starlette import status
from database.models import Chat
from tests.conftest import TestSessionLocal
from .test_user_auth import create_user
from .test_themes import create_theme


@pytest.fixture
async def create_chat(create_theme, create_user, ac: AsyncClient):
    form_data = {
        "username": "user@example.com",
        "password": "String123"
    }
    login = await ac.post(
        "/user/token", data=form_data
    )
    token = login.json().get("access_token")
    chat = Chat(
        theme_id=create_theme,
        user_id=create_user
    )
    db = TestSessionLocal()
    db.add(chat)
    await db.commit()

    return chat.id, token


async def test_create_guest_chat(create_theme, ac: AsyncClient):
    request_data = {
        "theme_id": create_theme,
        "user_id": None
    }
    response = await ac.post(
        "/chats/create", json=request_data
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_create_user_chat(create_chat, create_user, create_theme, ac: AsyncClient):
    chat_id, token = create_chat

    request_data = {
        "theme_id": create_theme,
        "user_id": create_user
    }
    assert request_data.get("user_id") == 1
    assert request_data.get("theme_id") == 1

    response = await ac.post(
        "/chats/create",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_get_list_of_chats(create_chat, ac: AsyncClient):
    response = await ac.get("/chats/")
    res_data = response.json()
    data = res_data[0]
    assert response.status_code == status.HTTP_200_OK
    assert data.get("user_id") == 1
    assert data.get("theme_id") == 1
    assert len(res_data) == 1


async def test_get_chat_by_id(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    response = await ac.get("/chats/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("user_id") == 1
    assert response.json().get("theme_id") == 1


async def test_save_unsave_chat(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    response = await ac.get("/chats/1/?save=True", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("detail") == "Chat is successfully saved"
    unsave_request = await ac.get("/chats/1/?save=False", headers={"Authorization": f"Bearer {token}"})
    assert unsave_request.status_code == status.HTTP_200_OK
    assert unsave_request.json().get("detail") == "Chat is successfully unsaved"


async def test_get_all_saved_chats(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    save_res = await ac.get("/chats/1/?save=True", headers={"Authorization": f"Bearer {token}"})
    assert save_res.status_code == status.HTTP_200_OK
    response = await ac.get("/chats/saved", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


async def test_delete_chat(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    response = await ac.delete("/chats/delete/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_all_chats(create_chat, ac: AsyncClient):
    token = create_chat
    response = await ac.delete("/chats/delete/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("detail") == "All chats were successfully deleted"
