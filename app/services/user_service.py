# app/services/user_service.py
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(username: str, email: str, password: str) -> User:
    password_hash = pwd_context.hash(password)

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
    )
    await user.save()
    return user


async def get_user_by_username(username: str) -> User | None:
    return await User.get_or_none(username=username)


async def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
