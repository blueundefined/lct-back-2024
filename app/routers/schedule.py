"""
POST /schedule: Настройка расписания для автоматизированного проведения работ.
GET /schedule: Получение текущих настроек расписания.
PUT /schedule: Изменение настроек расписания."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import config
from app.database.connection import get_session
from app.models import ScheduleCreate, ScheduleGet, SchedulePatch
from app.services import SchedulesService

router = APIRouter(prefix=config.BACKEND_PREFIX)

@router.get(
    "/schedule",
    response_model=ScheduleGet,
    response_description="Успешный возврат расписания для автоматизированного проведения работ",
    status_code=status.HTTP_200_OK,
    description="Получить текущие настройки расписания",
    summary="Получение расписания",
)
async def get(
    db: AsyncSession = Depends(get_session),
    schedules_service: SchedulesService = Depends(),
):
    return await schedules_service.get(db=db)

@router.post(
    "/schedule",
    response_model=ScheduleGet,
    response_description="Расписание успешно создано",
    status_code=status.HTTP_201_CREATED,
    description="Создать расписание и вернуть его",
    summary="Создание расписания",
)
async def create(
    model: ScheduleCreate,
    db: AsyncSession = Depends(get_session),
    schedules_service: SchedulesService = Depends(),
):
    return await schedules_service.create(db=db, model=model)

@router.patch(
    "/schedule",
    response_model=ScheduleGet,
    response_description="Расписание успешно изменено",
    status_code=status.HTTP_200_OK,
    description="Изменить расписание и вернуть его",
    summary="Изменение расписания",
)
async def patch(
    model: SchedulePatch,
    db: AsyncSession = Depends(get_session),
    schedules_service: SchedulesService = Depends(),
):
    return await schedules_service.patch(db=db, model=model)





