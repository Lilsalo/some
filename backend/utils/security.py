import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from jwt import PyJWTError

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
security = HTTPBearer()

# Crear token JWT
def create_jwt_token(
    firstname: str,
    lastname: str,
    email: str,
    active: bool,
    admin: bool,
    id: str
):
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode(
        {
            "id": id,
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "active": active,
            "admin": admin,
            "exp": expiration,
            "iat": datetime.utcnow()
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    return token

# 🔐 NUEVO: Función reutilizable para decodificar JWT
def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Expired token")
        return payload
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")

# Validación general para usuarios autenticados
def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_jwt_token(token)

    if payload.get("email") is None:
        raise HTTPException(status_code=401, detail="Token Invalid")
    if not payload.get("active"):
        raise HTTPException(status_code=401, detail="Inactive user")

    return {
        "id": payload["id"],
        "email": payload["email"],
        "firstname": payload["firstname"],
        "lastname": payload["lastname"],
        "active": payload["active"],
        "role": "admin" if payload.get("admin") else "user"
    }

# Validación para administradores
def validate_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_jwt_token(token)

    if payload.get("email") is None:
        raise HTTPException(status_code=401, detail="Token Invalid")
    if not payload.get("active") or not payload.get("admin"):
        raise HTTPException(status_code=401, detail="Inactive user or not admin")

    return {
        "id": payload["id"],
        "email": payload["email"],
        "firstname": payload["firstname"],
        "lastname": payload["lastname"],
        "active": payload["active"],
        "role": "admin"
    }
