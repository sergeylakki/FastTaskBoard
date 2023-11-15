import uuid
from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from pydantic import UUID4
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.db.models.base import Base
from app.db.repository import Repository

uuid_pk = Annotated[UUID, mapped_column(primary_key=True)]
timestamp = Annotated[datetime, mapped_column(nullable=False)]


class RefreshToken(Base):
    uuid: Mapped[uuid_pk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    refresh_token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[timestamp]
    created_at: Mapped[timestamp] = mapped_column(server_default=func.now())
    updated_at: Mapped[timestamp] = mapped_column(onupdate=func.now(), nullable=True)
    
    
class RefreshTokenRepository(Repository):
    model = RefreshToken

    @classmethod
    async def create_refresh_token(cls, user_id: int, expires_at: datetime, 
                                   refresh_token: str
                                   ) -> str:
        
            refresh_token = await cls.add_one({'uuid': uuid.uuid4(),
                                               'refresh_token': refresh_token,
                                               'expires_at': expires_at,
                                               'user_id': user_id})

            return refresh_token.refresh_token
    
    @classmethod
    async def get_refresh_token(cls, refresh_token: str) -> RefreshToken | None:
        return await cls.find_one(refresh_token=refresh_token)

    @classmethod
    async def expire_refresh_token(cls, refresh_token_uuid: UUID4) -> None:
        await cls.edit_one(data={'expires_at': datetime.utcnow() - timedelta(days=1)},
                           uuid=refresh_token_uuid)

    @classmethod
    async def update_refresh_token(cls, refresh_token: RefreshToken, new_refresh_token_value: str) -> None:
        await cls.edit_one({'expires_at': datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
                            'refresh_token':new_refresh_token_value},
                           uuid=refresh_token.uuid)
