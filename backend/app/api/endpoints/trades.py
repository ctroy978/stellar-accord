# File: app/api/endpoints/trades.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict
from uuid import UUID

from app.db.session import get_db
from app.schemas.resource import ResourceTransfer, ResourceTransferCreate
from app.schemas.enums import CivilizationName, HubName
from app.crud import trade as crud_trade
from app.services.trade_service import TradeService

router = APIRouter()

@router.post("/", response_model=ResourceTransfer, status_code=status.HTTP_201_CREATED)
def create_trade(
    trade: ResourceTransferCreate,
    db: Session = Depends(get_db)
):
    """Create a new resource trade between civilizations."""
    return crud_trade.create_trade(db=db, trade=trade)

@router.get("/game/{game_id}", response_model=List[ResourceTransfer])
def get_trades_by_game(
    game_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all trades for a specific game."""
    return crud_trade.get_trades_by_game(db=db, game_id=game_id)

@router.get("/{trade_id}", response_model=ResourceTransfer)
def get_trade(
    trade_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific trade by ID."""
    trade = crud_trade.get_trade(db=db, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    return trade

@router.post("/{trade_id}/execute", response_model=ResourceTransfer)
def execute_trade(
    trade_id: UUID,
    db: Session = Depends(get_db)
):
    """Execute a pending trade, transferring resources between civilizations."""
    return crud_trade.execute_trade(db=db, trade_id=trade_id)

@router.post("/{trade_id}/cancel")
def cancel_trade(
    trade_id: UUID,
    db: Session = Depends(get_db)
):
    """Cancel a pending trade."""
    crud_trade.cancel_trade(db=db, trade_id=trade_id)
    return {"message": "Trade cancelled successfully"}

# New endpoints that use the trade service

@router.get("/delivery-cost/{system_id}/{hub_id}")
def get_delivery_cost(
    system_id: str,
    hub_id: str
):
    """Get the delivery cost between a system and a hub."""
    try:
        cost = TradeService.calculate_delivery_cost(system_id, hub_id)
        return {
            "system_id": system_id,
            "hub_id": hub_id,
            "cost_percentage": cost
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating delivery cost: {str(e)}"
        )

@router.get("/hub-distances")
def get_hub_distances():
    """Get the hub distance table for all civilizations."""
    try:
        distances = TradeService.get_hub_distance_table()
        return distances
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting hub distances: {str(e)}"
        )

@router.get("/route")
def calculate_trade_route(
    sender: str = Query(..., description="Sender civilization name"),
    receiver: str = Query(..., description="Receiver civilization name")
):
    """Calculate the optimal trade route between two civilizations."""
    try:
        route = TradeService.calculate_trade_route(sender, receiver)
        if not route["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=route["error"]
            )
        return route
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating trade route: {str(e)}"
        )

@router.get("/can-trade")
def can_civilizations_trade(
    civ1: str = Query(..., description="First civilization name"),
    civ2: str = Query(..., description="Second civilization name")
):
    """Check if two civilizations can trade directly."""
    try:
        can_trade = TradeService.can_civilizations_trade(civ1, civ2)
        return {
            "civ1": civ1,
            "civ2": civ2,
            "can_trade": can_trade
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking trade capability: {str(e)}"
        )