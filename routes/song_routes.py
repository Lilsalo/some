from fastapi import APIRouter, Query
from models.song import Song, SongUpdate
from controllers.song import (
    create_song as controller_create_song,
    list_songs as controller_list_songs,
    patch_song as controller_patch_song,
    delete_song as controller_delete_song,
    get_songs_by_artist as controller_get_songs_by_artist,
    get_songs_by_album as controller_get_songs_by_album,
)
from utils.auth_dependency import validate_user
from utils.mongodb import get_collection
from bson import ObjectId

router = APIRouter(prefix="/songs", tags=["Songs"])


# Crear canción (requiere autenticación)
@router.post("/", summary="Create new song")
@validate_user
async def create_song(song: Song):
    return await controller_create_song(song)


# Listar todas las canciones (público)
@router.get("/", summary="List all songs")
async def get_songs():
    return await controller_list_songs()


# Actualizar canción por ID (requiere autenticación)
@router.patch("/{song_id}", summary="Update song by ID")
@validate_user
async def update_song(song_id: str, song: SongUpdate):
    return await controller_patch_song(song_id, song)


# Eliminar canción por ID (requiere autenticación)
@router.delete("/{song_id}", summary="Delete song by ID")
@validate_user
async def remove_song(song_id: str):
    return await controller_delete_song(song_id)


# Listar canciones por artista (público)
@router.get("/by-artist/{artist_id}", summary="List songs by artist ID")
async def get_songs_by_artist(artist_id: str):
    return await controller_get_songs_by_artist(artist_id)


# Listar canciones por álbum (público)
@router.get("/by-album/{album_id}", summary="List songs by album ID")
async def get_songs_by_album(album_id: str):
    return await controller_get_songs_by_album(album_id)


# Buscar canciones por nombre, género o artista (público)
@router.get("/search", summary="Search songs by name, genre or artist (no token)")
async def search_songs(
    name: str = Query(None, description="Nombre parcial de la canción"),
    genre: str = Query(None, description="ID del género"),
    artist: str = Query(None, description="ID del artista"),
    limit: int = Query(10, ge=1, le=50, description="Límite de resultados (1-50)")
):
    songs_coll = get_collection("songs")

    query = {}
    if name:
        query["title"] = {"$regex": name, "$options": "i"}
    if genre and ObjectId.is_valid(genre):
        query["genre_id"] = ObjectId(genre)
    if artist and ObjectId.is_valid(artist):
        query["artist_id"] = ObjectId(artist)

    songs = songs_coll.find(query).limit(limit)
    return [{**song, "_id": str(song["_id"])} for song in songs]
