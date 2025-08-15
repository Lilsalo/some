def artist_with_genres_pipeline():
    return [
        {
            "$project": {
                "name": 1,
                "country": 1,
                "albums": 1,
                "genre": 1,
            }
        }
    ]
