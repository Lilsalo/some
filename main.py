from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar routers
from routes.artist_routes import router as artist_router
from routes.album_routes import router as album_router
from routes.song_routes import router as song_router
from routes.genre_routes import router as genre_router
from routes.playlist_routes import router as playlist_router
from routes.auth_routes import router as auth_router

app = FastAPI(
    title="Music API",
    description="API para la gestión de canciones, álbumes, artistas, géneros y playlists.",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(artist_router)
app.include_router(album_router)
app.include_router(song_router)
app.include_router(genre_router)
app.include_router(playlist_router)

# Ruta raíz
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de música"}
