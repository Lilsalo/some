import os
import json
import logging
import base64
import requests
import traceback
from typing import Dict

from fastapi import HTTPException
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from firebase_admin._auth_utils import (
    EmailAlreadyExistsError,
    UserNotFoundError,
    ConfigurationNotFoundError,
)

from google.auth.exceptions import RefreshError  # para errores OAuth del Admin SDK

from models.users import User, UserLogin
from utils.mongodb import get_collection
from utils.security import create_jwt_token

# -----------------------------
# Config & Logging
# -----------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FIREBASE_PROJECT_ID = None  # para diagnóstico
BYPASS = os.getenv("AUTH_BYPASS_FIREBASE", "").lower() == "true"  # ← bypass opcional


# -----------------------------
# Helpers
# -----------------------------
def _get_firebase_api_key() -> str:
    """
    Obtiene la Web API Key de Firebase desde env.
    Soporta FIREBASE_API_KEY o FIREBASE_WEB_API_KEY.
    """
    key = os.getenv("FIREBASE_API_KEY") or os.getenv("FIREBASE_WEB_API_KEY")
    if not key:
        raise HTTPException(
            status_code=500,
            detail="FIREBASE_API_KEY/FIREBASE_WEB_API_KEY no configurada en el servidor.",
        )
    # Log útil para diagnóstico (sin exponer la key)
    try:
        logger.info("FIREBASE_API_KEY length: %d%s",
                    len(key), "" if key.startswith("AIza") else " (no inicia con 'AIza')")
    except Exception:
        pass
    return key


def _firebase_login_via_rest(email: str, password: str) -> Dict:
    """
    Realiza el login contra Firebase Identity REST.
    Devuelve el JSON de éxito de Firebase si status=200.
    Lanza HTTPException según el código de error de Firebase.
    """
    api_key = _get_firebase_api_key()
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}

    resp = requests.post(url, json=payload, timeout=12)

    # intenta decodificar JSON
    try:
        data = resp.json()
    except Exception:
        body_preview = (resp.text or "")[:300]
        logger.error("Firebase devolvió contenido no-JSON. status=%s body=%s", resp.status_code, body_preview)
        raise HTTPException(status_code=500, detail="Error al autenticar con Firebase")

    if resp.status_code == 200:
        return data

    # Mapeo de errores comunes de Firebase
    code = (data.get("error", {}).get("message") or "").upper()
    logger.warning("Firebase login error: %s (status=%s)", code, resp.status_code)

    if code in {"EMAIL_NOT_FOUND", "INVALID_PASSWORD", "USER_DISABLED"}:
        raise HTTPException(status_code=401, detail="Correo o contraseña inválidos")
    if code in {"INVALID_API_KEY", "PROJECT_NOT_FOUND"}:
        raise HTTPException(status_code=500, detail="API key inválida o proyecto incorrecto")
    if code in {"OPERATION_NOT_ALLOWED"}:
        raise HTTPException(status_code=500, detail="Método de inicio de sesión no habilitado en Firebase")

    raise HTTPException(status_code=500, detail="Error al autenticar con Firebase")


# -----------------------------
# Firebase Admin init
# -----------------------------
def initialize_firebase():
    """
    Inicializa Firebase Admin una sola vez.
    Usa FIREBASE_CREDENTIALS_BASE64 o secrets/firebase-secret.json.
    Deja rastro del project_id y client_email en logs.
    """
    global FIREBASE_PROJECT_ID

    if firebase_admin._apps:
        logger.info("Firebase ya estaba inicializado, se omite.")
        return

    try:
        b64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")
        if b64:
            creds_json = base64.b64decode(b64).decode("utf-8")
            creds = json.loads(creds_json)
            FIREBASE_PROJECT_ID = creds.get("project_id")
            logger.info(
                "Credenciales Firebase via ENV. project_id=%s, client_email=%s",
                FIREBASE_PROJECT_ID,
                creds.get("client_email"),
            )
            cred = credentials.Certificate(creds)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado desde variable de entorno")
            return

        # Fallback a archivo local
        local_path = "secrets/firebase-secret.json"
        if not os.path.exists(local_path):
            raise RuntimeError("No hay FIREBASE_CREDENTIALS_BASE64 ni secrets/firebase-secret.json")

        with open(local_path, "r", encoding="utf-8") as f:
            creds = json.load(f)

        FIREBASE_PROJECT_ID = creds.get("project_id")
        logger.info(
            "Credenciales Firebase via archivo. project_id=%s, client_email=%s",
            FIREBASE_PROJECT_ID,
            creds.get("client_email"),
        )
        cred = credentials.Certificate(creds)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase inicializado desde archivo local")

    except Exception as e:
        logger.error("Error al inicializar Firebase: %s", e)
        raise HTTPException(status_code=500, detail=f"Error de configuración de Firebase: {str(e)}")


# Ejecuta init al importar el módulo
initialize_firebase()


# -----------------------------
# Casos de uso
# -----------------------------
async def create_user(user: User) -> dict:
    """
    Crea usuario en Firebase y lo registra en MongoDB.
    Hace rollback en Firebase si falla Mongo.
    """
    try:
        logger.info("Intentando registrar usuario: %s (project_id=%s)", user.email, FIREBASE_PROJECT_ID)

        # Firebase Admin: crea usuario
        firebase_user = firebase_auth.create_user(email=user.email, password=user.password)
        logger.info("Usuario creado en Firebase con UID: %s", firebase_user.uid)

        # MongoDB: guarda documento
        coll = get_collection("users")
        user_data = user.dict()

        # normalización de nombres (name → firstname si viene así del front)
        user_data["firstname"] = user_data.get("firstname") or user_data.get("name", "")
        user_data["lastname"] = user_data.get("lastname", "")

        user_data["firebase_uid"] = firebase_user.uid
        user_data["playlists"] = []
        user_data.pop("password", None)  # nunca guardes contraseñas

        result = coll.insert_one(user_data)
        logger.info("Usuario guardado en MongoDB con ID: %s", result.inserted_id)

        return {"msg": "Usuario creado exitosamente", "user_id": str(result.inserted_id)}

    except EmailAlreadyExistsError:
        logger.warning("Correo ya registrado en Firebase.")
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    except ConfigurationNotFoundError as e:
        # típico: Email/Password no habilitado
        logger.error("CONFIGURATION_NOT_FOUND en project_id=%s: %s", FIREBASE_PROJECT_ID, e)
        raise HTTPException(
            status_code=500,
            detail=(
                "Proveedor de autenticación no configurado en Firebase. "
                "Ve a Firebase Console → Authentication → Sign-in method y habilita Email/Password "
                f"para el proyecto '{FIREBASE_PROJECT_ID}'."
            ),
        )

    except RefreshError as e:
        # problemas con la clave del service account (firma, caducidad, proyecto)
        logger.error("Firebase OAuth RefreshError: %r", e)
        raise HTTPException(status_code=500, detail="Credenciales de Firebase inválidas o corruptas")

    except Exception:
        logger.error("Error al registrar usuario:\n%s", traceback.format_exc())

        # rollback en Firebase si falla MongoDB
        if "firebase_user" in locals():
            try:
                firebase_auth.delete_user(firebase_user.uid)
                logger.info("Usuario revertido en Firebase por fallo en MongoDB.")
            except Exception:
                logger.warning("No se pudo revertir el usuario en Firebase.")

        raise HTTPException(status_code=500, detail="Error interno al registrar usuario")


async def login_user(user: UserLogin) -> dict:
    """
    Login: valida credenciales con Firebase REST, luego genera JWT con datos de Mongo.
    Si AUTH_BYPASS_FIREBASE=true, se omite la validación REST (solo para demo).
    """
    try:
        logger.info("Intentando login: %s (project_id=%s)", user.email, FIREBASE_PROJECT_ID)

        # ---- BYPASS TEMPORAL (solo demo) ----
        if BYPASS:
            coll = get_collection("users")
            user_data = coll.find_one({"email": user.email})
            if not user_data:
                raise HTTPException(status_code=404, detail="Usuario no encontrado en la base de datos")
            token_data = {
                "id": str(user_data["_id"]),
                "email": user_data["email"],
                "firstname": user_data.get("firstname") or user_data.get("name", ""),
                "lastname": user_data.get("lastname", ""),
                "active": user_data.get("active", True),
                "admin": user_data.get("admin", False),
            }
            token = create_jwt_token(**token_data)
            logger.warning("AUTH_BYPASS_FIREBASE activo: emitiendo JWT sin validar contraseña (solo demo).")
            return {"access_token": token}
        # -------------------------------------

        # 1) Firebase REST (valida credenciales)
        _ = _firebase_login_via_rest(user.email, user.password)  # si falla, lanza HTTPException

        # 2) Busca usuario en Mongo
        coll = get_collection("users")
        user_data = coll.find_one({"email": user.email})
        if not user_data:
            logger.error("Usuario no encontrado en la base de datos.")
            raise HTTPException(status_code=404, detail="Usuario no encontrado en la base de datos")

        # 3) Genera tu JWT de aplicación
        token_data = {
            "id": str(user_data["_id"]),
            "email": user_data["email"],
            "firstname": user_data.get("firstname") or user_data.get("name", ""),
            "lastname": user_data.get("lastname", ""),
            "active": user_data.get("active", True),
            "admin": user_data.get("admin", False),
        }
        token = create_jwt_token(**token_data)
        logger.info("Login exitoso. Token generado.")

        return {"access_token": token}

    except UserNotFoundError:
        # (poco probable aquí porque validamos por REST)
        logger.warning("Usuario no encontrado en Firebase.")
        raise HTTPException(status_code=401, detail="Correo o contraseña inválidos")

    except HTTPException:
        # ya mapeado arriba
        raise

    except Exception:
        logger.error("Error interno durante login:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error interno durante login")
