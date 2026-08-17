from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, Request

from app.models.user import User
from app.models.passkey import Passkey
from app.schemas.user import UserCreate
from app.core.config import settings

import webauthn
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    PublicKeyCredentialDescriptor,
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

    def _create_user(self, user: UserCreate) -> User:
        new_user = User(
            name=user.name,
            email=user.email
        )

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user

    def _get_credentials_by_email(self, user_email: str):
        return self.session.scalars(
            select(Passkey)
            .where(Passkey.user_email == user_email)
        ).all()

    def _get_user_by_email(self, user_email: str):
        return self.session.scalar(
            select(User)
            .where(User.email == user_email)
        )

    def register_options_service(self, user: UserCreate):
        existing_user = self._get_user_by_email(user.email)
        if existing_user:
            if existing_user.status:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe um utilizador ativo com esse email."
                )
        else:
            existing_user = self._create_user(user)

        authenticator_selec = self._get_authenticator_selection()
        exclude_credentials = self._get_credentials_by_email(user.email)
        exclude_credentials = [
            PublicKeyCredentialDescriptor(id=credential)
            for credential in exclude_credentials
        ]

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
        expected_challeng = request.session.get("registration_challenge")
        verification = webauthn.verify_registration_response(
            credential=credential,
            expected_challenge=expected_challeng,
            expected_origin=settings.RP_ORIGIN,
            expected_rp_id=settings.RP_ID,
            require_user_verification=True,
        )

        
    