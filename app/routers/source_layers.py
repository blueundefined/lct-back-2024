from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import json
from app.config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)

@router.get("/files", summary="Список GeoJSON файлов")
async def list_geojson_files():
    try:
        files = [f for f in os.listdir(config.GEOJSON_DIR) if f.endswith('.json')]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{filename}", summary="Получить GeoJSON файл")
async def get_geojson_file(filename: str):
    file_path = os.path.join(config.GEOJSON_DIR, filename)
    if not os.path.exists(file_path) or not file_path.endswith('.json'):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            geojson_content = json.load(f)
        return JSONResponse(content=geojson_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

