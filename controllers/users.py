import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin._auth_utils import EmailAlreadyExistsError, UserNotFoundError
from firebase_admin import credentials  # Necesario para cargar el JSON

# ✅ Inicializar Firebase si aún no está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate("secrets/firebase-secret.json")  # Asegúrate de tener este archivo
    firebase_admin.initialize_app(cred)

from fastapi import HTTPException
from models.users import User, UserLogin
from utils.mongodb import get_collection
from utils.security import create_jwt_token
from decouple import config
import requests
import traceback

# Crear usuario nuevo
async def create_user(user: User) -> dict:
    try:
        print("Intentando registrar usuario:", user.email)

        # Crear usuario en Firebase
        firebase_user = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )
        print("Usuario creado en Firebase:", firebase_user.uid)

        # Guardar usuario en MongoDB
        coll = get_collection("users")
        user_data = user.dict()
        user_data["firebase_uid"] = firebase_user.uid
        user_data["playlists"] = []
        del user_data["password"]

        result = coll.insert_one(user_data)
        print("Usuario guardado en MongoDB con ID:", result.inserted_id)

        return {
            "msg": "Usuario creado exitosamente",
            "user_id": str(result.inserted_id),
        }

    except EmailAlreadyExistsError:
        print("El correo ya está registrado en Firebase.")
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    except Exception as e:
        print("Error al registrar usuario:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error interno al registrar usuario")

# Login
async def login_user(user: UserLogin) -> dict:
    try:
        print("Intentando login:", user.email)

        # Obtener usuario desde Firebase
        firebase_user = firebase_auth.get_user_by_email(user.email)

        # Validar contraseña vía Firebase REST API
        FIREBASE_API_KEY = config("FIREBASE_API_KEY")
        signin_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {
            "email": user.email,
            "password": user.password,
            "returnSecureToken": True
        }

        response = requests.post(signin_url, json=payload)
        if response.status_code != 200:
            print(" Error al validar contraseña con Firebase:", response.json())
            raise HTTPException(status_code=401, detail="Correo o contraseña inválidos")

        # Buscar en MongoDB
        coll = get_collection("users")
        user_data = coll.find_one({"email": user.email})
        if not user_data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en la base de datos")

        token_data = {
       "id": str(user_data["_id"]),
       "email": user_data["email"],
       "firstname": user_data.get("firstname", ""),
       "lastname": user_data.get("lastname", ""),
       "active": user_data.get("active", True),
       "admin": user_data.get("admin", False)
}


        token = create_jwt_token(**token_data)
        print("Login exitoso. Token generado.")
        return {"access_token": token}

    except UserNotFoundError:
        print("Usuario no encontrado en Firebase.")
        raise HTTPException(status_code=401, detail="Correo o contraseña inválidos")
    except Exception as e:
        print("Error durante login:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error interno durante login")
