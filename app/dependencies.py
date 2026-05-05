"""Database dependency for FastAPI routes (pre-Annotated style)."""
from fastapi import Depends


def get_db():
    """Yield a fake DB connection. Real impl would use SQLAlchemy."""
    db = {"connected": True, "queries": 0}
    try:
        yield db
    finally:
        db["connected"] = False
