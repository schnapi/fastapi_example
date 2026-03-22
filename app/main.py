from fastapi import FastAPI
from oxyde import db
from oxyde_admin import FastAPIAdmin

from app.models import User
from app.config import settings

# Enable debugpy in development
if settings.debug:
    from app.debugger import enable_debugpy

    enable_debugpy()


app = FastAPI(lifespan=db.lifespan(default=settings.database_url))
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
