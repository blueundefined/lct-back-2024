from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import config
from app.database.connection import get_session

router = APIRouter(prefix=config.BACKEND_PREFIX)

import os
from fastapi import APIRouter, HTTPException
from enum import Enum
import geopandas as gpd
import fiona
from pydantic import BaseModel
from typing import List
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Geometry(BaseModel):
    type: str
    coordinates: Any

class ZUProperties(BaseModel):
    cadastra2: str
    address: str
    hasvalid5: str
    hascadas6: str
    isdraft: str
    ownershi8: float
    is_stroy: str
    is_nonca20: float
    Area: float

class OKSProperties(BaseModel):
    unom: float
    address: str
    cadastra3: str
    hascadas4: str
    hasbti: str
    hasownrf: str
    hasownmo8: str
    hasownot9: str
    shape_area: float

class ZOUITProperties(BaseModel):
    CAD_NUM: str
    OKRUG: str
    RAION_POS: str
    VID_ZOUIT: str
    TYPE_ZONE: str
    NAME: str
    OGRAN: str
    DOC: str
    Area: float

class SpritzonesProperties(BaseModel):
    LineCode: str
    Name: str
    Doc: str
    Comment: str
    Area: float

class YDC_ROADSProperties(BaseModel):
    NAME_OBJ: str
    NAME_STR: str
    VID_ROAD: str
    EXT_NAME: str
    SHAPE_Leng: float
    SHAPE_Area: float

class RenovationSitesProperties(BaseModel):
    okrug: str
    rayon: str
    address: str
    area: str
    prim: str
    plotnost: str
    vysota: str
    spp: str
    total_area: str
    flat_area: str
    osnovanie: str
    agr: str
    objectid: str

class PPZ_ZONESProperties(BaseModel):
    ZONE_NUM: str
    NUM_PP: str
    DOC_DATE: str
    TYPE: str
    INDEX_: str
    VRI_540: str
    Area: float

class PPZ_PODZONESProperties(BaseModel):
    PLOTNOST: str
    VYSOTA: str
    PROCZASTRO: str
    PODZONE_NU: str
    NUM_PP: str
    DOC_DATE: str
    TYPE: str
    Area: float

class KRTProperties(BaseModel):
    name: str
    area_krt: float
    type_krt: str

class DistrictsProperties(BaseModel):
    OBJECTID: int
    NAME: str
    LABEL: str
    TORZID: float
    SHAPE_AREA: float
    SHAPE_LEN: float

class RegionProperties(BaseModel):
    OBJECTID: int
    NAME: str
    LABEL: str
    TORZID: float
    SHAPE_AREA: float
    SHAPE_LEN: float

class SurveyProperties(BaseModel):
    NUMBERAREA: int
    DESCR: str
    KLASS: str
    FUNC_USE: str
    N_KVAR: str
    N_PARC: str
    YEAR: str
    AREA: float
    SHAPE_AREA: float

class OOZTProperties(BaseModel):
    objectid: str
    status: str
    zoneid: str
    docnum: str
    docdate: str
    doclist: str

class PPTProperties(BaseModel):
    REG_NUM: str
    VID_PPT: str
    NAME: str
    VID_DOC_RA: str
    NUM_DOC_RA: str
    DATA_DOC_R: str
    ZAKAZCHIK: str
    ISPOLNITEL: str
    ISTOCH_FIN: str
    OTVETST_MK: str
    NUM_KONTRA: str
    DATA_KONTR: str
    VID_DOC_UT: str
    NUM_DOC_UT: str
    DATA_DOC_U: str
    PRIOSTANOV: str
    ZAVERSHENI: str
    OTMENA: str
    STATUS: str
    GRUP1: str
    GRUP2: str
    US_PPT: str

class MKDProperties(BaseModel):
    unom: float
    address: str
    cadastra3: str
    hascadas4: str
    hasbti: str
    hascontr6: float
    hasownrf: str
    hasownmo8: str
    hasownot9: str
    cadastra10: str
    mgsntype: str
    hasmgsn: str
    cadastra13: str
    btitype: str
    objectid: str
    mkd_flag: float
    moddate: str

class Feature(BaseModel):
    type: str = "Feature"
    geometry: Geometry
    properties: Dict[str, Any]

class FeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Feature]

data_dir = '/app/app/shapefiles'
output_dir = '/app/app/geojson_files'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

class LayerName(str, Enum):
    ZU = "ЗУ.shp"
    OKS = "ОКС.shp"
    ZOUIT = "ZOUIT.shp"
    spritzones = "spritzones_2024_04_18_12_16_48.shp"
    YDC_ROADS = "УДС_дороги.shp"
    renovation_sites = "Стартовые площадки реновации.shp"
    PPZ_ZONES_NEW = "TZ_new.shp"
    PPZ_ZONES_OLD = "TZ_old.shp"
    PPZ_PODZONES_NEW = "TPZ_new.shp"
    PPZ_PODZONES_OLD = "TPZ_old.shp"
    KRT = "КРТ.shp"
    DISTRICTS = "округ.shp"
    REGION = "район.shp"
    SURVEY = "участки_межевания.shp"
    OOZT = "ООЗТ.shp"
    PPT_ALL = "PPT_ALL.shp"
    tpu_rv_metro_polygon = "tpu_rv_metro_polygon.shp"
    PPT_UDS = "PPT_UDS.shp"
    PP_GAZ = "PP_GAZ.shp"
    PP_METRO_ALL = "PP_METRO_ALL.shp"
    kvartal_region = "kvartal_region.shp"
    Cadastral = "Кадастровое деление.shp"
    MKD = "МКД.shp"


class LayerFolder(str, Enum):
    region = "_10_Округ, район"
    ZU = "_1_ЗУ"
    OKS = "_2_ОКС"
    ZOUIT = "_3_ЗОУИТ"
    spritzones = "_4_СПРИТ"
    YDC_ROADS = "_5_УДС"
    renovation_sites = "_6_Реновация стартовые площадки"
    PPZ_ZONES = "_7_ПЗЗ (территориальные зоны)"
    PPZ_PODZONES = "_8_ПЗЗ (территориальные подзоны)"
    KRT = "_9_КРТ"
    DISTRICTS = "_10_Округ, район"
    SURVEY = "_11_Участки межевания жилых кварталов"
    OOZT = "_12_ООЗТ"
    PPT = "_13_ППТ"
    Cadastral = "_14_Кадастровое деление"
    MKD = "_15_МКД"

"""
zу = read_shapefile('_1_ЗУ/ЗУ.shp', encode='UTF8')
 0   geometry    113759 non-null  geometry
 1   cadastra2   113759 non-null  object  
 2   address     113759 non-null  object  
 3   hasvalid5   113759 non-null  object  
 4   hascadas6   113759 non-null  object  
 5   isdraft     113759 non-null  object  
 6   ownershi8   113759 non-null  float64 
 7   is_stroy    113759 non-null  object  
 8   is_nonca20  113759 non-null  float64 
 9   Area        113759 non-null  float64 

ocs = read_shapefile('_2_ОКС/ОКС.shp', encode='UTF8')
Data columns (total 10 columns):
 #   Column      Non-Null Count   Dtype   
---  ------      --------------   -----   
 0   geometry    100627 non-null  geometry
 1   unom        100627 non-null  float64 
 2   address     100627 non-null  object  
 3   cadastra3   100627 non-null  object  
 4   hascadas4   100627 non-null  object  
 5   hasbti      100627 non-null  object  
 6   hasownrf    100627 non-null  object  
 7   hasownmo8   100627 non-null  object  
 8   hasownot9   100627 non-null  object  
 9   shape_area  100627 non-null  float64 

zouit = read_shapefile('_3_ЗОУИТ/ZOUIT.shp', encode='UTF8')
0   geometry   2848 non-null   geometry
 1   CAD_NUM    673 non-null    object  
 2   OKRUG      2663 non-null   object  
 3   RAION_POS  2381 non-null   object  
 4   VID_ZOUIT  2842 non-null   object  
 5   TYPE_ZONE  2831 non-null   object  
 6   NAME       1277 non-null   object  
 7   OGRAN      945 non-null    object  
 8   DOC        2054 non-null   object  
 9   Area       2848 non-null   float64 

spritzones = read_shapefile('_4_СПРИТ/spritzones_2024_04_18_12_16_48.shp', encode='UTF8')
 #   Column    Non-Null Count  Dtype   
---  ------    --------------  -----   
 0   geometry  10285 non-null  geometry
 1   LineCode  10285 non-null  object  
 2   Name      3150 non-null   object  
 3   Doc       3150 non-null   object  
 4   Comment   2790 non-null   object  
 5   Area      10285 non-null  float64 

ydc_roads = read_shapefile('_5_УДС/УДС_дороги.shp')
Data columns (total 7 columns):
 #   Column      Non-Null Count  Dtype   
---  ------      --------------  -----   
 0   geometry    6578 non-null   geometry
 1   NAME_OBJ    6578 non-null   object  
 2   NAME_STR    2785 non-null   object  
 3   VID_ROAD    467 non-null    object  
 4   EXT_NAME    526 non-null    object  
 5   SHAPE_Leng  6578 non-null   float64 
 6   SHAPE_Area  6578 non-null   float64

renovation_sites = read_shapefile('_6_Реновация стартовые площадки/Стартовые площадки реновации.shp', encode='UTF8')
Data columns (total 14 columns):
 #   Column      Non-Null Count  Dtype   
---  ------      --------------  -----   
 0   geometry    129 non-null    geometry
 1   okrug       129 non-null    object  
 2   rayon       129 non-null    object  
 3   address     129 non-null    object  
 4   area        129 non-null    object  
 5   prim        128 non-null    object  
 6   plotnost    129 non-null    object  
 7   vysota      129 non-null    object  
 8   spp         129 non-null    object  
 9   total_area  129 non-null    object  
 10  flat_area   129 non-null    object  
 11  osnovanie   122 non-null    object  
 12  agr         69 non-null     object  
 13  objectid    129 non-null    object  

ppz_zones_new = read_shapefile('_7_ПЗЗ (территориальные зоны)/TZ_new.shp', encode='UTF8')
Data columns (total 8 columns):
 #   Column    Non-Null Count  Dtype   
---  ------    --------------  -----   
 0   geometry  2608 non-null   geometry
 1   ZONE_NUM  2608 non-null   object  
 2   NUM_PP    2608 non-null   object  
 3   DOC_DATE  2608 non-null   object  
 4   TYPE      1374 non-null   object  
 5   INDEX_    1385 non-null   object  
 6   VRI_540   2607 non-null   object  
 7   Area      2608 non-null   float64 

ppz_zones_old = read_shapefile('_7_ПЗЗ (территориальные зоны)/TZ_old.shp', encode='UTF8')
Data columns (total 8 columns):
 #   Column    Non-Null Count  Dtype   
---  ------    --------------  -----   
 0   geometry  7654 non-null   geometry
 1   ZONE_NUM  7654 non-null   object  
 2   NUM_PP    7534 non-null   object  
 3   DOC_DATE  7648 non-null   object  
 4   TYPE      3896 non-null   object  
 5   INDEX_    401 non-null    object  
 6   VRI_540   7532 non-null   object  
 7   Area      7654 non-null   float64 

ppz_podzones_new = read_shapefile('_8_ПЗЗ (территориальные подзоны)/TPZ_new.shp', encode='UTF8')
Data columns (total 9 columns):
 #   Column      Non-Null Count  Dtype   
---  ------      --------------  -----   
 0   geometry    4397 non-null   geometry
 1   PODZONE_NU  4397 non-null   object  
 2   NUM_PP      4397 non-null   object  
 3   DOC_DATE    4396 non-null   object  
 4   TYPE        2566 non-null   object  
 5   PLOTNOST    3366 non-null   object  
 6   VYSOTA      3366 non-null   object  
 7   PROCZASTRO  3366 non-null   object  
 8   Area        4397 non-null   float64 

ppz_podzones_old = read_shapefile('_8_ПЗЗ (территориальные подзоны)/TPZ_old.shp', encode='UTF8')
Data columns (total 9 columns):
 #   Column      Non-Null Count  Dtype   
---  ------      --------------  -----   
 0   geometry    8803 non-null   geometry
 1   PLOTNOST    7737 non-null   object  
 2   VYSOTA      7725 non-null   object  
 3   PROCZASTRO  7723 non-null   object  
 4   PODZONE_NU  8803 non-null   object  
 5   NUM_PP      8673 non-null   object  
 6   DOC_DATE    8795 non-null   object  
 7   TYPE        4638 non-null   object  
 8   Area        8803 non-null   float64 

krt = read_shapefile('_9_КРТ/КРТ.shp', encode='UTF8')
Data columns (total 4 columns):
 #   Column    Non-Null Count  Dtype   
---  ------    --------------  -----   
 0   geometry  237 non-null    geometry
 1   name      237 non-null    object  
 2   area_krt  237 non-null    float64 
 3   type_krt  237 non-null    object  

districts = read_shapefile('_10_Округ, район/округ.shp')
Data columns (total 7 columns):
 #   Column      Non-Null Count  Dtype   
---  ------      --------------  -----   
 0   geometry    3 non-null      geometry
 1   OBJECTID    3 non-null      int64   
 2   NAME        3 non-null      object  
 3   LABEL       3 non-null      object  
 4   TORZID      3 non-null      float64 
 5   SHAPE_AREA  3 non-null      float64 
 6   SHAPE_LEN   3 non-null      float64 

survey = read_shapefile('_11_Участки межевания жилых кварталов/участки_межевания.shp')
Data columns (total 10 columns):
 #   Column      Non-Null Count  Dtype   
---  ------      --------------  -----   
 0   geometry    24572 non-null  geometry
 1   NUMBERAREA  24572 non-null  int64   
 2   DESCR       24572 non-null  object  
 3   KLASS       15109 non-null  object  
 4   FUNC_USE    24343 non-null  object  
 5   N_KVAR      24116 non-null  object  
 6   N_PARC      24423 non-null  object  
 7   YEAR        24500 non-null  object  
 8   AREA        24572 non-null  float64 
 9   SHAPE_AREA  24572 non-null  float64

oozt = read_shapefile('_12_ООЗТ/ООЗТ.shp', encode='UTF8')
Data columns (total 7 columns):
 #   Column    Non-Null Count  Dtype   
---  ------    --------------  -----   
 0   geometry  76 non-null     geometry
 1   objectid  76 non-null     object  
 2   status    76 non-null     object  
 3   zoneid    76 non-null     object  
 4   docnum    76 non-null     object  
 5   docdate   76 non-null     object  
 6   doclist   76 non-null     object 

cadastral = read_shapefile('_14_Кадастровое деление/Кадастровое деление.shp')
Data columns (total 3 columns):
 #   Column     Non-Null Count  Dtype   
---  ------     --------------  -----   
 0   geometry   869 non-null    geometry
 1   cadastra1  869 non-null    object  
 2   objectid   869 non-null    object

mkd = read_shapefile('_15_МКД/МКД.shp', encode='UTF8')
---  ------      --------------  -----   
 0   geometry    8212 non-null   geometry
 1   unom        7884 non-null   float64 
 2   address     8212 non-null   object  
 3   cadastra3   8212 non-null   object  
 4   hascadas4   8212 non-null   object  
 5   hasbti      8212 non-null   object  
 6   hascontr6   8015 non-null   float64 
 7   hasownrf    8212 non-null   object  
 8   hasownmo8   8212 non-null   object  
 9   hasownot9   8212 non-null   object  
 10  cadastra10  8212 non-null   object  
 11  mgsntype    8212 non-null   object  
 12  hasmgsn     8212 non-null   object  
 13  cadastra13  8212 non-null   object  
 14  btitype     8212 non-null   object  
 15  objectid    8212 non-null   object  
 16  mkd_flag    132 non-null    float64 
 17  moddate     8212 non-null   object 

##13 ППТ

# Загрузка основных данных для PPT_ALL.shp
ppt_all = read_shapefile('_13_ППТ/PPT_ALL.shp')
# get_head(ppt_all)
# get_info(ppt_all)

ppt_all = remove_empty_and_zero_columns(ppt_all)
get_head(ppt_all)
get_info(ppt_all)

# Загрузка основных данных для TPU_RV_METRO_Polygon.shp
tpu_rv_metro_polygon = read_shapefile('_13_ППТ/TPU_RV_METRO_Polygon.shp')
# get_head(tpu_rv_metro_polygon)
# get_info(tpu_rv_metro_polygon)

tpu_rv_metro_polygon = remove_empty_and_zero_columns(tpu_rv_metro_polygon)
get_head(tpu_rv_metro_polygon)
get_info(tpu_rv_metro_polygon)

# Загрузка основных данных для PPT_UDS.shp
ppt_uds = read_shapefile('_13_ППТ/PPT_UDS.shp')
# get_head(ppt_uds)
# get_info(ppt_uds)

ppt_uds = remove_empty_and_zero_columns(ppt_uds)
get_head(ppt_uds)
get_info(ppt_uds)

# Загрузка основных данных для PP_GAZ.shp
pp_gaz = read_shapefile('_13_ППТ/PP_GAZ.shp')
# get_head(pp_gaz)
# get_info(pp_gaz)

pp_gaz = remove_empty_and_zero_columns(pp_gaz)
get_head(pp_gaz)
get_info(pp_gaz)

# Загрузка основных данных для PP_METRO_ALL.shp
pp_metro_all = read_shapefile('_13_ППТ/PP_METRO_ALL.shp')
# get_head(pp_metro_all)
# get_info(pp_metro_all)

pp_metro_all = remove_empty_and_zero_columns(pp_metro_all)
get_head(pp_metro_all)
get_info(pp_metro_all)

# Загрузка основных данных для kvartal_region.shp
kvartal_region = read_shapefile('_13_ППТ/kvartal_region.shp')
# get_head(kvartal_region)
# get_info(kvartal_region)

kvartal_region = remove_empty_and_zero_columns(kvartal_region)
get_head(kvartal_region)
get_info(kvartal_region)

для ППТ схема одинаковая: 
Data columns (total 26 columns):
 #   Column      Non-Null Count  Dtype   
---  ------      --------------  -----   
 0   geometry    75 non-null     geometry
 1   REG_NUM     75 non-null     object  
 2   VID_PPT     75 non-null     object  
 3   NAME        75 non-null     object  
 4   VID_DOC_RA  72 non-null     object  
 5   NUM_DOC_RA  72 non-null     object  
 6   DATA_DOC_R  72 non-null     object  
 7   ZAKAZCHIK   75 non-null     object  
 8   ISPOLNITEL  48 non-null     object  
 9   ISTOCH_FIN  75 non-null     object  
 10  OTVETST_MK  75 non-null     object  
 11  NUM_KONTRA  12 non-null     object  
 12  DATA_KONTR  12 non-null     object  
 13  VID_DOC_UT  44 non-null     object  
 14  NUM_DOC_UT  44 non-null     object  
 15  DATA_DOC_U  44 non-null     object  
 16  PRIOSTANOV  3 non-null      object  
 17  ZAVERSHENI  23 non-null     object  
 18  OTMENA      1 non-null      object  
 19  STATUS      75 non-null     object  
 20  GRUP1       38 non-null     object  
 21  GRUP2       72 non-null     object  
 22  US_PPT      74 non-null     object  
 23  SPPGNS_OBS  2 non-null      object  
 24  SPPGNS_JIL  1 non-null      object  
 25  Shape_Area  75 non-null     float64 
"""

class ZUColumnName(str, Enum):
    geometry = "geometry"
    cadastra2 = "cadastra2"
    address = "address"
    hasvalid5 = "hasvalid5"
    hascadas6 = "hascadas6"
    isdraft = "isdraft"
    ownershi8 = "ownershi8"
    is_stroy = "is_stroy"
    is_nonca20 = "is_nonca20"
    Area = "Area"

class OKSColumnName(str, Enum):
    geometry = "geometry"
    unom = "unom"
    address = "address"
    cadastra3 = "cadastra3"
    hascadas4 = "hascadas4"
    hasbti = "hasbti"
    hasownrf = "hasownrf"
    hasownmo8 = "hasownmo8"
    hasownot9 = "hasownot9"
    shape_area = "shape_area"

class ZOUITColumnName(str, Enum):
    geometry = "geometry"
    CAD_NUM = "CAD_NUM"
    OKRUG = "OKRUG"
    RAION_POS = "RAION_POS"
    VID_ZOUIT = "VID_ZOUIT"
    TYPE_ZONE = "TYPE_ZONE"
    NAME = "NAME"
    OGRAN = "OGRAN"
    DOC = "DOC"
    Area = "Area"

class SpritzonesColumnName(str, Enum):
    geometry = "geometry"
    LineCode = "LineCode"
    Name = "Name"
    Doc = "Doc"
    Comment = "Comment"
    Area = "Area"

class YDC_ROADSColumnName(str, Enum):
    geometry = "geometry"
    NAME_OBJ = "NAME_OBJ"
    NAME_STR = "NAME_STR"
    VID_ROAD = "VID_ROAD"
    EXT_NAME = "EXT_NAME"
    SHAPE_Leng = "SHAPE_Leng"
    SHAPE_Area = "SHAPE_Area"

class RenovationSitesColumnName(str, Enum):
    geometry = "geometry"
    okrug = "okrug"
    rayon = "rayon"
    address = "address"
    area = "area"
    prim = "prim"
    plotnost = "plotnost"
    vysota = "vysota"
    spp = "spp"
    total_area = "total_area"
    flat_area = "flat_area"
    osnovanie = "osnovanie"
    agr = "agr"
    objectid = "objectid"

class PPZ_ZONESColumnName(str, Enum):
    geometry = "geometry"
    ZONE_NUM = "ZONE_NUM"
    NUM_PP = "NUM_PP"
    DOC_DATE = "DOC_DATE"
    TYPE = "TYPE"
    INDEX_ = "INDEX_"
    VRI_540 = "VRI_540"
    Area = "Area"

class PPZ_PODZONESColumnName(str, Enum):
    geometry = "geometry"
    PODZONE_NU = "PODZONE_NU"
    NUM_PP = "NUM_PP"
    DOC_DATE = "DOC_DATE"
    TYPE = "TYPE"
    PLOTNOST = "PLOTNOST"
    VYSOTA = "VYSOTA"
    PROCZASTRO = "PROCZASTRO"
    Area = "Area"

class KRTColumnName(str, Enum):
    geometry = "geometry"
    name = "name"
    area_krt = "area_krt"
    type_krt = "type_krt"

class DistrictsColumnName(str, Enum):
    geometry = "geometry"
    OBJECTID = "OBJECTID"
    NAME = "NAME"
    LABEL = "LABEL"
    TORZID = "TORZID"
    SHAPE_AREA = "SHAPE_AREA"
    SHAPE_LEN = "SHAPE_LEN"

class RegionColumnName(str, Enum):
    geometry = "geometry"
    OBJECTID = "OBJECTID"
    NAME = "NAME"
    SHAPE_AREA = "SHAPE_AREA"
    SHAPE_LEN = "SHAPE_LEN"

class SurveyColumnName(str, Enum):
    geometry = "geometry"
    NUMBERAREA = "NUMBERAREA"
    DESCR = "DESCR"
    KLASS = "KLASS"
    FUNC_USE = "FUNC_USE"
    N_KVAR = "N_KVAR"
    N_PARC = "N_PARC"
    YEAR = "YEAR"
    AREA = "AREA"
    SHAPE_AREA = "SHAPE_AREA"

class OOZTColumnName(str, Enum):
    geometry = "geometry"
    objectid = "objectid"
    status = "status"
    zoneid = "zoneid"
    docnum = "docnum"
    docdate = "docdate"
    doclist = "doclist"

class CadastralColumnName(str, Enum):
    geometry = "geometry"
    cadastra1 = "cadastra1"
    objectid = "objectid"

class MKDColumnName(str, Enum):
    geometry = "geometry"
    unom = "unom"
    address = "address"
    cadastra3 = "cadastra3"
    hascadas4 = "hascadas4"
    hasbti = "hasbti"
    hascontr6 = "hascontr6"
    hasownrf = "hasownrf"
    hasownmo8 = "hasownmo8"
    hasownot9 = "hasownot9"
    cadastra10 = "cadastra10"
    mgsntype = "mgsntype"
    hasmgsn = "hasmgsn"
    cadastra13 = "cadastra13"
    btitype = "btitype"
    objectid = "objectid"
    mkd_flag = "mkd_flag"
    moddate = "moddate"

@router.get(
    "/visualize/ZU", 
    response_model=FeatureCollection,
    response_description="Слой земельных участков",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя земельных участков",
    summary="Земельные участки",
    # responses={},
        )
def visualize_zu(layer: LayerName = LayerName.ZU, column: ZUColumnName = ZUColumnName.ownershi8):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.ZU}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/OKS", 
    response_model=FeatureCollection,
    response_description="Слой объектов капитального строительства",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя объектов капитального строительства",
    summary="Объекты капитального строительства",
    # responses={},
        )
def visualize_oks(layer: LayerName = LayerName.OKS, column: OKSColumnName = OKSColumnName.hasbti):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.OKS}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/ZOUIT", 
    response_model=FeatureCollection,
    response_description="Слой зон охраняемых уникальных историко-культурных территорий",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя зон охраняемых уникальных историко-культурных территорий",
    summary="Зоны охраняемых уникальных историко-культурных территорий",
    # responses={},
        )
def visualize_zouit(layer: LayerName = LayerName.ZOUIT, column: ZOUITColumnName = ZOUITColumnName.VID_ZOUIT):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.ZOUIT}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/spritzones", 
    response_model=FeatureCollection,
    response_description="Слой зон регулирования застройки и застройки",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя зон регулирования застройки и застройки",
    summary="Зоны регулирования застройки и застройки",
    # responses={},
        )
def visualize_spritzones(layer: LayerName = LayerName.spritzones, column: SpritzonesColumnName = SpritzonesColumnName.LineCode):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.spritzones}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/YDC_ROADS", 
    response_model=FeatureCollection,
    response_description="Слой дорог",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя дорог",
    summary="Дороги",
    # responses={},
        )
def visualize_ydc_roads(layer: LayerName = LayerName.YDC_ROADS, column: YDC_ROADSColumnName = YDC_ROADSColumnName.VID_ROAD):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.YDC_ROADS}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/renovation_sites", 
    response_model=FeatureCollection,
    response_description="Слой стартовых площадок реновации",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя стартовых площадок реновации",
    summary="Стартовые площадки реновации",
    # responses={},
        )
def visualize_renovation_sites(layer: LayerName = LayerName.renovation_sites, column: RenovationSitesColumnName = RenovationSitesColumnName.vysota):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.renovation_sites}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/PPZ_ZONES", 
    response_model=FeatureCollection,
    response_description="Слой ПЗЗ (территориальные зоны)",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя ПЗЗ (территориальные зоны)",
    summary="ПЗЗ (территориальные зоны)",
    # responses={},
        )
def visualize_ppz_zones(layer: LayerName = LayerName.PPZ_ZONES_NEW, column: PPZ_ZONESColumnName = PPZ_ZONESColumnName.TYPE):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.PPZ_ZONES}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/PPZ_PODZONES", 
    response_model=FeatureCollection,
    response_description="Слой ПЗЗ (территориальные подзоны)",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя ПЗЗ (территориальные подзоны)",
    summary="ПЗЗ (территориальные подзоны)",
    # responses={},
        )
def visualize_ppz_podzones(layer: LayerName = LayerName.PPZ_PODZONES_NEW, column: PPZ_PODZONESColumnName = PPZ_PODZONESColumnName.PLOTNOST):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.PPZ_PODZONES}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/KRT", 
    response_model=FeatureCollection,
    response_description="Слой капитального ремонта территории",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя капитального ремонта территории",
    summary="Капитальный ремонт территории",
    # responses={},
        )
def visualize_krt(layer: LayerName = LayerName.KRT, column: KRTColumnName = KRTColumnName.type_krt):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.KRT}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/Districts", 
    response_model=FeatureCollection,
    response_description="Слой округов",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя округов",
    summary="Округа",
    # responses={},
        )
def visualize_districts(layer: LayerName = LayerName.DISTRICTS, column: DistrictsColumnName = DistrictsColumnName.NAME):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.DISTRICTS}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/Region",
    response_model=FeatureCollection,
    response_description="Слой районов",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя районов",
    summary="Районы",
    # responses={},
        )
def visualize_region(layer: LayerName = LayerName.REGION, column: RegionColumnName = RegionColumnName.NAME):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.region}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/Survey", 
    response_model=FeatureCollection,
    response_description="Слой участков межевания жилых кварталов",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя участков межевания жилых кварталов",
    summary="Участки межевания жилых кварталов",
    # responses={},
        )
def visualize_survey(layer: LayerName = LayerName.SURVEY, column: SurveyColumnName = SurveyColumnName.KLASS):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.SURVEY}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/OOZT", 
    response_model=FeatureCollection,
    response_description="Слой объектов охраняемой зоны территории",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя объектов охраняемой зоны территории",
    summary="Объекты охраняемой зоны территории",
    # responses={},
        )
def visualize_oozt(layer: LayerName = LayerName.OOZT, column: OOZTColumnName = OOZTColumnName.status):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.OOZT}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/Cadastral", 
    response_model=FeatureCollection,
    response_description="Слой кадастрового деления",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя кадастрового деления",
    summary="Кадастровое деление",
    # responses={},
        )
def visualize_cadastral(layer: LayerName = LayerName.Cadastral, column: CadastralColumnName = CadastralColumnName.cadastra1):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.Cadastral}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@router.get(
    "/visualize/MKD", 
    response_model=FeatureCollection,
    response_description="Слой многоквартирных домов",
    status_code=status.HTTP_200_OK,
    description="Визуализация слоя многоквартирных домов",
    summary="Многоквартирные дома",
    # responses={},
        )
def visualize_mkd(layer: LayerName = LayerName.MKD, column: MKDColumnName = MKDColumnName.hasbti):
    try:
        # layer folder + layer name
        gdf = read_shapefile(f"{LayerFolder.MKD}/{layer.value}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson


def read_shapefile(file, encode='cp1251'):
    with fiona.open(os.path.join(data_dir, file), encoding=encode) as src:
        gdf = gpd.GeoDataFrame.from_features(src, crs=src.crs)
        return gdf

def remove_empty_and_zero_columns(gdf):
    non_empty_columns = [col for col in gdf.columns if gdf[col].notnull().any()]
    non_zero_columns = [col for col in non_empty_columns if not ((gdf[col] == 0) | (gdf[col] == 0.0)).all()]
    gdf = gdf[non_zero_columns]
    return gdf

def add_color(gdf, column):
    unique_values = gdf[column].unique()
    colors = list(mcolors.TABLEAU_COLORS.values())
    color_map = {val: colors[i % len(colors)] for i, val in enumerate(unique_values)}
    gdf['color'] = gdf[column].map(color_map)
    return gdf

def gdf_to_geojson(gdf) -> FeatureCollection:
    features = []
    for _, row in gdf.iterrows():
        feature = Feature(
            geometry=row['geometry'].__geo_interface__,
            properties=row.drop('geometry').to_dict()
        )
        features.append(feature)
    return FeatureCollection(features=features)
