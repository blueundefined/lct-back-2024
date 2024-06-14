from pydantic import BaseModel, Field
from typing import Optional

"""
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
"""

class CadastralManualBase(BaseModel):
    cadastral_quarter_number: str = Field(
        ..., 
        alias="cadastral_quarter_number", 
        description="Номер кадастрового квартала"
    )
    land_for_high_rise_residential_buildings: Optional[float] = Field(
        None, 
        alias="high_rise_residential", 
        description="Земельные участки, предназначенные для размещения объектов многоэтажной жилой застройки"
    )
    land_for_low_rise_residential_buildings: Optional[float] = Field(
        None, 
        alias="low_rise_residential", 
        description="Земельные участки, предназначенные для размещения малоэтажной жилой застройки, включая индивидуальную жилую застройку"
    )
    land_for_garages_parking: Optional[float] = Field(
        None, 
        alias="garages_parking", 
        description="Земельные участки, предназначенные для размещения гаражей, машино-мест, автостоянок"
    )
    land_for_commerce_recreation: Optional[float] = Field(
        None, 
        alias="commerce_recreation", 
        description="Земельные участки, предназначенные для размещения объектов торговли, общественного питания, бытового обслуживания, сервиса, отдыха и развлечений, включая объекты многофункционального назначения"
    )
    land_for_temporary_residence: Optional[float] = Field(
        None, 
        alias="temporary_residence", 
        description="Земельные участки под объектами, предназначенными для временного проживания"
    )
    land_for_office_buildings: Optional[float] = Field(
        None, 
        alias="office_buildings", 
        description="Земельные участки, предназначенные для размещения административных и офисных зданий"
    )
    land_for_industrial_purposes: Optional[float] = Field(
        None, 
        alias="industrial_purposes", 
        description="Земельные участки производственного назначения"
    )
    land_for_sanatoriums_tourism: Optional[float] = Field(
        None, 
        alias="sanatoriums_tourism", 
        description="Земельные участки, предназначенные для размещения санаториев и объектов туристического назначения"
    )
    land_for_social_infrastructure: Optional[float] = Field(
        None, 
        alias="social_infrastructure", 
        description="Земельные участки, предназначенные для размещения объектов социальной инфраструктуры"
    )
    land_for_ports_stations: Optional[float] = Field(
        None, 
        alias="ports_stations", 
        description="Земельные участки, предназначенные для размещения объектов портов, вокзалов, станций"
    )
    land_for_gardening: Optional[float] = Field(
        None, 
        alias="gardening", 
        description="Земельные участки, предназначенные для размещения объектов садоводства и огородничества"
    )

class CadastralManualCreate(CadastralManualBase):
    pass

class CadastralManualGet(CadastralManualBase):
    id: int = Field(
        ..., 
        alias="id", 
        description="Уникальный идентификатор"
    )

    class Config:
        from_attributes = True
        populate_by_name = True

class CadastralManualPatch(CadastralManualCreate):
    pass
