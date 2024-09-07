from fastapi import APIRouter, HTTPException, Path
from sqlalchemy import select, desc
from starlette import status
from dependencies import db_dependency, user_dependency
from database.models import Chat, Theme
from .schemas import ChatCreate, ChatRead

chats_router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)


@chats_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_chat(db: db_dependency, chat: ChatCreate):
    create_chat = Chat(
        theme_id=chat.theme_id,
        user_id=chat.user_id or None  # user or guest
    )
    query = select(Theme).where(Theme.id == create_chat.theme_id)
    result = await db.execute(query)
    theme_list = result.scalars().first()
    if not theme_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please choose a valid theme")
    db.add(create_chat)
    await db.commit()
    return create_chat


@chats_router.get("/", response_model=list[ChatRead], status_code=status.HTTP_200_OK)
async def get_all_chats(user: user_dependency, db: db_dependency):
    query = select(Chat).where(Chat.user_id == user.get("id")).order_by(desc(Chat.created_at))
    result = await db.execute(query)
    chats_list = result.scalars().all()
    if not chats_list:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Your chats history is clear"
        )
    return chats_list


@chats_router.get("/get_saved_chats", status_code=status.HTTP_200_OK)
async def get_all_saved_chats(user: user_dependency, db: db_dependency):
    query = select(Chat).where(Chat.user_id == user.get("id")).where(Chat.is_saved == True)
    result = await db.execute(query)
    chats_list = result.scalars().all()
    if not chats_list:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Your saved chats history is clear"
        )
    return chats_list


@chats_router.delete("/delete/all_chats", status_code=status.HTTP_200_OK)
async def delete_all_chats(user: user_dependency, db: db_dependency):
    query = select(Chat).where(Chat.user_id == user.get("id"))
    result = await db.execute(query)
    delete_all = result.scalars().all()
    if not delete_all:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your chat history is clear"
        )
    for chat in delete_all:
        await db.delete(chat)

    await db.commit()
    return {"detail": "All chats were successfully deleted"}


@chats_router.delete("/delete/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(user: user_dependency, db: db_dependency, chat_id: int = Path(gt=0)):
    query = select(Chat).where(Chat.user_id == user.get("id")).where(Chat.id == chat_id)
    result = await db.execute(query)
    chat_to_delete = result.scalars().first()
    if not chat_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    await db.delete(chat_to_delete)
    await db.commit()
    return None


@chats_router.get("/{chat_id}/save_chat", status_code=status.HTTP_200_OK)
async def save_unsafe_specific_chat(
        user: user_dependency,
        save: bool,
        db: db_dependency,
        chat_id: int = Path(gt=0),
):
    query = select(Chat).where(Chat.user_id == user.get("id")).where(Chat.id == chat_id)
    result = await db.execute((query))
    save_chat = result.scalars().first()
    if not save_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    save_chat.is_saved = save
    await db.commit()
    return {"detail": f"Chat is successfully {'saved' if save else 'unsaved'}"}
