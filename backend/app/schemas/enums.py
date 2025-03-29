#file:  app/schemas/enums.py
from enum import Enum as PyEnum

class ResourceCategory(str, PyEnum):
    RAW_MATERIAL = "Raw Material"
    REFINED_MATERIAL = "Refined Material"
    TECHNOLOGY = "Technology"
    INFORMATION = "Information"
    CULTURAL_ITEM = "Cultural Item"
    ENERGY_SOURCE = "Energy Source"

class ResourceRarity(str, PyEnum):
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    VERY_RARE = "Very Rare"

class CivilizationName(str, PyEnum):
    THRIZOTH = "Thrizoth"
    METHANE_COLLECTIVE = "Methane Collective"
    SILICON_LIBERATION = "Silicon Liberation"
    GLACIAN_CURRENT = "Glacian Current"
    KYRATHI = "Kyrathi"
    VASKU = "Vasku"

class HubName(str, PyEnum):
    ALPHA = "Alpha"
    BETA = "Beta"
    GAMMA = "Gamma"

class TransferStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class BlackMarketStatus(str, PyEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BidStatus(str, PyEnum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"

class GameStatus(str, PyEnum):
    SETUP = "setup"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class GamePhase(str, PyEnum):
    PLANNING = "planning"
    NEGOTIATION = "negotiation"
    ACTION = "action"
    RESOLUTION = "resolution"
    ASSESSMENT = "assessment"

class TeamRoleName(str, PyEnum):
    CHIEF_DIPLOMAT = "chief_diplomat"
    RESOURCE_MANAGER = "resource_manager"
    INTELLIGENCE_OFFICER = "intelligence_officer"
    PROJECT_DIRECTOR = "project_director"

class AccessLevel(str, PyEnum):
    OWNER = "owner"
    VIEWER = "viewer"
    COLLABORATOR = "collaborator"

class TechType(str, PyEnum):
    BIG_TECH = "big_tech"
    UBER_TECH = "uber_tech"
    UNIVERSAL = "universal"
    RESOURCE = "resource"

class ProjectPhase(str, PyEnum):
    RESEARCH = "research"
    PROTOTYPE = "prototype"
    CONSTRUCTION = "construction"