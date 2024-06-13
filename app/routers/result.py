from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import json
from app.config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)

# api route for getting geo result file by given properties

@router.get("/result", summary="Получить GeoJSON файл с результатом")
async def get_geojson_file():
    try:
        files = [f for f in os.listdir(config.RESULT_DIR) if f.endswith('.json')]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))