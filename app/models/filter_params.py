from datetime import datetime
from typing import List, Optional

from fastapi import Query
from pydantic import UUID4, BaseModel, EmailStr, Field
from app.models.vri import VRIGet


class FilterParams(BaseModel):
    min_area: Optional[float] = Query(None, description="Минимальная площадь участка, кв.м")
    max_area: Optional[float] = Query(None, description="Максимальная площадь участка, кв.м")
    cadastra_numbers: Optional[List[str]] = Query(None, description="Список кадастровых номеров")
    address: Optional[str] = Query(None, description="Адрес")
    has_valid_document: Optional[bool] = Query(None, description="Наличие действующего правоудостоверяющего документа")
    has_cadastral_registration: Optional[bool] = Query(None, description="Участок поставлен на кадастровый учет")
    is_draft: Optional[bool] = Query(None, description="Проектный участок")
    ownership_type: Optional[List[int]] = Query(None, description="Тип собственности (1 - МСК, 2 - РФ, 3 - Частная, 5 - Неразграниченная)")
    has_construction_permission: Optional[bool] = Query(None, description="Наличие разрешения на строительство")
    is_noncapital_use: Optional[bool] = Query(None, description="Участок для размещения некапитальных объектов")
    district: Optional[str] = Query(None, description="Округ")
    subdistrict: Optional[str] = Query(None, description="Район")
    valid_zouit_types: Optional[List[str]] = Query(None, description="Виды ЗОУИТ (например, 'Границы приаэродромной территории')")
    valid_vri_codes: Optional[List[str]] = Query(None, description="Коды ВРИ")
    in_red_zones: Optional[bool] = Query(None, description="Находится в красной зоне реорганизации")
    valid_ppt_status: Optional[List[str]] = Query(None, description="Статус ППТ (например, 'Утвержденные, действующие')")
    valid_ppt_type: Optional[List[str]] = Query(None, description="Тип ППТ")

    class Config:
        from_attributes = True
        populate_by_name = True
        schema_extra = {
            "example": {
                "min_area": 100,
                "max_area": 200,
                "cadastra_numbers": ["77:01:0000000:000"],
                "address": "г. Москва, ул. Ленина, д. 1",
                "has_valid_document": True,
                "has_cadastral_registration": True,
                "is_draft": False,
                "ownership_type": [1, 2],
                "has_construction_permission": True,
                "is_noncapital_use": False,
                "district": "Центральный",
                "subdistrict": "Тверской",
                "valid_zouit_types": ["Границы приаэродромной территории"],
                "valid_vri_codes": ["1.0", "1.1"],
                "in_red_zones": False,
                "valid_ppt_status": ["Утвержденные, действующие"],
                "valid_ppt_type": ["ППТ"]
            }
        }