from pydantic import BaseModel, Field
from typing import Optional

class Song(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier for the song")
    title: str = Field(..., min_length=1, max_length=200, description="Title of the song")
    artist: str = Field(..., description="Artist ID or name associated with the song")
    album: str = Field(..., description="Album ID this song belongs to")
    duration: int = Field(..., ge=0, description="Duration in seconds")

class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    duration: Optional[int] = None
