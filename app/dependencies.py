"""Database dependency for FastAPI routes."""


def get_db():
    """Yield a fake DB connection. Real impl would use SQLAlchemy."""
    db = {"connected": True, "queries": 0}
    try:
        yield db
    finally:
        db["connected"] = False
