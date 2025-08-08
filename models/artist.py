from pydantic import BaseModel, Field, validator
from typing import Optional, List

class Artist(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier for the artist")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the artist")
    genre: str = Field(..., description="Genre ID or name associated with the artist")
    country: str = Field(..., min_length=2, max_length=100, description="Country of origin")
    albums: Optional[List[str]] = Field(default_factory=list, description="List of album IDs for this artist")
    
    @validator("name")
    def name_must_be_alpha(cls, v):
        if not v.replace(" ", "").isalpha():
            raise ValueError("Artist name must contain only alphabetic characters and spaces")
        return v

    @validator("country")
    def country_must_be_alpha(cls, v):
        if not v.replace(" ", "").isalpha():
            raise ValueError("Country must contain only alphabetic characters and spaces")
        return v

class ArtistUpdate(BaseModel):
    name: Optional[str] = None
    genre: Optional[str] = None
    country: Optional[str] = None

class ArtistResponse(BaseModel):
    id: str
    name: str
    genre: str
    country: str
    albums: List[str]
