# app/services/auth_service.py
from app.services.user_service import get_user_by_username, verify_password
from datetime import datetime, timedelta
from jose import jwt


SECRET_KEY = "supersecret"
ALGORITHM = "HS256"


async def authenticate_user(username: str, password: str):
    user = await get_user_by_username(username)
    if not user:
        return None
    if not await verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict, expires_minutes: int = 60):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
