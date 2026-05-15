from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict


# ── Auth Schemas ──────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["kaipulla"])
    email: EmailStr = Field(..., examples=["kaipulla@example.com"])
    password: str = Field(..., min_length=6, examples=["secret123"])


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime


class LoginRequest(BaseModel):
    username: str = Field(..., examples=["kaipulla"])
    password: str = Field(..., examples=["secret123"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ── Task Schemas ──────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, examples=["Buy groceries"])
    description: Optional[str] = Field(None, max_length=1000, examples=["Milk, eggs, bread"])


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int


class PaginatedTaskResponse(BaseModel):
    total: int
    page: int
    limit: int
    tasks: List[TaskResponse]
