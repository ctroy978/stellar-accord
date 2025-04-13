import sys
print(sys.path)

# File Path: backend/app/main.py (TEMPORARY MINIMAL VERSION)
# Purpose: Basic FastAPI app without any config loading for testing core functionality.

import logging
import datetime
from fastapi import FastAPI

# --- Basic Logging Setup ---
# Crucial to see startup messages in Docker logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("--- Minimal main.py: Attempting to create FastAPI app instance ---")

try:
    # --- Create FastAPI App Instance ---
    app = FastAPI(
        title="Stellar Accord - Minimal Test Server",
        description="This is a temporary minimal server instance used for debugging setup issues. It does NOT load game configuration.",
        version="0.0.1"
    )
    logger.info(f"--- Minimal main.py: FastAPI app instance '{app.title}' created successfully ---")

except Exception as e:
    # If this fails, there's a problem with the FastAPI installation itself.
    logger.exception("--- Minimal main.py: !!! CRITICAL ERROR CREATING FastAPI INSTANCE !!! ---")
    raise # Stop execution if basic app creation fails

# --- Simple Diagnostic Endpoint ---
@app.get("/api/ping", tags=["Debug - Minimal"]) # Match Nginx path prefix if needed
async def simple_ping():
    """
    A basic endpoint to confirm the minimal server is running and responsive.
    """
    logger.info("--- Minimal main.py: /api/ping endpoint hit ---")
    return {
        "message": "Pong! Minimal Stellar Accord server is alive.",
        "server_time_utc": datetime.datetime.utcnow().isoformat()
    }

# --- Add another simple endpoint just to be sure ---
@app.get("/api/status", tags=["Debug - Minimal"])
async def get_status():
     logger.info("--- Minimal main.py: /api/status endpoint hit ---")
     return {"status": "Minimal server running", "title": app.title}


logger.info("--- Minimal main.py: Finished loading script (no config loaded) ---")

# --- IMPORTANT ---
# Ensure NO imports related to your configuration are present in this file
# DO NOT import: from .core.settings import settings
# DO NOT import: from .core.config_loader import ...
# --- --------- ---