from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Routers
from routes.artist_routes import router as artist_router
from routes.album_routes import router as album_router
from routes.song_routes import router as song_router
from routes.genre_routes import router as genre_router
from routes.playlist_routes import router as playlist_router
from routes.auth_routes import router as auth_router

# Auth decorators
from utils.auth_dependency import validate_user_decorator, validate_admin

app = FastAPI(
    title="Music API",
    description="API para la gestión de canciones, álbumes, artistas, géneros y playlists.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # restringe en producción según necesites
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(artist_router)
app.include_router(album_router)
app.include_router(song_router)
app.include_router(genre_router)
app.include_router(playlist_router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de música"}

@app.get("/health")
def health_check():
    try:
        return {
            "status": "healthy",
            "service": "music-api",
            "environment": "development",
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/ready")
def readiness_check():
    """
    Import diferido de test_connection para no romper `from main import app`
    en CI o en entornos sin variables configuradas al importar el módulo.
    """
    try:
        from utils.mongodb import test_connection  # import dentro del endpoint
        db_status = test_connection()
        return {
            "status": "ready" if db_status else "not_ready",
            "database": "connected" if db_status else "disconnected",
            "service": "music_api",
        }
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}

@app.get("/exampleuser")
@validate_user_decorator
async def example_user(request: Request):
    return {
        "message": "Este es un endpoint para usuarios autenticados.",
        "user_email": request.state.user.get("email"),
    }

@app.get("/exampleadmin")
@validate_admin
async def example_admin(request: Request):
    return {
        "message": "Este es un endpoint exclusivo para administradores.",
        "admin_email": request.state.user.get("email"),
    }

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["get", "post", "put", "patch", "delete"]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Arranque local/producción (usa $PORT si existe; 8000 por defecto)
if __name__ == "__main__":
    import os
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_level="info",
    )
