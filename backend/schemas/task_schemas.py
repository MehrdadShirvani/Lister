from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

# Task status options
class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

# Task type options
class TaskType(str, Enum):
    TASK = "task"
    PROJECT = "project"
    MILESTONE = "milestone"
    RECURRING = "recurring"

# Base Task schema
class TaskBase(BaseModel):
    title: str
    type: Optional[TaskType] = TaskType.TASK
    scheduled_date: Optional[date] = None
    estimated_duration: Optional[int] = None  # in minutes
    priority: Optional[int] = None  # 1-5 
    status: TaskStatus = TaskStatus.NOT_STARTED

# For creating tasks
class TaskCreate(TaskBase):
    list_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    urls: Optional[List[str]] = None  # List of URLs to add

# For updating tasks
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[TaskType] = None
    list_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    scheduled_date: Optional[date] = None
    estimated_duration: Optional[int] = None
    priority: Optional[int] = None
    status: Optional[TaskStatus] = None
    completed_at: Optional[datetime] = None
    tag_ids: Optional[List[int]] = None  # Replace all tags
    add_tag_ids: Optional[List[int]] = None  # Add specific tags
    remove_tag_ids: Optional[List[int]] = None  # Remove specific tags
    urls: Optional[List[str]] = None  # Replace all URLs
    add_urls: Optional[List[str]] = None  # Add specific URLs
    remove_urls: Optional[List[str]] = None  # Remove specific URLs

# For URL response
class TaskUrlResponse(BaseModel):
    url: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# For hierarchy display
class TaskHierarchyNode(BaseModel):
    id: int
    title: str
    type: str
    status: str
    priority: Optional[int]
    scheduled_date: Optional[date]
    children: List['TaskHierarchyNode'] = []
    model_config = ConfigDict(from_attributes=True)

# TaskHierarchyNode needs to reference itself
TaskHierarchyNode.model_rebuild()

# Task response
class TaskResponse(TaskBase):
    id: int
    account_id: int
    list_id: Optional[int]
    parent_task_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Relationships
    tags: List[dict] = []  # Simplified tag info
    urls: List[TaskUrlResponse] = []
    subtask_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

# Detailed task response with hierarchy
class TaskDetailResponse(TaskResponse):
    parent_task: Optional['TaskResponse'] = None
    subtasks: List['TaskResponse'] = []
    lists: List[dict] = []
    
    model_config = ConfigDict(from_attributes=True)


class TaskFilterParams(BaseModel):
    list_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    type: Optional[TaskType] = None
    priority_min: Optional[int] = None
    priority_max: Optional[int] = None
    scheduled_before: Optional[date] = None
    scheduled_after: Optional[date] = None
    has_parent: Optional[bool] = None  
    parent_task_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    search: Optional[str] = None
    is_completed: Optional[bool] = None
    is_planned: Optional[bool] = None  