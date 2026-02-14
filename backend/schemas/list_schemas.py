from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

from schemas.tag_schemas import TagResponse

# List status options
class ListStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    FROZEN = "frozen"
    COMPLETED = "completed"

# Base List schema
class ListBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[int] = None  # 1-5 scale
    status: ListStatus = ListStatus.ACTIVE

# For creating lists
class ListCreate(ListBase):
    tag_ids: Optional[List[int]] = None  # Tags to associate with the list

# For updating lists
class ListUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[ListStatus] = None
    tag_ids: Optional[List[int]] = None  # Replace all tags
    add_tag_ids: Optional[List[int]] = None  # Add specific tags
    remove_tag_ids: Optional[List[int]] = None  # Remove specific tags

# Task summary for list view
class TaskSummary(BaseModel):
    id: int
    title: str
    status: str
    priority: Optional[int]
    scheduled_date: Optional[date]
    has_subtasks: bool
    subtask_count: int
    model_config = ConfigDict(from_attributes=True)

# Hierarchy node for tasks in list
class TaskHierarchyNode(BaseModel):
    id: int
    title: str
    status: str
    priority: Optional[int]
    scheduled_date: Optional[date]
    depth: int  # How deep in hierarchy (0 for root tasks in this list)
    children: List['TaskHierarchyNode'] = []
    model_config = ConfigDict(from_attributes=True)

# Need to rebuild for self-reference
TaskHierarchyNode.model_rebuild()

# List response (basic)
class ListResponse(ListBase):
    id: int
    account_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Stats
    task_count: int = 0
    completed_task_count: int = 0
    active_task_count: int = 0
    
    # Tags
    tags: List[TagResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# Detailed list response with tasks
class ListDetailResponse(ListResponse):
    tasks: List[TaskSummary] = []
    task_hierarchy: List[TaskHierarchyNode] = []
    
    # Additional stats
    total_subtasks: int = 0
    estimated_total_duration: Optional[int] = None  # Sum of all task durations in minutes
    
    model_config = ConfigDict(from_attributes=True)

# For filtering lists
class ListFilterParams(BaseModel):
    status: Optional[ListStatus] = None
    priority_min: Optional[int] = None
    priority_max: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    search: Optional[str] = None
    has_tasks: Optional[bool] = None  
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None