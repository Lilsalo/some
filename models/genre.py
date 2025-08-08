from pydantic import BaseModel, Field
from typing import Optional

class Genre(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the genre")
