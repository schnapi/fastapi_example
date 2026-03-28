from oxyde import Model, Field


class User(Model):
    id: int | None = Field(default=None, db_pk=True)
    username: str
    email: str

    class Meta:
        is_table = True  # Tells Oxyde to treat this as a DB table


class Item(Model):
    id: int | None = Field(default=None, db_pk=True)
    title: str
    description: str | None = None
    owner_id: int

    class Meta:
        is_table = True  # Tells Oxyde to treat this as a DB table
