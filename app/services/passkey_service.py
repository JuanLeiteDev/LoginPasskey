from sqlalchemy.orm import Session
from fastapi import HTTPException, Request

from app.repository.passkey_repo import PasskeyRepo
from app.schemas.user import UserCreate
from app.core.config import settings

import base64
import webauthn
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    RegistrationCredential
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
        existing_user = PasskeyRepo(self.session).get_user_by_email(user.email)
        if existing_user:
            if existing_user.status:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe um utilizador ativo com esse email."
                )
        else:
            existing_user = PasskeyRepo(self.session).create_user(user)

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

        return options

    def register_verify_service(self, credential: RegistrationCredential, request: Request):
        challenge = request.session.get("registration_challenge")
        challenge_bytes = base64.urlsafe_b64decode(challenge)

        verification = webauthn.verify_registration_response(
            credential=credential,
            expected_challenge=challenge_bytes,
            expected_origin=settings.RP_ORIGIN,
            expected_rp_id=settings.RP_ID,
            require_user_verification=True,
        )

        return verification
    