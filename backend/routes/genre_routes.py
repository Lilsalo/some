from fastapi import APIRouter, Request, Query, status
from models.genre import Genre, UpdateGenre
import controllers.genre as genre_controller
from utils.auth_dependency import validate_user  # usa validate_admin si solo admins pueden

router = APIRouter(prefix="/genres", tags=["Genres"])

# Crear género (requiere autenticación)
@router.post(
    "/",
    summary="Crear género",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Género creado"},
        400: {"description": "Body inválido"},
        409: {"description": "Género duplicado"},
    },
)
@validate_user
async def create_genre(genre: Genre, request: Request):
    return await genre_controller.create_genre(genre, request)


# Listar géneros (público)
# Por defecto solo activos; usar ?include_inactive=true para ver también inactivos
@router.get(
    "/",
    summary="Listar géneros (por defecto solo activos)",
    responses={200: {"description": "OK"}},
)
async def get_all_genres(include_inactive: bool = Query(False)):
    return await genre_controller.get_all_genres(include_inactive)


# Obtener género por ID (público)
@router.get(
    "/{genre_id}",
    summary="Obtener género por ID",
    responses={
        200: {"description": "OK"},
        400: {"description": "ID inválido"},
        404: {"description": "No encontrado"},
    },
)
async def get_genre_by_id(genre_id: str):
    return await genre_controller.get_genre_by_id(genre_id)


# Actualizar género (requiere autenticación)
@router.put(
    "/{genre_id}",
    summary="Actualizar género",
    responses={
        200: {"description": "Género actualizado"},
        400: {"description": "ID o body inválido"},
        404: {"description": "No encontrado"},
        409: {"description": "Duplicado"},
    },
)
@validate_user
async def update_genre(genre_id: str, genre: UpdateGenre, request: Request):
    return await genre_controller.update_genre(genre_id, genre, request)


# Eliminar género (con restricción) – requiere autenticación
# Si el género está asignado a artistas → 409 Conflict (NO se elimina)
@router.delete(
    "/{genre_id}",
    summary="Eliminar género (con restricción)",
    responses={
        200: {"description": "Género eliminado"},
        400: {"description": "ID inválido"},
        404: {"description": "No encontrado"},
        409: {"description": "Género en uso (asignado a artistas)"},
    },
)
@validate_user
async def delete_genre(genre_id: str, request: Request):
    return await genre_controller.delete_genre(genre_id, request)
