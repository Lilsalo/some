from pydantic import BaseModel, Field
from typing import Optional, List


class Playlist(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Playlist name")
    songs: Optional[List[str]] = Field(default_factory=list, description="List of song IDs")
    user: Optional[str] = Field(None, description="Owner user ID")


class UpdatePlaylist(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    songs: Optional[List[str]] = Field(default=None, description="Updated list of song IDs")


class PlaylistResponse(Playlist):
    id: str


class PlaylistAddSongs(BaseModel):
    song_ids: List[str] = Field(..., description="IDs de las canciones a agregar")


class PlaylistRemoveSongs(BaseModel):
    song_ids: List[str] = Field(..., description="IDs de las canciones a quitar")
