from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import config
from app.database.connection import get_session
from pydantic import UUID4, BaseModel, EmailStr, Field
from app.models.vri import VRIGet
from app.models.cadastral_manual import CadastralManualGet

from app.services import CadastralManualsService


router = APIRouter(prefix=config.BACKEND_PREFIX)

@router.get(
    "/cadastral/{cadastral_quarter_number}",
    response_model=CadastralManualGet,
    response_description="Успешный возврат данных по кадастровому кварталу",
    status_code=status.HTTP_200_OK,
    description="Получить данные по кадастровому кварталу",
    summary="Получение данных по кадастровому кварталу",
)
async def get(
    db: AsyncSession = Depends(get_session),
    cadastral_quarter_number: str = Field(..., description="Номер кадастрового квартала"),
):
    return await CadastralManualsService.get(db=db, cadastral_quarter_number=cadastral_quarter_number)

@router.get( 
    "/cadastral",
    response_model=list[CadastralManualGet],
    response_description="Успешный возврат списка данных по кадастровым кварталам",
    status_code=status.HTTP_200_OK,
    description="Получить список данных по кадастровым кварталам",
    summary="Получение данных по кадастровым кварталам",
)
async def get_all(
    db: AsyncSession = Depends(get_session),
    limit: int = 100,
    offset: int = 0,
):
    return await CadastralManualsService.get_all(db=db, limit=limit, offset=offset)