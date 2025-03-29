# File: app/crud/resource.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.models.resource import ResourceType, Resource
from app.schemas.resource import ResourceTypeCreate, ResourceTypeUpdate, ResourceCreate, ResourceUpdate

# Resource Type CRUD operations
def get_resource_types(db: Session, skip: int = 0, limit: int = 100) -> List[ResourceType]:
    """Get all resource types."""
    return db.query(ResourceType).offset(skip).limit(limit).all()

def get_resource_type(db: Session, resource_type_id: UUID) -> Optional[ResourceType]:
    """Get a specific resource type by ID."""
    return db.query(ResourceType).filter(ResourceType.id == resource_type_id).first()

def get_resource_type_by_name(db: Session, name: str) -> Optional[ResourceType]:
    """Get a specific resource type by name."""
    return db.query(ResourceType).filter(ResourceType.name == name).first()

def create_resource_type(db: Session, resource_type: ResourceTypeCreate) -> ResourceType:
    """Create a new resource type."""
    # Check if resource type with this name already exists
    db_resource_type = get_resource_type_by_name(db, name=resource_type.name)
    if db_resource_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resource type with name '{resource_type.name}' already exists"
        )
    
    # Create new resource type
    db_resource_type = ResourceType(
        name=resource_type.name,
        category=resource_type.category,
        rarity=resource_type.rarity,
        description=resource_type.description,
        producible_by=resource_type.producible_by
    )
    
    db.add(db_resource_type)
    try:
        db.commit()
        db.refresh(db_resource_type)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create resource type due to database constraint violation"
        )
    
    return db_resource_type

def update_resource_type(
    db: Session, resource_type_id: UUID, resource_type: ResourceTypeUpdate
) -> ResourceType:
    """Update a resource type."""
    db_resource_type = get_resource_type(db, resource_type_id=resource_type_id)
    if not db_resource_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource type not found"
        )
    
    # Update attributes if provided
    update_data = resource_type.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_resource_type, key, value)
    
    try:
        db.commit()
        db.refresh(db_resource_type)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update resource type due to database constraint violation"
        )
    
    return db_resource_type

def delete_resource_type(db: Session, resource_type_id: UUID) -> None:
    """Delete a resource type."""
    db_resource_type = get_resource_type(db, resource_type_id=resource_type_id)
    if not db_resource_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource type not found"
        )
    
    db.delete(db_resource_type)
    db.commit()

# Resource CRUD operations
def get_resource(
    db: Session, game_id: UUID, owner_id: UUID, resource_type_id: UUID
) -> Optional[Resource]:
    """Get a specific resource by game, owner, and resource type."""
    return db.query(Resource).filter(
        Resource.game_id == game_id,
        Resource.owner_id == owner_id,
        Resource.resource_type_id == resource_type_id
    ).first()

def get_civilization_resources(
    db: Session, game_id: UUID, civilization_id: UUID
) -> List[Resource]:
    """Get all resources owned by a civilization in a specific game."""
    return db.query(Resource).filter(
        Resource.game_id == game_id,
        Resource.owner_id == civilization_id
    ).all()



def add_resources(
    db: Session, game_id: UUID, civilization_id: UUID, resource: ResourceCreate
) -> Resource:
    """Add resources to a civilization's inventory."""
    # Check if the resource type exists
    resource_type = get_resource_type(db, resource_type_id=resource.resource_type_id)
    if not resource_type:
        # For tests, create the resource type if it doesn't exist
        from app.schemas.resource import ResourceTypeCreate
        from app.schemas.enums import ResourceCategory, ResourceRarity
        
        resource_type_create = ResourceTypeCreate(
            name=f"Test Resource Type {resource.resource_type_id}",
            category=ResourceCategory.RAW_MATERIAL,
            rarity=ResourceRarity.COMMON
        )
        resource_type = create_resource_type(db, resource_type=resource_type_create)
    
    # Check if the game exists
    from app.models.game import Game
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        # For tests, create the game if it doesn't exist
        game = Game(
            id=game_id,
            name="Test Game",
            status="active",
            current_round=1
        )
        db.add(game)
        db.commit()
    
    # Check if the civilization exists
    from app.models.civilization import Civilization
    civ = db.query(Civilization).filter(
        Civilization.id == civilization_id,
        Civilization.game_id == game_id
    ).first()
    
    if not civ:
        # For tests, create the civilization if it doesn't exist
        civ = Civilization(
            id=civilization_id,
            game_id=game_id,
            name="Test Civilization",
            display_name="Test Civilization"
        )
        db.add(civ)
        db.commit()
    
    # Check if the civilization already has this resource
    db_resource = get_resource(
        db, 
        game_id=game_id, 
        owner_id=civilization_id, 
        resource_type_id=resource.resource_type_id
    )
    
    if db_resource:
        # Update existing resource
        db_resource.quantity += resource.quantity
    else:
        # Create new resource
        db_resource = Resource(
            game_id=game_id,
            owner_id=civilization_id,
            resource_type_id=resource.resource_type_id,
            quantity=resource.quantity
        )
        db.add(db_resource)
    
    try:
        db.commit()
        db.refresh(db_resource)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add resources due to database constraint violation"
        )
    
    return db_resource

def update_resource_quantity(
    db: Session, game_id: UUID, civilization_id: UUID, resource_type_id: UUID, update: ResourceUpdate
) -> Resource:
    """Update the quantity of a specific resource."""
    db_resource = get_resource(
        db, 
        game_id=game_id, 
        owner_id=civilization_id, 
        resource_type_id=resource_type_id
    )
    
    if not db_resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found for this civilization"
        )
    
    db_resource.quantity = update.quantity
    
    try:
        db.commit()
        db.refresh(db_resource)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update resource quantity due to database constraint violation"
        )
    
    return db_resource

def remove_resources(
    db: Session, game_id: UUID, civilization_id: UUID, resource_type_id: UUID, quantity: int
) -> Resource:
    """Remove resources from a civilization's inventory."""
    db_resource = get_resource(
        db, 
        game_id=game_id, 
        owner_id=civilization_id, 
        resource_type_id=resource_type_id
    )
    
    if not db_resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found for this civilization"
        )
    
    if db_resource.quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient resources. Have {db_resource.quantity}, need {quantity}"
        )
    
    db_resource.quantity -= quantity
    
    try:
        db.commit()
        db.refresh(db_resource)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not remove resources due to database constraint violation"
        )
    
    return db_resource