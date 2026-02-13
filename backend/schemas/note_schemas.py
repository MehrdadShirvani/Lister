from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Sort options
class NoteSortBy(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    TITLE = "title"
    QUALITY_SCORE = "quality_score"
    WORD_COUNT = "word_count"
    READING_TIME = "reading_time_minutes"

# Base Note schema
class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None
    quality_score: Optional[int] = None
    is_pinned: bool = False
    is_favorite: bool = False
    formatting_data: Dict[str, Any] = {}

# For creating notes
class NoteCreate(NoteBase):
    plan_id: Optional[int] = None  
    parent_note_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    related_note_ids: Optional[List[int]] = None
    task_ids: Optional[List[int]] = None

# For updating notes
class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    quality_score: Optional[int] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None
    formatting_data: Optional[Dict[str, Any]] = None
    
    # Tag operations
    tag_ids: Optional[List[int]] = None  # Replace all tags
    add_tag_ids: Optional[List[int]] = None
    remove_tag_ids: Optional[List[int]] = None
    
    # Related notes operations
    related_note_ids: Optional[List[int]] = None  # Replace all related notes
    add_related_note_ids: Optional[List[int]] = None
    remove_related_note_ids: Optional[List[int]] = None
    
    # Task operations
    task_ids: Optional[List[int]] = None  # Replace all linked tasks
    add_task_ids: Optional[List[int]] = None
    remove_task_ids: Optional[List[int]] = None

# For preview in lists
class NotePreview(BaseModel):
    id: int
    title: str
    content_preview: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    is_pinned: bool
    is_favorite: bool
    word_count: int
    reading_time_minutes: int
    tag_count: int
    has_related_notes: bool
    has_tasks: bool
    model_config = ConfigDict(from_attributes=True)

# For related item display
class RelatedTask(BaseModel):
    id: int
    title: str
    status: str
    priority: Optional[int]
    model_config = ConfigDict(from_attributes=True)

class RelatedNote(BaseModel):
    id: int
    title: str
    preview: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class RelatedPlan(BaseModel):
    id: int
    task_id: Optional[int]
    time_block_id: Optional[int]
    start_time: Optional[datetime]
    status: str
    model_config = ConfigDict(from_attributes=True)

# Full note response
class NoteResponse(NoteBase):
    id: int
    account_id: int
    plan_id: Optional[int]
    parent_note_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    last_accessed_at: Optional[datetime]
    word_count: int
    reading_time_minutes: int
    is_archived: bool
    
    # Relationships
    tags: List[Dict[str, Any]] = []
    parent_note: Optional['NotePreview'] = None
    child_notes: List['NotePreview'] = []
    related_notes: List['RelatedNote'] = []
    tasks: List['RelatedTask'] = []
    plan: Optional['RelatedPlan'] = None
    
    model_config = ConfigDict(from_attributes=True)

# For filtering notes
class NoteFilterParams(BaseModel):
    search: Optional[str] = None
    tag_ids: Optional[List[int]] = None
    is_pinned: Optional[bool] = None
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_follow_up: Optional[bool] = None
    has_plan: Optional[bool] = None
    has_tasks: Optional[bool] = None
    has_related_notes: Optional[bool] = None
    quality_score_min: Optional[int] = None
    quality_score_max: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    
    sort_by: NoteSortBy = NoteSortBy.UPDATED_AT
    sort_desc: bool = True