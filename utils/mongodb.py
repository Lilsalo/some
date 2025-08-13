import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Cargar variables de entorno desde .env
load_dotenv()

# Intentar obtener las variables con distintos nombres por compatibilidad
DB_NAME = os.getenv("DB_NAME") or os.getenv("DATABASE_NAME") or os.getenv("MONGO_DB_NAME")
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("URI")

# Validación de variables requeridas
if not DB_NAME:
    raise ValueError("No se encontró el nombre de la base de datos. Usa DB_NAME o DATABASE_NAME.")
if not MONGODB_URI:
    raise ValueError("No se encontró la URI de MongoDB. Usa MONGODB_URI o URI.")

# Cliente Mongo global reutilizable
_client = None

def get_mongo_client():
    """
    Retorna una instancia de MongoClient global.
    """
    global _client
    if _client is None:
        _client = MongoClient(
            MONGODB_URI,
            server_api=ServerApi("1"),
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000  # Timeout más corto para pruebas
        )
    return _client

def get_collection(name: str):
    """
    Retorna una colección de MongoDB por nombre.
    """
    client = get_mongo_client()
    return client[DB_NAME][name]

def test_connection() -> bool:
    """
    Verifica si la conexión a MongoDB funciona correctamente.
    Usado en el endpoint /ready.
    """
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        return True
    except Exception as e:
        print(f"Error conectando a MongoDB: {e}")
        return False
