from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as star_status

from app.config import config
from app.database.connection import get_session

router = APIRouter(prefix=config.BACKEND_PREFIX)

@router.get(
    "/health",
    response_description="Успешный возврат статуса здоровья БД",
    status_code=star_status.HTTP_200_OK,
)
async def health(db: AsyncSession = Depends(get_session)):
    return {"status": "ok"}

@router.get(
    "/status",
    response_description="Успешный возврат статуса сервиса",
    status_code=star_status.HTTP_200_OK,
)
async def status():
    return {"status": "ok"}

@router.post(
    "/set_cookie",
    response_description="Успешное установление cookie",
    status_code=star_status.HTTP_201_CREATED,
)
async def set_cookie(cookie: str):
    response = JSONResponse(content={"cookie": cookie})
    response.set_cookie(
        key="cookie",
        httponly=True,
        value=cookie,
        max_age=config.BACKEND_JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return response