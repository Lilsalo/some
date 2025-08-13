from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from utils.mongodb import test_connection


# Importar routers principales del proyecto
from routes.artist_routes import router as artist_router
from routes.album_routes import router as album_router
from routes.song_routes import router as song_router
from routes.genre_routes import router as genre_router
from routes.playlist_routes import router as playlist_router
from routes.auth_routes import router as auth_router

# Importar decoradores de autenticación
from utils.auth_dependency import validate_user_decorator, validate_admin

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="Music API",
    description="API para la gestión de canciones, álbumes, artistas, géneros y playlists.",
    version="1.0.0"
)

# Configuración de CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes (útil en desarrollo)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)

# Incluir todos los routers definidos en el proyecto
app.include_router(auth_router)
app.include_router(artist_router)
app.include_router(album_router)
app.include_router(song_router)
app.include_router(genre_router)
app.include_router(playlist_router)

# Ruta raíz que responde con un mensaje de bienvenida
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de música"}

# Endpoint para verificar estado general del servicio
@app.get("/health")
def health_check():
    try:
        return {
            "status": "healthy",
            "service": "music-api",
            "environment": "development"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Endpoint para verificar si la base de datos está conectada correctamente
@app.get("/ready")
def readiness_check():
    try:
        db_status = test_connection()
        return {
            "status": "ready" if db_status else "not_ready",
            "database": "connected" if db_status else "disconnected",
            "service": "music_api"
        }
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}
    
# Endpoint de ejemplo que requiere autenticación de usuario (token válido)
@app.get("/exampleuser")
@validate_user_decorator
async def example_user(request: Request):
    return {
        "message": "Este es un endpoint para usuarios autenticados.",
        "user_email": request.state.user.get("email")
    }

# Endpoint de ejemplo que requiere permisos de administrador
@app.get("/exampleadmin")
@validate_admin
async def example_admin(request: Request):
    return {
        "message": "Este es un endpoint exclusivo para administradores.",
        "admin_email": request.state.user.get("email")
    }

# Personalización del esquema OpenAPI para mostrar el botón "Authorize" en Swagger
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
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["get", "post", "put", "patch", "delete"]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Reemplaza el generador de documentación por el personalizado
app.openapi = custom_openapi
