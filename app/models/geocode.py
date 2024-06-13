from pydantic import BaseModel
from typing import List

class GeocodeRequest(BaseModel):
    address: str

class GeocoderCustomResponse(BaseModel):
    address_line: str
    coordinates: List[float]

class SuggestionItem(BaseModel):
    title: str
    subtitle: str
    tags: List[str]
    distance: float

class GeosuggestResponse(BaseModel):
    suggestions: List[SuggestionItem]