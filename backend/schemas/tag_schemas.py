from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# Base Tag Schema
class TagBase(BaseModel):
    title: str
    type: Optional[str] = None
    description: Optional[str] = None

class UserTagCreate(TagBase):
    pass

class PublicTagCreate(TagBase):
    is_public: bool = True

class TagUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None

class TagResponse(TagBase):
    id: int
    account_id: Optional[int] = None
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class TagFilterParams(BaseModel):
    type: Optional[str] = None
    is_public: Optional[bool] = None
    search: Optional[str] = None
    created_by_me: Optional[bool] = None