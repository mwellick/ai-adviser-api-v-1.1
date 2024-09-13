import json
import random
from fastapi import APIRouter, Path, Response
from starlette import status
from dependencies import db_dependency, user_dependency
from .crud import (
    chat_create,
    get_chats_list,
    get_saved_chats_list,
    delete_specific_chat,
    delete_all_chat_history, save_or_unsafe_specific_chat
)
from .schemas import ChatCreate, ChatRead

chats_router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)


@chats_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_chat(db: db_dependency, response: Response, chat: ChatCreate):
    chat_instance = await chat_create(db, chat)

    if chat.user_id is None:
        chat_id = random.randint(1, 100)
        chat_data = {
            "chat_id": chat_id,
            "theme_id": chat_instance.theme_id
        }
        response.set_cookie(
            key="guest_chat_data",
            value=json.dumps(chat_data),
            max_age=1800,
            httponly=True,
            secure=True
        )

    return chat_instance


@chats_router.get("/", response_model=list[ChatRead], status_code=status.HTTP_200_OK)
async def get_all_chats(user: user_dependency, db: db_dependency):
    chats = await get_chats_list(user, db)
    return chats


@chats_router.get("/get_saved_chats", status_code=status.HTTP_200_OK)
async def get_all_saved_chats(user: user_dependency, db: db_dependency):
    saved_chats = await get_saved_chats_list(user, db)
    return saved_chats


@chats_router.delete("/delete/all_chats", status_code=status.HTTP_200_OK)
async def delete_all_chats(user: user_dependency, db: db_dependency):
    await delete_all_chat_history(user, db)
    return {"detail": "All chats were successfully deleted"}


@chats_router.delete("/delete/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(user: user_dependency, db: db_dependency, chat_id: int = Path(gt=0)):
    await delete_specific_chat(user, db, chat_id)
    return None


@chats_router.get("/{chat_id}/save_chat", status_code=status.HTTP_200_OK)
async def save_unsafe_specific_chat(
        user: user_dependency,
        save: bool,
        db: db_dependency,
        chat_id: int = Path(gt=0),
):
    await save_or_unsafe_specific_chat(user, save, db, chat_id)
    return {"detail": f"Chat is successfully {'saved' if save else 'unsaved'}"}
