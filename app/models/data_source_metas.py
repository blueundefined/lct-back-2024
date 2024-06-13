from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, Field

from app.models.utils import optional

class DataSourceMetaBase(BaseModel):
    data_source_id: int = Field(description="Идентификатор источника данных")
    field_name: str = Field(description="Название поля")
    field_description: Optional[str] = Field(None, description="Описание поля")

    class Config:
        from_attributes = True
        populate_by_name = True

class DataSourceMetaCreate(DataSourceMetaBase):
    pass

class DataSourceMetaGet(DataSourceMetaBase):
    id: int = Field(description="Уникальный идентификатор поля")

    class Config:
        from_attributes = True
        populate_by_name = True


@optional
class DataSourceMetaPatch(DataSourceMetaCreate):
    pass
