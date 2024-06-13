from typing import List

from fastapi import HTTPException
from pydantic import UUID4, EmailStr
from sqlalchemy import BigInteger, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app.database.tables import DataSourceMeta
from app.models import DataSourceMetaCreate, DataSourceMetaPatch

class DataSourceMetasRepository:
    @staticmethod
    async def create(db: AsyncSession, model: DataSourceMetaCreate) -> DataSourceMeta:
        data_source_meta = DataSourceMeta(**model.dict())
        db.add(data_source_meta)
        await db.commit()
        await db.refresh(data_source_meta)
        return data_source_meta

    @staticmethod
    async def get_all(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[DataSourceMeta]:
        res = await db.execute(select(DataSourceMeta).offset(cast(offset, BigInteger)).limit(limit))
        return res.scalars().unique().all()
    
    @staticmethod
    async def get_by_data_source_id(db: AsyncSession, data_source_id: int, offset: int = 0, limit: int = 100) -> List[DataSourceMeta]:
        res = await db.execute(select(DataSourceMeta).where(DataSourceMeta.data_source_id == data_source_id).offset(cast(offset, BigInteger)).limit(limit))
        return res.scalars().unique().all()

    @staticmethod
    async def get(db: AsyncSession, id: int) -> DataSourceMeta:
        res = await db.execute(select(DataSourceMeta).where(DataSourceMeta.id == id).limit(1))
        return res.scalar()

    @staticmethod
    async def update(db: AsyncSession, id: int, model: DataSourceMetaCreate) -> DataSourceMeta:
        data_source_meta = await DataSourceMetasRepository.get(db, id)

        if data_source_meta is None:
            raise HTTPException(404, "Метаданные источника данных не найдены")

        await db.execute(update(DataSourceMeta).where(DataSourceMeta.id == id).values(**model.dict()))
        await db.commit()
        await db.refresh(data_source_meta)

        return data_source_meta

    @staticmethod
    async def patch(db: AsyncSession, id: int, model: DataSourceMetaPatch) -> DataSourceMeta:
        data_source_meta = await DataSourceMetasRepository.get(db, id)

        if data_source_meta is None:
            raise HTTPException(404, "Метаданные источника данных не найдены")

        await db.execute(update(DataSourceMeta).where(DataSourceMeta.id == id).values(**model.dict()))
        await db.commit()
        await db.refresh(data_source_meta)

        return data_source_meta