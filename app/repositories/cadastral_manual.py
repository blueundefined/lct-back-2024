from typing import List

from fastapi import HTTPException
from pydantic import UUID4, EmailStr
from sqlalchemy import BigInteger, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app.database.tables import CadastralManual
from app.models import CadastralManualCreate, CadastralManualPatch

class CadastralManualsRepository:
    @staticmethod
    async def create(db: AsyncSession, model: CadastralManualCreate) -> CadastralManual:
        cadastral_manual = CadastralManual(**model.dict())
        db.add(cadastral_manual)
        await db.commit()
        await db.refresh(cadastral_manual)
        return cadastral_manual

    @staticmethod
    async def get_all(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[CadastralManual]:
        res = await db.execute(select(CadastralManual).offset(cast(offset, BigInteger)).limit(limit))
        return res.scalars().unique().all()
    
    @staticmethod
    async def get(db: AsyncSession, id: int) -> CadastralManual:
        res = await db.execute(select(CadastralManual).where(CadastralManual.id == id).limit(1))
        return res.scalar()

    @staticmethod
    async def update(db: AsyncSession, id: int, model: CadastralManualCreate) -> CadastralManual:
        cadastral_manual = await CadastralManualsRepository.get(db, id)

        if cadastral_manual is None:
            raise HTTPException(404, "Мануал кадастрового квартала не найден")

        await db.execute(update(CadastralManual).where(CadastralManual.id == id).values(**model.dict()))
        await db.commit()
        await db.refresh(cadastral_manual)

        return cadastral_manual

    @staticmethod
    async def patch(db: AsyncSession, id: int, model: CadastralManualPatch) -> CadastralManual:
        cadastral_manual = await CadastralManualsRepository.get(db, id)

        if cadastral_manual is None:
            raise HTTPException(404, "Мануал кадастрового квартала не найден")

        await db.execute(update(CadastralManual).where(CadastralManual.id == id).values(**model.dict()))
        await db.commit()
        await db.refresh(cadastral_manual)

        return cadastral_manual