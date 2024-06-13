from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, Field


class VRIBase(BaseModel):
    code: str = Field(description="Код ВРИ")
    name: str = Field(description="Наименование ВРИ")
    description: Optional[str] = Field(None, description="Описание ВРИ")

    class Config:
        from_attributes = True
        populate_by_name = True


class VRICreate(VRIBase):
    pass


class VRIGet(VRIBase):
    code: str = Field(description="Код ВРИ")

    class Config:
        from_attributes = True
        populate_by_name = True


class VRIPatch(VRICreate):
    pass
