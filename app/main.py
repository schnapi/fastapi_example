from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/health/")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
