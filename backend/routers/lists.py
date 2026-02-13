from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from core.database import get_db
from core.dependencies import get_current_active_user
from models.account_models import Account
from schemas.list_schemas import (
    ListCreate,
    ListUpdate,
    ListResponse,
    ListDetailResponse,
    ListFilterParams,
    ListStatus,
    TaskHierarchyNode
)
from services.list_service import ListService

router = APIRouter(
    prefix="/lists",
    tags=["lists"]
)

list_service = ListService()

# ============= CRUD ENDPOINTS =============

@router.post("/", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: ListCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create a new list"""
    return list_service.create_list(db, list_data, current_user.id)

@router.get("/", response_model=List[ListResponse])
def get_lists(
    # Filter parameters
    status: Optional[ListStatus] = Query(None, description="Filter by status"),
    priority_min: Optional[int] = Query(None, ge=1, le=5, description="Minimum priority"),
    priority_max: Optional[int] = Query(None, ge=1, le=5, description="Maximum priority"),
    tag_ids: Optional[List[int]] = Query(None, description="Filter by tag IDs"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    has_tasks: Optional[bool] = Query(None, description="Lists with/without tasks"),
    created_after: Optional[datetime] = Query(None, description="Created after this date"),
    created_before: Optional[datetime] = Query(None, description="Created before this date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all lists with filters"""
    filters = ListFilterParams(
        status=status,
        priority_min=priority_min,
        priority_max=priority_max,
        tag_ids=tag_ids,
        search=search,
        has_tasks=has_tasks,
        created_after=created_after,
        created_before=created_before
    )
    
    return list_service.get_lists(db, current_user.id, filters, skip, limit)

@router.get("/by-tag/{tag_id}", response_model=List[ListResponse])
def get_lists_by_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all lists with a specific tag"""
    return list_service.get_lists_by_tag(db, tag_id, current_user.id)

@router.get("/{list_id}", response_model=ListResponse)
def get_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get a specific list by ID"""
    return list_service.get_list(db, list_id, current_user.id)

@router.get("/{list_id}/detail", response_model=ListDetailResponse)
def get_list_detail(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get detailed list info with tasks and hierarchy"""
    return list_service.get_list_detail(db, list_id, current_user.id)

@router.get("/{list_id}/hierarchy", response_model=List[TaskHierarchyNode])
def get_list_hierarchy(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get task hierarchy for a list"""
    return list_service.get_list_hierarchy(db, list_id, current_user.id)

@router.put("/{list_id}", response_model=ListResponse)
def update_list(
    list_id: int,
    list_update: ListUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Update a list"""
    return list_service.update_list(db, list_id, list_update, current_user.id)

@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Delete a list"""
    result = list_service.delete_list(db, list_id, current_user.id)
    return None

# ============= LIST OPERATIONS =============

@router.post("/{list_id}/archive", response_model=ListResponse)
def archive_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Archive a list"""
    return list_service.archive_list(db, list_id, current_user.id)

@router.post("/move-tasks")
def move_tasks_to_list(
    source_list_id: int = Query(..., description="Source list ID"),
    target_list_id: int = Query(..., description="Target list ID"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Move all tasks from one list to another"""
    return list_service.move_tasks_to_list(db, source_list_id, target_list_id, current_user.id)

# ============= BULK OPERATIONS =============

@router.post("/bulk", response_model=List[ListResponse])
def create_multiple_lists(
    lists_data: List[ListCreate],
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create multiple lists at once"""
    created = []
    for data in lists_data:
        created.append(list_service.create_list(db, data, current_user.id))
    return created