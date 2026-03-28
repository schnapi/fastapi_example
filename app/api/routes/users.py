from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# from app.services.user_service import create_user
from app.models import User
from app.utils import crud_utils

router = APIRouter()


# --- Schemas ---
class UserCreate(BaseModel):
    name: str
    email: str


@router.get("/")
async def list_users():
    return await User.objects.all()


@router.get("/{id}")
async def get_user(id: int):
    return await crud_utils.get_or_404(User, id=id)


@router.post("/", status_code=201)
async def create_user(data: UserCreate):
    return await crud_utils.create_safe(User, data=data.model_dump())


@router.patch("/{id}")
async def update_user(id: int, data: UserCreate):
    users = await crud_utils.update_safe(
        User.objects.filter(id=id), dict(name=data.name, email=data.email)
    )
    return users[0] if users else HTTPException(404, "User not found")


@router.delete("/{id}", status_code=204)
async def delete_user(id: int):
    _count = await crud_utils.delete_safe(User.objects.filter(id=id))
