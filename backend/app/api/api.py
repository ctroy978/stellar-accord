# File: app/api/api.py
from fastapi import APIRouter
from app.api.endpoints import resources

api_router = APIRouter()

api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
# We'll add more routers here as we develop other features