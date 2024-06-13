from __future__ import annotations

from fastapi import HTTPException, Response
from pydantic import UUID4, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ScheduleCreate, ScheduleGet, SchedulePatch
from app.repositories import SchedulesRepository


class SchedulesService:
    @staticmethod
    async def create(db: AsyncSession, model: ScheduleCreate) -> ScheduleGet:
        schedule = await SchedulesRepository.create(db, model)
        return ScheduleGet.model_validate(schedule)

    @staticmethod
    async def get(db: AsyncSession) -> ScheduleGet:
        schedule = await SchedulesRepository.get(db)
        if schedule is None:
            raise HTTPException(404, "Расписание не найдено")
        return ScheduleGet.model_validate(schedule)

    @staticmethod
    async def update(db: AsyncSession, id: int, model: ScheduleCreate) -> ScheduleGet:
        schedule = await SchedulesRepository.update(db, id, model)
        if schedule is None:
            raise HTTPException(404, "Расписание не найдено")
        return ScheduleGet.model_validate(schedule)

    @staticmethod
    async def patch(db: AsyncSession, id: int, model: SchedulePatch) -> ScheduleGet:
        schedule = await SchedulesRepository.patch(db, id, model)
        if schedule is None:
            raise HTTPException(404, "Расписание не найдено")
        return ScheduleGet.model_validate(schedule)