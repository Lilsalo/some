from pydantic import BaseModel, Field, validator
from typing import Optional, List


class ArtistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the artist")
    genre: List[str] = Field(..., description="List of genre names associated with the artist")
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
    genre: Optional[List[str]] = None  # nombres de género
    country: Optional[str] = None
    albums: Optional[List[str]] = None


# Respuesta cuando se crea o actualiza (solo ID de respuesta)
class ArtistResponse(BaseModel):
    msg: str
    id: str


# Modelo de salida ya enriquecido con nombres de géneros (para list_artists y detalles)
class ArtistOut(BaseModel):
    id: str
    name: str
    genre: List[str]  # género por nombre, gracias al lookup
    country: str
    albums: List[str] = []
