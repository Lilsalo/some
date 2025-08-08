from pydantic import BaseModel, Field
from typing import Optional, List

class Album(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier for the album")
    title: str = Field(..., min_length=1, max_length=200, description="Title of the album")
    year: int = Field(..., ge=0, description="Release year")
    genre: str = Field(..., description="Genre ID or name associated with the album")
    artist: str = Field(..., description="Artist ID or name associated with the album")
    songs: Optional[List[str]] = Field(default_factory=list, description="List of song IDs that belong to this album")

class AlbumUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    artist: Optional[str] = None
    songs: Optional[List[str]] = None
