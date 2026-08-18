from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Any

from webauthn.helpers.parse_registration_credential_json import (
    parse_registration_credential_json
)

from webauthn.helpers.parse_authentication_credential_json import (
    parse_authentication_credential_json
)

from app.core.dependencies import get_session
from app.schemas.user import UserCreate
from app.services.passkey_service import (
    PasskeyService
)

auth_router = APIRouter(prefix="/ChaveDeAcesso", tags=["ChaveDeAcesso"])

@auth_router.post("/Registrar/Opcoes", status_code=200)
def register_options_route(
    user: UserCreate,
    request: Request,
    session: Session = Depends(get_session)
):
    options, challenge = PasskeyService(session).register_options_service(user)

    request.session["current_user"] = user.email
    request.session["registration_challenge"] = challenge

    return options

@auth_router.post("/Registrar/Verificar", status_code=200)
def register_verify_route(
    credential_json: dict[str, Any],
    request: Request,
    session: Session = Depends(get_session)
):
    credential = parse_registration_credential_json(credential_json)
    return PasskeyService(session).register_verify_service(credential, request)

@auth_router.post("/Autenticar/Opcoes", status_code=200)
def auth_options_route(
    request: Request,
    session: Session = Depends(get_session)
):
    options, challenge = PasskeyService(session).auth_options_service()

    request.session["authentication_challenge"] = challenge

    return options

@auth_router.post("/Autenticar/Verificar")
def auth_verify_route(
    credentials_json: dict[str, Any],
    request: Request,
    session: Session = Depends(get_session)
):
    credentials = parse_authentication_credential_json(credentials_json)
    return PasskeyService(session).auth_verify_service(credentials, request)