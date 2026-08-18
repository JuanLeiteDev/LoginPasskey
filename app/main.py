from fastapi import FastAPI
from app.routes.auth_routes import auth_router
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.DATABASE_URL
)

app.include_router(auth_router)