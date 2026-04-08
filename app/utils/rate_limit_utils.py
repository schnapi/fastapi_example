# from slowapi.util import get_remote_address
from fastapi import Request
from jose import jwt


def user_key(request: Request):
    """
    Returns a unique identifier for rate limiting:
    - User ID if authenticated (JWT in Authorization header)
    - Fallback to client IP if unauthenticated
    """
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            token_type, token = auth_header.split()
            if token_type.lower() != "bearer":
                return request.client.host  # fallback
            payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"  # prefix to avoid collisions with IPs
        except Exception:
            pass  # fallback to IP
    return real_ip(request)


def api_key_key(request: Request):
    return request.headers.get("X-API-Key", "anonymous")


def real_ip(request: Request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host
