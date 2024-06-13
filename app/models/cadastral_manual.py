from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

class CadastralManualBase(BaseModel):
    cadastral_quarter_number: str = Field(..., alias="Номер кадастрового квартала")
    land_for_high_rise_residential_buildings: Optional[float] = Field(None, alias="Земельные участки, предназначенные для размещения объектов многоэтажной жилой застройки")
    land_for_low_rise_residential_buildings: Optional[float] = Field(None, alias="Земельные участки, предназначенные для размещения малоэтажной жилой застройки, включая индивидуальную жилую застройку")
    land_for_garages_parking: Optional[float] = Field(None, alias="Земельные участки, предназначенные для размещения гаражей, машино-мест, автостоянок")
    land_for_commerce_recreation: Optional[float] = Field(None, alias="Земельные участки, предназначенные для размещения объектов торговли, общественного питания, бытового обслуживания, сервиса, отдыха и развлечений, включая объекты многофункционального назначения")
    land_for_temporary_residence: Optional[float] = Field(None, alias="Земельные участки под объектами, предназначенными для временного проживания")
    land_for_office_buildings: Optional[float] = Field(None, alias="Земельные участки, предназначенные для размещения административных и офисных зданий")
    land_for_industrial_purposes: Optional[float] = Field(None, alias="Земельные участки производственного назначения")
    land_for_sanatoriums_tourism: Optional[float] = Field(None, alias="Земельные участки, предназначенные для размещения санаториев и объектов туристического назначения")
    land_for_social_infrastructure: Optional[float] = Field(None, alias="Земельные участки, предназначенные для размещения объектов социальной инфраструктуры")
    land_for_ports_stations: Optional[float] = Field(None, alias="Земельные участки, предназначенные для размещения объектов портов, вокзалов, станций")
    land_for_gardening: Optional[float] = Field(None, alias="Земельные участки, предназначенные для размещения объектов садоводства и огородничества")

class CadastralManualCreate(CadastralManualBase):
    pass

class CadastralManualGet(CadastralManualBase):
    id: int = Field(..., alias="Уникальный идентификатор")

    class Config:
        from_attributes = True
        populate_by_name = True

class CadastralManualPatch(CadastralManualCreate):
    pass