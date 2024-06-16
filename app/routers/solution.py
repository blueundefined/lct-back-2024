from typing import List
from fastapi import APIRouter, FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import geopandas as gpd
import os
import io
import fiona
from app.database.tables import Shape
from app.config import config
from app.database.connection import AsyncSession
from app.models import ShapeGet, ShapeCreate, ShapePatch
from app.database.connection import get_session
from shapely.geometry import Point, Polygon, LineString, MultiPoint, MultiPolygon, MultiLineString

router = APIRouter(prefix=f'{config.BACKEND_PREFIX}/solution')


output_dir = "app/processed_data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# In-memory storage for uploaded shapefiles
uploaded_files = {}

# Функция для чтения и преобразования координат с коррекцией
def read_and_transform_shapefile_with_correction(file: io.BytesIO, encoding: str, target_crs='EPSG:4326', lat_correction=0.000405, lon_correction=-0.001721):
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

# Функция для вычитания пересечений
def subtract_intersections(base_gdf, intersecting_gdfs):
    remaining_gdf = base_gdf.copy()
    for gdf in intersecting_gdfs:
        try:
            remaining_gdf = gpd.overlay(remaining_gdf, gdf, how='difference')
        except Exception as e:
            print(f"Ошибка при вычитании слоя: {e}")
    return remaining_gdf

# Функция для сохранения контуров в базу данных с версионированностью
def save_shapes_to_db(gdf, version, db: Session):
    for _, row in gdf.iterrows():
        shape = ShapeCreate(
            version=version,
            geometry=row['geometry'].wkt,
            comment=''
        )
        db.add(shape)
    db.commit()

# Маршрут для загрузки shapefile
@router.post("/upload_shapefile", response_description="Upload a shapefile")
async def upload_shapefile(file: UploadFile = File(...)):
    content = await file.read()
    uploaded_files[file.filename] = io.BytesIO(content)
    return {"filename": file.filename}

# Маршрут для обработки shapefiles и возврата результирующего GeoJSON файла
@router.get("/process_geojson", response_description="Process shapefiles and return resulting GeoJSON file")
async def process_geojson(db: Session = Depends(get_session)):
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
    version = db.query(Shape).count() // len(geoms) + 1
    save_shapes_to_db(gdf_parts, version, db)

    geojson_path = os.path.join(output_dir, 'small_parts.geojson')
    gdf_parts.to_file(geojson_path, driver='GeoJSON')

    filters_used = {
        "base_layer": "base_layer.shp",
        "intersecting_layers": intersecting_layers,
        "corrections": {"lat_correction": 0.000405, "lon_correction": -0.001721}
    }

    return JSONResponse(content={"filters_used": filters_used, "geojson_file": geojson_path})

# Маршрут для получения всех контуров определенной версии
@router.get("/shapes/{version}", response_model=List[ShapeGet])
def get_shapes(version: int, db: Session = Depends(get_session)):
    shapes = db.query(Shape).filter(Shape.version == version).all()
    if not shapes:
        raise HTTPException(status_code=404, detail="Shapes not found for this version")
    return shapes

# Модель для обновления комментария
class CommentUpdate(BaseModel):
    comment: str

# Маршрут для добавления комментария к контуру
@router.patch("/shapes/{shape_id}/comment")
def update_shape_comment(shape_id: int, comment_update: CommentUpdate, db: Session = Depends(get_session)):
    shape = db.query(Shape).filter(Shape.id == shape_id).first()
    if not shape:
        raise HTTPException(status_code=404, detail="Shape not found")
    shape.comment = comment_update.comment
    db.commit()
    return shape

# Маршрут для получения существующего файла small_parts.geojson
@router.get("/download_geojson", response_description="Download the existing small_parts.geojson file")
async def download_geojson():
    geojson_path = os.path.join(output_dir, 'small_parts.geojson')
    if not os.path.exists(geojson_path):
        raise HTTPException(status_code=404, detail="GeoJSON file not found")
    return FileResponse(geojson_path, media_type='application/json', filename='small_parts.geojson')

# Маршрут для выгрузки существующего файла small_parts.geojson в базу данных
@router.post("/upload_geojson_to_db", response_description="Upload existing small_parts.geojson file to the database")
async def upload_geojson_to_db(db: Session = Depends(get_session)):
    geojson_path = os.path.join(output_dir, 'small_parts.geojson')
    if not os.path.exists(geojson_path):
        raise HTTPException(status_code=404, detail="GeoJSON file not found")
    
    gdf = gpd.read_file(geojson_path)
    version = db.query(Shape).count() // len(gdf) + 1
    save_shapes_to_db(gdf, version, db)

    return JSONResponse(content={"detail": "GeoJSON file uploaded to the database", "version": version})
