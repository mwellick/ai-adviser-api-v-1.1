import json
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




