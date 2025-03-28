#file: app/models/resource.py
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, TEXT, ARRAY, UniqueConstraint, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class ResourceType(Base):
    __tablename__ = 'resource_types'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(50), nullable=False)  # Raw Material, Technology, etc.
    rarity = Column(String(50), nullable=False)  # Common, Uncommon, Rare, Very Rare
    description = Column(TEXT)
    producible_by = Column(ARRAY(String))  # Array of civilization IDs
    created_at = Column(DateTime, default=func.now())

class Resource(Base):
    __tablename__ = 'resources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    resource_type_id = Column(UUID(as_uuid=True), ForeignKey('resource_types.id'), nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)  # Will reference civilizations/teams
    quantity = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Composite unique constraint for aggregation
    __table_args__ = (
        UniqueConstraint('game_id', 'resource_type_id', 'owner_id', name='uix_resource_game_type_owner'),
    )

class CounterfeitResource(Base):
    __tablename__ = 'counterfeit_resources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    resource_type_id = Column(UUID(as_uuid=True), ForeignKey('resource_types.id'), nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)  # References civilizations/teams
    quantity = Column(Integer, nullable=False)
    batch_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Each batch is unique within a game, and quantity must be positive
    __table_args__ = (
        UniqueConstraint('game_id', 'batch_id', name='uix_batch_per_game'),
        CheckConstraint('quantity > 0', name='check_positive_quantity'),
    )

class ResourceTransfer(Base):
    __tablename__ = 'resource_transfers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    resource_type_id = Column(UUID(as_uuid=True), ForeignKey('resource_types.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    sender_id = Column(UUID(as_uuid=True), nullable=False)  # Original owner
    receiver_id = Column(UUID(as_uuid=True), nullable=False)  # New owner
    hub_id = Column(String(50), nullable=False)  # Alpha, Beta, or Gamma
    delivery_cost_percentage = Column(Integer, nullable=False)
    round_initiated = Column(Integer, nullable=False)
    status = Column(String(50), default='pending', nullable=False)  # pending, completed, failed
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_transfer_quantity'),
    )

class ChronoShardBalance(Base):
    __tablename__ = 'chrono_shard_balances'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)  # References civilizations
    balance = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('game_id', 'owner_id', name='uix_chrono_shards_per_owner'),
    )

class BlackMarketShipment(Base):
    __tablename__ = 'black_market_shipments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    resource_type_id = Column(UUID(as_uuid=True), ForeignKey('resource_types.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    minimum_bid = Column(Integer, nullable=False)
    round_available = Column(Integer, nullable=False)
    status = Column(String(50), default='active', nullable=False)  # active, completed, cancelled
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_shipment_quantity'),
        CheckConstraint('minimum_bid > 0', name='check_positive_minimum_bid'),
    )

class BlackMarketBid(Base):
    __tablename__ = 'black_market_bids'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('black_market_shipments.id'), nullable=False)
    bidder_id = Column(UUID(as_uuid=True), nullable=False)  # References civilizations
    bid_amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())  # For tie-breaking
    status = Column(String(50), default='pending', nullable=False)  # pending, won, lost
    
    __table_args__ = (
        CheckConstraint('bid_amount > 0', name='check_positive_bid_amount'),
    )