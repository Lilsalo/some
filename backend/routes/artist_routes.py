from fastapi import APIRouter, HTTPException, Request
from typing import List
from bson import ObjectId

from models.artist import ArtistCreate, ArtistUpdate, ArtistOut
from models.genre import GenreListAssignment

from controllers.album import get_album_statistics as controller_get_album_statistics
from controllers.artist import (
    create_artist as controller_create_artist,
    update_artist as controller_update_artist,
    list_artists as controller_get_artists,
    list_albums_by_artist as controller_list_albums_by_artist,
    delete_artist as controller_delete_artist,
)

from utils.auth_dependency import validate_user, validate_admin
from utils.mongodb import get_collection

router = APIRouter(prefix="/artists", tags=["Artists"])

# Crear artista (requiere autenticación)
@router.post("/", summary="Create new artist")
@validate_user
async def create_artist(artist: ArtistCreate, request: Request):
    return await controller_create_artist(artist, request)

# Obtener todos los artistas (público)
@router.get("/", summary="List all artists", response_model=List[ArtistOut])
async def get_artists():
    return await controller_get_artists()

# Ruta estática primero para evitar conflictos con /{artist_id}/albums
@router.get("/statistics/top", summary="Obtener artista con más álbumes")
async def get_top_artist_by_albums():
    return await controller_get_album_statistics()

# Obtener álbumes de un artista por ID (público)
@router.get("/{artist_id}/albums", summary="Obtener álbumes de un artista por su ID")
async def get_albums_by_artist(artist_id: str):
    return await controller_list_albums_by_artist(artist_id)

# Actualizar artista por ID (requiere autenticación)
@router.put("/{artist_id}", summary="Update artist")
@validate_user
async def update_artist(artist_id: str, artist: ArtistUpdate, request: Request):
    return await controller_update_artist(artist_id, artist, request)

# Asignar múltiples géneros a un artista (requiere autenticación)
@router.patch("/{artist_id}/assign-genres", summary="Assign multiple genres to artist")
@validate_user
async def assign_genres_to_artist(artist_id: str, payload: GenreListAssignment, request: Request):
    artist_coll = get_collection("artist")
    genre_coll = get_collection("genre")

    if not ObjectId.is_valid(artist_id):
        raise HTTPException(status_code=400, detail="Invalid artist ID format")

    if not artist_coll.find_one({"_id": ObjectId(artist_id)}):
        raise HTTPException(status_code=404, detail="Artist not found")

    for gid in payload.genre_ids:
        if not ObjectId.is_valid(gid):
            raise HTTPException(status_code=400, detail=f"Invalid genre ID format: {gid}")
        if not genre_coll.find_one({"_id": ObjectId(gid)}):
            raise HTTPException(status_code=404, detail=f"Genre with ID {gid} not found")

    artist_coll.update_one(
        {"_id": ObjectId(artist_id)},
        {"$set": {"genre": payload.genre_ids}},
    )

    return {
        "msg": "Genres assigned to artist successfully",
        "artist_id": artist_id,
        "genre_ids": payload.genre_ids,
    }

# Eliminar artista por ID (requiere administrador)
@router.delete("/{artist_id}", summary="Delete artist by ID")
@validate_user
async def delete_artist(artist_id: str, request: Request):
    return await controller_delete_artist(artist_id, request)
