# file: app/api/endpoints/technology.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from uuid import UUID

from app.db.session import get_db
from app.schemas.technology import (
    BigTechComponent, UberTechComponent, UniversalProject,
    TechRequirement, ProjectDevelopment, ProjectDevelopmentCreate,
    TechnologyOwnership, ProjectComponentAssignment, ProjectComponentAssignmentCreate
)
from app.crud import technology as crud_technology

router = APIRouter()

# Technology template endpoints
@router.get("/big-tech/{big_tech_id}", response_model=BigTechComponent)
def get_big_tech_component(big_tech_id: UUID, db: Session = Depends(get_db)):
    """Get a specific Big Tech component template."""
    component = crud_technology.get_big_tech_component(db, big_tech_id=big_tech_id)
    if not component:
        raise HTTPException(status_code=404, detail="Big Tech component not found")
    return component

@router.get("/uber-tech/{uber_tech_id}", response_model=UberTechComponent)
def get_uber_tech_component(uber_tech_id: UUID, db: Session = Depends(get_db)):
    """Get a specific Uber-Tech component template."""
    component = crud_technology.get_uber_tech_component(db, uber_tech_id=uber_tech_id)
    if not component:
        raise HTTPException(status_code=404, detail="Uber-Tech component not found")
    return component

@router.get("/universal-projects/{project_id}", response_model=UniversalProject)
def get_universal_project(project_id: UUID, db: Session = Depends(get_db)):
    """Get a specific Universal Project template."""
    project = crud_technology.get_universal_project(db, universal_project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Universal Project not found")
    return project

# Technology ownership endpoints
@router.get("/games/{game_id}/civilizations/{civilization_id}/inventory", response_model=List[TechnologyOwnership])
def get_civilization_inventory(
    game_id: UUID,
    civilization_id: UUID,
    technology_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all technology components owned by a civilization."""
    return crud_technology.get_available_components(
        db, game_id=game_id, civilization_id=civilization_id, component_type=technology_type
    )

@router.post("/games/{game_id}/civilizations/{civilization_id}/projects", response_model=ProjectDevelopment)
def start_project(
    game_id: UUID,
    civilization_id: UUID,
    project: ProjectDevelopmentCreate,
    db: Session = Depends(get_db)
):
    """Start a new project development."""
    # Ensure the project is associated with the correct game and civilization
    project.game_id = game_id
    project.civilization_id = civilization_id
    return crud_technology.start_project(db, project=project)

@router.get("/games/{game_id}/civilizations/{civilization_id}/projects", response_model=List[ProjectDevelopment])
def get_civilization_projects(
    game_id: UUID,
    civilization_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all projects being developed by a civilization."""
    return crud_technology.get_civilization_projects(
        db, game_id=game_id, civilization_id=civilization_id
    )

@router.get("/projects/{project_id}", response_model=ProjectDevelopment)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific project development."""
    project = crud_technology.get_project_development(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# Component assignment endpoints
@router.post("/games/{game_id}/projects/{project_id}/assignments", response_model=ProjectComponentAssignment)
def assign_component(
    game_id: UUID,
    project_id: UUID,
    assignment: ProjectComponentAssignmentCreate,
    db: Session = Depends(get_db)
):
    """Assign a component to a project."""
    # Ensure the assignment is associated with the correct game and project
    assignment.game_id = game_id
    assignment.project_id = project_id
    return crud_technology.assign_component_to_project(db, assignment=assignment)

@router.delete("/assignments/{assignment_id}", response_model=Dict)
def unassign_component(
    assignment_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove a component assignment from a project."""
    return crud_technology.unassign_component(db, assignment_id=assignment_id)

# Assembly endpoints
@router.post("/games/{game_id}/civilizations/{civilization_id}/big-tech/{big_tech_id}/assemble", response_model=Dict)
def assemble_big_tech_component(
    game_id: UUID,
    civilization_id: UUID,
    big_tech_id: UUID,
    db: Session = Depends(get_db)
):
    """Assemble a Big Tech component from resources."""
    return crud_technology.assemble_big_tech(
        db, game_id=game_id, civilization_id=civilization_id, big_tech_id=big_tech_id
    )

@router.post("/games/{game_id}/projects/{project_id}/assemble", response_model=Dict)
def assemble_project(
    game_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Finalize project assembly, consuming all assigned components."""
    return crud_technology.assemble_project(
        db, game_id=game_id, project_id=project_id
    )

# Counterfeit handling
@router.delete("/games/{game_id}/civilizations/{civilization_id}/counterfeit/{batch_id}", response_model=Dict)
def destroy_counterfeit(
    game_id: UUID,
    civilization_id: UUID,
    batch_id: str,
    db: Session = Depends(get_db)
):
    """Destroy a counterfeit resource batch."""
    return crud_technology.destroy_counterfeit_resource(
        db, game_id=game_id, civilization_id=civilization_id, batch_id=batch_id
    )