from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, Field

from app.models.utils import optional

class DataSourceBase(BaseModel):
    source_name: str = Field(description="Название источника данных")
    source_description: Optional[str] = Field(None, description="Описание источника данных")

    class Config:
        from_attributes = True
        populate_by_name = True

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceGet(DataSourceBase):
    id: int = Field(description="Уникальный идентификатор источника данных")

    class Config:
        from_attributes = True
        populate_by_name = True

@optional
class DataSourcePatch(DataSourceCreate):
    pass