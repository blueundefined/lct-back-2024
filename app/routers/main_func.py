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

class Properties(BaseModel):
    OBJECTID: int
    NAME: str
    SHAPE_AREA: float
    SHAPE_LEN: float
    color: str

class Feature(BaseModel):
    type: str = "Feature"
    properties: Properties
    geometry: Geometry

class FeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Feature]

data_dir = '/app/shapefiles'
output_dir = '/app/geojson_files'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

class LayerName(str, Enum):
    rayon = "район.shp"

class ColumnName(str, Enum):
    name = "NAME"

@router.get("/visualize/", response_model=FeatureCollection)
def visualize(layer: LayerName = LayerName.rayon, column: ColumnName = ColumnName.name):
    try:
        gdf = read_shapefile(layer.value)
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
            properties=Properties(
                OBJECTID=row['OBJECTID'],
                NAME=row['NAME'],
                SHAPE_AREA=row['SHAPE_AREA'],
                SHAPE_LEN=row['SHAPE_LEN'],
                color=row['color']
            ),
            geometry=Geometry(
                type=row['geometry'].geom_type,
                coordinates=row['geometry'].__geo_interface__['coordinates']
            )
        )
        features.append(feature)
    
    return FeatureCollection(features=features)