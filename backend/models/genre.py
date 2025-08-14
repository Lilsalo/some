from pydantic import BaseModel, Field
from typing import Optional
from typing import List

# Para crear géneros
class Genre(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Name of the genre")

# Para devolver géneros (con ID)
class GenreResponse(Genre):
    id: str

# Para actualizar géneros (PUT/PATCH)
class UpdateGenre(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="Updated name of the genre")

# Para asignar un género a un artista
class GenreAssignment(BaseModel):
    genre_id: str = Field(..., description="Identifier of the genre to assign")

class GenreListAssignment(BaseModel):
    genre_ids: List[str]