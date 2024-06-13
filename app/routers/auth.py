from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import config
from app.database.connection import get_session
from app.models import Token, UserAuth, UserCreate
from app.services import AuthService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post(
    "/signin",
    response_model=Token,
    response_description="Успешный возврат токена авторизации",
    status_code=status.HTTP_200_OK,
    description="Войти в сервис и получить токен",
    summary="Вход в сервис",
    # responses={},
)
async def signin(model: UserAuth, db: AsyncSession = Depends(get_session), auth_service: AuthService = Depends()):
    token = await auth_service.signin(db=db, model=model)
    response = JSONResponse(content={"access_token": token.access_token})
    response.set_cookie(
        key="access_token",
        httponly=True,
        value=token.access_token,
        max_age=config.BACKEND_JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        path="/",
    )
    return response


@router.post(
    "/signup",
    response_model=Token,
    response_description="Успешный возврат токена авторизации",
    status_code=status.HTTP_200_OK,
    description="Зарегистирироваться в сервисе и получить токен",
    summary="Регистрация в сервисе",
    # responses={},
)
async def signup(model: UserCreate, db: AsyncSession = Depends(get_session), auth_service: AuthService = Depends()):
    token = await auth_service.signup(db=db, model=model)
    response = JSONResponse(content={"access_token": token.access_token})
    response.set_cookie(
        key="access_token",
        httponly=True,
        value=token.access_token,
        max_age=config.BACKEND_JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        path="/",
    )
    return response
    
@router.get( # logout endpoint
    "/logout",
    response_description="Успешный выход из сервиса",
    status_code=status.HTTP_200_OK,
    description="Выйти из сервиса и удалить токен",
    summary="Выход из сервиса",
    # responses={},
)
async def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key="access_token")
    return response
