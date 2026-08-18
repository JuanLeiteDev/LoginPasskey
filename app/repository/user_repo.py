from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate

class UserRepo():
    def __init__(self, session: Session):
            self.session = session

    def create_user(self, user: UserCreate) -> User:
        new_user = User(
            name=user.username,
        )

        self.session.add(new_user)
        self.session.flush()
        return new_user

    def get_user_by_email(self, user_email: str):
        return self.session.scalar(
            select(User)
            .where(User.email == user_email)
        )

    def get_user_by_name(self, user_name: str):
         return self.session.scalar(
              select(User)
              .where(User.username == user_name)
         )

    def get_user_by_id(self, user_id: bytes):
         return self.session.scalar(
              select(User)
              .where(User.id == user_id)
         )

    def update_user_name(self, new_name: str, user: User):
         user.username = new_name
         self.session.flush()

    def update_user_status(self, user: User):
         user.status = True
         self.session.flush()
