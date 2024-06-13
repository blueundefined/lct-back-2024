from typing import List

from fastapi import APIRouter, Depends, Path, Query
from pydantic import UUID4, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import config
from app.database.connection import get_session
from app.models import DataSourceCreate, DataSourceGet, DataSourcePatch
from app.services import DataSourcesService
from app.services.auth import verify_access_token

#router = APIRouter(prefix=config.BACKEND_PREFIX, dependencies=[Depends(verify_access_token)])
router = APIRouter(prefix=config.BACKEND_PREFIX)

@router.get(
    "/data_source",
    response_model=List[DataSourceGet],
    response_description="Успешный возврат списка источников данных",
    status_code=status.HTTP_200_OK,
    description="Получить список всех источников данных",
    summary="Получение всех источников данных",
    # responses={},
)
async def get_all(
    db: AsyncSession = Depends(get_session),
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
    data_sources_service: DataSourcesService = Depends(),
):
    return await data_sources_service.get_all(db=db, limit=limit, offset=offset)

@router.get(
    "/data_source/{id}",
    response_model=DataSourceGet,
    response_description="Успешный возврат источника данных",
    status_code=status.HTTP_200_OK,
    description="Получить источник данных по его id",
    summary="Получение источника данных",
)
async def get(
    id: int = Path(..., description="Идентификатор источника данных"),
    db: AsyncSession = Depends(get_session),
    data_sources_service: DataSourcesService = Depends(),
):
    return await data_sources_service.get(db=db, id=id)

@router.post(
    "/data_source",
    response_model=DataSourceGet,
    deprecated=True,
    response_description="Источник данных успешно создан",
    status_code=status.HTTP_201_CREATED,
    description="Создать источник данных и вернуть его",
    summary="Создание источника данных",
    # responses={},
)
async def create(
    model: DataSourceCreate,
    db: AsyncSession = Depends(get_session),
    data_sources_service: DataSourcesService = Depends(),
):
    return await data_sources_service.create(db=db, model=model)

@router.put(
    "/data_source/{id}",
    response_model=DataSourceGet,
    deprecated=True,
    response_description="Источник данных успешно обновлен",
    status_code=status.HTTP_200_OK,
    description="Обновить источник данных по его id",
    summary="Обновление источника данных",
    # responses={},
)
async def update(
    model: DataSourceCreate,
    id: int = Path(..., description="Идентификатор источника данных"),
    db: AsyncSession = Depends(get_session),
    data_sources_service: DataSourcesService = Depends(),
):
    return await data_sources_service.update(db=db, id=id, model=model)

@router.patch(
    "/data_source/{id}",
    response_model=DataSourceGet,
    deprecated=True,
    response_description="Источник данных успешно обновлен",
    status_code=status.HTTP_200_OK,
    description="Изменить источник данных по его id (частичное обновление модели)",
    summary="Изменение источника по id (только указанные поля будут изменены)",
    # responses={},
)
async def patch(
    model: DataSourcePatch,
    id: int = Path(..., description="Идентификатор источника данных"),
    db: AsyncSession = Depends(get_session),
    data_sources_service: DataSourcesService = Depends(),
):
    return await data_sources_service.patch(db=db, id=id, model=model)
