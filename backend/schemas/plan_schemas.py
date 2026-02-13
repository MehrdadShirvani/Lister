from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Plan status
class PlanStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"

# Base Plan schema
class PlanBase(BaseModel):
    task_id: Optional[int] = None
    note_id: Optional[int] = None
    time_block_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: PlanStatus = PlanStatus.PLANNED
    progress: int = 0
    notes: Optional[str] = None

# For creating plans from suggestions
class PlanFromSuggestion(BaseModel):
    suggestion_task_id: int
    suggestion_time_block_id: int
    suggestion_title: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

# For creating plans manually
class PlanCreate(PlanBase):
    pass

# For updating plans
class PlanUpdate(BaseModel):
    task_id: Optional[int] = None
    note_id: Optional[int] = None
    time_block_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    status: Optional[PlanStatus] = None
    progress: Optional[int] = None
    notes: Optional[str] = None

# For starting/completing plans
class PlanAction(BaseModel):
    action: str  # start, pause, resume, complete, cancel
    timestamp: Optional[datetime] = None
    notes: Optional[str] = None

# Plan response schema
class PlanResponse(PlanBase):
    id: int
    account_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    completion_rate: float
    
    # Related data
    task_title: Optional[str] = None
    task_status: Optional[str] = None
    note_title: Optional[str] = None
    time_block_title: Optional[str] = None
    
    # Suggestion source
    from_suggestion: bool = False
    suggestion_details: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)

# For filtering plans
class PlanFilterParams(BaseModel):
    status: Optional[PlanStatus] = None
    task_id: Optional[int] = None
    time_block_id: Optional[int] = None
    has_note: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    progress_min: Optional[int] = None
    progress_max: Optional[int] = None
    from_suggestion: Optional[bool] = None