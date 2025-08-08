from bson import ObjectId

# Validación compleja: Verifica que las canciones existen y no están eliminadas
def validate_songs_pipeline(song_ids: list):
    return [
        {
            "$match": {
                "_id": {"$in": [ObjectId(song_id) for song_id in song_ids]},
                "deleted": {"$ne": True}
            }
        },
        {
            "$project": {
                "_id": 1
            }
        }
    ]
