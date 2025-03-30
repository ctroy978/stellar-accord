from app.models.game import Game
from app.models.resource import (
    ResourceType, 
    Resource, 
    CounterfeitResource, 
    ResourceTransfer, 
    ChronoShardBalance,
    BlackMarketShipment,
    BlackMarketBid
)
from app.models.civilization import Civilization
from app.models.player import Player
from app.models.teacher import Teacher
from app.models.team_role import TeamRole
from app.models.game_phase import GamePhase
from app.models.game_access import GameAccess
from app.models.law import LawProposal, EnactedLaw
from app.models.technology import (
    BigTechComponent,
    UberTechComponent,
    UniversalProject,
    TechRequirement,
    ProjectDevelopment,
    TechnologyOwnership,
    ProjectComponentAssignment
)