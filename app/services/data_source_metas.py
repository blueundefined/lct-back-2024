from __future__ import annotations

from fastapi import HTTPException, Response
from pydantic import UUID4, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DataSourceMetaCreate, DataSourceMetaGet, DataSourceMetaPatch
from app.repositories import DataSourceMetasRepository


class DataSourceMetasService:
    @staticmethod
    async def create(db: AsyncSession, model: DataSourceMetaCreate) -> DataSourceMetaGet:
        data_source_meta = await DataSourceMetasRepository.create(db, model)
        return DataSourceMetaGet.model_validate(data_source_meta)

    @staticmethod
    async def get_all(db: AsyncSession, offset: int = 0, limit: int = 100) -> list[DataSourceMetaGet]:
        data_source_metas = await DataSourceMetasRepository.get_all(db, offset=offset, limit=limit)
        if data_source_metas is None:
            raise HTTPException(404, "Метаданные источников данных не найдены")
        return [DataSourceMetaGet.model_validate(dsm) for dsm in data_source_metas]

    @staticmethod
    async def get_by_data_source_id(db: AsyncSession, data_source_id: int, offset: int = 0, limit: int = 100) -> list[DataSourceMetaGet]:
        data_source_metas = await DataSourceMetasRepository.get_by_data_source_id(db, data_source_id, offset=offset, limit=limit)
        if data_source_metas is None:
            raise HTTPException(404, "Метаданные источников данных не найдены")
        return [DataSourceMetaGet.model_validate(dsm) for dsm in data_source_metas]

    @staticmethod
    async def get(db: AsyncSession, id: int) -> DataSourceMetaGet:
        data_source_meta = await DataSourceMetasRepository.get(db, id)
        if data_source_meta is None:
            raise HTTPException(404, "Метаданные источника данных не найдены")
        return DataSourceMetaGet.model_validate(data_source_meta)

    @staticmethod
    async def update(db: AsyncSession, id: int, model: DataSourceMetaCreate) -> DataSourceMetaGet:
        data_source_meta = await DataSourceMetasRepository.update(db, id, model)
        if data_source_meta is None:
            raise HTTPException(404, "Метаданные источника данных не найдены")
        return DataSourceMetaGet.model_validate(data_source_meta)

    @staticmethod
    async def patch(db: AsyncSession, id: int, model: DataSourceMetaPatch) -> DataSourceMetaGet:
        data_source_meta = await DataSourceMetasRepository.patch(db, id, model)
        if data_source_meta is None:
            raise HTTPException(404, "Метаданные источника данных не найдены")