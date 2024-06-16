import uuid
from sqlalchemy import Column, DateTime, String, Integer, Boolean, Float, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.connection import Base

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



