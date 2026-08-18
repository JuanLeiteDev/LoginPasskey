from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.passkey import Passkey

from webauthn.registration.verify_registration_response import VerifiedRegistration

class PasskeyRepo():
    def __init__(self, session: Session):
        self.session = session

    def save_credentials_passkey(self, credentials: VerifiedRegistration, user_id: bytes):
        new_passkey = Passkey(
            credential_id=credentials.credential_id,
            public_key=credentials.credential_public_key,
            sign_count=credentials.sign_count,
            device_type=credentials.credential_device_type,
            backup=credentials.credential_backed_up,
            user_id=user_id
        )
        
        self.session.add(new_passkey)
        self.session.flush()

    def get_credential_by_id(self, credential_id: bytes):
        return self.session.scalar(
            select(Passkey)
            .where(Passkey.credential_id == credential_id)
        )

    def update_sign_count(self, new_sign_count: int, credential: Passkey):
        credential.sign_count = new_sign_count
        self.session.flush()
        