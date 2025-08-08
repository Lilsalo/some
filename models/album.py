from pydantic import BaseModel, Field
from typing import Optional, List

class Album(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title of the album")
    year: int = Field(..., ge=0, description="Release year")
    genre: str = Field(..., description="Genre name associated with the album")
    artist: str = Field(..., description="Artist ID")
    songs: Optional[List[str]] = Field(default_factory=list, description="List of song IDs")

class AlbumUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    artist: Optional[str] = None
    songs: Optional[List[str]] = None

class AlbumOut(Album):
    id: str
