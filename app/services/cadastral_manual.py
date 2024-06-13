from __future__ import annotations

from fastapi import HTTPException, Response
from pydantic import UUID4, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CadastralManualGet, CadastralManualPatch, CadastralManualCreate
from app.repositories import CadastralManualsRepository

class CadastralManualsService:
    @staticmethod
    async def create(db: AsyncSession, model: CadastralManualCreate) -> CadastralManualGet:
        cadastral_manual = await CadastralManualsRepository.create(db, model)
        return CadastralManualGet.model_validate(cadastral_manual)

    @staticmethod
    async def get_all(db: AsyncSession, offset: int = 0, limit: int = 100) -> list[CadastralManualGet]:
        cadastral_manuals = await CadastralManualsRepository.get_all(db, offset=offset, limit=limit)
        if cadastral_manuals is None:
            raise HTTPException(404, "Мануалы кадастровых кварталов не найдены")
        return [CadastralManualGet.model_validate(cm) for cm in cadastral_manuals]

    @staticmethod
    async def get(db: AsyncSession, id: int) -> CadastralManualGet:
        cadastral_manual = await CadastralManualsRepository.get(db, id)
        if cadastral_manual is None:
            raise HTTPException(404, "Мануал кадастрового квартала не найден")
        return CadastralManualGet.model_validate(cadastral_manual)

    @staticmethod
    async def update(db: AsyncSession, id: int, model: CadastralManualCreate) -> CadastralManualGet:
        cadastral_manual = await CadastralManualsRepository.update(db, id, model)
        if cadastral_manual is None:
            raise HTTPException(404, "Мануал кадастрового квартала не найден")
        return CadastralManualGet.model_validate(cadastral_manual)

    @staticmethod
    async def patch(db: AsyncSession, id: int, model: CadastralManualPatch) -> CadastralManualGet:
        cadastral_manual = await CadastralManualsRepository.patch(db, id, model)
        if cadastral_manual is None:
            raise HTTPException(404, "Мануал кадастрового квартала не найден")
        return CadastralManualGet.model_validate(cadastral_manual)