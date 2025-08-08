from fastapi import HTTPException
from models.playlist import Playlist
from utils.mongodb import get_collection
from bson import ObjectId

# Crear nueva playlist
async def create_playlist(playlist: Playlist, user_email: str):
    try:
        users = get_collection("users")
        songs_coll = get_collection("songs")
        playlist_coll = get_collection("playlist")

        user = users.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        for song_id in playlist.songs:
            if not ObjectId.is_valid(song_id) or not songs_coll.find_one({"_id": ObjectId(song_id), "deleted": {"$ne": True}}):
                raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found or is deleted")

        data = playlist.model_dump()
        data["user"] = str(user["_id"])
        result = playlist_coll.insert_one(data)

        users.update_one({"_id": user["_id"]}, {"$addToSet": {"playlists": str(result.inserted_id)}})

        return {"msg": "Playlist created", "id": str(result.inserted_id)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error creating playlist")


# Obtener playlists del usuario
async def get_playlists_by_user(user_email: str):
    coll = get_collection("playlist")
    playlists = list(coll.find({"user": {"$exists": True}}))
    user_playlists = [p for p in playlists if p.get("user") == user_email or str(p.get("user")) == user_email]
    return [{"id": str(p["_id"]), "name": p.get("name"), "songs": p.get("songs", [])} for p in user_playlists]


# Eliminar playlist por ID
async def delete_playlist(playlist_id: str, user_email: str):
    coll = get_collection("playlist")
    result = coll.delete_one({"_id": ObjectId(playlist_id), "user": user_email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Playlist not found or unauthorized")
    return {"msg": "Playlist deleted"}


# Agregar canciones a una playlist
async def add_songs_to_playlist(playlist_id: str, song_ids: list[str], user_email: str):
    coll = get_collection("playlist")
    songs_coll = get_collection("songs")

    for song_id in song_ids:
        if not ObjectId.is_valid(song_id) or not songs_coll.find_one({"_id": ObjectId(song_id), "deleted": {"$ne": True}}):
            raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found or is deleted")

    result = coll.update_one(
        {"_id": ObjectId(playlist_id), "user": user_email},
        {"$addToSet": {"songs": {"$each": song_ids}}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Playlist not found or unauthorized")

    return {"msg": "Songs added"}


# Quitar canciones de una playlist
async def remove_songs_from_playlist(playlist_id: str, song_ids: list[str], user_email: str):
    coll = get_collection("playlist")
    result = coll.update_one(
        {"_id": ObjectId(playlist_id), "user": user_email},
        {"$pull": {"songs": {"$in": song_ids}}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Playlist not found or unauthorized")
    return {"msg": "Songs removed"}
