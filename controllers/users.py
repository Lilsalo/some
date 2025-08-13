import os
import json
import logging
import base64
import requests
import traceback

from fastapi import HTTPException
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from firebase_admin._auth_utils import EmailAlreadyExistsError, UserNotFoundError

from models.users import User, UserLogin
from utils.mongodb import get_collection
from utils.security import create_jwt_token

# Cargar .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Firebase si no está activo
def initialize_firebase():
    if firebase_admin._apps:
        return

    try:
        firebase_creds_base64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")

        if firebase_creds_base64:
            firebase_creds_json = base64.b64decode(firebase_creds_base64).decode('utf-8')
            firebase_creds = json.loads(firebase_creds_json)
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado desde variable de entorno")
        else:
            cred = credentials.Certificate("secrets/firebase-secret.json")
            firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado desde archivo local")

    except Exception as e:
        logger.error(f"Error al inicializar Firebase: {e}")
        raise HTTPException(status_code=500, detail=f"Error de configuración de Firebase: {str(e)}")

initialize_firebase()

# Crear usuario
async def create_user(user: User) -> dict:
    try:
        logger.info(f"Intentando registrar usuario: {user.email}")

        firebase_user = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )
        logger.info(f"Usuario creado en Firebase con UID: {firebase_user.uid}")

        # Guardar en MongoDB
        coll = get_collection("users")
        user_data = user.dict()
        user_data["firebase_uid"] = firebase_user.uid
        user_data["playlists"] = []
        del user_data["password"]

        result = coll.insert_one(user_data)
        logger.info(f"Usuario guardado en MongoDB con ID: {result.inserted_id}")

        return {
            "msg": "Usuario creado exitosamente",
            "user_id": str(result.inserted_id),
        }

    except EmailAlreadyExistsError:
        logger.warning("Correo ya registrado en Firebase.")
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    except Exception as e:
        logger.error("Error al registrar usuario en MongoDB:")
        traceback.print_exc()
        # Rollback en Firebase si falla MongoDB
        try:
            if 'firebase_user' in locals():
                firebase_auth.delete_user(firebase_user.uid)
        except:
            logger.warning("No se pudo revertir el usuario en Firebase.")
        raise HTTPException(status_code=500, detail="Error interno al registrar usuario")

# Login de usuario
async def login_user(user: UserLogin) -> dict:
    try:
        logger.info(f"Intentando login: {user.email}")

        # Validar login con Firebase REST API
        firebase_api_key = os.getenv("FIREBASE_API_KEY")
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}"

        payload = {
            "email": user.email,
            "password": user.password,
            "returnSecureToken": True
        }

        response = requests.post(url, json=payload)
        response_data = response.json()

        if "error" in response_data:
            logger.warning(f"Error en login de Firebase: {response_data['error']['message']}")
            raise HTTPException(status_code=401, detail="Correo o contraseña inválidos")

        # Buscar usuario en MongoDB
        coll = get_collection("users")
        user_data = coll.find_one({"email": user.email})

        if not user_data:
            logger.error("Usuario no encontrado en la base de datos.")
            raise HTTPException(status_code=404, detail="Usuario no encontrado en la base de datos")

        token_data = {
            "id": str(user_data["_id"]),
            "email": user_data["email"],
            "firstname": user_data.get("firstname", ""),
            "lastname": user_data.get("lastname", ""),
            "active": user_data.get("active", True),
            "admin": user_data.get("admin", False),
        }

        token = create_jwt_token(**token_data)
        logger.info("Login exitoso. Token generado.")
        return {"access_token": token}

    except UserNotFoundError:
        logger.warning("Usuario no encontrado en Firebase.")
        raise HTTPException(status_code=401, detail="Correo o contraseña inválidos")

    except Exception as e:
        logger.error("Error interno durante login:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error interno durante login")
