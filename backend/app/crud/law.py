# File: app/crud/law.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.models.law import LawProposal, EnactedLaw
from app.models.game import Game

def create_law_proposal(db: Session, proposal_data: Dict[str, Any]) -> LawProposal:
    """Create a new law proposal."""
    # Get the current round from the game
    game = db.query(Game).filter(Game.id == proposal_data["game_id"]).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    db_proposal = LawProposal(
        game_id=proposal_data["game_id"],
        template_id=proposal_data["template_id"],
        template_name=proposal_data["template_name"],
        parameters=proposal_data["parameters"],
        category=proposal_data.get("category"),
        law_text=proposal_data["law_text"],
        effects=proposal_data["effects"],
        proposing_civilization=proposal_data["proposing_civilization"],
        round_number=game.current_round,
        votes=proposal_data.get("votes", [])
    )
    
    db.add(db_proposal)
    
    try:
        db.commit()
        db.refresh(db_proposal)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create law proposal"
        )
    
    return db_proposal

def get_law_proposal(db: Session, proposal_id: UUID) -> Optional[LawProposal]:
    """Get a specific law proposal by ID."""
    return db.query(LawProposal).filter(LawProposal.id == proposal_id).first()

def get_law_proposals(db: Session, game_id: UUID, round_number: Optional[int] = None) -> List[LawProposal]:
    """Get all law proposals for a specific game, optionally filtered by round."""
    query = db.query(LawProposal).filter(LawProposal.game_id == game_id)
    
    if round_number is not None:
        query = query.filter(LawProposal.round_number == round_number)
    
    return query.all()

def get_votes_by_game(db: Session, game_id: UUID) -> Dict[str, List[str]]:
    """Get current votes for all proposals in a game."""
    proposals = get_law_proposals(db, game_id=game_id)
    
    votes = {}
    for proposal in proposals:
        votes[str(proposal.id)] = proposal.votes
    
    return votes

def update_votes(db: Session, game_id: UUID, votes: Dict[str, List[str]]) -> None:
    """Update votes for proposals in a game."""
    for proposal_id, proposal_votes in votes.items():
        try:
            proposal_uuid = UUID(proposal_id)
            proposal = get_law_proposal(db, proposal_id=proposal_uuid)
            if proposal and proposal.game_id == game_id:
                proposal.votes = proposal_votes
        except ValueError:
            # Invalid UUID, skip
            continue
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update votes"
        )

def enact_law(db: Session, proposal_id: UUID, round_number: int) -> EnactedLaw:
    """Enact a law from a proposal."""
    proposal = get_law_proposal(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Create the enacted law
    db_law = EnactedLaw(
        game_id=proposal.game_id,
        proposal_id=proposal.id,
        law_text=proposal.law_text,
        template_id=proposal.template_id,
        parameters=proposal.parameters,
        category=proposal.category,
        effects=proposal.effects,
        enacted_round=round_number,
        duration=3,  # Default to 3 rounds
        is_active=True
    )
    
    db.add(db_law)
    
    try:
        db.commit()
        db.refresh(db_law)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not enact law"
        )
    
    return db_law

def get_active_laws(db: Session, game_id: UUID) -> List[EnactedLaw]:
    """Get all active laws for a specific game."""
    return db.query(EnactedLaw).filter(
        EnactedLaw.game_id == game_id,
        EnactedLaw.is_active == True
    ).all()

def void_law(db: Session, law_id: UUID, voided_by: Optional[UUID] = None) -> None:
    """Void an active law."""
    law = db.query(EnactedLaw).filter(EnactedLaw.id == law_id).first()
    if law:
        law.is_active = False
        law.voided_by = voided_by
        
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not void law"
            )

def expire_law(db: Session, law_id: UUID) -> None:
    """Expire a law that has reached its duration."""
    law = db.query(EnactedLaw).filter(EnactedLaw.id == law_id).first()
    if law:
        law.is_active = False
        
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not expire law"
            )