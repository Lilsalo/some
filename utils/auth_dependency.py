from functools import wraps
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.security import decode_jwt_token

# Middleware de seguridad Bearer
security = HTTPBearer()

# -------------------------------------------------
# Decorador: requiere usuario autenticado (JWT válido)
# Uso: @validate_user  (y también @validate_user_decorator por compatibilidad)
# La ruta decorada debe aceptar request: Request
# -------------------------------------------------
def validate_user(route_function):
    @wraps(route_function)
    async def wrapper(*args, request: Request, **kwargs):
        credentials: HTTPAuthorizationCredentials = await security(request)
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
            )

        token = credentials.credentials
        payload = decode_jwt_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        request.state.user = payload
        return await route_function(*args, request=request, **kwargs)
    return wrapper

# Alias para compatibilidad con importaciones existentes
validate_user_decorator = validate_user

# -------------------------------------------------
# Decorador: requiere administrador (admin=True en el JWT)
# Uso: @validate_admin
# La ruta decorada debe aceptar request: Request
# -------------------------------------------------
def validate_admin(route_function):
    @wraps(route_function)
    async def wrapper(*args, request: Request, **kwargs):
        credentials: HTTPAuthorizationCredentials = await security(request)
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
            )

        token = credentials.credentials
        payload = decode_jwt_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        if payload.get("admin") is not True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Admins only",
            )

        request.state.user = payload
        return await route_function(*args, request=request, **kwargs)
    return wrapper

# -------------------------------------------------
# (Opcional) Dependencia equivalente por si alguna ruta necesita Depends()
# -------------------------------------------------
async def validate_user_dep(request: Request) -> dict:
    credentials: HTTPAuthorizationCredentials = await security(request)
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    token = credentials.credentials
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return payload
