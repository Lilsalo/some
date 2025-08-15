from fastapi import HTTPException, Request
from bson import ObjectId
from utils.mongodb import get_collection
from models.genre import Genre, UpdateGenre
from datetime import datetime
import re

# Colecciones MongoDB
genre_coll = get_collection("genre")
song_coll = get_collection("song")
album_coll = get_collection("album")
artist_coll = get_collection("artist")

def _normalize_name(name: str) -> str:
    return (name or "").strip()

def _now():
    return datetime.utcnow()

def _to_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name"),
        "active": doc.get("active", True),
    }

# Obtener todos los géneros (público)
async def get_all_genres(include_inactive: bool = False):
    try:
        query = {} if include_inactive else {"active": True}
        genres = []
        for g in genre_coll.find(query).sort("name", 1):
            genres.append(_to_out(g))
        return genres
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving genres")

# Obtener un género por ID (público)
async def get_genre_by_id(genre_id: str):
    if not ObjectId.is_valid(genre_id):
        raise HTTPException(status_code=400, detail="Invalid genre ID")

    g = genre_coll.find_one({"_id": ObjectId(genre_id)})
    if not g:
        raise HTTPException(status_code=404, detail="Genre not found")
    return _to_out(g)

# Crear un nuevo género (requiere autenticación)
async def create_genre(data: Genre, request: Request):
    name = _normalize_name(data.name)
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    # Duplicado case-insensitive (usa name_lc o regex como respaldo)
    name_lc = name.lower()
    dup = genre_coll.find_one({
        "$or": [
            {"name_lc": name_lc},
            {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
        ]
    })
    if dup:
        raise HTTPException(status_code=409, detail="Genre already exists")

    doc = {
        "name": name,
        "name_lc": name_lc,
        "active": True,
        "created_at": _now(),
        "updated_at": _now(),
    }
    result = genre_coll.insert_one(doc)
    return {
        "msg": "Genre registered successfully",
        "id": str(result.inserted_id)
    }

# Actualizar un género por ID (requiere autenticación)
async def update_genre(genre_id: str, data: UpdateGenre, request: Request):
    if not ObjectId.is_valid(genre_id):
        raise HTTPException(status_code=400, detail="Invalid genre ID")

    update_data = data.dict(exclude_unset=True)

    # si viene name, normaliza y valida duplicado
    if "name" in update_data and update_data["name"] is not None:
        name = _normalize_name(update_data["name"])
        if not name:
            raise HTTPException(status_code=400, detail="Name cannot be empty")
        name_lc = name.lower()

        dup = genre_coll.find_one({
            "$or": [
                {"name_lc": name_lc},
                {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
            ],
            "_id": {"$ne": ObjectId(genre_id)}
        })
        if dup:
            raise HTTPException(status_code=409, detail="Genre with that name already exists")

        update_data["name"] = name
        update_data["name_lc"] = name_lc

    if not update_data:
        raise HTTPException(status_code=400, detail="Nothing to update")

    update_data["updated_at"] = _now()

    res = genre_coll.update_one({"_id": ObjectId(genre_id)}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Genre not found")

    return {"msg": "Genre updated successfully"}

# Eliminar un género por ID (requiere autenticación) – ELIMINACIÓN RESTRINGIDA
async def delete_genre(genre_id: str, request: Request):
    if not ObjectId.is_valid(genre_id):
        raise HTTPException(status_code=400, detail="Invalid genre ID")

    _id = ObjectId(genre_id)
    g = genre_coll.find_one({"_id": _id})
    if not g:
        raise HTTPException(status_code=404, detail="Genre not found")

    # Verificar uso por artistas; se consideran posibles campos "genre" o "genre_ids"
    in_use_by_artist = artist_coll.find_one(
        {"$or": [{"genre": _id}, {"genre_ids": _id}]},
        projection={"_id": 1},
    )

    # (Opcional) si también usas genre en songs/albums, puedes activar estos:
    # in_use_by_song = song_coll.find_one({"$or": [{"genre": _id}, {"genre_id": _id}]}, {"_id": 1})
    # in_use_by_album = album_coll.find_one({"$or": [{"genre": _id}, {"genre_id": _id}]}, {"_id": 1})

    if in_use_by_artist:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete genre: it is assigned to one or more artists."
        )

    # Eliminación definitiva
    genre_coll.delete_one({"_id": _id})
    return {"msg": "Genre deleted"}
