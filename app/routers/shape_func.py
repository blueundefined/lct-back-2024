"""
class TrueShape(Base):
    __tablename__ = 'true_shape'

    id = Column(Integer, primary_key=True, autoincrement=True)

    shape_id = Column(Integer, nullable=False)
    shape_version = Column(Integer, nullable=False)
    comment = Column(Text, default='')
    added_to_favorites = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    ai_gen_comment = Column(Text, default='')
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from pydantic import UUID4, BaseModel, EmailStr, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import config
from app.database.connection import get_session
from app.database.tables.shape_proccess import TrueShape
from app.models.utils import optional

router = APIRouter(prefix=config.BACKEND_PREFIX)

class ShapeBase(BaseModel):
    shape_id: int = Field(description="Уникальный идентификатор фигуры")
    shape_version: int = Field(description="Версия фигуры")
    comment: Optional[str] = Field(None, description="Комментарий к фигуре")
    added_to_favorites: bool = Field(description="Добавлено в избранное")
    created_at: datetime = Field(description="Дата создания фигуры")
    updated_at: datetime = Field(description="Дата обновления фигуры")
    ai_gen_comment: Optional[str] = Field(None, description="Комментарий, сгенерированный ИИ")

    class Config:
        from_attributes = True
        populate_by_name = True


class ShapeCreate(ShapeBase):
    pass


class ShapeGet(ShapeBase):
    shape_id: int = Field(description="Уникальный идентификатор фигуры")

    class Config:
        from_attributes = True
        populate_by_name = True

class ShapeService:
    @staticmethod
    async def get(db: AsyncSession, shape_id: int):
        response = await db.execute(text("SELECT * FROM true_shape WHERE shape_id = :shape_id"), {"shape_id": shape_id})
        return ShapeGet.model_validate(response.first())

    @staticmethod
    async def get_all(db: AsyncSession, limit: int, offset: int):
        response = await db.execute(text("SELECT * FROM true_shape LIMIT :limit OFFSET :offset"), {"limit": limit, "offset": offset})
        return [ShapeGet.model_validate(row) for row in response.fetchall()]
    

    @staticmethod
    async def create(db: AsyncSession, shape: ShapeCreate):
        return await db.execute(text("INSERT INTO true_shape (shape_id, shape_version, comment, added_to_favorites, ai_gen_comment) VALUES (:shape_id, :shape_version, :comment, :added_to_favorites, :ai_gen_comment)"), {"shape_id": shape.shape_id, "shape_version": shape.shape_version, "comment": shape.comment, "added_to_favorites": shape.added_to_favorites, "ai_gen_comment": shape.ai_gen_comment})

    @staticmethod
    async def update(db: AsyncSession, shape_id: int, shape: ShapeCreate):
        return await db.execute(text("UPDATE true_shape SET shape_version = :shape_version, comment = :comment, added_to_favorites = :added_to_favorites, ai_gen_comment = :ai_gen_comment WHERE shape_id = :shape_id"), {"shape_id": shape_id, "shape_version": shape.shape_version, "comment": shape.comment, "added_to_favorites": shape.added_to_favorites, "ai_gen_comment": shape.ai_gen_comment})

    @staticmethod
    async def delete(db: AsyncSession, shape_id: int):
        return await db.execute(text("DELETE FROM true_shape WHERE shape_id = :shape_id"), {"shape_id": shape_id})

    @staticmethod
    async def get_all_favorite(db: AsyncSession, limit: int, offset: int):
        return await db.execute(text("SELECT * FROM true_shape WHERE added_to_favorites = TRUE LIMIT :limit OFFSET :offset"), {"limit": limit, "offset": offset})
    
    @staticmethod
    async def change_favorite_status(db: AsyncSession, shape_id: int, status: bool):
        return await db.execute(text("UPDATE true_shape SET added_to_favorites = :status WHERE shape_id = :shape_id"), {"shape_id": shape_id, "status": status})
    
    @staticmethod
    async def get_favorite_status(db: AsyncSession, shape_id: int) -> bool:
        result = await db.execute(select(TrueShape.added_to_favorites).where(TrueShape.shape_id == shape_id))
        favorite_status = result.scalar()
        return favorite_status is True
    
    @staticmethod
    async def add_ai_gen_comment(db: AsyncSession, shape_id: int, ai_gen_comment: str):
        return await db.execute(text("UPDATE true_shape SET ai_gen_comment = :ai_gen_comment WHERE shape_id = :shape_id"), {"shape_id": shape_id, "ai_gen_comment": ai_gen_comment})
    
    @staticmethod
    async def get_ai_gen_comment(db: AsyncSession, shape_id: int):
        return await db.execute(text("SELECT ai_gen_comment FROM true_shape WHERE shape_id = :shape_id"), {"shape_id": shape_id})
    
    @staticmethod
    async def add_comment(db: AsyncSession, shape_id: int, comment: str):
        return await db.execute(text("UPDATE true_shape SET comment = :comment WHERE shape_id = :shape_id"), {"shape_id": shape_id, "comment": comment})
    
    @staticmethod
    async def get_comment(db: AsyncSession, shape_id: int):
        return await db.execute(text("SELECT comment FROM true_shape WHERE shape_id = :shape_id"), {"shape_id": shape_id})


# route to get all favorite shapes
@router.get('/shapes/favorite', response_model=List[ShapeGet])
async def get_all_favorite_shapes(
    db: AsyncSession = Depends(get_session),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    return await ShapeService.get_all_favorite(db=db, limit=limit, offset=offset)

# route to add shape to favorite
@router.put('/shapes/{shape_id}/favorite')
async def add_shape_to_favorite(
    shape_id: int = Path(..., title="Уникальный идентификатор фигуры"),
    db: AsyncSession = Depends(get_session),
):
    await ShapeService.change_favorite_status(db=db, shape_id=shape_id)
    return {'fav_status': ShapeService.get_favorite_status(db=db, shape_id=shape_id)}
            

# route to get favorite status of shape
@router.get('/shapes/{shape_id}/favorite', response_model=bool)
async def get_favorite_status(
    shape_id: int = Path(..., title="Уникальный идентификатор фигуры"),
    db: AsyncSession = Depends(get_session),
):
    return await ShapeService.get_favorite_status(db=db, shape_id=shape_id)

# route to add ai gen comment to shape
@router.put('/shapes/{shape_id}/ai_gen_comment')
async def add_ai_gen_comment(
    shape_id: int = Path(..., title="Уникальный идентификатор фигуры"),
    ai_gen_comment: str = Query(..., title="Комментарий, сгенерированный ИИ"),
    db: AsyncSession = Depends(get_session),
):
    await ShapeService.add_ai_gen_comment(db=db, shape_id=shape_id, ai_gen_comment=ai_gen_comment)
    return status.HTTP_200_OK

# route to get ai gen comment of shape
@router.get('/shapes/{shape_id}/ai_gen_comment', response_model=str)
async def get_ai_gen_comment(
    shape_id: int = Path(..., title="Уникальный идентификатор фигуры"),
    db: AsyncSession = Depends(get_session),
):
    return await ShapeService.get_ai_gen_comment(db=db, shape_id=shape_id)

# route to add comment to shape
@router.put('/shapes/{shape_id}/comment')
async def add_comment(
    shape_id: int = Path(..., title="Уникальный идентификатор фигуры"),
    comment: str = Query(..., title="Комментарий к фигуре"),
    db: AsyncSession = Depends(get_session),
):
    await ShapeService.add_comment(db=db, shape_id=shape_id, comment=comment)
    return status.HTTP_200_OK

# route to get comment of shape
@router.get('/shapes/{shape_id}/comment', response_model=str)
async def get_comment(
    shape_id: int = Path(..., title="Уникальный идентификатор фигуры"),
    db: AsyncSession = Depends(get_session),
):
    return await ShapeService.get_comment(db=db, shape_id=shape_id)

# route to get shape by id
@router.get('/shapes/{shape_id}', response_model=ShapeGet)
async def get_shape(
    shape_id: int = Path(..., title="Уникальный идентификатор фигуры"),
    db: AsyncSession = Depends(get_session),
):
    return await ShapeService.get(db=db, shape_id=shape_id)

# route to create several shapes of the same version only for testing purposes: create using only version num
@router.post('/shapes', response_model=List[ShapeGet])
async def create_shapes(
    shapes: List[ShapeCreate],
    db: AsyncSession = Depends(get_session),
):
    for shape in shapes:
        await ShapeService.create(db=db, shape=shape)
    return shapes