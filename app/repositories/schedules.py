from typing import List

from fastapi import HTTPException
from pydantic import UUID4, EmailStr
from sqlalchemy import BigInteger, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app.database.tables import Schedule
from app.models import ScheduleCreate, SchedulePatch


class SchedulesRepository:
    @staticmethod
    async def create(db: AsyncSession, model: ScheduleCreate) -> Schedule:
        schedule = Schedule(**model.dict())
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        return schedule

    @staticmethod
    async def get(db: AsyncSession) -> Schedule:
        res = await db.execute(select(Schedule).order_by(Schedule.id.desc()).limit(1))
        return res.scalar()

    @staticmethod
    async def update(db: AsyncSession, id: int, model: ScheduleCreate) -> Schedule:
        schedule = await SchedulesRepository.get(db, id)

        if schedule is None:
            raise HTTPException(404, "Расписание не найдено")

        await db.execute(update(Schedule).where(Schedule.id == id).values(**model.dict()))
        await db.commit()
        await db.refresh(schedule)

        return schedule

    @staticmethod
    async def patch(db: AsyncSession, id: int, model: SchedulePatch) -> Schedule:
        schedule = await SchedulesRepository.get(db, id)

        if schedule is None:
            raise HTTPException(404, "Расписание не найдено")

        await db.execute(update(Schedule).where(Schedule.id == id).values(**model.dict()))
        await db.commit()
        await db.refresh(schedule)

        return schedule