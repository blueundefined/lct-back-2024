import traceback
from typing import List, Optional

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from loguru import logger
from pydantic import UUID4, BaseModel
from starlette.responses import JSONResponse

from app.config import config

class Message(BaseModel):
    id: Optional[UUID4] = None
    message: str

    def __hash__(self):
        return hash((self.id, self.message))

async def catch_unhandled_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        error = {
            "message": get_endpoint_message(request),
            "errors": [Message(id=None, message="Отказано в обработке из-за неизвестной ошибки на сервере")],
        }
        if not config.DEBUG:
            logger.info(traceback.format_exc())
            return JSONResponse(status_code=500, content=jsonable_encoder(error))
        else:
            raise

endpoint_message = {
    ("POST", "/api/signin"): "Ошибка входа в систему",
    ("POST", "/api/signup"): "Ошибка регистрации в системе",
    ("POST", "/api/user"): "Ошибка создания пользователя",
    ("GET", "/api/user"): "Ошибка получения всех пользователей",
    ("GET", "/api/user/{id}"): "Ошибка получения пользователя по id",
    ("GET", "/api/user/email/{email}"): "Ошибка получения пользователя по email",
    ("PUT", "/api/user/{id}"): "Ошибка изменения пользователя по id",
    ("PATCH", "/api/user/{id}"): "Ошибка частичного изменения пользователя по id",
    ("DELETE", "/api/user/{id}"): "Ошибка удаления пользователя по id",
    ("GET", "/api/data_source"): "Ошибка получения всех источников данных",
    ("GET", "/api/data_source/{id}"): "Ошибка получения источника данных по id",
    ("POST", "/api/data_source"): "Ошибка создания источника данных",
    ("PUT", "/api/data_source/{id}"): "Ошибка изменения источника данных по id",
    ("PATCH", "/api/data_source/{id}"): "Ошибка частичного изменения источника данных по id",
    ("DELETE", "/api/data_source/{id}"): "Ошибка удаления источника данных по id",
    ("GET", "/api/data_source/{id}/data_set"): "Ошибка получения всех наборов данных по id источника данных",
    ("GET", "/api/data_source/{id}/data_set/{data_set_id}"): "Ошибка получения набора данных по id и id источника данных",
    ("POST", "/api/data_source/{id}/data_set"): "Ошибка создания набора данных по id источника данных",
    ("PUT", "/api/data_source/{id}/data_set/{data_set_id}"): "Ошибка изменения набора данных по id и id источника данных",
    ("PATCH", "/api/data_source/{id}/data_set/{data_set_id}"): "Ошибка частичного изменения набора данных по id и id источника данных",
    ("DELETE", "/api/data_source/{id}/data_set/{data_set_id}"): "Ошибка удаления набора данных по id и id источника данных",
} 

def get_endpoint_message(request: Request):
    method, path = request.scope["method"], request.scope["path"]
    for path_parameter, value in request.scope["path_params"].items():
        path = path.replace(value, "{" + path_parameter + "}")
    return endpoint_message.get((method, path))

class ValidationUtils:
    @staticmethod
    def validate_type_error(error):
        field = error["loc"][-1]
        type_ = error["type"].split(".")[-1]
        msg = error["msg"]
        return f'Поле "{field}" Имеет неверный тип данных. Укажите "{type_}" ({msg})'

    @staticmethod
    def validate_const(error):
        field = error["loc"][-1]
        value = error["ctx"]["given"]
        allowed_values = error["ctx"]["permitted"]
        return (
            f'Поле "{field}" имеет некорректное значение, Вы указали  "{value}". Возможные значения: {allowed_values}'
        )

    @staticmethod
    def validate_invalid_discriminator(error):
        allowed_values = error["ctx"]["allowed_values"]
        discriminator_value = error["ctx"]["discriminator_key"]
        user_value = error["ctx"]["discriminator_value"]

        return (
            f'Поле "{discriminator_value}" является обязательным. Вы указали "{user_value}".'
            f"Возможные значения {allowed_values}"
        )

    @staticmethod
    def validate_missing_discriminator(error):
        discriminator_value = error["ctx"]["discriminator_key"]

        return f'Поле "{discriminator_value}" является обязательным.'

    @staticmethod
    def validate_missing(error):
        field = error["loc"][-1]
        return f"Поле {field} является обязательным"

templates_function = {
    "missing": ValidationUtils.validate_missing,
    "const": ValidationUtils.validate_const,
    "": ValidationUtils.validate_type_error,
    "invalid_discriminator": ValidationUtils.validate_invalid_discriminator,
    "missing_discriminator": ValidationUtils.validate_missing_discriminator,
}

class ValidationHandler:
    @classmethod
    async def _build_final_error(cls, request: Request, errors: List[Message]):
        return {"message": get_endpoint_message(request), "errors": list(set(errors))}

    @classmethod
    async def _build_message(cls, type_: str, error: dict):
        try:
            if type_ in templates_function.keys():
                return templates_function[type_](error)
            else:
                return templates_function[""](error)
        except KeyError:
            return error["msg"]

    @classmethod
    async def validation_handler(cls, request: Request, exc):
        errors = []
        for error in exc.errors():
            type_ = error["type"].split(".")[-1]
            message = await cls._build_message(type_, error)
            errors.append(Message(id=None, message=message))

        error = await cls._build_final_error(request, errors)

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(error))

async def logging_handler(request: Request, exc: HTTPException):
    error = {"message": get_endpoint_message(request), "errors": exc.detail}
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(error))

def add_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, ValidationHandler.validation_handler)
    app.add_exception_handler(HTTPException, logging_handler)
