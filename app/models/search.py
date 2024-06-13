from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, Field

from app.models.utils import optional


class SearchBase(BaseModel):
    search: str = Field(description="Поисковый запрос", example="search")

    class Config:
        from_attributes = True
        populate_by_name = True


class SearchCreate(SearchBase):
    pass


class SearchGet(SearchBase):
    id: int = Field(description="Уникальный идентификатор поиска", alias="id")
    created_at: datetime = Field(description="Время создания поиска", alias="createdAt")
    updated_at: datetime = Field(description="Время последнего обновления поиска", alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True
