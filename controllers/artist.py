from models.artist import Artist, ArtistUpdate
from utils.mongodb import get_collection
from bson import ObjectId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
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
            cleaned[k] = [convert_object_ids(i) if isinstance(i, dict) else str(i) if isinstance(i, ObjectId) else i for i in v]
        elif isinstance(v, dict):
            cleaned[k] = convert_object_ids(v)
        else:
            cleaned[k] = v
    return cleaned

# Crear artista
async def create_artist(artist: Artist):
    try:
        artist_coll = get_collection("artist")
        genre_coll = get_collection("genre")

        # Validar que todos los géneros existan
        for genre_id in artist.genre_ids:
            if not ObjectId.is_valid(genre_id):
                raise HTTPException(status_code=400, detail=f"ID de género inválido: {genre_id}")
            if not genre_coll.find_one({"_id": ObjectId(genre_id)}):
                raise HTTPException(status_code=404, detail=f"Género con ID '{genre_id}' no encontrado")

        # Validar que no exista un artista con el mismo nombre
        if artist_coll.find_one({"name": artist.name}):
            raise HTTPException(status_code=400, detail="El artista ya existe")

        # Convertir el artista a diccionario y agregar campo albums vacío
        artist_data = artist.dict()
        artist_data["albums"] = []

        # Insertar en la base de datos
        result = artist_coll.insert_one(artist_data)

        return {
            "msg": f"Artista '{artist.name}' registrado exitosamente",
            "id": str(result.inserted_id)
        }

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error al registrar el artista")

# Obtener artistas con géneros por lookup
async def list_artists():
    try:
        artist_coll = get_collection("artist")
        pipeline = artist_with_genres_pipeline()
        results = list(artist_coll.aggregate(pipeline))

        # Convertir ObjectId a string
        for artist in results:
            artist["_id"] = str(artist["_id"])
            artist["albums"] = [str(aid) for aid in artist.get("albums", [])]

            for genre in artist.get("genres", []):
                genre["_id"] = str(genre["_id"])

        return results

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error retrieving artists")
# Actualizar artista
async def update_artist(artist_id: str, artist: ArtistUpdate):
    try:
        artist_coll = get_collection("artist")
        genre_coll = get_collection("genre")

        if not ObjectId.is_valid(artist_id):
            raise HTTPException(status_code=400, detail="Invalid artist ID")

        existing = artist_coll.find_one({"_id": ObjectId(artist_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Artist not found")

        update_data = artist.dict(exclude_unset=True)

        if "genre_id" in update_data:
            genre_id = update_data["genre_id"]
            if not ObjectId.is_valid(genre_id):
                raise HTTPException(status_code=400, detail="Invalid genre ID format")
            genre_exists = genre_coll.find_one({"_id": ObjectId(genre_id)})
            if not genre_exists:
                raise HTTPException(status_code=404, detail=f"Genre with ID '{genre_id}' not found")

        artist_coll.update_one({"_id": ObjectId(artist_id)}, {"$set": update_data})

        updated_artist = artist_coll.find_one({"_id": ObjectId(artist_id)})

        return {
            "msg": "Artist updated successfully",
            "artist": convert_object_ids(updated_artist)
        }

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error updating the artist")

# Listar álbumes por artista
async def list_albums_by_artist(artist_id: str):
    try:
        album_coll = get_collection("album")
        artist_coll = get_collection("artist")
        genre_coll = get_collection("genre")

        if not ObjectId.is_valid(artist_id):
            raise HTTPException(status_code=400, detail="Invalid artist ID")

        artist = artist_coll.find_one({"_id": ObjectId(artist_id)})
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")

        artist_clean = convert_object_ids(artist)

        genre = genre_coll.find_one({"_id": ObjectId(artist["genre_id"])}) if "genre_id" in artist else None
        artist_clean["genre"] = genre["name"] if genre else "Unknown"
        artist_clean.pop("genre_id", None)

        albums = list(album_coll.find({"artist": artist_id}))
        cleaned_albums = []
        for alb in albums:
            alb_clean = convert_object_ids(alb)
            alb_clean.pop("artist", None)
            cleaned_albums.append(alb_clean)

        return {
            "artist": artist_clean,
            "albums": cleaned_albums
        }

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error retrieving albums")


# Eliminar artista con validación de álbumes asociados
async def delete_artist(artist_id: str):
    artist_coll = get_collection("artist")
    album_coll = get_collection("album")

    if not ObjectId.is_valid(artist_id):
        raise HTTPException(status_code=400, detail="Invalid artist ID")

    artist = artist_coll.find_one({"_id": ObjectId(artist_id)})
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    album_count = album_coll.count_documents({"artist": artist_id})
    if album_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete artist with associated albums"
        )

    artist_coll.delete_one({"_id": ObjectId(artist_id)})

    return {"msg": f"Artist '{artist['name']}' deleted successfully"}