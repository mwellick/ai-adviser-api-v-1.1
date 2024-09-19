import ast
import json
import re
from httpx import AsyncClient
from starlette import status
from .test_chats import create_chat
from .test_themes import create_theme
from .test_user_auth import create_user


async def test_create_user_message_and_ai_response(create_theme, create_chat, create_user, ac: AsyncClient):
    chat_id, token = create_chat
    request_data = {
        "content": "Hello world",
        "chat_id": chat_id
    }
    assert request_data.get("chat_id") == 1
    response = await ac.post(
        "/user_chat/1/message",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("chat_id") == 1
    assert response.json().get("is_ai_response") is True


async def test_create_guest_message_and_ai_response(create_theme, ac: AsyncClient):
    chat_form_data = {
        "theme_id": create_theme,
        "user_id": None
    }
    response = await ac.post(
        "/chats/create", json=chat_form_data
    )
    cookies = response.cookies.get("guest_chat_data")
    cookies = cookies.replace("054", "").replace("\\", "")
    str_chat_id = ""
    for i in range(len(cookies)):
        if cookies[i].isdigit() and cookies[i + 1].isdigit():
            str_chat_id += cookies[i] + cookies[i + 1]
            break
        elif cookies[i].isdigit() and not cookies[i + 1].isdigit():
            str_chat_id += cookies[i]
            break
    chat_id = int(str_chat_id)
    message_form_data = {
        "content": "Hello world",
        "chat_id": chat_id
    }
    ai_response = await ac.post(
        f"/guest_chat/{chat_id}/message",
        json=message_form_data
    )
    assert ai_response.status_code == status.HTTP_200_OK
    assert ai_response.json().get("response") is not None
