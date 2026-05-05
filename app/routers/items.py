"""Items router."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_db

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/{item_id}")
def read_item(item_id: int, db: Annotated[dict, Depends(get_db)]):
    db["queries"] += 1
    return {"item_id": item_id, "db_queries": db["queries"]}
