from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models.base import Base, int_pk
from app.db.repository import Repository
from app.core.password import get_password_hash


unique_str_k = Annotated[str, mapped_column(unique=True, nullable=False)]


class User(Base):
    id: Mapped[int_pk]
    username: Mapped[unique_str_k]
    full_name: Mapped[str]
    email: Mapped[unique_str_k]
    age: Mapped[int]
    hashed_password: Mapped[bytes]
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner")


class UserRepository(Repository):
    model = User

    @classmethod
    async def get_user_by_username(cls, username) -> User:
        user = await cls.find_one(username=username)
        return user

    @classmethod
    async def add_user(cls, user_data: dict) -> User:
        user_data['hashed_password'] = get_password_hash(user_data.pop('password'))
        user = await cls.add_one(user_data)
        return user

    @classmethod
    async def get_user_by_id(cls, user_id: str) -> User:
        user = await cls.find_one(id=user_id)
        return user
