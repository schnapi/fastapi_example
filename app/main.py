from fastapi import FastAPI
from oxyde import db
from oxyde_admin import FastAPIAdmin

from oxyde_config import DATABASES
from .models import User


app = FastAPI(lifespan=db.lifespan(default=DATABASES["default"]))
admin = FastAPIAdmin(title="My Dashboard")
admin.register(User, list_display=["username", "email"], search_fields=["username"])
app.mount("/admin", admin.app)

# from oxyde.db import transaction

# async with transaction.atomic():
#     user = await User.objects.create(name="Alice", email="alice@example.com")
#     await Profile.objects.create(user_id=user.id)


@app.get("/users")
async def get_users():
    # Use Django-style queries!
    return await User.objects.all()


@app.post("/users")
async def create_user(user: User):
    return await user.save()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
