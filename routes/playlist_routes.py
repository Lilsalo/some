from fastapi import APIRouter, Request
from models.playlist import Playlist, PlaylistAddSongs
from utils.auth_dependency import validate_user
from controllers import playlist as playlist_controller

router = APIRouter(prefix="/playlists", tags=["Playlists"])

# Crear playlist (requiere autenticación y validación de canciones eliminadas)
@router.post("/", summary="Crear una nueva playlist")
@validate_user
async def create_playlist_route(playlist: Playlist, request: Request):
    user_email = request.state.user["email"]
    return await playlist_controller.create_playlist(playlist, user_email)

# Obtener playlists del usuario autenticado
@router.get("/", summary="Obtener playlists del usuario autenticado")
@validate_user
async def get_user_playlists_route(request: Request):
    user_email = request.state.user["email"]
    return await playlist_controller.get_playlists_by_user(user_email)

# Agregar canciones a playlist (con validación)
@router.patch("/{playlist_id}/add-song", summary="Agregar canciones a una playlist")
@validate_user
async def add_songs_to_playlist_route(playlist_id: str, payload: PlaylistAddSongs, request: Request):
    user_email = request.state.user["email"]
    return await playlist_controller.add_songs_to_playlist(
        playlist_id, payload.song_ids, user_email
    )

# Remover canciones de playlist
@router.patch("/{playlist_id}/remove-song", summary="Quitar canciones de una playlist")
@validate_user
async def remove_songs_from_playlist_route(playlist_id: str, payload: PlaylistAddSongs, request: Request):
    user_email = request.state.user["email"]
    return await playlist_controller.remove_songs_from_playlist(
        playlist_id, payload.song_ids, user_email
    )

# Eliminar playlist por ID
@router.delete("/{playlist_id}", summary="Eliminar playlist por ID")
@validate_user
async def delete_playlist_route(playlist_id: str, request: Request):
    user_email = request.state.user["email"]
    return await playlist_controller.delete_playlist(playlist_id, user_email)
