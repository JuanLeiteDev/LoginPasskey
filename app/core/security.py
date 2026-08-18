from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    PublicKeyCredentialCreationOptions,
    RegistrationCredential,
    AuthenticationCredential
)

from webauthn.helpers.exceptions import (
    InvalidRegistrationResponse,
    InvalidAuthenticationResponse
)

from webauthn.registration.verify_registration_response import (
    VerifiedRegistration
)

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response
)

from app.core import exceptions as ex

import base64
import logging
import jwt

from datetime import datetime, timezone, timedelta
from fastapi import Response
from app.core.config import settings, token_settings
from app.models.user import User
from app.models.passkey import Passkey

logger = logging.getLogger(__name__)

def get_authenticator_selection() -> AuthenticatorSelectionCriteria:
    return AuthenticatorSelectionCriteria(
    resident_key=ResidentKeyRequirement.REQUIRED,
    user_verification=UserVerificationRequirement.PREFERRED
)

def get_generate_registration_options(
    user: User, 
    auth_selection: AuthenticatorSelectionCriteria
) -> PublicKeyCredentialCreationOptions:
    return generate_registration_options(
        rp_id=settings.RP_ID,
        rp_name=settings.RP_NAME,
        user_id=user.id,
        user_name=user.username,
        user_display_name=user.username,
        authenticator_selection=auth_selection,
        exclude_credentials=[]
    )

def get_verify_registration_response(
    credential: RegistrationCredential, 
    challenge: bytes
) -> VerifiedRegistration:
    try:
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=challenge,
            expected_origin=settings.RP_ORIGIN,
            expected_rp_id=settings.RP_ID,
            require_user_verification=True,
        )

        return verification
    except InvalidRegistrationResponse as exc:
        raise ex.InvalidRegistrationResponseError() from exc
    except Exception as exc:
        logger.exception("Erro interno durante a verificação do registro WebAuthn.")
        raise ex.InternalServerError() from exc

def get_generate_authentication_options():
    return generate_authentication_options(
        rp_id=settings.RP_ID,
        user_verification=UserVerificationRequirement.REQUIRED
    )

def get_verify_authentication_response(
    credentials: AuthenticationCredential, 
    challenge_bytes: bytes, 
    existing_credential: Passkey
):
    try:
        verification = verify_authentication_response(
            credential=credentials,
            expected_challenge=challenge_bytes,
            expected_origin=settings.RP_ORIGIN,
            expected_rp_id=settings.RP_ID,
            require_user_verification=True,
            credential_public_key=existing_credential.public_key,
            credential_current_sign_count=existing_credential.sign_count
        )

        return verification
    except InvalidAuthenticationResponse as exc:
        raise ex.InvalidAuthenticationResponseError() from exc
    except Exception as exc:
        logger.exception("Erro interno durante a verificação da autenticação WebAuthn.")
        raise ex.InternalServerError() from exc

def bytes_to_str_base64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")

def str_to_bytes_base64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value)

def create_jwt_token(user_id: bytes, token_type: str, minutes: int) -> str:
    payload = {
        "sub": bytes_to_str_base64(user_id),
        "iat": datetime.now(),
        "type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes)
    }

    token = jwt.encode(
        payload=payload,
        algorithm=settings.ALGORITHM,
        key=settings.SECRET_KEY
    )

    return token

def decode_token_jwt(token: str) -> dict:
    return jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={
            "require": ["sub", "exp", "type"]
        }
    )

def set_token(
    response: Response,
    key: str,
    value: str,
    path: str = "/",
    max_age: int = 900,
):
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=max_age,
        path=path
    )

def delete_all_jwt_token(response: Response) -> Response:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

def set_login_tokens(response: Response, user_id: bytes) -> None:
    access_token = create_jwt_token(
        user_id,
        token_settings.ACCESS,
        token_settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    refresh_token = create_jwt_token(
        user_id, 
        token_settings.REFRESH, 
        token_settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    set_token(
        response=response,
        key=token_settings.ACCESS,
        value=access_token,
        max_age=token_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    set_token(
        response=response,
        key=token_settings.REFRESH,
        value=refresh_token,
        max_age=token_settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
    )
