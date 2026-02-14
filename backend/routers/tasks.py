from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from core.database import get_db
from core.dependencies import get_current_active_user
from models.account_models import Account
from schemas.task_schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskDetailResponse,
    TaskHierarchyNode,
    TaskFilterParams,
    TaskStatus,
    TaskType
)
from services.task_service import TaskService

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

task_service = TaskService()

# ============= CRUD ENDPOINTS =============

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create a new task"""
    return task_service.create_task(db, task_data, current_user.id)

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    # Filter parameters
    list_id: Optional[int] = Query(None, description="Filter by list ID"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    type: Optional[TaskType] = Query(None, description="Filter by task type"),
    priority_min: Optional[int] = Query(None, ge=1, le=5, description="Minimum priority"),
    priority_max: Optional[int] = Query(None, ge=1, le=5, description="Maximum priority"),
    scheduled_after: Optional[date] = Query(None, description="Scheduled on or after this date"),
    scheduled_before: Optional[date] = Query(None, description="Scheduled on or before this date"),
    has_parent: Optional[bool] = Query(None, description="True for subtasks, False for root tasks"),
    parent_task_id: Optional[int] = Query(None, description="Filter by parent task"),
    tag_ids: Optional[List[int]] = Query(None, description="Filter by tag IDs"),
    search: Optional[str] = Query(None, description="Search in title"),
    is_completed: Optional[bool] = Query(None, description="Filter by completion status"),
    is_planned: Optional[bool] = Query(None, description="Tasks with future plans"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all tasks with filters"""
    filters = TaskFilterParams(
        list_id=list_id,
        status=status,
        type=type,
        priority_min=priority_min,
        priority_max=priority_max,
        scheduled_after=scheduled_after,
        scheduled_before=scheduled_before,
        has_parent=has_parent,
        parent_task_id=parent_task_id,
        tag_ids=tag_ids,
        search=search,
        is_completed=is_completed,
        is_planned=is_planned
    )
    
    return task_service.get_tasks(db, current_user.id, filters, skip, limit)

@router.get("/hierarchy", response_model=List[TaskHierarchyNode])
def get_task_hierarchy(
    root_task_id: Optional[int] = Query(None, description="Get hierarchy from specific root"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get task hierarchy tree"""
    return task_service.get_task_hierarchy(db, current_user.id, root_task_id)

@router.get("/with-future-plans", response_model=List[TaskResponse])
def get_incomplete_tasks_with_future_plans(
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get tasks that are not done and have future plans"""
    return task_service.get_incomplete_tasks_with_future_plans(db, current_user.id)

@router.get("/by-tag/{tag_id}", response_model=List[TaskResponse])
def get_tasks_by_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all tasks with a specific tag"""
    return task_service.get_tasks_by_tag(db, tag_id, current_user.id)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get a specific task by ID"""
    return task_service.get_task(db, task_id, current_user.id)

@router.get("/{task_id}/detail", response_model=TaskDetailResponse)
def get_task_detail(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get detailed task info with relationships"""
    return task_service.get_task_detail(db, task_id, current_user.id)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Update a task"""
    return task_service.update_task(db, task_id, task_update, current_user.id)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Delete a task"""
    result = task_service.delete_task(db, task_id, current_user.id)
    return None

# ============= TASK OPERATIONS =============

@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Mark a task as completed"""
    return task_service.complete_task(db, task_id, current_user.id)

@router.post("/{task_id}/duplicate", response_model=TaskResponse)
def duplicate_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Duplicate a task (creates a copy)"""
    original = task_service.get_task(db, task_id, current_user.id)
    
    # Create duplicate data
    duplicate_data = TaskCreate(
        title=f"{original.title} (copy)",
        type=original.type,
        list_id=original.list_id,
        parent_task_id=original.parent_task_id,
        scheduled_date=original.scheduled_date,
        estimated_duration=original.estimated_duration,
        priority=original.priority,
        status="not_started",
        tag_ids=[tag.id for tag in original.tags],
        urls=[url.url for url in original.urls]
    )
    
    return task_service.create_task(db, duplicate_data, current_user.id)