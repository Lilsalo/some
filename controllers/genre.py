from fastapi import HTTPException
from bson import ObjectId
from utils.mongodb import get_collection
from models.genre import Genre, UpdateGenre, GenreResponse

# Colección MongoDB
collection = get_collection("genre")


#  Obtener todos los géneros
async def get_all_genres():
    try:
        genres = []
        for genre in collection.find():
            genres.append({
                "id": str(genre["_id"]),
                "name": genre["name"]
            })
        return genres
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving genres: {e}")


#  Obtener un género por ID
async def get_genre_by_id(genre_id: str):
    if not ObjectId.is_valid(genre_id):
        raise HTTPException(status_code=400, detail="Invalid genre ID")

    genre = collection.find_one({"_id": ObjectId(genre_id)})
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    return {"id": str(genre["_id"]), "name": genre["name"]}


#  Crear un nuevo género
async def create_genre(data: Genre):
    if collection.find_one({"name": data.name}):
        raise HTTPException(status_code=400, detail="Genre already exists")

    result = collection.insert_one(data.dict())
    return {
        "msg": "Genre registered successfully",
        "id": str(result.inserted_id)
    }


#  Actualizar un género por ID
async def update_genre(genre_id: str, data: UpdateGenre):
    if not ObjectId.is_valid(genre_id):
        raise HTTPException(status_code=400, detail="Invalid genre ID")

    update_data = data.dict(exclude_unset=True)
    result = collection.update_one({"_id": ObjectId(genre_id)}, {"$set": update_data})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Genre not found or no changes made")

    return {"msg": "Genre updated successfully"}

#  Eliminar un género por ID
async def delete_genre(genre_id: str):
    if not ObjectId.is_valid(genre_id):
        raise HTTPException(status_code=400, detail="Invalid genre ID")

    result = collection.delete_one({"_id": ObjectId(genre_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Genre not found")

    return {"msg": "Genre deleted successfully"}
