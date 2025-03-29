# File: app/crud/trade.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.models.resource import ResourceTransfer, Resource, ResourceType
from app.schemas.resource import ResourceTransferCreate, ResourceCreate
from app.crud import resource as crud_resource


def get_trade(db: Session, trade_id: UUID) -> Optional[ResourceTransfer]:
    """Get a specific trade by ID."""
    return db.query(ResourceTransfer).filter(ResourceTransfer.id == trade_id).options(
        joinedload(ResourceTransfer.resource_type)
    ).first()

def get_trades_by_game(db: Session, game_id: UUID) -> List[ResourceTransfer]:
    """Get all trades for a specific game."""
    return db.query(ResourceTransfer).filter(ResourceTransfer.game_id == game_id).options(
        joinedload(ResourceTransfer.resource_type)
    ).all()

def create_trade(db: Session, trade: ResourceTransferCreate) -> ResourceTransfer:
    """Create a new trade."""
    # Verify the sender has enough resources
    sender_resource = crud_resource.get_resource(
        db, 
        game_id=trade.game_id, 
        owner_id=trade.sender_id, 
        resource_type_id=trade.resource_type_id
    )
    
    if not sender_resource or sender_resource.quantity < trade.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sender does not have enough resources"
        )
    
    # Calculate delivery cost (this would be based on hub and distance)
    # For simplicity, using a fixed percentage
    delivery_cost_percentage = 10
    
    # Create the trade
    db_trade = ResourceTransfer(
        game_id=trade.game_id,
        resource_type_id=trade.resource_type_id,
        quantity=trade.quantity,
        sender_id=trade.sender_id,
        receiver_id=trade.receiver_id,
        hub_id=trade.hub_id,
        delivery_cost_percentage=delivery_cost_percentage,
        round_initiated=1,  # This should come from the game state
        status="pending"
    )
    
    db.add(db_trade)
    
    try:
        db.commit()
        db.refresh(db_trade)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create trade due to database constraint violation"
        )
    
    # Explicitly fetch the trade with relationships loaded
    return db.query(ResourceTransfer).options(
        joinedload(ResourceTransfer.resource_type)
    ).filter(ResourceTransfer.id == db_trade.id).first()

def execute_trade(db: Session, trade_id: UUID) -> ResourceTransfer:
    """Execute a trade, transferring resources from sender to receiver."""
    db_trade = get_trade(db, trade_id=trade_id)
    
    if not db_trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    
    if db_trade.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trade is already {db_trade.status}"
        )
    
    # Verify sender still has enough resources
    sender_resource = crud_resource.get_resource(
        db, 
        game_id=db_trade.game_id, 
        owner_id=db_trade.sender_id, 
        resource_type_id=db_trade.resource_type_id
    )
    
    if not sender_resource or sender_resource.quantity < db_trade.quantity:
        db_trade.status = "failed"
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sender no longer has enough resources"
        )
    
    # Calculate actual delivery amount after costs
    delivery_amount = int(db_trade.quantity * (100 - db_trade.delivery_cost_percentage) / 100)
    
    # Remove resources from sender
    crud_resource.remove_resources(
        db, 
        game_id=db_trade.game_id, 
        civilization_id=db_trade.sender_id, 
        resource_type_id=db_trade.resource_type_id, 
        quantity=db_trade.quantity
    )
    
    # Add resources to receiver
    crud_resource.add_resources(
        db, 
        game_id=db_trade.game_id, 
        civilization_id=db_trade.receiver_id, 
        resource=ResourceCreate(
            resource_type_id=db_trade.resource_type_id,
            quantity=delivery_amount
        )
    )
    
    # Mark trade as completed
    db_trade.status = "completed"
    
    try:
        db.commit()
        db.refresh(db_trade)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not execute trade due to database constraint violation"
        )
    
    # Explicitly fetch the trade with relationships loaded
    return db.query(ResourceTransfer).options(
        joinedload(ResourceTransfer.resource_type)
    ).filter(ResourceTransfer.id == db_trade.id).first()

def cancel_trade(db: Session, trade_id: UUID) -> None:
    """Cancel a trade."""
    db_trade = get_trade(db, trade_id=trade_id)
    
    if not db_trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    
    if db_trade.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel trade with status {db_trade.status}"
        )
    
    db_trade.status = "cancelled"
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not cancel trade due to database constraint violation"
        )