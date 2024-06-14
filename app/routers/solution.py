from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from fastapi.responses import JSONResponse, FileResponse
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import io
from shapely.geometry import Point, Polygon, LineString, MultiPoint, MultiLineString, MultiPolygon
import fiona
from typing import List
import json

from app.config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)

output_dir = os.path.join('app/processed_data')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# In-memory storage for uploaded shapefiles
uploaded_files = {}

# Function to read and transform shapefile with correction
def read_and_transform_shapefile_with_correction(file: io.BytesIO, encoding: str, target_crs='EPSG:4326', lat_correction=0.000405-0.000245, lon_correction=-0.001721+0.000245):
    with fiona.BytesCollection(file.read()) as src:
        gdf = gpd.GeoDataFrame.from_features(src, crs=src.crs)
        if gdf.crs is None:
            raise ValueError(f"CRS for {file} is not defined. Please provide the correct CRS.")
        gdf = gdf.to_crs(target_crs)

        def correct_coords(geom, lon_corr, lat_corr):
            if geom.geom_type == 'Point':
                return Point(geom.x + lon_corr, geom.y + lat_corr)
            elif geom.geom_type == 'LineString':
                return LineString([(x + lon_corr, y + lat_corr) for x, y in geom.coords])
            elif geom.geom_type == 'Polygon':
                return Polygon([(x + lon_corr, y + lat_corr) for x, y in geom.exterior.coords])
            elif geom.geom_type == 'MultiPoint':
                return MultiPoint([Point(x + lon_corr, y + lat_corr) for x, y in geom.coords])
            elif geom.geom_type == 'MultiLineString':
                return MultiLineString([LineString([(x + lon_corr, y + lat_corr) for x, y in line.coords]) for line in geom])
            elif geom.geom_type == 'MultiPolygon':
                new_polygons = []
                for poly in geom.geoms:
                    new_exterior = [(x + lon_corr, y + lat_corr) for x, y in poly.exterior.coords]
                    new_interiors = [[(x + lon_corr, y + lat_corr) for x, y in interior.coords] for interior in poly.interiors]
                    new_polygons.append(Polygon(new_exterior, new_interiors))
                return MultiPolygon(new_polygons)
            else:
                return geom

        gdf['geometry'] = gdf['geometry'].apply(lambda geom: correct_coords(geom, lon_correction, lat_correction))
    return gdf

# Function to subtract intersections
def subtract_intersections(base_gdf, intersecting_gdfs):
    remaining_gdf = base_gdf.copy()
    for gdf in intersecting_gdfs:
        try:
            remaining_gdf = gpd.overlay(remaining_gdf, gdf, how='difference')
        except Exception as e:
            print(f"Ошибка при вычитании слоя: {e}")
    return remaining_gdf

@router.post("/solution/upload_shapefile", response_description="Upload a shapefile")
async def upload_shapefile(file: UploadFile = File(...)):
    content = await file.read()
    uploaded_files[file.filename] = io.BytesIO(content)
    return {"filename": file.filename}

@router.get("/solution/process_geojson", response_description="Process shapefiles and return resulting GeoJSON file")
async def process_geojson():
    if 'base_layer.shp' not in uploaded_files:
        raise HTTPException(status_code=400, detail="Base layer shapefile not uploaded.")
    
    base_gdf = read_and_transform_shapefile_with_correction(uploaded_files['base_layer.shp'], encoding='cp1251')

    intersecting_layers = ['zpo_valid.shp', 'zouit.shp', 'spritzones.shp', 'oozt.shp', 'renovation_sites.shp', 'krt.shp', 'mkd.shp']
    intersecting_gdfs = []
    
    for layer in intersecting_layers:
        if layer in uploaded_files:
            gdf = read_and_transform_shapefile_with_correction(uploaded_files[layer], encoding='cp1251')
            intersecting_gdfs.append(gdf)

    remaining_area = subtract_intersections(base_gdf, intersecting_gdfs)

    remaining_area.to_file(os.path.join(output_dir, 'remaining_area.shp'), encoding='cp1251')

    gdf_remain = read_and_transform_shapefile_with_correction(io.BytesIO(remaining_area.to_json().encode()), encoding='utf-8')
    geom = gdf_remain.unary_union
    geoms = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)

    gdf_parts = gpd.GeoDataFrame(geometry=geoms, crs=gdf_remain.crs)
    geojson_path = os.path.join(output_dir, 'small_parts.geojson')
    gdf_parts.to_file(geojson_path, driver='GeoJSON')

    filters_used = {
        "base_layer": "base_layer.shp",
        "intersecting_layers": intersecting_layers,
        "corrections": {"lat_correction": 0.000405, "lon_correction": -0.001721}
    }

    return JSONResponse(content={"filters_used": filters_used, "geojson_file": geojson_path})

@router.get("/solution/processed_geojson", response_description="Download processed GeoJSON file")
async def processed_geojson():
    return FileResponse(os.path.join(output_dir, 'small_parts.geojson'))

