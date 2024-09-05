from fastapi import FastAPI
from user_auth.routers import router
from theme.routers import themes_router

app = FastAPI(
    title="AI Adviser"
)
app.include_router(router)
app.include_router(themes_router)
