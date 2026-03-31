from typing import Union
from fastapi import HTTPException
from oxyde.models import Model
from oxyde.exceptions import (
    IntegrityError,
    ManagerError,
    FieldError,
    FieldLookupError,
    NotFoundError,
)
from oxyde.queries.manager import QueryManager


def get_model_name(target):
    if isinstance(target, Model):
        return target.__class__.__name__
    elif hasattr(target, "_model") and hasattr(target._model, "__name__"):
        return target._model.__name__
    else:
        return "UnknownModel"


async def create_safe(model_class, data: dict):
    """
    Generic create helper for Oxyde ORM.
    Raises 409 Conflict if unique constraint violated.
    """
    try:
        return await model_class.objects.create(**data)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail=f"{model_class.__name__} already exists"
        )
    except (FieldError, FieldLookupError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ManagerError as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_or_404(model_class, **filters):
    """
    Generic get helper.
    Raises 404 Not Found if object does not exist.
    """
    try:
        return await model_class.objects.get(**filters)
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"{model_class.__name__} not found")


async def update_safe(target: Union[Model, QueryManager], data: dict):
    """
    Generic update helper for Oxyde ORM.
    Handles validation and unique constraint conflicts.
    Works with single instances or QuerySets.
    """
    model_name = get_model_name(target)
    try:
        if isinstance(target, QueryManager):
            return await target.update(**data, returning=True)
        # Single instance update
        else:
            for key, value in data.items():
                setattr(target, key, value)
            await target.save()
            return target

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=f"{model_name} update conflicts with existing data",
        )
    except (FieldError, FieldLookupError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ManagerError as e:
        raise HTTPException(
            status_code=500, detail=f"Database error during update: {str(e)}"
        )


async def delete_safe(target: Union[Model, QueryManager]):
    """
    Generic delete helper for Oxyde ORM.
    Handles database errors.
    """
    model_name = get_model_name(target)
    try:
        if hasattr(target, "update") and callable(getattr(target, "update")):
            return await target.delete()
        else:
            await target.delete()
    except ManagerError as e:
        raise HTTPException(status_code=500, detail=str(e))
