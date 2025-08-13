from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps
from utils.security import decode_jwt_token

# Middleware de seguridad Bearer
security = HTTPBearer()

# --------------------------
# ✅ DECORADOR para proteger rutas con JWT
# --------------------------
def validate_user_decorator(route_function):
    @wraps(route_function)
    async def wrapper(*args, request: Request, **kwargs):
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        payload = decode_jwt_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        request.state.user = payload
        return await route_function(*args, request=request, **kwargs)
    return wrapper

# --------------------------
# ✅ DEPENDENCIA para usar con Depends(validate_user)
# --------------------------
async def validate_user(request: Request) -> dict:
    credentials: HTTPAuthorizationCredentials = await security(request)
    token = credentials.credentials
    payload = decode_jwt_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


# ✅ DECORADOR solo para administradores
# --------------------------
def validate_admin(route_function):
    @wraps(route_function)
    async def wrapper(*args, request: Request, **kwargs):
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        payload = decode_jwt_token(token)

        if not payload or payload.get("admin") is not True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Admins only"
            )

        request.state.user = payload
        return await route_function(*args, request=request, **kwargs)
    return wrapper
