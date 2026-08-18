from sqlalchemy.orm import Session
from fastapi import Request

from app.core.exceptions import (
    InternalServerError,
    InvalidRegistrationResponseError,
    PasskeyUserVerificationFailedError,
    ActiveUserEmailAlreadyExistsError,
    ChallengeNotFoundError,
    CredentialNotFoundError,
    UserNotFoundError
)
from app.repository.passkey_repo import PasskeyRepo
from app.repository.user_repo import UserRepo
from app.schemas.user import UserCreate
from app.core.config import settings


import base64
import webauthn
from webauthn.helpers.exceptions import InvalidRegistrationResponse
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    RegistrationCredential,
    AuthenticationCredential
)

class PasskeyService():
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _get_authenticator_selection():
        return AuthenticatorSelectionCriteria(
        resident_key=ResidentKeyRequirement.REQUIRED,
        user_verification=UserVerificationRequirement.REQUIRED
    )

    def register_options_service(self, user: UserCreate):
        existing_user = UserRepo(self.session).get_user_by_email(user.email)
        if existing_user:
            if existing_user.status:
                raise ActiveUserEmailAlreadyExistsError()
        else:
            existing_user = UserRepo(self.session).create_user(user)

        authenticator_selec = self._get_authenticator_selection()

        options = webauthn.generate_registration_options(
            rp_id=settings.RP_ID,
            rp_name=settings.RP_NAME,
            user_id=existing_user.id,
            user_name=existing_user.email,
            user_display_name=existing_user.name,
            authenticator_selection=authenticator_selec,
            exclude_credentials=[]
        )

        challenge = base64.urlsafe_b64encode(options.challenge).decode("ascii")
        options_json = webauthn.options_to_json(options)

        return options_json, challenge

    def register_verify_service(self, credential: RegistrationCredential, request: Request):
        challenge = request.session.get("registration_challenge")
        if not challenge:
            raise ChallengeNotFoundError()

        if not credential:
            raise CredentialNotFoundError()
        
        challenge_bytes = base64.urlsafe_b64decode(challenge)

        try:
            verification = webauthn.verify_registration_response(
                credential=credential,
                expected_challenge=challenge_bytes,
                expected_origin=settings.RP_ORIGIN,
                expected_rp_id=settings.RP_ID,
                require_user_verification=True,
            )
        except InvalidRegistrationResponse:
            raise InvalidRegistrationResponseError()
        except Exception:
            raise InternalServerError()

        if not verification.user_verified:
            raise PasskeyUserVerificationFailedError()
        
        user_email = request.session.get("current_user")
        PasskeyRepo(self.session).save_credentials_passkey(verification, user_email)

        user = UserRepo(self.session).get_user_by_email(user_email)
        user.status = True
        self.session.commit()
        request.session.clear()
        return f"Conta criada com succeso!"

    def auth_options_service(self):
        options = webauthn.generate_authentication_options(
            rp_id=settings.RP_ID,
            user_verification=UserVerificationRequirement.REQUIRED
        )

        options_json = webauthn.options_to_json(options)
        challenge = base64.urlsafe_b64encode(options.challenge).decode("ascii")
        
        return options_json, challenge

    def auth_verify_service(self, credentials: AuthenticationCredential, request: Request):
        challenge = request.session.get("authentication_challenge")
        if not challenge:
            raise ChallengeNotFoundError()

        if not credentials:
            raise CredentialNotFoundError()

        challenge_bytes = base64.urlsafe_b64decode(challenge)
        user_id = credentials.response.user_handle

        existing_user = UserRepo(self.session).get_user_by_id(user_id)
        if not existing_user:
            raise UserNotFoundError()

        existing_credential = PasskeyRepo(self.session).get_credential_by_id(credentials.raw_id)
        if not existing_credential:
            raise CredentialNotFoundError()

        try:
            verification = webauthn.verify_authentication_response(
                credential=credentials,
                expected_challenge=challenge_bytes,
                expected_origin=settings.RP_ORIGIN,
                expected_rp_id=settings.RP_ID,
                require_user_verification=True,
                credential_public_key=existing_credential.public_key,
                credential_current_sign_count=existing_credential.sign_count
            )
        except InvalidRegistrationResponse:
            raise InvalidRegistrationResponseError()
        except Exception:
            raise InternalServerError()

        if not verification.user_verified:
            raise PasskeyUserVerificationFailedError() 

        PasskeyRepo(self.session).update_sign_count(
            verification.new_sign_count, 
            existing_credential
        )

        return f"Login efetuado com sucesso!"
    