from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, Field

from app.models.utils import optional

"""
class Shape(Base):
    __tablename__ = 'shapes'

    id = Column(Integer, Sequence('shape_id_seq'), primary_key=True)
    version = Column(Integer, nullable=False)
    geometry = Column(Geometry('POLYGON'), nullable=False)
    comment = Column(Text, default='')

"""

class ShapeBase(BaseModel):
    version: int = Field(description="Версия фигуры")
    geometry: str = Field(description="Геометрия фигуры")
    comment: Optional[str] = Field(None, description="Комментарий к фигуре")

    class Config:
        from_attributes = True
        populate_by_name = True


class ShapeCreate(ShapeBase):
    pass


class ShapeGet(ShapeBase):
    id: int = Field(description="Уникальный идентификатор фигуры")

    class Config:
        from_attributes = True
        populate_by_name = True


@optional
class ShapePatch(ShapeCreate):
    pass