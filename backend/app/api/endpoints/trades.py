# File: app/api/endpoints/trades.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.resource import ResourceTransfer, ResourceTransferCreate
from app.crud import trade as crud_trade

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