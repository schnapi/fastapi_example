# app/api/routes/users.py
from fastapi import APIRouter, HTTPException
from app.services.user_service import create_user
from app.models import User

router = APIRouter()


@router.post("/users")
async def register_user(payload: dict):
    """
    Using raw dict instead of schema (Oxyde handles validation).
    """
    user = await create_user(
        username=payload["username"],
        email=payload["email"],
        password=payload["password"],
    )

    # Manual serialization (since no schemas)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await User.get_or_none(id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
