from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

import webauthn
import base64
from webauthn.helpers.structs import RegistrationCredential

from app.core.dependencies import get_session
from app.schemas.user import UserCreate
from app.services.passkey_service import (
    PasskeyService
)

auth_router = APIRouter(prefix="/ChaveDeAcesso", tags=["ChaveDeAcesso"])

@auth_router.post("/Registrar/Opcoes")
def register_options_route(
    user: UserCreate,
    request: Request,
    session: Session = Depends(get_session)
):
    options = PasskeyService(session).register_options_service(user)
    challenge = base64.urlsafe_b64encode(options.challenge).decode("ascii")

    request.session["registration_challenge"] = challenge

    return webauthn.options_to_json(options)

@auth_router.post("/Registrar/Verificar")
def register_verify_route(
    credential: RegistrationCredential,
    request: Request,
    session: Session = Depends(get_session)
):
    return PasskeyService(session).register_options_service(credential, request)

@auth_router.post("/Autenticar/Opcoes")
def auth_options_route():
    pass

@auth_router.post("/Autenticar/Verificar")
def auth_verify_route():
    pass
