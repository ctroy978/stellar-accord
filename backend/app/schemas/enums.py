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