from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.models.passkey import Passkey
from app.schemas.user import UserCreate

class PasskeyRepo():
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user: UserCreate) -> User:
        new_user = User(
            name=user.name,
            email=user.email
        )

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user

    def get_credentials_by_email(self, user_email: str):
        return self.session.scalars(
            select(Passkey)
            .where(Passkey.user_email == user_email)
        ).all()

    def get_user_by_email(self, user_email: str):
        return self.session.scalar(
            select(User)
            .where(User.email == user_email)
        )
    