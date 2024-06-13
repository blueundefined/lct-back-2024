import uuid
from sqlalchemy import Column, DateTime, String, Integer, Boolean, Float, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.connection import Base

class CadastralManual(Base):
    __tablename__ = 'cadastral_manual'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cadastral_quarter_number = Column(String, nullable=False)
    land_for_high_rise_residential_buildings = Column(Float, nullable=True)
    land_for_low_rise_residential_buildings = Column(Float, nullable=True)
    land_for_garages_parking = Column(Float, nullable=True)
    land_for_commerce_recreation = Column(Float, nullable=True)
    land_for_temporary_residence = Column(Float, nullable=True)
    land_for_office_buildings = Column(Float, nullable=True)
    land_for_industrial_purposes = Column(Float, nullable=True)
    land_for_sanatoriums_tourism = Column(Float, nullable=True)
    land_for_social_infrastructure = Column(Float, nullable=True)
    land_for_ports_stations = Column(Float, nullable=True)
    land_for_gardening = Column(Float, nullable=True)
