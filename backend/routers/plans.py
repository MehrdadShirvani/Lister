from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from core.database import get_db
from core.dependencies import get_current_active_user
from models.account_models import Account
from schemas.plan_schemas import (
    PlanCreate,
    PlanUpdate,
    PlanFromSuggestion,
    PlanAction,
    PlanFilterParams,
    PlanStatus,
    PlanResponse
)
from services.plan_service import PlanService

router = APIRouter(
    prefix="/plans",
    tags=["plans"]
)

plan_service = PlanService()

# ============= CRUD ENDPOINTS =============

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create a new plan manually"""
    return plan_service.create_plan(db, plan_data, current_user.id)

@router.post("/from-suggestion", response_model=dict)
def create_plan_from_suggestion(
    plan_data: PlanFromSuggestion,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create a plan from an accepted suggestion"""
    return plan_service.create_plan_from_suggestion(db, plan_data, current_user.id)

@router.get("/", response_model=List[dict])
def get_plans(
    # Filter parameters
    status: Optional[PlanStatus] = Query(None, description="Filter by status"),
    task_id: Optional[int] = Query(None, description="Filter by task ID"),
    time_block_id: Optional[int] = Query(None, description="Filter by timeblock ID"),
    has_note: Optional[bool] = Query(None, description="Plans with/without notes"),
    date_from: Optional[datetime] = Query(None, description="Plans starting after this"),
    date_to: Optional[datetime] = Query(None, description="Plans ending before this"),
    is_recurring: Optional[bool] = Query(None),
    progress_min: Optional[int] = Query(None, ge=0, le=100),
    progress_max: Optional[int] = Query(None, ge=0, le=100),
    from_suggestion: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all plans with filters"""
    filters = PlanFilterParams(
        status=status,
        task_id=task_id,
        time_block_id=time_block_id,
        has_note=has_note,
        date_from=date_from,
        date_to=date_to,
        is_recurring=is_recurring,
        progress_min=progress_min,
        progress_max=progress_max,
        from_suggestion=from_suggestion
    )
    
    return plan_service.get_plans(db, current_user.id, filters, skip, limit)

@router.get("/today", response_model=List[dict])
def get_today_plans(
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get plans for today"""
    return plan_service.get_today_plans(db, current_user.id)

@router.get("/upcoming", response_model=List[dict])
def get_upcoming_plans(
    days: int = Query(7, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get upcoming plans"""
    return plan_service.get_upcoming_plans(db, current_user.id, days)

@router.get("/{plan_id}", response_model=dict)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get a specific plan by ID"""
    return plan_service.get_plan(db, plan_id, current_user.id)

@router.put("/{plan_id}", response_model=dict)
def update_plan(
    plan_id: int,
    plan_update: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Update a plan"""
    return plan_service.update_plan(db, plan_id, plan_update, current_user.id)

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Delete a plan"""
    result = plan_service.delete_plan(db, plan_id, current_user.id)
    return None

# ============= PLAN ACTIONS =============

@router.post("/{plan_id}/action")
def plan_action(
    plan_id: int,
    action: PlanAction,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Perform an action on a plan (start, complete, etc.)"""
    return plan_service.plan_action(db, plan_id, action, current_user.id)

@router.post("/{plan_id}/start", response_model=dict)
def start_plan(
    plan_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Quick start a plan"""
    action = PlanAction(action="start", notes=notes)
    return plan_service.plan_action(db, plan_id, action, current_user.id)

@router.post("/{plan_id}/complete", response_model=dict)
def complete_plan(
    plan_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Quick complete a plan"""
    action = PlanAction(action="complete", notes=notes)
    return plan_service.plan_action(db, plan_id, action, current_user.id)

@router.post("/{plan_id}/cancel", response_model=dict)
def cancel_plan(
    plan_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Quick cancel a plan"""
    action = PlanAction(action="cancel", notes=notes)
    return plan_service.plan_action(db, plan_id, action, current_user.id)