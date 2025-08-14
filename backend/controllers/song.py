from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from models.song import Song, SongUpdate
from utils.mongodb import get_collection
from bson import ObjectId

# Crear canción
async def create_song(song: Song):
    try:
        song_coll = get_collection("songs")
        album_coll = get_collection("album")

        # Verificar si ya existe una canción con el mismo título y artista
        if song_coll.find_one({"title": song.title, "artist": song.artist}):
            raise HTTPException(status_code=400, detail="Song already exists")

        # Validar el ID del álbum
        if not ObjectId.is_valid(song.album):
            raise HTTPException(status_code=400, detail="Invalid album ID")

        album = album_coll.find_one({"_id": ObjectId(song.album)})
        if not album:
            raise HTTPException(status_code=404, detail="Album not found")

        # Verificar que el artista del álbum coincida con el artista de la canción
        if album["artist"] != song.artist:
            raise HTTPException(status_code=400, detail="Album artist mismatch")

        data = song.model_dump()
        result = song_coll.insert_one(data)

        # Asociar la canción al álbum
        album_coll.update_one(
            {"_id": ObjectId(song.album)},
            {"$addToSet": {"songs": str(result.inserted_id)}}
        )

        return {"msg": "Song created", "id": str(result.inserted_id)}
    except Exception:
        raise HTTPException(status_code=500, detail="Error creating the song")

# Listar todas las canciones
async def list_songs():
    try:
        coll = get_collection("songs")
        songs = list(coll.find())
        for song in songs:
            song["id"] = str(song["_id"])
            del song["_id"]
        return songs
    except Exception:
        raise HTTPException(status_code=500, detail="Error retrieving songs")

# Actualizar canción
async def patch_song(song_id: str, song: SongUpdate):
    try:
        song_coll = get_collection("songs")
        album_coll = get_collection("album")

        if not ObjectId.is_valid(song_id):
            raise HTTPException(status_code=400, detail="Invalid song ID")

        existing = song_coll.find_one({"_id": ObjectId(song_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Song not found")

        update_data = song.model_dump(exclude_unset=True)

        new_artist = update_data.get("artist", existing["artist"])
        new_album = update_data.get("album", existing.get("album"))

        # Validaciones si se cambia el álbum
        if new_album:
            if not ObjectId.is_valid(new_album):
                raise HTTPException(status_code=400, detail="Invalid album ID")
            album = album_coll.find_one({"_id": ObjectId(new_album)})
            if not album:
                raise HTTPException(status_code=404, detail="Album not found")
            if album["artist"] != new_artist:
                raise HTTPException(status_code=400, detail="Album artist mismatch")

        # Aplicar la actualización
        song_coll.update_one({"_id": ObjectId(song_id)}, {"$set": update_data})

        # Reasociar álbum si cambió
        if "album" in update_data and update_data["album"] != existing.get("album"):
            if existing.get("album"):
                album_coll.update_one({"_id": ObjectId(existing["album"])} , {"$pull": {"songs": song_id}})
            album_coll.update_one({"_id": ObjectId(update_data["album"])} , {"$addToSet": {"songs": song_id}})

        updated = {**existing, **update_data}
        return {"msg": "Song updated", "song": jsonable_encoder(updated)}
    except Exception:
        raise HTTPException(status_code=500, detail="Error updating the song")

# Eliminar canción
async def delete_song(song_id: str):
    try:
        song_coll = get_collection("songs")
        album_coll = get_collection("album")

        if not ObjectId.is_valid(song_id):
            raise HTTPException(status_code=400, detail="Invalid song ID")

        song = song_coll.find_one({"_id": ObjectId(song_id)})
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")

        result = song_coll.delete_one({"_id": ObjectId(song_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Song not found")

        if song.get("album"):
            album_coll.update_one({"_id": ObjectId(song["album"])} , {"$pull": {"songs": song_id}})

        return {"msg": "Song deleted"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error deleting the song")

# Obtener canciones por artista
async def get_songs_by_artist(artist_id: str):
    try:
        if not ObjectId.is_valid(artist_id):
            raise HTTPException(status_code=400, detail="Invalid artist ID")

        coll = get_collection("songs")
        songs = list(coll.find({"artist": artist_id}))

        for song in songs:
            song["id"] = str(song["_id"])
            del song["_id"]

        return songs
    except Exception:
        raise HTTPException(status_code=500, detail="Error retrieving songs by artist")

# Obtener canciones por álbum
async def get_songs_by_album(album_id: str):
    try:
        if not ObjectId.is_valid(album_id):
            raise HTTPException(status_code=400, detail="Invalid album ID")

        coll = get_collection("songs")
        songs = list(coll.find({"album": album_id}))

        for song in songs:
            song["id"] = str(song["_id"])
            del song["_id"]

        return songs
    except Exception:
        raise HTTPException(status_code=500, detail="Error retrieving songs by album")
