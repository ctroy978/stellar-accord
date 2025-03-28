# File: app/api/endpoints/resources.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.schemas.resource import (
    ResourceType, ResourceTypeCreate, ResourceTypeUpdate,
    Resource, ResourceCreate, ResourceUpdate
)
from app.crud import resource as crud_resource

router = APIRouter()

# Resource Type endpoints
@router.get("/types/", response_model=List[ResourceType])
def get_resource_types(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Retrieve all resource types.
    """
    return crud_resource.get_resource_types(db, skip=skip, limit=limit)

@router.post("/types/", response_model=ResourceType, status_code=status.HTTP_201_CREATED)
def create_resource_type(
    resource_type: ResourceTypeCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new resource type.
    """
    return crud_resource.create_resource_type(db, resource_type=resource_type)

@router.get("/types/{resource_type_id}", response_model=ResourceType)
def get_resource_type(
    resource_type_id: UUID, 
    db: Session = Depends(get_db)
):
    """
    Get a specific resource type by ID.
    """
    db_resource_type = crud_resource.get_resource_type(db, resource_type_id=resource_type_id)
    if db_resource_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Resource type not found"
        )
    return db_resource_type

@router.put("/types/{resource_type_id}", response_model=ResourceType)
def update_resource_type(
    resource_type_id: UUID,
    resource_type: ResourceTypeUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a resource type.
    """
    return crud_resource.update_resource_type(db, resource_type_id=resource_type_id, resource_type=resource_type)

@router.delete("/types/{resource_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource_type(
    resource_type_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a resource type.
    """
    crud_resource.delete_resource_type(db, resource_type_id=resource_type_id)
    return None

# Resource endpoints
@router.get("/game/{game_id}/civilization/{civilization_id}", response_model=List[Resource])
def get_civilization_resources(
    game_id: UUID, 
    civilization_id: UUID, 
    db: Session = Depends(get_db)
):
    """
    Get all resources owned by a civilization in a specific game.
    """
    return crud_resource.get_civilization_resources(
        db, game_id=game_id, civilization_id=civilization_id
    )

@router.post("/game/{game_id}/civilization/{civilization_id}", response_model=Resource)
def add_resources(
    game_id: UUID,
    civilization_id: UUID,
    resource: ResourceCreate,
    db: Session = Depends(get_db)
):
    """
    Add resources to a civilization's inventory.
    """
    return crud_resource.add_resources(
        db, game_id=game_id, civilization_id=civilization_id, resource=resource
    )

@router.put("/game/{game_id}/civilization/{civilization_id}/resource/{resource_type_id}", response_model=Resource)
def update_resource_quantity(
    game_id: UUID,
    civilization_id: UUID,
    resource_type_id: UUID,
    update: ResourceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the quantity of a specific resource.
    """
    return crud_resource.update_resource_quantity(
        db, 
        game_id=game_id, 
        civilization_id=civilization_id, 
        resource_type_id=resource_type_id, 
        update=update
    )

@router.delete("/game/{game_id}/civilization/{civilization_id}/resource/{resource_type_id}", status_code=status.HTTP_200_OK)
def remove_resources(
    game_id: UUID,
    civilization_id: UUID,
    resource_type_id: UUID,
    quantity: int,
    db: Session = Depends(get_db)
):
    """
    Remove a specified quantity of resources from a civilization's inventory.
    """
    return crud_resource.remove_resources(
        db,
        game_id=game_id,
        civilization_id=civilization_id,
        resource_type_id=resource_type_id,
        quantity=quantity
    )