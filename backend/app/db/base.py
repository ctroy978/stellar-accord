#file: app/db/base.py
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()