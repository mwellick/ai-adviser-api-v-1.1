from httpx import AsyncClient
from starlette import status
from database.models import Theme
from .conftest import TestSessionLocal
from .test_chats import create_chat
from .test_themes import create_theme
from .test_user_auth import create_user


async def create_message(
        ac: AsyncClient,
        token: str,
        chat_id: int,
        content="Hello world"
):
    request_data = {"content": content, "chat_id": chat_id}
    return await ac.post(
        f"/chats/{chat_id}/message",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"}
    )


async def save_or_unsave_message(
        ac: AsyncClient,
        chat_id: int,
        message_id: int,
        save: bool,
        token: str
):
    return await ac.get(
        f"/{chat_id}/message/{message_id}/?save={str(save).lower()}",
        headers={"Authorization": f"Bearer {token}"}
    )


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
    await create_message(ac, token, chat_id)
    msg_save = await save_or_unsave_message(ac, chat_id, 1, True, token)
    assert msg_save.status_code == status.HTTP_200_OK
    assert msg_save.json().get("detail") == "Message is successfully saved"

    msg_unsave = await save_or_unsave_message(ac, chat_id, 1, False, token)
    assert msg_unsave.status_code == status.HTTP_200_OK
    assert msg_unsave.json().get("detail") == "Message is successfully unsaved"


async def test_get_all_saved_messages(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    await create_message(ac, token, chat_id)
    msg_save = await save_or_unsave_message(ac, chat_id, 2, True, token)

    assert msg_save.status_code == status.HTTP_200_OK
    response = await ac.get(
        "/messages/saved",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


async def test_get_saved_messages_by_id(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    await create_message(ac, token, chat_id)
    msg_save = await save_or_unsave_message(ac, chat_id, 2, True, token)

    assert msg_save.status_code == status.HTTP_200_OK
    response = await ac.get(
        f"/saved/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data.get("id") == 1
    assert len(response.json()) == 3


async def test_delete_saved_message(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    await create_message(ac, token, chat_id)
    msg_save = await save_or_unsave_message(ac, chat_id, 2, True, token)
    assert msg_save.status_code == status.HTTP_200_OK
    response = await ac.delete(
        "/saved/1/delete",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_all_saved_messages(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    await create_message(ac, token, chat_id)
    msg_save = await save_or_unsave_message(ac, chat_id, 2, True, token)
    assert msg_save.status_code == status.HTTP_200_OK
    response = await ac.delete(
        "/saved/delete",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK


async def test_still_saved_message_if_chat_deleted(create_chat, ac: AsyncClient):
    chat_id, token = create_chat
    await create_message(ac, token, chat_id)
    await save_or_unsave_message(ac, chat_id, 2, True, token)
    chat_response = await ac.delete(
        "/chats/1/delete",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert chat_response.status_code == status.HTTP_204_NO_CONTENT
    response = await ac.get(
        f"/saved/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data.get("id") == 1
    assert len(response.json()) == 3
