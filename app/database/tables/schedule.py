import uuid
from sqlalchemy import Column, DateTime, String, Integer, Boolean, Float, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Schedule(Base):
    __tablename__ = 'schedule'
    
    guid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    frequency = Column(String(50), nullable=False)
    time = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())