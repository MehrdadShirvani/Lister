from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Suggestion status
class SuggestionStatus(str, Enum):
    PENDING = "pending"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

# Response type
class SuggestionResponseType(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    SNOOZE = "snooze"

# Base Suggestion schema
class SuggestionBase(BaseModel):
    title: str
    description: Optional[str] = None
    confidence_score: int = 50
    priority: int = 0

# For creating suggestions (system-generated)
class SuggestionCreate(BaseModel):
    task_id: int
    time_block_id: int
    title: str
    description: Optional[str] = None
    confidence_score: int = 50
    priority: int = 0
    expires_at: Optional[datetime] = None

# For responding to suggestions
class SuggestionResponse(BaseModel):
    response: SuggestionResponseType
    notes: Optional[str] = None
    snooze_minutes: Optional[int] = None  # If snoozing

# For updating suggestions (system use)
class SuggestionUpdate(BaseModel):
    status: Optional[SuggestionStatus] = None
    viewed_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    is_expired: Optional[bool] = None

# Suggestion response schema
class SuggestionResponseSchema(BaseModel):
    task_id: int
    time_block_id: int
    title: str
    description: Optional[str]
    confidence_score: int
    priority: int
    status: str
    viewed_at: Optional[datetime]
    responded_at: Optional[datetime]
    expires_at: Optional[datetime]
    response_notes: Optional[str]
    created_at: datetime
    
    # Related data (for display)
    task_title: Optional[str] = None
    time_block_title: Optional[str] = None
    time_block_start: Optional[datetime] = None
    time_block_end: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# For filtering suggestions
class SuggestionFilterParams(BaseModel):
    status: Optional[SuggestionStatus] = None
    task_id: Optional[int] = None
    time_block_id: Optional[int] = None
    priority_min: Optional[int] = None
    confidence_min: Optional[int] = None
    is_expired: Optional[bool] = False
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    expires_before: Optional[datetime] = None