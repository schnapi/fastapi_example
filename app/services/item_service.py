from app.models import User, Item
# from app.core.database import SessionLocal


def get_items_by_user(user_id: int):
    db = SessionLocal()
    items = db.query(Item).filter(Item.owner_id == user_id).all()
    db.close()
    return items


def create_item_for_user(user_id: int, item_data):
    db = SessionLocal()
    item = Item(**item_data.dict(), owner_id=user_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    db.close()
    return item
