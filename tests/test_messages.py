from httpx import AsyncClient
from starlette import status
from database.models import Theme
from .conftest import TestSessionLocal
from .test_chats import create_chat
from .test_themes import create_theme
from .test_user_auth import create_user


async def test_create_user_message_and_ai_response(
        create_theme,
        create_chat,
        create_user,
        ac: AsyncClient
):
    chat_id, token = create_chat
    request_data = {
        "content": "Hello world",
        "chat_id": chat_id
    }
    assert request_data.get("chat_id") == 1
    response = await ac.post(
        "/chats/1/message",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get("chat_id") == 1
    assert response.json().get("is_ai_response") is True


async def test_create_guest_message_and_ai_response(ac: AsyncClient):
    theme = Theme(
        name="Test Theme",
        description="test description"
    )
    db = TestSessionLocal()
    db.add(theme)
    await db.commit()

    chat_form_data = {
        "theme_id": theme.id,
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
        "chat_id": "1",
        "theme_id": "1",
        "is_ai_response": False
    }

    ai_response = await ac.post(
        f"/chats/{chat_id}/guest/message",
        json=message_form_data
    )
    assert ai_response.status_code == status.HTTP_201_CREATED, ai_response.json()
    assert ai_response.json().get("response") is not None


async def test_save_unsave_message(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    request_data = {
        "content": "Hello world",
        "chat_id": chat_id
    }
    assert request_data.get("chat_id") == 1
    await ac.post(
        "/chats/1/message",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    msg_save = await ac.get(
        "/1/message/1/?save=True",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert msg_save.status_code == status.HTTP_200_OK
    assert msg_save.json().get("detail") == "Message is successfully saved"
    msg_unsave = await ac.get(
        "/1/message/1/?save=False",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert msg_unsave.status_code == status.HTTP_200_OK
    assert msg_unsave.json().get("detail") == "Message is successfully unsaved"


async def test_get_all_saved_messages(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    request_data = {
        "content": "Hello world",
        "chat_id": chat_id
    }
    assert request_data.get("chat_id") == 1
    await ac.post(
        "/chats/1/message",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    save_res = await ac.get(
        "/1/message/1/?save=True",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert save_res.status_code == status.HTTP_200_OK
    response = await ac.get(
        "/messages/saved",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
