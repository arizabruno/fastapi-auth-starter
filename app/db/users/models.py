from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from pydantic import BaseModel
from typing import List, Optional
from app.db.config import Base


###################################################
# SQLAlchemy Model
###################################################

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    roles = Column(String, server_default="user", nullable=False)

###################################################
# Pydantic Schemas
###################################################

class UserBase(BaseModel):
    email: str
    username: str
    roles: str

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserPublic(UserBase):
    user_id: int
    created_at: str
