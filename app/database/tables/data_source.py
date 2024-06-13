import uuid
from sqlalchemy import Column, DateTime, String, Integer, Boolean, Float, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.connection import Base

class DataSource(Base):
    __tablename__ = 'data_source'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(50), nullable=False)
    source_description = Column(Text, nullable=True)

    # Связь с таблицей data_source_meta
    meta_data = relationship('DataSourceMeta', back_populates='data_source')