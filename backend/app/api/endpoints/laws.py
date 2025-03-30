# File: app/api/endpoints/laws.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.db.session import get_db
from app.schemas.law import (
    LawTemplateInfo, 
    LawTemplateDetails, 
    LawProposalCreate, 
    LawProposal,
    LawVote,
    EnactedLaw
)
from app.services.law_system_service import LawSystemService
from app.crud import law as crud_law

router = APIRouter()

@router.get("/templates/", response_model=List[LawTemplateInfo])
def get_law_templates(
    category: Optional[str] = Query(None, description="Filter templates by category")
):
    """
    Get available law templates, optionally filtered by category.
    """
    templates = LawSystemService.get_available_templates(category)
    return templates

@router.get("/templates/{template_id}", response_model=LawTemplateDetails)
def get_law_template_details(
    template_id: str = Path(..., description="ID of the template")
):
    """
    Get detailed information about a specific law template.
    """
    details = LawSystemService.get_template_details(template_id)
    if "error" in details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=details["error"]
        )
    return details

@router.post("/proposals/", response_model=LawProposal, status_code=status.HTTP_201_CREATED)
def create_law_proposal(
    proposal: LawProposalCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new law proposal.
    """
    # First use the service to validate and create the proposal
    result = LawSystemService.create_law_proposal(
        proposal.template_id,
        proposal.parameters,
        proposal.proposing_civilization
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("errors", ["Invalid proposal"])
        )
    
    # Save the proposal to the database
    db_proposal = crud_law.create_law_proposal(db, result["proposal"])
    
    return db_proposal

@router.get("/proposals/", response_model=List[LawProposal])
def get_law_proposals(
    game_id: UUID = Query(..., description="Game ID"),
    round_number: Optional[int] = Query(None, description="Round number"),
    db: Session = Depends(get_db)
):
    """
    Get all law proposals for a specific game, optionally filtered by round.
    """
    proposals = crud_law.get_law_proposals(
        db, game_id=game_id, round_number=round_number
    )
    return proposals

@router.get("/proposals/{proposal_id}", response_model=LawProposal)
def get_law_proposal(
    proposal_id: UUID = Path(..., description="Proposal ID"),
    db: Session = Depends(get_db)
):
    """
    Get a specific law proposal by ID.
    """
    proposal = crud_law.get_law_proposal(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    return proposal

@router.post("/votes/", status_code=status.HTTP_200_OK)
def vote_on_law(
    vote: LawVote,
    db: Session = Depends(get_db)
):
    """
    Record a civilization's vote on a law proposal.
    """
    # Get current votes for all proposals in this game
    current_votes = crud_law.get_votes_by_game(db, game_id=vote.game_id)
    
    # Use the service to validate and record the vote
    result = LawSystemService.vote_on_law(
        str(vote.proposal_id),
        vote.voting_civilization,
        vote.vote,
        current_votes
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Vote failed")
        )
    
    # Update votes in the database
    crud_law.update_votes(db, game_id=vote.game_id, votes=result["updated_votes"])
    
    return {"message": "Vote recorded successfully"}

@router.post("/resolve/{game_id}/{round_number}", response_model=Dict[str, Any])
def resolve_law_votes(
    game_id: UUID = Path(..., description="Game ID"),
    round_number: int = Path(..., description="Round number"),
    db: Session = Depends(get_db)
):
    """
    Resolve votes for law proposals in a specific game and round.
    """
    # Get all proposals for this game and round
    proposals = crud_law.get_law_proposals(db, game_id=game_id, round_number=round_number)
    
    if not proposals:
        return {"message": "No proposals to resolve"}
    
    # Get current votes
    current_votes = crud_law.get_votes_by_game(db, game_id=game_id)
    
    # Use the service to resolve votes
    result = LawSystemService.resolve_law_votes(proposals, current_votes)
    
    if not result["success"]:
        # If tie with no tiebreaker, return the tied proposals
        if "tied_proposals" in result:
            return {
                "resolution": "tie",
                "tied_proposals": result["tied_proposals"],
                "message": "Tied vote with no tiebreaker rule"
            }
        else:
            return {
                "resolution": "failed",
                "message": result.get("error", "Failed to resolve votes")
            }
    
    # Enact the winning law
    winning_proposal = result["winning_proposal"]
    
    # Get existing laws to check for conflicts
    active_laws = crud_law.get_active_laws(db, game_id=game_id)
    
    # Check for conflicts
    conflicts = LawSystemService.check_law_conflicts(winning_proposal, active_laws)
    
    # Void conflicting laws
    for conflict in conflicts:
        crud_law.void_law(db, law_id=conflict["id"])
    
    # Enact the new law
    enacted_law = crud_law.enact_law(db, proposal_id=winning_proposal["id"], round_number=round_number)
    
    return {
        "resolution": "success",
        "enacted_law": enacted_law,
        "conflicts_voided": len(conflicts),
        "vote_counts": result["vote_counts"],
        "tie_occurred": result["tie_occurred"]
    }

@router.get("/active/{game_id}", response_model=List[EnactedLaw])
def get_active_laws(
    game_id: UUID = Path(..., description="Game ID"),
    db: Session = Depends(get_db)
):
    """
    Get all active laws for a specific game.
    """
    laws = crud_law.get_active_laws(db, game_id=game_id)
    return laws

@router.post("/effects", response_model=Dict[str, Any])
def calculate_law_effects(
    game_id: UUID = Query(..., description="Game ID"),
    action_type: str = Body(..., description="Type of action being performed"),
    context_data: Dict[str, Any] = Body({}, description="Context data for the action"),
    db: Session = Depends(get_db)
):
    """
    Calculate the combined effects of all active laws on a specific action.
    """
    # Get active laws for this game
    active_laws = crud_law.get_active_laws(db, game_id=game_id)
    
    # Prepare context with both the action type and the provided context data
    context = {"action_type": action_type, **context_data}
    
    # Calculate effects
    effects = LawSystemService.calculate_law_effects(active_laws, context)
    
    return effects

@router.post("/expire-check/{game_id}/{round_number}")
def check_law_expiration(
    game_id: UUID = Path(..., description="Game ID"),
    round_number: int = Path(..., description="Current round number"),
    db: Session = Depends(get_db)
):
    """
    Check for and expire laws that have reached their duration limit.
    """
    # Get active laws
    active_laws = crud_law.get_active_laws(db, game_id=game_id)
    
    expired_laws = []
    
    # Check each law for expiration
    for law in active_laws:
        enacted_round = law.enacted_round
        duration = law.duration or 3  # Default to 3 rounds if not specified
        
        if round_number - enacted_round >= duration:
            # Law has expired
            crud_law.expire_law(db, law_id=law.id)
            expired_laws.append(law)
    
    return {
        "expired_laws": len(expired_laws),
        "active_laws_remaining": len(active_laws) - len(expired_laws)
    }