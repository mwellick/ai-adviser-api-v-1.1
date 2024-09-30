from fastapi import APIRouter, Path, Request, Response, Query
from starlette import status

from dependencies import db_dependency, user_dependency
from .crud import (
    message_create,
    save_or_unsafe_specific_message,
    get_saved_messages_list,
    delete_specific_saved_message,
    delete_saved_messages
)
from .schemas import MessageCreate, MessageRead, SavedMessageRead
from dotenv import load_dotenv
from typing import Union
from .utils import generate_guest_response, set_cookie, get_cookie

load_dotenv()

messages_router = APIRouter(
    tags=["messages"]
)

MAX_MESSAGES = 5


@messages_router.post("/chats/{chat_id}/guest/message", status_code=status.HTTP_201_CREATED)
async def create_message_by_guest(
        db: db_dependency,
        request: Request,
        response: Response,
        message: MessageCreate,
        chat_id: int = Path(gt=0),
):
    chat_data_cookies = await get_cookie(request, "guest_chat_data")

    chat_id = chat_data_cookies.get("chat_id")
    theme_id = chat_data_cookies.get("theme_id")

    messages = await get_cookie(request, "guest_messages")

    if not isinstance(messages, list):
        messages = []

    messages.append(
        {
            "content": message.content,
            "chat_id": chat_id,
            "theme_id": theme_id,
            "is_ai_response": False
        }
    )

    if len(messages) > MAX_MESSAGES:
        messages = messages[:MAX_MESSAGES]

    await set_cookie(response, "guest_messages", messages, max_age=1800)

    ai_response = await generate_guest_response(db, messages)
    response_message = {"response": ai_response}

    return response_message


@messages_router.post("/chats/{chat_id}/message", status_code=status.HTTP_201_CREATED)
async def create_message(
        db: db_dependency,
        message: MessageCreate,
        chat_id: int = Path(gt=0)
):
    response = await message_create(db, message, chat_id)

    return response


@messages_router.get("/messages/saved", response_model=list[Union[MessageRead, SavedMessageRead]],
                     status_code=status.HTTP_200_OK)
async def get_all_saved_messages(user: user_dependency, db: db_dependency):
    saved_chats = await get_saved_messages_list(user, db)
    return saved_chats


@messages_router.get("/{chat_id}/message/{message_id}/", status_code=status.HTTP_200_OK)
async def save_unsave_specific_message(
        user: user_dependency,
        db: db_dependency,
        chat_id: int = Path(gt=0),
        message_id: int = Path(gt=0),
        save: bool = Query(True)
):
    await save_or_unsafe_specific_message(user, save, db, chat_id, message_id)  # TODO
    return {"detail": f"Message is successfully {'saved' if save else 'unsaved'}"}


@messages_router.delete("/saved/{saved_message_id}/delete", status_code=status.HTTP_200_OK)
async def delete_saved_message(
        user: user_dependency,
        db: db_dependency,
        saved_message_id: int = Path(gt=0)
):
    return await delete_specific_saved_message(user, db, saved_message_id)


@messages_router.delete("/saved/delete", status_code=status.HTTP_200_OK)
async def delete_all_saved_messages(
        user: user_dependency,
        db: db_dependency
):
    return await delete_saved_messages(user, db)
