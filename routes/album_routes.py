from fastapi import APIRouter, Request
from models.album import Album, AlbumUpdate
from utils.auth_dependency import validate_user
from controllers.album import (
    create_album,
    list_albums,
    patch_album,
    delete_album,
    album_with_most_songs,
    albums_with_least_songs,
)

router = APIRouter(prefix="/albums", tags=["Albums"])


# Crear álbum (requiere autenticación)
@router.post("/", summary="Create new album")
@validate_user
async def create_album_route(album: Album, request: Request):
    return create_album(album, request)


# Obtener todos los álbumes (público)
@router.get("/", summary="List all albums")
async def list_albums_route():
    return list_albums()


# Actualizar álbum por ID (requiere autenticación)
@router.patch("/{album_id}", summary="Update album")
@validate_user
async def patch_album_route(album_id: str, album: AlbumUpdate, request: Request):
    return patch_album(album_id, album, request)


# Eliminar álbum por ID (requiere autenticación)
@router.delete("/{album_id}", summary="Delete album")
@validate_user
async def delete_album_route(album_id: str, request: Request):
    return delete_album(album_id, request)


# Obtener álbum con más canciones (público)
@router.get("/statistics/most-songs", summary="Album with most songs")
async def album_with_most_songs_route():
    return await album_with_most_songs()


# Obtener álbumes con menos canciones (público)
@router.get("/statistics/least-songs", summary="Albums with least songs")
async def albums_with_least_songs_route():
    return await albums_with_least_songs()
