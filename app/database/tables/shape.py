import uuid
from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, String, func, Integer, Sequence, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database.connection import Base


class Shape(Base):
    __tablename__ = 'shapes'

    id = Column(Integer, Sequence('shape_id_seq'), primary_key=True)
    version = Column(Integer, nullable=False)
    geometry = Column(Geometry('POLYGON'), nullable=False)
    comment = Column(Text, default='')
