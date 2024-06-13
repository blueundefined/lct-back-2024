import uuid
from sqlalchemy import Column, DateTime, String, Integer, Boolean, Float, Text, func
from sqlalchemy.dialects.postgresql import UUID
from app.database.connection import Base

class VRI(Base):
    __tablename__ = 'vri'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)