#file: app/schemas/resource.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID

from app.schemas.enums import ResourceCategory, ResourceRarity, TransferStatus, HubName

# Resource Type Schemas
class ResourceTypeBase(BaseModel):
    name: str
    category: ResourceCategory
    rarity: ResourceRarity
    description: Optional[str] = None
    producible_by: List[str] = []

class ResourceTypeCreate(ResourceTypeBase):
    pass

class ResourceTypeUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[ResourceCategory] = None
    rarity: Optional[ResourceRarity] = None
    description: Optional[str] = None
    producible_by: Optional[List[str]] = None

class ResourceTypeInDB(ResourceTypeBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class ResourceType(ResourceTypeInDB):
    pass

# Resource Schemas
class ResourceBase(BaseModel):
    resource_type_id: UUID
    quantity: int

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class ResourceInDB(ResourceBase):
    id: UUID
    game_id: UUID
    owner_id: UUID
    created_at: datetime
    modified_at: datetime

    class Config:
        orm_mode = True

class Resource(ResourceInDB):
    resource_type: ResourceType

# Resource Transfer Schemas
class ResourceTransferBase(BaseModel):
    resource_type_id: UUID
    quantity: int = Field(..., gt=0)
    sender_id: UUID
    receiver_id: UUID
    hub_id: HubName

class ResourceTransferCreate(ResourceTransferBase):
    pass

class ResourceTransferInDB(ResourceTransferBase):
    id: UUID
    game_id: UUID
    delivery_cost_percentage: int
    round_initiated: int
    status: TransferStatus
    created_at: datetime

    class Config:
        orm_mode = True

class ResourceTransfer(ResourceTransferInDB):
    resource_type: ResourceType