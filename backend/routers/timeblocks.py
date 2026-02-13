from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from core.database import get_db
from core.dependencies import get_current_active_user
from models.account_models import Account
from schemas.timeblock_schemas import (
    TimeBlockCreate,
    TimeBlockUpdate,
    TimeBlockResponse,
    TimeBlockFilterParams,
    BlockType,
    BlockStatus
)
from services.timeblock_service import TimeBlockService

router = APIRouter(
    prefix="/timeblocks",
    tags=["timeblocks"]
)

timeblock_service = TimeBlockService()

# ============= CRUD ENDPOINTS =============

@router.post("/", response_model=TimeBlockResponse, status_code=status.HTTP_201_CREATED)
def create_timeblock(
    timeblock_data: TimeBlockCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create a new time block"""
    return timeblock_service.create_timeblock(db, timeblock_data, current_user.id)

@router.get("/", response_model=List[TimeBlockResponse])
def get_timeblocks(
    # Filter parameters
    start_date: Optional[datetime] = Query(None, description="Filter by start date (from)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (to)"),
    block_type: Optional[BlockType] = Query(None, description="Filter by block type"),
    status: Optional[BlockStatus] = Query(None, description="Filter by status"),
    is_recurring: Optional[bool] = Query(None, description="Filter recurring/non-recurring"),
    energy_level: Optional[str] = Query(None, description="Filter by energy level"),
    tag_ids: Optional[List[int]] = Query(None, description="Filter by tag IDs"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all time blocks with filters"""
    filters = TimeBlockFilterParams(
        start_date=start_date,
        end_date=end_date,
        block_type=block_type,
        status=status,
        is_recurring=is_recurring,
        energy_level=energy_level,
        tag_ids=tag_ids,
        search=search
    )
    
    return timeblock_service.get_timeblocks(db, current_user.id, filters, skip, limit)

@router.get("/upcoming", response_model=List[TimeBlockResponse])
def get_upcoming_timeblocks(
    days: int = Query(7, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get upcoming time blocks for the next X days"""
    return timeblock_service.get_upcoming_timeblocks(db, current_user.id, days)

@router.get("/energy-levels")
def get_energy_levels(
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get available energy levels with tag info"""
    return timeblock_service.get_energy_levels(db, current_user.id)

@router.get("/{timeblock_id}", response_model=TimeBlockResponse)
def get_timeblock(
    timeblock_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get a specific time block by ID"""
    return timeblock_service.get_timeblock(db, timeblock_id, current_user.id)

@router.put("/{timeblock_id}", response_model=TimeBlockResponse)
def update_timeblock(
    timeblock_id: int,
    timeblock_update: TimeBlockUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Update a time block"""
    return timeblock_service.update_timeblock(db, timeblock_id, timeblock_update, current_user.id)

@router.delete("/{timeblock_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timeblock(
    timeblock_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Delete a time block"""
    result = timeblock_service.delete_timeblock(db, timeblock_id, current_user.id)
    return None

# ============= BULK OPERATIONS =============

@router.post("/bulk", response_model=List[TimeBlockResponse])
def create_multiple_timeblocks(
    timeblocks_data: List[TimeBlockCreate],
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create multiple time blocks at once"""
    created = []
    for data in timeblocks_data:
        created.append(timeblock_service.create_timeblock(db, data, current_user.id))
    return created