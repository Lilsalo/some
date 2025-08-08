
from fastapi import APIRouter
from models.genre import Genre, UpdateGenre
import controllers.genre as genre_controller  
from utils.auth_dependency import validate_user

router = APIRouter(prefix="/genres", tags=["Genres"])


# Crear género (requiere estar autenticado)
@router.post("/")
@validate_user
async def create_genre(genre: Genre):
    return await genre_controller.create_genre(genre)


# Obtener todos los géneros (público)
@router.get("/")
async def get_all_genres():
    return await genre_controller.get_all_genres()


# Obtener género por ID (público)
@router.get("/{genre_id}")
async def get_genre_by_id(genre_id: str):
    return await genre_controller.get_genre_by_id(genre_id)


# Actualizar género (requiere estar autenticado)
@router.put("/{genre_id}")
@validate_user
async def update_genre(genre_id: str, genre: UpdateGenre):
    return await genre_controller.update_genre(genre_id, genre)


# Eliminar género (requiere estar autenticado)
@router.delete("/{genre_id}")
@validate_user
async def delete_genre(genre_id: str):
    return await genre_controller.delete_genre(genre_id)
