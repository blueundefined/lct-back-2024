from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

class CadastralManualBase(BaseModel):
    cadastral_quarter_number: str = Field(
        ..., 
        alias="cadastral_quarter_number", 
        description="Номер кадастрового квартала"
    )
    high_rise_residential: Optional[float] = Field(
        None, 
        alias="high_rise_residential", 
        description="Земельные участки, предназначенные для размещения объектов многоэтажной жилой застройки"
    )
    low_rise_residential: Optional[float] = Field(
        None, 
        alias="low_rise_residential", 
        description="Земельные участки, предназначенные для размещения малоэтажной жилой застройки, включая индивидуальную жилую застройку"
    )
    garages_parking: Optional[float] = Field(
        None, 
        alias="garages_parking", 
        description="Земельные участки, предназначенные для размещения гаражей, машино-мест, автостоянок"
    )
    commerce_recreation: Optional[float] = Field(
        None, 
        alias="commerce_recreation", 
        description="Земельные участки, предназначенные для размещения объектов торговли, общественного питания, бытового обслуживания, сервиса, отдыха и развлечений, включая объекты многофункционального назначения"
    )
    temporary_residence: Optional[float] = Field(
        None, 
        alias="temporary_residence", 
        description="Земельные участки под объектами, предназначенными для временного проживания"
    )
    office_buildings: Optional[float] = Field(
        None, 
        alias="office_buildings", 
        description="Земельные участки, предназначенные для размещения административных и офисных зданий"
    )
    industrial_purposes: Optional[float] = Field(
        None, 
        alias="industrial_purposes", 
        description="Земельные участки производственного назначения"
    )
    sanatoriums_tourism: Optional[float] = Field(
        None, 
        alias="sanatoriums_tourism", 
        description="Земельные участки, предназначенные для размещения санаториев и объектов туристического назначения"
    )
    social_infrastructure: Optional[float] = Field(
        None, 
        alias="social_infrastructure", 
        description="Земельные участки, предназначенные для размещения объектов социальной инфраструктуры"
    )
    ports_stations: Optional[float] = Field(
        None, 
        alias="ports_stations", 
        description="Земельные участки, предназначенные для размещения объектов портов, вокзалов, станций"
    )
    gardening: Optional[float] = Field(
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
