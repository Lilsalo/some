

from bson import ObjectId

def artist_with_genres_pipeline(artist_id: str):
    return [
        {"$match": {"_id": ObjectId(artist_id)}},
        {
            "$lookup": {
                "from": "genre",
                "localField": "genre_ids",
                "foreignField": "_id",
                "as": "genres"
            }
        },
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "country": 1,
                "albums": 1,
                "genres.name": 1
            }
        }
    ]
