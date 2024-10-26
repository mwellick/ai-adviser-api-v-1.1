import random
from fastapi import APIRouter, Path, Response
from starlette import status
from dependencies import db_dependency, user_dependency
from message.utils import set_cookie
from .crud import (
    guest_chat_create,
    chat_create,
    get_chats_list,
    delete_specific_chat,
    delete_all_chat_history,
    get_chat_by_id
)
from .schemas import (
    ChatCreate,
    ChatRead,
    RetrieveChat,
    ChatCreated,
    GuestChatCreated,
    GuestChatCreate
)

chats_router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)


@chats_router.post("/guest/create/", response_model=GuestChatCreated,
                   status_code=status.HTTP_201_CREATED)
async def create_guest_chat(db: db_dependency, response: Response, chat: GuestChatCreate):
    chat_instance = await guest_chat_create(db, chat)

    if chat.user_id is None:
        chat_id = random.randint(1, 100)
        chat_data = {
            "chat_id": chat_id,
            "theme_id": chat_instance.theme_id
        }
        await set_cookie(response, "guest_chat_data", chat_data, max_age=1800)
        return GuestChatCreated(id=chat_id)

    return chat_instance


@chats_router.post("/create/", response_model=ChatCreated,
                   status_code=status.HTTP_201_CREATED)
async def create_chat(db: db_dependency, user: user_dependency, chat: ChatCreate):
    chat = await chat_create(db, user, chat)
    return chat


@chats_router.get("/", response_model=list[ChatRead], status_code=status.HTTP_200_OK)
async def get_all_chats(user: user_dependency, db: db_dependency):
    chats = await get_chats_list(user, db)
    return chats


@chats_router.get("/{chat_id}/", response_model=RetrieveChat, status_code=status.HTTP_200_OK)
async def retrieve_chat(user: user_dependency, db: db_dependency, chat_id: int = Path(gt=0)):
    chat = await get_chat_by_id(user, db, chat_id)
    return chat


@chats_router.delete("/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_chats(user: user_dependency, db: db_dependency):
    await delete_all_chat_history(user, db)


@chats_router.delete("/{chat_id}/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(user: user_dependency, db: db_dependency, chat_id: int = Path(gt=0)):
    await delete_specific_chat(user, db, chat_id)
