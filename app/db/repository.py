from sqlalchemy.exc import IntegrityError, NoResultFound
from app.db.database import async_session
from abc import ABC, abstractmethod
from sqlalchemy import insert, select, update, delete


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self):
        raise NotImplementedError

    @abstractmethod
    async def edit_one_by_id(self, id: int, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_some(self, **filter_by):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int):
        raise NotImplementedError


class Repository(AbstractRepository):
    model = None
    async_session = async_session()

    @classmethod
    async def add_one(cls, data: dict) -> model:
        async with cls.async_session as session:
            stmt = insert(cls.model).values(**data).returning(cls.model)
            res = await session.execute(stmt)
            try:
                await session.commit()
                return res.scalar_one()
            except IntegrityError as e:
                await session.rollback()
                raise e

    @classmethod
    async def find_all(cls) -> list[model]:
        async with cls.async_session as session:
            query = select(cls.model)
            res = await session.execute(query)
            return res.scalars().all()

    @classmethod
    async def edit_one_by_id(cls, id: int, data: dict) -> model:
        async with cls.async_session as session:
            stmt = update(cls.model).values(**data).filter_by(id=id).returning(cls.model)
            res = await session.execute(stmt)
            try:
                await session.commit()
                return res.scalar_one()
            except IntegrityError as e:
                await session.rollback()
                raise e
            except NoResultFound as e:
                return None
    
    @classmethod
    async def edit_one(cls, data: dict, **filter_by) -> model:
        async with cls.async_session as session:
            stmt = update(cls.model).values(**data).filter_by(**filter_by).returning(cls.model)
            res = await session.execute(stmt)
            try:
                await session.commit()
                return res.scalar_one()
            except IntegrityError as e:
                await session.rollback()
                raise e

    @classmethod
    async def find_one(cls, **filter_by) -> model:
        async with cls.async_session as session:
            query = select(cls.model).filter_by(**filter_by)
            res = await session.execute(query)
            try:
                return res.scalar_one()
            except NoResultFound:
                return None

    @classmethod
    async def find_some(cls, limit=0, offset=0, **filter_by) -> list[model]:
        async with cls.async_session as session:
            query = select(cls.model).filter_by(**filter_by)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            res = await session.execute(query)
            return res.scalars().all()

    @classmethod
    async def delete_one(cls, id: int) -> model:
        async with cls.async_session as session:
            stmt = delete(cls.model).where(cls.model.id == id).returning(cls.model)
            res = await session.execute(stmt)
            try:
                await session.commit()
                return res.scalar_one()
            except IntegrityError as e:
                await session.rollback()
                raise e
            except NoResultFound as e:
                return None
