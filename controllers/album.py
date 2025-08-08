from fastapi.encoders import jsonable_encoder
from models.album import Album, AlbumUpdate
from utils.mongodb import get_collection
from bson import ObjectId
from fastapi import HTTPException, Request
from pipelines.album_pipeline import (
    artist_with_most_albums_pipeline,
    artists_with_least_albums_pipeline,
    album_with_most_songs_pipeline,
    albums_with_least_songs_pipeline
)

# POST /albums - Crear un nuevo álbum
def create_album(album: Album, request: Request): 
    try:
        # Opcional: obtener el email del usuario autenticado
        user_email = request.state.user_email

        album_coll = get_collection("album")
        artist_coll = get_collection("artist")
        genre_coll = get_collection("genre")
        song_coll = get_collection("songs")

        if not ObjectId.is_valid(album.artist):
            raise HTTPException(status_code=400, detail="Invalid artist ID")

        artist = artist_coll.find_one({"_id": ObjectId(album.artist)})
        if not artist:
            raise HTTPException(status_code=404, detail=f"Artist with ID '{album.artist}' not found")

        if not genre_coll.find_one({"name": album.genre}):
            raise HTTPException(status_code=404, detail=f"Genre '{album.genre}' not found")

        if album.songs:
            for song_id in album.songs:
                if not ObjectId.is_valid(song_id):
                    raise HTTPException(status_code=400, detail="Invalid song ID")
                song_doc = song_coll.find_one({"_id": ObjectId(song_id)})
                if not song_doc:
                    raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found")
                if song_doc.get("artist") != album.artist:
                    raise HTTPException(status_code=400, detail="Song artist mismatch")

        if album_coll.find_one({"title": album.title, "artist": album.artist}):
            raise HTTPException(status_code=400, detail="Album already exists")

        data = album.model_dump()
        result = album_coll.insert_one(data)

        artist_coll.update_one(
            {"_id": ObjectId(album.artist)},
            {"$addToSet": {"albums": str(result.inserted_id)}}
        )

        if album.songs:
            for song_id in album.songs:
                song_coll.update_one(
                    {"_id": ObjectId(song_id)},
                    {"$set": {"album": str(result.inserted_id)}}
                )

        return {"msg": "Album created", "id": str(result.inserted_id)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error creating the album")


# GET /albums - Listar todos los álbumes
def list_albums():
    try:
        coll = get_collection("album")
        albums = list(coll.find())
        for alb in albums:
            alb["id"] = str(alb["_id"])
            del alb["_id"]
        return albums
    except Exception:
        raise HTTPException(status_code=500, detail="Error retrieving albums")


# PATCH /albums/{album_id} - Actualizar álbum por ID
def patch_album(album_id: str, album: AlbumUpdate):
    try:
        coll = get_collection("album")
        artist_coll = get_collection("artist")
        genre_coll = get_collection("genre")
        song_coll = get_collection("songs")

        if not ObjectId.is_valid(album_id):
            raise HTTPException(status_code=400, detail="Invalid album ID")

        existing = coll.find_one({"_id": ObjectId(album_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Album not found")

        update_data = album.model_dump(exclude_unset=True)

        if "artist" in update_data:
            if not ObjectId.is_valid(update_data["artist"]):
                raise HTTPException(status_code=400, detail="Invalid artist ID")
            new_artist = artist_coll.find_one({"_id": ObjectId(update_data["artist"])})
            if not new_artist:
                raise HTTPException(status_code=404, detail=f"Artist with ID '{update_data['artist']}' not found")

        if "genre" in update_data and not genre_coll.find_one({"name": update_data["genre"]}):
            raise HTTPException(status_code=404, detail=f"Genre '{update_data['genre']}' not found")

        if "songs" in update_data:
            for song_id in update_data["songs"]:
                if not ObjectId.is_valid(song_id):
                    raise HTTPException(status_code=400, detail="Invalid song ID")
                song_doc = song_coll.find_one({"_id": ObjectId(song_id)})
                if not song_doc:
                    raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found")
                if song_doc.get("artist") != update_data.get("artist", existing["artist"]):
                    raise HTTPException(status_code=400, detail="Song artist mismatch")

        coll.update_one({"_id": ObjectId(album_id)}, {"$set": update_data})

        if "songs" in update_data:
            old_songs = set(existing.get("songs", []))
            new_songs = set(update_data["songs"])
            removed = old_songs - new_songs
            added = new_songs - old_songs

            for sid in removed:
                song_coll.update_one({"_id": ObjectId(sid)}, {"$unset": {"album": ""}})
            for sid in added:
                song_coll.update_one({"_id": ObjectId(sid)}, {"$set": {"album": album_id}})

        if "artist" in update_data and update_data["artist"] != existing.get("artist"):
            artist_coll.update_one({"_id": ObjectId(existing["artist"])} ,{"$pull": {"albums": album_id}})
            artist_coll.update_one({"_id": ObjectId(update_data["artist"])} ,{"$addToSet": {"albums": album_id}})

        updated = {**existing, **update_data}
        return {"msg": "Album updated", "album": jsonable_encoder(updated)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error updating the album")


# DELETE /albums/{album_id} - Eliminar álbum por ID
def delete_album(album_id: str):
    try:
        coll = get_collection("album")
        artist_coll = get_collection("artist")
        song_coll = get_collection("songs")

        if not ObjectId.is_valid(album_id):
            raise HTTPException(status_code=400, detail="Invalid album ID")

        album = coll.find_one({"_id": ObjectId(album_id)})
        if not album:
            raise HTTPException(status_code=404, detail="Album not found")

        result = coll.delete_one({"_id": ObjectId(album_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Album not found")

        if album.get("songs"):
            for sid in album["songs"]:
                song_coll.update_one({"_id": ObjectId(sid)}, {"$unset": {"album": ""}})

        artist_coll.update_one(
            {"_id": ObjectId(album["artist"])},
            {"$pull": {"albums": album_id}}
        )

        return {"msg": "Album deleted"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error deleting the album")


# GET /albums/statistics/most-songs - Álbum con más canciones
async def album_with_most_songs():
    try:
        coll = get_collection("album")
        pipeline = album_with_most_songs_pipeline()
        result = list(coll.aggregate(pipeline))
        return result[0] if result else {}
    except Exception:
        raise HTTPException(status_code=500, detail="Error retrieving statistics")


# GET /albums/statistics/least-songs - Álbumes con menos canciones
async def albums_with_least_songs():
    try:
        coll = get_collection("album")
        pipeline = albums_with_least_songs_pipeline()
        result = list(coll.aggregate(pipeline))
        return result[0] if result else {}
    except Exception:
        raise HTTPException(status_code=500, detail="Error retrieving statistics")


# GET /albums/statistics/top - Artista con más álbumes
async def get_album_statistics():
    try:
        album_coll = get_collection("album")
        pipeline = artist_with_most_albums_pipeline()
        result = list(album_coll.aggregate(pipeline))
        return result[0] if result else {}
    except Exception:
        raise HTTPException(status_code=500, detail="Error retrieving statistics")


# GET /albums/statistics/least - Artistas con menos álbumes
async def get_artists_with_least_albums():
    try:
        album_coll = get_collection("album")
        pipeline = artists_with_least_albums_pipeline(limit=5)
        results = list(album_coll.aggregate(pipeline))
        return results
    except Exception:
        raise HTTPException(status_code=500, detail="Error retrieving statistics")
