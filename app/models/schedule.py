from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, Field

from app.models.utils import optional

class ScheduleBase(BaseModel): #расписание автоматической работы, то есть выбор периодичности обновлений а так же времени (например каждый день в 03:00 или каждый понедельник в 6:55)
    frequency: str = Field(description="Периодичность обновления расписания", example="daily")
    time: str = Field(description="Время обновления расписания", example="03:00")

    class Config:
        from_attributes = True
        populate_by_name = True

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleGet(ScheduleBase):
    guid: UUID4 = Field(description="Уникальный идентификатор расписания")
    created_at: datetime = Field(description="Время создания расписания", alias="createdAt")
    updated_at: datetime = Field(description="Время последнего обновления расписания", alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True

@optional
class SchedulePatch(ScheduleBase):
    pass