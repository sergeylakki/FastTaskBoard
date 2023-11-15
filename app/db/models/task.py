from typing import Annotated
from sqlalchemy import ForeignKey
from app.db.models.base import Base, int_pk
from sqlalchemy.orm import Mapped, mapped_column, relationship, Relationship
from app.db.repository import Repository


user_fk = Annotated[int, mapped_column(ForeignKey("user.id"))]


class Task(Base):
    id: Mapped[int_pk]
    title: Mapped[str]
    description: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)
    owner_id: Mapped[user_fk]
    owner: Mapped["User"] = relationship(back_populates="tasks", lazy='selectin')

    #owner: list["User"] = relationship(
    #    back_populates='tasks', sa_relationship_kwargs={'lazy': 'selectin'}
#)


class TaskRepository(Repository):
    model = Task

    @classmethod
    async def create_user_task(cls, user_id: int, data: dict):
        data['owner_id'] = user_id
        return await cls.add_one(data)
