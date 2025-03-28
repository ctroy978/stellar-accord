from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.models import Game, ResourceType, Resource, CounterfeitResource, ResourceTransfer, ChronoShardBalance, BlackMarketShipment, BlackMarketBid

def init_db():
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)