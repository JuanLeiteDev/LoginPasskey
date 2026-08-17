from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_session
from app.schemas.user import UserCreate
from app.services.passkey_service import (
    PasskeyService
)

auth_router = APIRouter(prefix="/ChaveDeAcesso", tags=["ChaveDeAcesso"])

@auth_router.post("/Registrar/Opcoes")
def register_options_route(
    user: UserCreate,
    session: Session = Depends(get_session)
):
    return PasskeyService(session).register_options_service(user)

@auth_router.post("/Registrar/Verificar")
def register_verify_route():
    pass

@auth_router.post("/Autenticar/Opcoes")
def auth_options_route():
    pass

@auth_router.post("/Autenticar/Verificar")
def auth_verify_route():
    pass