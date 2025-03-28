# File: app/models/teacher.py
import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class Teacher(Base):
    __tablename__ = 'teachers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)  # Teachers need secure login
    display_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)