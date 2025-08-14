from fastapi import APIRouter, Depends
from models.users import User, UserLogin
from controllers.users import create_user, login_user
from utils.auth_dependency import validate_user

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# Registro de usuario
@router.post("/register", summary="Registrar nuevo usuario")
async def register(user: User):
    return await create_user(user)

# Login de usuario
@router.post("/login", summary="Autenticar usuario")
async def login(user: UserLogin):
    return await login_user(user)

# Obtener información del usuario autenticado (requiere token)
@router.get("/me", summary="Obtener usuario actual")
async def get_current_user(current_user: dict = Depends(validate_user)):
    """
    Devuelve los datos del usuario autenticado a partir del token JWT.
    """
    return {"user": current_user}
