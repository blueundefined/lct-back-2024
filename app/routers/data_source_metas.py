from typing import List

from fastapi import APIRouter, Depends, Path, Query
from pydantic import UUID4, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import config
from app.database.connection import get_session
from app.models import DataSourceMetaCreate, DataSourceMetaGet, DataSourceMetaPatch
from app.services import DataSourceMetasService
from app.services.auth import verify_access_token

#router = APIRouter(prefix=config.BACKEND_PREFIX, dependencies=[Depends(verify_access_token)])
router = APIRouter(prefix=config.BACKEND_PREFIX)

@router.get(
    "/data_source_meta",
    response_model=List[DataSourceMetaGet],
    response_description="Успешный возврат списка метаданных источников данных",
    status_code=status.HTTP_200_OK,
    description="Получить список всех метаданных источников данных",
    summary="Получение всех метаданных источников данных",
    # responses={},
)
async def get_all(
    db: AsyncSession = Depends(get_session),
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
    data_source_metas_service: DataSourceMetasService = Depends(),
):
    return await data_source_metas_service.get_all(db=db, limit=limit, offset=offset)

@router.get(
    "/data_source_meta/{id}",
    response_model=DataSourceMetaGet,
    response_description="Успешный возврат метаданных источника данных",
    status_code=status.HTTP_200_OK,
    description="Получить метаданные источника данных по его id",
    summary="Получение метаданных источника данных",
)
async def get(
    id: int = Path(..., description="Идентификатор метаданных источника данных"),
    db: AsyncSession = Depends(get_session),
    data_source_metas_service: DataSourceMetasService = Depends(),
):
    return await data_source_metas_service.get(db=db, id=id)

@router.get(
    "/data_source_meta/data_source/{data_source_id}",
    response_model=List[DataSourceMetaGet],
    response_description="Успешный возврат списка метаданных источников данных",
    status_code=status.HTTP_200_OK,
    description="Получить список всех метаданных источников данных по id источника данных",
    summary="Получение всех метаданных источников данных по id источника данных",
    # responses={},
)
async def get_by_data_source_id(
    data_source_id: int = Path(..., description="Идентификатор источника данных"),
    db: AsyncSession = Depends(get_session),
    data_source_metas_service: DataSourceMetasService = Depends(),
):
    return await data_source_metas_service.get_by_data_source_id(db=db, data_source_id=data_source_id)

@router.post(
    "/data_source_meta",
    response_model=DataSourceMetaGet,
    response_description="Метаданные источника данных успешно созданы",
    status_code=status.HTTP_201_CREATED,
    description="Создать метаданные источника данных и вернуть их",
    summary="Создание метаданных источника данных",
    # responses={},
)
async def create(
    model: DataSourceMetaCreate,
    db: AsyncSession = Depends(get_session),
    data_source_metas_service: DataSourceMetasService = Depends(),
):
    return await data_source_metas_service.create(db=db, model=model)

@router.put(
    "/data_source_meta/{id}",
    response_model=DataSourceMetaGet,
    response_description="Метаданные источника данных успешно обновлены",
    status_code=status.HTTP_200_OK,
    description="Обновить метаданные источника данных по его id",
    summary="Обновление метаданных источника данных",
    # responses={},
)
async def update(
    model: DataSourceMetaCreate,
    id: int = Path(..., description="Идентификатор метаданных источника данных"),
    db: AsyncSession = Depends(get_session),
    data_source_metas_service: DataSourceMetasService = Depends(),
):
    return await data_source_metas_service.update(db=db, id=id, model=model)

@router.patch(
    "/data_source_meta/{id}",
    response_model=DataSourceMetaGet,
    response_description="Метаданные источника данных успешно обновлены",
    status_code=status.HTTP_200_OK,
    description="Изменение метаданные источника данных по его id",
    summary="Изменение метаданных источника по id (только указанные поля будут изменены)",
    # responses={},
)
async def patch(
    model: DataSourceMetaPatch,
    id: int = Path(..., description="Идентификатор метаданных источника данных"),
    db: AsyncSession = Depends(get_session),
    data_source_metas_service: DataSourceMetasService = Depends(),
):
    return await data_source_metas_service.patch(db=db, id=id, model=model)