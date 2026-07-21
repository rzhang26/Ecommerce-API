from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import EmailStr

EASTERN_TZ = ZoneInfo('America/New_York')

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, nullable=False)

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

class User(UserBase, table=True):
    __tablename__ = 'users'

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(EASTERN_TZ), nullable=False) 