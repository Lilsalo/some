from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class User(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Correo electrónico válido")
    password: str = Field(..., min_length=8, max_length=64, description="Contraseña segura")
    admin: Optional[bool] = Field(default=False, description="Indica si es administrador")
    active: Optional[bool] = Field(default=True, description="Estado activo del usuario")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Correo del usuario")
    password: str = Field(..., description="Contraseña del usuario")
