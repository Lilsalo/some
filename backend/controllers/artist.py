from models.artist import ArtistCreate, ArtistUpdate
from utils.mongodb import get_collection
from bson import ObjectId
from fastapi import HTTPException, Request
import traceback
from pipelines.artist_pipeline import artist_with_genres_pipeline


def convert_object_ids(doc: dict) -> dict:
    cleaned = {}
    for k, v in doc.items():
        if k == "_id":
            cleaned["id"] = str(v)
        elif isinstance(v, ObjectId):
            cleaned[k] = str(v)
        elif isinstance(v, list):
            cleaned[k] = [
                convert_object_ids(i) if isinstance(i, dict)
                else str(i) if isinstance(i, ObjectId)
                else i for i in v
            ]
        elif isinstance(v, dict):
            cleaned[k] = convert_object_ids(v)
        else:
            cleaned[k] = v
    return cleaned


# Crear artista
async def create_artist(artist: ArtistCreate, request: Request):
    try:
        user_email = request.state.user["email"]
        artist_coll = get_collection("artist")
        genre_coll = get_collection("genre")

        genre_ids = []
        for genre_id in artist.genre:
            if not ObjectId.is_valid(genre_id):
                raise HTTPException(
                    status_code=400, detail=f"Invalid genre ID '{genre_id}'"
                )
            genre_doc = genre_coll.find_one({"_id": ObjectId(genre_id)})
            if not genre_doc:
                raise HTTPException(status_code=404, detail=f"Genre '{genre_id}' not found")
            genre_ids.append(genre_doc["_id"])

        if artist_coll.find_one({"name": artist.name}):
            raise HTTPException(status_code=400, detail="El artista ya existe")

        artist_data = artist.dict()
        artist_data["genre"] = genre_ids

        result = artist_coll.insert_one(artist_data)

        return {
            "msg": f"Artista '{artist.name}' registrado exitosamente",
            "id": str(result.inserted_id)
        }

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error al registrar el artista")


# Obtener artistas con géneros
async def list_artists():
    try:
        artist_coll = get_collection("artist")
        pipeline = artist_with_genres_pipeline()
        results = list(artist_coll.aggregate(pipeline))

        for artist in results:
            artist["id"] = str(artist.pop("_id"))
            artist["albums"] = [str(aid) for aid in artist.get("albums", [])]

            raw_genres = artist.pop("genre", [])
            if isinstance(raw_genres, list):
                artist["genre_ids"] = [str(gid) for gid in raw_genres]
            elif raw_genres:
                # handle legacy data where genre was stored as a single string
                artist["genre_ids"] = [str(raw_genres)]
            else:
                artist["genre_ids"] = []

            artist.pop("genres", None)

        return results

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error retrieving artists")


# Actualizar artista
async def update_artist(artist_id: str, artist: ArtistUpdate, request: Request):
    try:
        user_email = request.state.user["email"]
        artist_coll = get_collection("artist")
        genre_coll = get_collection("genre")

        if not ObjectId.is_valid(artist_id):
            raise HTTPException(status_code=400, detail="Invalid artist ID")

        existing = artist_coll.find_one({"_id": ObjectId(artist_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Artist not found")

        update_data = artist.dict(exclude_unset=True)

        if "genre" in update_data:
            new_genre_ids = []
            for genre_id in update_data["genre"]:
                if not ObjectId.is_valid(genre_id):
                    raise HTTPException(
                        status_code=400, detail=f"Invalid genre ID '{genre_id}'"
                    )
                genre_doc = genre_coll.find_one({"_id": ObjectId(genre_id)})
                if not genre_doc:
                    raise HTTPException(status_code=404, detail=f"Genre '{genre_id}' not found")
                new_genre_ids.append(genre_doc["_id"])
            update_data["genre"] = new_genre_ids

        artist_coll.update_one({"_id": ObjectId(artist_id)}, {"$set": update_data})

        updated_artist = artist_coll.find_one({"_id": ObjectId(artist_id)})
        artist_clean = convert_object_ids(updated_artist)
        artist_clean["genre_ids"] = artist_clean.pop("genre", [])

        return {
            "msg": "Artist updated successfully",
            "artist": artist_clean,
        }

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error updating the artist")


# Listar álbumes por artista
async def list_albums_by_artist(artist_id: str):
    try:
        artist_coll = get_collection("artist")
        album_coll = get_collection("album")

        if not ObjectId.is_valid(artist_id):
            raise HTTPException(status_code=400, detail="Invalid artist ID")

        artist = artist_coll.find_one({"_id": ObjectId(artist_id)})
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")

        artist_clean = convert_object_ids(artist)
        artist_clean["genre_ids"] = artist_clean.pop("genre", [])

        albums = list(album_coll.find({"artist": artist_id}))
        cleaned_albums = [convert_object_ids(alb) for alb in albums]

        return {
            "artist": artist_clean,
            "albums": cleaned_albums
        }

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error retrieving albums by artist")


# Eliminar artista
async def delete_artist(artist_id: str, request: Request):
    try:
        user_email = request.state.user["email"]
        artist_coll = get_collection("artist")
        album_coll = get_collection("album")

        if not ObjectId.is_valid(artist_id):
            raise HTTPException(status_code=400, detail="Invalid artist ID")

        artist = artist_coll.find_one({"_id": ObjectId(artist_id)})
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")

        album_count = album_coll.count_documents({"artist": artist_id})
        if album_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete artist with associated albums")

        artist_coll.delete_one({"_id": ObjectId(artist_id)})

        return {"msg": f"Artist '{artist['name']}' deleted successfully"}

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error deleting artist")
