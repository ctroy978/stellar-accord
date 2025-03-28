# File: app/schemas/teacher.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

# Base Teacher schema
class TeacherBase(BaseModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None

# Schema for creating a new Teacher
class TeacherCreate(TeacherBase):
    password: str

# Schema for updating a Teacher
class TeacherUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    password: Optional[str] = None

# Schema for returning a Teacher
class Teacher(TeacherBase):
    id: UUID
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True