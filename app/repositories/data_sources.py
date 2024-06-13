from typing import List

from fastapi import HTTPException
from pydantic import UUID4, EmailStr
from sqlalchemy import BigInteger, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app.database.tables import DataSource
from app.models import DataSourceCreate, DataSourcePatch

class DataSourcesRepository:
    @staticmethod
    async def create(db: AsyncSession, model: DataSourceCreate) -> DataSource:
        data_source = DataSource(**model.dict())
        db.add(data_source)
        await db.commit()
        await db.refresh(data_source)
        return data_source

    @staticmethod
    async def get_all(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[DataSource]:
        res = await db.execute(select(DataSource).offset(cast(offset, BigInteger)).limit(limit))
        return res.scalars().unique().all()

    @staticmethod
    async def get(db: AsyncSession, id: int) -> DataSource:
        res = await db.execute(select(DataSource).where(DataSource.id == id).limit(1))
        return res.scalar()

    @staticmethod
    async def update(db: AsyncSession, id: int, model: DataSourceCreate) -> DataSource:
        data_source = await DataSourcesRepository.get(db, id)

        if data_source is None:
            raise HTTPException(404, "Источник данных не найден")

        await db.execute(update(DataSource).where(DataSource.id == id).values(**model.dict()))
        await db.commit()
        await db.refresh(data_source)

        return data_source

    @staticmethod
    async def patch(db: AsyncSession, id: int, model: DataSourcePatch) -> DataSource:
        data_source = await DataSourcesRepository.get(db, id)

        if data_source is None:
            raise HTTPException(404, "Источник данных не найден")

        await db.execute(update(DataSource).where(DataSource.id == id).values(**model.dict()))
        await db.commit()
        await db.refresh(data_source)

        return data_source