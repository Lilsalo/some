def artist_with_genres_pipeline():
    return [
        {
            "$lookup": {
                "from": "genre",
                "localField": "genre",
                "foreignField": "_id",
                "as": "genres"
            }
        },
        {
            "$project": {
                "name": 1,
                "country": 1,
                "albums": 1,
                "genres.name": 1,
                "genre": 1  # opcional, si quieres conservar los ObjectId
            }
        }
    ]
