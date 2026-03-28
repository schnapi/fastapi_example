from fastapi import APIRouter
from pydantic import BaseModel

from app.services.item_service import get_items_by_user, create_item_for_user
from app.models import Item


class ItemOut(Item):
    pass
    # class Config:
    #     fields = {"password_hash": {"exclude": True}}


class ItemCreate(BaseModel):
    title: str
    description: str | None = None


router = APIRouter()


@router.get("/users/{user_id}/items", response_model=list[ItemOut])
def read_user_items(user_id: int):
    return get_items_by_user(user_id)


@router.post("/users/{user_id}/items", response_model=ItemOut)
def create_user_item(user_id: int, item: ItemCreate):
    return create_item_for_user(user_id, item)
