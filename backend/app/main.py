from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Stellar Accord API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Stellar Accord API is running"}

@app.get("/api/game-info")
async def game_info():
    return {
        "name": "Stellar Accord",
        "description": "Interstellar Diplomacy Simulation Game",
        "civilizations": [
            "The Thrizoth (Arborealis Nexus)",
            "The Methane Collective", 
            "The Silicon Liberation",
            "The Glacian Current",
            "The Kyrathi (Crystalline Convergence)",
            "The Vasku (Voidborn Nomads)"
        ]
    }
