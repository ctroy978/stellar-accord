# app/api/endpoints/tech_rules.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID

from app.db.session import get_db
from app.services.tech_rules_service import TechnologyService


router = APIRouter()

@router.get("/available/{civilization_id}")
def get_available_technologies(
    civilization_id: str = Path(..., description="Civilization identifier")
):
    """Get all technologies available to a specific civilization."""
    try:
        return TechnologyService.get_available_technologies(civilization_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving available technologies: {str(e)}")

@router.get("/requirements/{component_id}")
def get_component_requirements(
    component_id: str = Path(..., description="Technology component identifier")
):
    """Get all requirements for developing a specific technology component."""
    try:
        return TechnologyService.get_component_requirements(component_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving component requirements: {str(e)}")

@router.get("/check-prerequisites")
def check_development_prerequisites(
    civilization_id: str = Query(..., description="Civilization identifier"),
    component_id: str = Query(..., description="Technology component identifier")
):
    """Check if a civilization meets prerequisites for developing a technology."""
    try:
        result = TechnologyService.check_development_prerequisites(civilization_id, component_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking prerequisites: {str(e)}")