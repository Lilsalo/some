from pydantic import BaseModel, Field
from typing import Optional, List

class Playlist(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Playlist name")
    songs: Optional[List[str]] = Field(default_factory=list, description="List of song IDs")
    user: Optional[str] = Field(None, description="Owner user ID")
