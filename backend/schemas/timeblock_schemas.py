from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Recurrence options
class RecurrenceType(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    WEEKDAYS = "weekdays"
    WEEKENDS = "weekends"

# Block type options
class BlockType(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    BREAK = "break"
    MEETING = "meeting"
    TASK = "task"
    FOCUS = "focus"
    GENERAL = "general"

# Status options
class BlockStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Base TimeBlock schema
class TimeBlockBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    block_type: BlockType = BlockType.GENERAL
    status: BlockStatus = BlockStatus.PLANNED
    
    # Recurrence fields
    is_recurring: bool = False
    recurrence_rule: Optional[RecurrenceType] = None
    day_of_week: Optional[int] = None  # 0-6 for Sunday-Saturday
    
    @field_validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v
    
    @field_validator('day_of_week')
    def validate_day_of_week(cls, v, values):
        if v is not None and (v < 0 or v > 6):
            raise ValueError('day_of_week must be between 0 and 6')
        return v

# For creating a single time block
class TimeBlockCreate(TimeBlockBase):
    energy_tag_ids: Optional[List[int]] = None  
    other_tag_ids: Optional[List[int]] = None   

# For updating time blocks
class TimeBlockUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    block_type: Optional[BlockType] = None
    status: Optional[BlockStatus] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[RecurrenceType] = None
    day_of_week: Optional[int] = None
    energy_tag_ids: Optional[List[int]] = None
    other_tag_ids: Optional[List[int]] = None

class EnergyInfo(BaseModel):
    level: Optional[str] = None  # Very Low, Low, Medium, High, Very High
    tag_id: Optional[int] = None

# Response schema
class TimeBlockResponse(TimeBlockBase):
    id: int
    account_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Tags organized by type
    energy_tag: Optional[EnergyInfo] = None
    other_tags: List[dict] = []  # Other tags with id, title, type
    
    model_config = ConfigDict(from_attributes=True)

# For filtering time blocks
class TimeBlockFilterParams(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    block_type: Optional[BlockType] = None
    status: Optional[BlockStatus] = None
    is_recurring: Optional[bool] = None
    energy_level: Optional[str] = None  # Filter by energy level
    tag_ids: Optional[List[int]] = None  # Filter by any tags
    search: Optional[str] = None