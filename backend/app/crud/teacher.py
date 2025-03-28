# File: app/crud/teacher.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import bcrypt

from app.models.teacher import Teacher
from app.models.game_access import GameAccess
from app.schemas.teacher import TeacherCreate, TeacherUpdate
from app.schemas.game_access import GameAccessCreate

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against a provided password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_teacher(db: Session, teacher_id: UUID) -> Optional[Teacher]:
    """Get a specific teacher by ID."""
    return db.query(Teacher).filter(Teacher.id == teacher_id).first()

def get_teacher_by_username(db: Session, username: str) -> Optional[Teacher]:
    """Get a teacher by username."""
    return db.query(Teacher).filter(Teacher.username == username).first()

def get_teacher_by_email(db: Session, email: str) -> Optional[Teacher]:
    """Get a teacher by email."""
    return db.query(Teacher).filter(Teacher.email == email).first()

def create_teacher(db: Session, teacher: TeacherCreate) -> Teacher:
    """Create a new teacher with secure password hashing."""
    # Check if username or email already exists
    if get_teacher_by_username(db, username=teacher.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username {teacher.username} already registered"
        )
    
    if get_teacher_by_email(db, email=teacher.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {teacher.email} already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(teacher.password)
    
    db_teacher = Teacher(
        username=teacher.username,
        email=teacher.email,
        password_hash=hashed_password,
        display_name=teacher.display_name
    )
    
    db.add(db_teacher)
    
    try:
        db.commit()
        db.refresh(db_teacher)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create teacher due to database constraint violation"
        )
    
    return db_teacher

def update_teacher(db: Session, teacher_id: UUID, teacher: TeacherUpdate) -> Teacher:
    """Update a teacher's details."""
    db_teacher = get_teacher(db, teacher_id=teacher_id)
    if not db_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    # Check if updating username or email to something that already exists
    if teacher.username and teacher.username != db_teacher.username:
        if get_teacher_by_username(db, username=teacher.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username {teacher.username} already registered"
            )
    
    if teacher.email and teacher.email != db_teacher.email:
        if get_teacher_by_email(db, email=teacher.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {teacher.email} already registered"
            )
    
    # Update password if provided
    if teacher.password:
        db_teacher.password_hash = hash_password(teacher.password)
        # Remove password from update_data to prevent it from being set as an attribute
        teacher.password = None
    
    # Update other attributes if provided
    update_data = teacher.dict(exclude_unset=True, exclude={"password"})
    for key, value in update_data.items():
        setattr(db_teacher, key, value)
    
    try:
        db.commit()
        db.refresh(db_teacher)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update teacher due to database constraint violation"
        )
    
    return db_teacher

def delete_teacher(db: Session, teacher_id: UUID) -> None:
    """Delete a teacher."""
    db_teacher = get_teacher(db, teacher_id=teacher_id)
    if not db_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    db.delete(db_teacher)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete teacher due to database constraint violation"
        )

def authenticate_teacher(db: Session, username: str, password: str) -> Optional[Teacher]:
    """Authenticate a teacher with username and password."""
    db_teacher = get_teacher_by_username(db, username=username)
    if not db_teacher:
        return None
    
    if not verify_password(password, db_teacher.password_hash):
        return None
    
    return db_teacher

def update_last_login(db: Session, teacher_id: UUID) -> Teacher:
    """Update a teacher's last login timestamp."""
    db_teacher = get_teacher(db, teacher_id=teacher_id)
    if not db_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    db_teacher.last_login = datetime.now()
    
    try:
        db.commit()
        db.refresh(db_teacher)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update teacher last login due to database constraint violation"
        )
    
    return db_teacher

def grant_game_access(db: Session, game_access: GameAccessCreate) -> GameAccess:
    """Grant a teacher access to a game."""
    # Check if the teacher already has access to this game
    existing_access = db.query(GameAccess).filter(
        GameAccess.game_id == game_access.game_id,
        GameAccess.teacher_id == game_access.teacher_id
    ).first()
    
    if existing_access:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher already has access to this game"
        )
    
    db_game_access = GameAccess(
        game_id=game_access.game_id,
        teacher_id=game_access.teacher_id,
        access_level=game_access.access_level
    )
    
    db.add(db_game_access)
    
    try:
        db.commit()
        db.refresh(db_game_access)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not grant game access due to database constraint violation"
        )
    
    return db_game_access

def revoke_game_access(db: Session, game_id: UUID, teacher_id: UUID) -> None:
    """Revoke a teacher's access to a game."""
    db_game_access = db.query(GameAccess).filter(
        GameAccess.game_id == game_id,
        GameAccess.teacher_id == teacher_id
    ).first()
    
    if not db_game_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game access not found"
        )
    
    db.delete(db_game_access)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not revoke game access due to database constraint violation"
        )