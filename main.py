from fastapi import FastAPI
from user_auth.routers import router
from theme.routers import themes_router
from chat.routers import chats_router
from message.routers import messages_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Adviser", docs_url="/")

origins = ["https://adviser-elli.netlify.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(router)
app.include_router(themes_router)
app.include_router(chats_router)
app.include_router(messages_router)
