from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pyproj import Proj, transform
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import config
from app.database.connection import get_session

from shapely.geometry import Point, Polygon, LineString, MultiPoint, MultiLineString, MultiPolygon

from functools import lru_cache

router = APIRouter(prefix=config.BACKEND_PREFIX)

import os
from fastapi import APIRouter, HTTPException
from enum import Enum
import geopandas as gpd
import fiona
from pydantic import BaseModel
from typing import List, Type
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
        gdf = read_shapefile(f"{LayerFolder.ZU.value}/{layer.value}", encoding='UTF8')
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.OKS.value}/{layer.value}", encoding='UTF8')
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.ZOUIT.value}/{layer.value}", encoding='UTF8')
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.spritzones.value}/{layer.value}", encoding='UTF8')
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.YDC_ROADS.value}/{layer.value}")
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.renovation_sites.value}/{layer.value}", encoding='UTF8')
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.PPZ_ZONES.value}/{layer.value}", encoding='UTF8')
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.PPZ_PODZONES.value}/{layer.value}", encoding='UTF8')
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.KRT.value}/{layer.value}", encoding='UTF8')
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.DISTRICTS.value}/{layer.value}")
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.region.value}/{layer.value}")
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.SURVEY.value}/{layer.value}")
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.OOZT.value}/{layer.value}", encoding='UTF8')
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.Cadastral.value}/{layer.value}")
        gdf = gdf.to_crs("EPSG:4326")
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
        gdf = read_shapefile(f"{LayerFolder.MKD.value}/{layer.value}", encoding='UTF8')
        gdf = gdf.to_crs("EPSG:4326")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the shapefile: {str(e)}")
    
    if column.value not in gdf.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column.value}' not found in the data")

    gdf = remove_empty_and_zero_columns(gdf)
    gdf = add_color(gdf, column.value)
    
    geojson = gdf_to_geojson(gdf)

    return geojson

@lru_cache
def read_shapefile(file, encode='cp1251'):
    with fiona.open(os.path.join(data_dir, file), encoding=encode) as src:
        gdf = gpd.GeoDataFrame.from_features(src, crs=src.crs)
        return gdf
    
def transform_geometry(transformer, target_crs, geom):
    if isinstance(geom, Point):
        return transform(transformer, target_crs, geom.x, geom.y)
    elif isinstance(geom, LineString):
        transformed_coords = [transform(transformer, target_crs, *point) for point in geom.coords]
        return LineString(transformed_coords)
    elif isinstance(geom, Polygon):
        exterior = [transform(transformer, target_crs, *coord) for coord in geom.exterior.coords]
        interiors = [[transform(transformer, target_crs, *coord) for coord in interior.coords] for interior in geom.interiors]
        return Polygon(exterior, interiors)
    elif isinstance(geom, MultiPoint):
        return MultiPoint([transform(transformer, target_crs, point.x, point.y) for point in geom.geoms])
    elif isinstance(geom, MultiLineString):
        return MultiLineString([LineString([transform(transformer, target_crs, *point) for point in line.coords]) for line in geom.geoms])
    elif isinstance(geom, MultiPolygon):
        return MultiPolygon([Polygon([transform(transformer, target_crs, *coord) for coord in polygon.exterior.coords],
                                     [[transform(transformer, target_crs, *coord) for coord in interior.coords] for interior in polygon.interiors])
                            for polygon in geom.geoms])
    else:
        raise ValueError(f"Unsupported geometry type: {type(geom)}")

@lru_cache
def read_shapefile_trans(file, encode='cp1251'):
    

    with fiona.open(os.path.join(data_dir, file), encoding=encode) as src:
        # Get the source CRS and create a transformer to WGS-84
        src_crs = src.crs
        transformer = Proj(projparams='+proj=tmerc +lat_0=55.667 +lon_0=37.4998 +k=1 +x_0=-19.1 +y_0=4.9 +ellps=krass +towgs84=23.92,-141.27,-80.9,-0,0.35,0.82,-0.12 +units=m +no_defs')
        target_crs = Proj(init='epsg:4326')  # WGS-84 CRS

        # Read the shapefile into a GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(src, crs=src_crs)

        # Transform geometries to WGS-84
        gdf['geometry'] = gdf['geometry'].apply(lambda geom: transform_geometry(transformer, target_crs, geom))

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


def change_src_crs_to_wgs84(gdf):
    # Get the source CRS and create a transformer to WGS-84
    return gdf.to_crs(epsg=4326)



@lru_cache
def load_shapefiles():
    # load all shapefiles into memory to speed up the visualization and avoid reading the files each time
    # if ЗУ, ОКС, ЗОУИТ, СПРИТ, Реновация, ПЗЗ, КРТ, ООЗТ, МКД - encoding='UTF8'
    for layer, folder in LayerFolder.__members__.items():
        for file in os.listdir(os.path.join(data_dir, folder.value)):
            if file.endswith('.shp'):
                if layer == LayerName.ZU or layer == LayerName.OKS or layer == LayerName.ZOUIT or layer == LayerName.spritzones or layer == LayerName.renovation_sites or layer == LayerName.PPZ_ZONES_NEW or layer == LayerName.PPZ_ZONES_OLD or layer == LayerName.PPZ_PODZONES_OLD or layer == LayerName.PPZ_PODZONES_NEW or layer == LayerName.KRT or layer == LayerName.OOZT or layer == LayerName.MKD:
                    try:
                        gdf = read_shapefile(f"{folder.value}/{file}", encode='UTF8')
                    except Exception as e:
                        print(f"Error reading the shapefile: {str(e)}")
                else:
                    try:
                        gdf = read_shapefile(f"{folder.value}/{file}")
                    except Exception as e:
                        print(f"Error reading the shapefile: {str(e)}")

    
    print("All shapefiles loaded into memory")

from enum import Enum
from pydantic import BaseModel

class ZUPropertiesEnum(Enum):
    CADASTRA2 = "Кадастровый/учетный номер"
    ADDRESS = "Адрес"
    HASVALID5 = "Наличие действующего правоудостоверяющего документа (1 - есть, 0 - нет)"
    HASCADAS6 = "На кадастровом учете (1 - да, 0 - нет)"
    ISDRAFT = "Проекты (распоряжения) (1 - да, 0 - нет)"
    OWNERSHI8 = "Тип собственности (1 - МСК, 2 - РФ, 3 - Частная, 5 - Неразграниченная)"
    IS_STROY = "Наличие действующего разрешения на строительство (1 - да, 0 - нет)"
    IS_NONCA20 = "Земельные участки с ЗПО для некапитальных объектов (1 - да, 0 - нет)"
    AREA = "Площадь, кв.м"

class ZUProperties(BaseModel):
    cadastra2: str
    address: str
    hasvalid5: str
    hascadas6: str
    isdraft: str
    ownershi8: float
    is_stroy: str
    is_nonca20: float
    area: float

class OKSPropertiesEnum(Enum):
    UNOM = "УНОМ"
    ADDRESS = "Адрес"
    CADASTRA3 = "Кадастровый номер"
    HASCADAS4 = "На кадастровом учете"
    HASBTI = "На кадастровом учете БТИ"
    HASOWNRF = "РФ"
    HASOWNMO8 = "Москва"
    HASOWNOT9 = "Другие"
    SHAPE_AREA = "Площадь"

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

class ZOUITPropertiesEnum(Enum):
    CAD_NUM = "Кадастровый номер зоны"
    OKRUG = "Округ"
    RAION_POS = "Район"
    VID_ZOUIT = "Вид ЗОУИТ"
    TYPE_ZONE = "Тип ЗОУИТ"
    NAME = "Название зоны"
    OGRAN = "Дополнительные сведения"
    DOC = "Документ"
    AREA = "Площадь"

class ZOUITProperties(BaseModel):
    cad_num: str
    okrug: str
    raion_pos: str
    vid_zouit: str
    type_zone: str
    name: str
    ogran: str
    doc: str
    area: float

class SpritzonesPropertiesEnum(Enum):
    LINECODE = "Код линии"
    NAME = "Наименование зоны"
    DOC = "Документ"
    COMMENT = "Комментарий"
    AREA = "Площадь"

class SpritzonesProperties(BaseModel):
    linecode: str
    name: str
    doc: str
    comment: str
    area: float

class YDC_ROADSPropertiesEnum(Enum):
    NAME_OBJ = "Наименование"
    NAME_STR = "Наименование улицы"
    VID_ROAD = "Вид дороги"
    EXT_NAME = "Наименование улицы"
    SHAPE_LENG = "Геометрический периметр"
    SHAPE_AREA = "Геометрическая площадь"

class YDC_ROADSProperties(BaseModel):
    name_obj: str
    name_str: str
    vid_road: str
    ext_name: str
    shape_leng: float
    shape_area: float

class RenovationSitesPropertiesEnum(Enum):
    OKRUG = "Административный округ"
    RAYON = "Административный район"
    ADDRESS = "Адрес"
    AREA = "Площадь"
    PRIM = "Примечание"
    PLOTNOST = "Плотность"
    VYSOTA = "Высота"
    SPP = "СПП"
    TOTAL_AREA = "Общая площадь"
    FLAT_AREA = "Площадь квартир"
    OSNOVANIE = "Основание"
    AGR = "АГР"
    OBJECTID = "OBJECTID"

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

class PPZ_ZONESPropertiesEnum(Enum):
    ZONE_NUM = "Номер зоны"
    NUM_PP = "Номер утверждающего документа"
    DOC_DATE = "Дата утверждающего документа"
    TYPE = "Тип"
    INDEX_ = "ВРИ"
    VRI_540 = "ВРИ"
    AREA = "Площадь"

class PPZ_ZONESProperties(BaseModel):
    zone_num: str
    num_pp: str
    doc_date: str
    type: str
    index_: str
    vri_540: str
    area: float

class PPZ_PODZONESPropertiesEnum(Enum):
    PLOTNOST = "Плотность"
    VYSOTA = "Высота"
    PROCZASTRO = "Процент застройки"
    PODZONE_NU = "Номер подзоны"
    NUM_PP = "Номер утверждающего документа"
    DOC_DATE = "Дата утверждающего документа"
    TYPE = "Тип"
    AREA = "Площадь"

class PPZ_PODZONESProperties(BaseModel):
    plotnost: str
    vysota: str
    proczastro: str
    podzone_nu: str
    num_pp: str
    doc_date: str
    type: str
    area: float

class KRTPropertiesEnum(Enum):
    NAME = "Наименование КРТ"
    AREA_KRT = "Площадь КРТ"
    TYPE_KRT = "Наименование типа слоя"

class KRTProperties(BaseModel):
    name: str
    area_krt: float
    type_krt: str

class DistrictsPropertiesEnum(Enum):
    OBJECTID = "Номер объекта"
    NAME = "Наименование"
    LABEL = "Метка"
    TORZID = "Идентификатор территории"
    SHAPE_AREA = "Геометрическая площадь"
    SHAPE_LEN = "Геометрическая длина"

class DistrictsProperties(BaseModel):
    objectid: int
    name: str
    label: str
    torzid: float
    shape_area: float
    shape_len: float

class RegionPropertiesEnum(Enum):
    OBJECTID = "Номер объекта"
    NAME = "Наименование"
    LABEL = "Метка"
    TORZID = "Идентификатор территории"
    SHAPE_AREA = "Геометрическая площадь"
    SHAPE_LEN = "Геометрическая длина"

class RegionProperties(BaseModel):
    objectid: int
    name: str
    label: str
    torzid: float
    shape_area: float
    shape_len: float

class SurveyPropertiesEnum(Enum):
    NUMBERAREA = "Системное поле"
    DESCR = "Учетный номер участка межевания"
    KLASS = "Класс"
    FUNC_USE = "Функциональное использование"
    N_KVAR = "Номер квартала"
    N_PARC = "Номер участка"
    YEAR = "Год разработки"
    AREA = "Площадь по документу"
    SHAPE_AREA = "Геометрическая площадь"

class SurveyProperties(BaseModel):
    numberarea: int
    descr: str
    klass: str
    func_use: str
    n_kvar: str
    n_parc: str
    year: str
    area: float
    shape_area: float

class OOZTPropertiesEnum(Enum):
    OBJECTID = "Номер объекта"
    STATUS = "Статус"
    ZONEID = "Зона"
    DOCNUM = "Номер документа"
    DOCDATE = "Дата документа"
    DOCLIST = "Лист"

class OOZTProperties(BaseModel):
    objectid: str
    status: str
    zoneid: str
    docnum: str
    docdate: str
    doclist: str

class PPTPropertiesEnum(Enum):
    REG_NUM = "Регистрационный номер"
    VID_PPT = "Вид ППТ"
    NAME = "Название"
    VID_DOC_RA = "Вид распоряжения"
    NUM_DOC_RA = "Номер распоряжения"
    DATA_DOC_R = "Дата распоряжения"
    ZAKAZCHIK = "Заказчик"
    ISPOLNITEL = "Исполнитель"
    ISTOCH_FIN = "Источник финансов"
    OTVETST_MK = "Ответственный МК"
    NUM_KONTRA = "Номер контракта"
    DATA_KONTR = "Дата контракта"
    REKV_PROEK = "Реквизиты проектных документов"
    DOVER_ORG = "Доверенная организация"
    OSNOVANIEN = "Основание"
    DATA_PP = "Дата утверждения ПП"

class PPTProperties(BaseModel):
    reg_num: str
    vid_ppt: str
    name: str
    vid_doc_ra: str
    num_doc_ra: str
    data_doc_r: str
    zakazchik: str
    ispolnitel: str
    istoch_fin: str
    otvetst_mk: str
    num_kontra: str
    data_kontr: str
    rekv_proek: str
    dover_org: str
    osnovanien: str
    data_pp: str


# api router to return every possible column for each layer to be used in the visualization
class LayerName(Enum):
    ZUProperties = "ZUProperties"
    OKSProperties = "OKSProperties"
    ZOUITProperties = "ZOUITProperties"
    SpritzonesProperties = "SpritzonesProperties"
    YDC_ROADSProperties = "YDC_ROADSProperties"
    RenovationSitesProperties = "RenovationSitesProperties"
    PPZ_ZONESProperties = "PPZ_ZONESProperties"
    PPZ_PODZONESProperties = "PPZ_PODZONESProperties"
    KRTProperties = "KRTProperties"
    DistrictsProperties = "DistrictsProperties"
    RegionProperties = "RegionProperties"
    SurveyProperties = "SurveyProperties"
    OOZTProperties = "OOZTProperties"
    PPTProperties = "PPTProperties"

class ColumnInfo(BaseModel):
    name: str
    #type: str
    description: str

class LayerColumnsResponse(BaseModel):
    layer: str
    columns: List[ColumnInfo]


@router.get(
    "/columns/",
    response_model=Dict[str, List[ColumnInfo]],
    response_description="Список всех возможных колонок для каждого слоя",
    status_code=status.HTTP_200_OK,
    description="Список всех возможных колонок для каждого слоя",
    summary="Список всех возможных колонок для каждого слоя",
)
def get_columns() -> Dict[str, List[ColumnInfo]]:
    columns: Dict[str, List[ColumnInfo]] = {}
    layer_models: Dict[str, Type[BaseModel]] = {
        "ZUProperties": ZUProperties,
        "OKSProperties": OKSProperties,
        "ZOUITProperties": ZOUITProperties,
        "SpritzonesProperties": SpritzonesProperties,
        "YDC_ROADSProperties": YDC_ROADSProperties,
        "RenovationSitesProperties": RenovationSitesProperties,
        "PPZ_ZONESProperties": PPZ_ZONESProperties,
        "PPZ_PODZONESProperties": PPZ_PODZONESProperties,
        "KRTProperties": KRTProperties,
        "DistrictsProperties": DistrictsProperties,
        "RegionProperties": RegionProperties,
        "SurveyProperties": SurveyProperties,
        "OOZTProperties": OOZTProperties,
        "PPTProperties": PPTProperties,
    }

    layer_enums: Dict[str, Type[Enum]] = {
        "ZUProperties": ZUPropertiesEnum,
        "OKSProperties": OKSPropertiesEnum,
        "ZOUITProperties": ZOUITPropertiesEnum,
        "SpritzonesProperties": SpritzonesPropertiesEnum,
        "YDC_ROADSProperties": YDC_ROADSPropertiesEnum,
        "RenovationSitesProperties": RenovationSitesPropertiesEnum,
        "PPZ_ZONESProperties": PPZ_ZONESPropertiesEnum,
        "PPZ_PODZONESProperties": PPZ_PODZONESPropertiesEnum,
        "KRTProperties": KRTPropertiesEnum,
        "DistrictsProperties": DistrictsPropertiesEnum,
        "RegionProperties": RegionPropertiesEnum,
        "SurveyProperties": SurveyPropertiesEnum,
        "OOZTProperties": OOZTPropertiesEnum,
        "PPTProperties": PPTPropertiesEnum,
    }

    for layer in LayerName:
        layer_name = layer.value
        model = layer_models[layer_name]
        enum = layer_enums[layer_name]
        columns[layer_name] = []

        print("Layer: ", layer_name)
        for field_name, field in model.__fields__.items():
            column_info = ColumnInfo(
                name=field_name,
                description=enum[field_name.upper()].value
            )
            columns[layer_name].append(column_info)

    return columns

# load all shapefiles into memory to speed up the visualization and avoid reading the files each time
# load_shapefiles()