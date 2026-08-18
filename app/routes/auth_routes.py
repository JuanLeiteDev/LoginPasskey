from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Any

import base64

from webauthn.helpers.parse_registration_credential_json import (
    parse_registration_credential_json
)

from webauthn.helpers.parse_authentication_credential_json import (
    parse_authentication_credential_json
)
from webauthn.helpers.exceptions import (
    InvalidAuthenticationResponse,
    InvalidJSONStructure,
    InvalidRegistrationResponse
)

from app.core.dependencies import get_session
from app.core.exceptions import InvalidCredentialJSONError
from app.schemas.user import UserCreate
from app.services.passkey_service import (
    PasskeyService
)

auth_router = APIRouter(prefix="/ChaveDeAcesso", tags=["ChaveDeAcesso"])

@auth_router.post("/Registrar/Opcoes", status_code=200)
def register_options_route(
    new_user: UserCreate,
    request: Request,
    session: Session = Depends(get_session)
):
    options, challenge, user = PasskeyService(session).register_options_service(new_user)

    user_id_str = base64.urlsafe_b64encode(user.id).decode("ascii")
    request.session["current_user"] = user_id_str
    request.session["registration_challenge"] = challenge

    return options

@auth_router.post("/Registrar/Verificar", status_code=200)
def register_verify_route(
    credential_json: dict[str, Any],
    request: Request,
    session: Session = Depends(get_session)
):
    try:
        credential = parse_registration_credential_json(credential_json)
    except (InvalidJSONStructure, InvalidRegistrationResponse) as exc:
        raise InvalidCredentialJSONError() from exc

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
    try:
        credentials = parse_authentication_credential_json(credentials_json)
    except (InvalidJSONStructure, InvalidAuthenticationResponse) as exc:
        raise InvalidCredentialJSONError() from exc

    return PasskeyService(session).auth_verify_service(credentials, request)
