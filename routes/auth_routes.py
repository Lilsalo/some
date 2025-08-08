from fastapi import APIRouter, Depends
from models.users import User, UserLogin
from controllers.users import create_user, login_user
from utils.auth_dependency import validate_user  # <- usa tu dependencia de auth

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(user: User):
    return await create_user(user)

@router.post("/login")
async def login(user: UserLogin):
    return await login_user(user)

# NUEVO: quién soy
@router.get("/me")
async def me(current_user: dict = Depends(validate_user)):
    """
    Devuelve los datos del usuario autenticado a partir del token.
    """
    return {"user": current_user}
