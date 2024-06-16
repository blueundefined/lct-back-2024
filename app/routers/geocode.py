from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import httpx


from app.config import config
from app.models.geocode import GeocodeRequest, GeocoderCustomResponse, GeosuggestResponse, SuggestionItem

router = APIRouter(prefix=config.BACKEND_PREFIX)

GEOCODER_API_KEY = config.GEOCODER_API_KEY
GEOSUGGEST_API_KEY = config.GEOSUGGEST_API_KEY

@router.post("/geocoder", response_model=GeocoderCustomResponse)
async def geocoder(geocode_request: GeocodeRequest):
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={GEOCODER_API_KEY}&format=json&geocode={geocode_request.address}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error from geocoding service")
        
        data = response.json()
        try:
            address_line = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['AddressLine']
            pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            coordinates = [float(coord) for coord in pos.split()]
            coordinates.reverse()  # Reverse to [latitude, longitude]
        except (KeyError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid response from geocoding service")

        return GeocoderCustomResponse(address_line=address_line, coordinates=coordinates)

@router.post("/geosuggest", response_model=GeosuggestResponse)
async def geosuggest(geocode_request: GeocodeRequest):
    url = f"https://suggest-maps.yandex.ru/v1/suggest?apikey={GEOSUGGEST_API_KEY}&format=json&text={geocode_request.address}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error from geosuggest service")
        
        data = response.json()
        suggestions = []
        
        for item in data.get('results', []):
            title = item['title']['text']
            subtitle = item['subtitle']['text']
            tags = item.get('tags', [])
            distance = item['distance']['value']
            suggestions.append(SuggestionItem(title=title, subtitle=subtitle, tags=tags, distance=distance))
        
        return GeosuggestResponse(suggestions=suggestions)
