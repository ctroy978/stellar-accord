# File: app/main.py
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.db.init_db import init_db

app = FastAPI(
    title="Stellar Accord API",
    description="API for the Stellar Accord interstellar diplomacy simulation game",
    version="0.1.0",
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to Stellar Accord API"}

@app.on_event("startup")
def startup_event():
    # Initialize the database tables
    init_db()