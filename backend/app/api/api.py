# Update app/api/api.py to include the new routers
from fastapi import APIRouter
from app.api.endpoints import resources, games, civilizations, trades, technology, tech_rules


api_router = APIRouter()

api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(civilizations.router, prefix="/civilizations", tags=["civilizations"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(technology.router, prefix="/technology", tags=["technology"])
api_router.include_router(tech_rules.router, prefix="/tech-rules", tags=["tech-rules"])
