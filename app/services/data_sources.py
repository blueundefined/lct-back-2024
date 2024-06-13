from __future__ import annotations

from fastapi import HTTPException, Response
from pydantic import UUID4, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DataSourceCreate, DataSourceGet, DataSourcePatch
from app.repositories import DataSourcesRepository


class DataSourcesService:
    @staticmethod
    async def create(db: AsyncSession, model: DataSourceCreate) -> DataSourceGet:
        data_source = await DataSourcesRepository.create(db, model)
        return DataSourceGet.model_validate(data_source)

    @staticmethod
    async def get_all(db: AsyncSession, offset: int = 0, limit: int = 100) -> list[DataSourceGet]:
        data_sources = await DataSourcesRepository.get_all(db, offset=offset, limit=limit)
        if data_sources is None:
            raise HTTPException(404, "Источники данных не найдены")
        return [DataSourceGet.model_validate(ds) for ds in data_sources]

    @staticmethod
    async def get(db: AsyncSession, id: int) -> DataSourceGet:
        data_source = await DataSourcesRepository.get(db, id)
        if data_source is None:
            raise HTTPException(404, "Источник данных не найден")
        return DataSourceGet.model_validate(data_source)

    @staticmethod
    async def update(db: AsyncSession, id: int, model: DataSourceCreate) -> DataSourceGet:
        data_source = await DataSourcesRepository.update(db, id, model)
        if data_source is None:
            raise HTTPException(404, "Источник данных не найден")
        return DataSourceGet.model_validate(data_source)

    @staticmethod
    async def patch(db: AsyncSession, id: int, model: DataSourcePatch) -> DataSourceGet:
        data_source = await DataSourcesRepository.patch(db, id, model)
        if data_source is None:
            raise HTTPException(404, "Источник данных не найден")
        return DataSourceGet.model_validate(data_source)