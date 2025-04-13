# In backend/app/main.py or similar startup location
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Now import settings AFTER setting up logging if possible
from .core.settings import settings
from fastapi import FastAPI

app = FastAPI(title="Stellar Accord Server")

@app.on_event("startup")
async def startup_event():
    # You can access settings here, they should be loaded
    logger.info(f"Stellar Accord server starting with max rounds: {settings.game_settings.get('game',{}).get('recommended_rounds')}")
    # Add database connection pool setup here, etc.

# ... rest of your FastAPI app ...