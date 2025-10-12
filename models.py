from pydantic import BaseModel, Field
from typing import Optional, List

#Input model (Query parameters)
class PlaceSearchParams(BaseModel):
    query: Optional[str] = Field(default=None, description="Search term like 'coffee', 'restaurant', etc.")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    radius: Optional[int] = Field(default=1000, description="Search radius in meters")
    limit: Optional[int] = Field(default=10, description="Max number of results")

#Response models (Simplified version of Foursquare response)

class Location(BaseModel):
    address: Optional[str]
    locality: Optional[str]
    region: Optional[str]
    postcode: Optional[str]
    country: Optional[str]

#class Category(BaseModel):
    id: str
    name: str
    icon: Optional[dict]

#class Hours(BaseModel):
    display: Optional[str]
    is_open: Optional[bool]

class Place(BaseModel):
    fsq_id: str
    name: str
    Location: Location
    #categories: Category
    #distance: Optional[int]
    #hours: Optional[Hours]
    #rating: Optional[float]
    #website: Optional[str]
    #tel: str

class PlacesResponse(BaseModel):
    results: List[Place]
    