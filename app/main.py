"""FastAPI application entry point."""
from fastapi import FastAPI

from app.routers import alarms
from app.routers.items import router as items_router

app = FastAPI(lifespan=alarms.lifespan)
app.include_router(items_router)
app.include_router(alarms.router)
