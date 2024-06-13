from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, Field

from app.models.utils import optional


class UserBase(BaseModel):
    email: EmailStr = Field(description="Email адрес пользователя")
    first_name: str = Field(description="Имя пользователя", alias="firstName")
    last_name: str = Field(description="Фамилия пользователя", alias="lastName")
    middle_name: Optional[str] = Field(None, description="Отчество пользователя(при наличии)", alias="middleName")

    class Config:
        from_attributes = True
        populate_by_name = True


class UserCreate(UserBase):
    password: str = Field(description="Пароль пользователя")


class UserGet(UserBase):
    guid: UUID4 = Field(description="Уникальный идентификатор пользователя")
    password: str = Field(description="Пароль пользователя")
    created_at: datetime = Field(description="Время создания пользователя", alias="createdAt")
    updated_at: datetime = Field(description="Время последнего обновления пользователя", alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


@optional
class UserPatch(UserCreate):
    pass
