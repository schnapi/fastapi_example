# app/api/routes/auth.py
from fastapi import APIRouter, HTTPException
from app.services.auth_service import authenticate_user, create_access_token

router = APIRouter()


@router.post("/auth/login")
async def login(payload: dict):
    user = await authenticate_user(
        username=payload["username"],
        password=payload["password"],
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
    }
