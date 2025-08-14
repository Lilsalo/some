#Devuelve el artista con más álbumes (por cantidad de álbumes agrupados)

def artist_with_most_albums_pipeline():
    return [
        {
            "$group": {
                "_id": "$artist",
                "albumCount": {"$sum": 1}
            }
        },
        {
            "$sort": {"albumCount": -1}
        },
        {
            "$limit": 1
        },
        {
            "$addFields": {
                "artistObjectId": {"$toObjectId": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "artist",
                "localField": "artistObjectId",
                "foreignField": "_id",
                "as": "artist"
            }
        },
        {
            "$unwind": "$artist"
        },
        {
            "$project": {
                "_id": 0,
                "name": "$artist.name",
                "albumCount": 1
            }
        }
    ]

#Devuelve los artistas con menos álbumes (orden ascendente)

def artists_with_least_albums_pipeline(limit: int = 5):
    return [
        {
            "$group": {
                "_id": "$artist",
                "albumCount": {"$sum": 1}
            }
        },
        {
            "$sort": {"albumCount": 1}
        },
        {
            "$limit": limit
        },
        {
            "$addFields": {
                "artistObjectId": {"$toObjectId": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "artist",
                "localField": "artistObjectId",
                "foreignField": "_id",
                "as": "artist"
            }
        },
        {
            "$unwind": "$artist"
        },
        {
            "$project": {
                "_id": 0,
                "name": "$artist.name",
                "albumCount": 1
            }
        }
    ]

# Devuelve el álbum con más canciones
def album_with_most_songs_pipeline():
    return [
        {
            "$project": {
                "title": 1,
                "songCount": {
                    "$size": {"$ifNull": ["$songs", []]}
                }
            }
        },
        {
            "$sort": {"songCount": -1}
        },
        {
            "$limit": 1
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "songCount": 1
            }
        }
    ]


#Devuelve los álbumes con menos canciones
def albums_with_least_songs_pipeline():
    return [
        {
            "$project": {
                "title": 1,
                "songCount": {
                    "$size": {"$ifNull": ["$songs", []]}
                }
            }
        },
        {
            "$sort": {"songCount": 1}
        },
        {
            "$group": {
                "_id": "$songCount",
                "albums": {"$push": "$title"}
            }
        },
        {
            "$limit": 1
        },
        {
            "$project": {
                "_id": 0,
                "songCount": "$_id",
                "albums": 1
            }
        }
    ]
