import uuid
from sqlalchemy import Column, DateTime, String, Integer, Boolean, Float, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.connection import Base

class DataSourceMeta(Base): 
    __tablename__ = 'data_source_meta'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_source_id = Column(Integer, ForeignKey('data_source.id'), nullable=False)
    field_name = Column(String(50), nullable=False)
    field_description = Column(Text, nullable=True)
    
    # Связь с таблицей data_source
    data_source = relationship('DataSource', back_populates='meta_data')
