from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from core.database import get_db
from core.dependencies import get_current_active_user
from models.account_models import Account
from schemas.suggestion_schemas import (
    SuggestionCreate,
    SuggestionResponse,
    SuggestionFilterParams,
    SuggestionStatus,
    SuggestionResponseType
)
from services.suggestion_service import SuggestionService

router = APIRouter(
    prefix="/suggestions",
    tags=["suggestions"]
)

suggestion_service = SuggestionService()

# ============= USER ENDPOINTS =============

@router.get("/", response_model=List[dict])
def get_suggestions(
    # Filter parameters
    status: Optional[SuggestionStatus] = Query(None, description="Filter by status"),
    task_id: Optional[int] = Query(None, description="Filter by task ID"),
    time_block_id: Optional[int] = Query(None, description="Filter by timeblock ID"),
    priority_min: Optional[int] = Query(None, ge=0, le=10),
    confidence_min: Optional[int] = Query(None, ge=0, le=100),
    include_expired: bool = Query(False, description="Include expired suggestions"),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    expires_before: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all suggestions with filters"""
    filters = SuggestionFilterParams(
        status=status,
        task_id=task_id,
        time_block_id=time_block_id,
        priority_min=priority_min,
        confidence_min=confidence_min,
        is_expired=include_expired if include_expired else None,
        created_after=created_after,
        created_before=created_before,
        expires_before=expires_before
    )
    
    return suggestion_service.get_suggestions(db, current_user.id, filters, skip, limit)

@router.get("/pending/count")
def get_pending_suggestions_count(
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get count of pending suggestions"""
    filters = SuggestionFilterParams(status=SuggestionStatus.PENDING)
    suggestions = suggestion_service.get_suggestions(db, current_user.id, filters, 0, 1000)
    return {"count": len(suggestions)}

@router.get("/{task_id}/{time_block_id}/{title}")
def get_suggestion(
    task_id: int,
    time_block_id: int,
    title: str,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get a specific suggestion by its composite key"""
    return suggestion_service.get_suggestion(
        db, task_id, time_block_id, title, current_user.id
    )

@router.post("/{task_id}/{time_block_id}/{title}/respond")
def respond_to_suggestion(
    task_id: int,
    time_block_id: int,
    title: str,
    response: SuggestionResponse,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Respond to a suggestion (accept/reject/snooze)"""
    return suggestion_service.respond_to_suggestion(
        db, task_id, time_block_id, title, response, current_user.id
    )

@router.post("/{task_id}/{time_block_id}/{title}/dismiss")
def dismiss_suggestion(
    task_id: int,
    time_block_id: int,
    title: str,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Dismiss/view a suggestion without responding"""
    return suggestion_service.dismiss_suggestion(
        db, task_id, time_block_id, title, current_user.id
    )

@router.post("/{task_id}/{time_block_id}/{title}/accept", response_model=dict)
def accept_suggestion(
    task_id: int,
    time_block_id: int,
    title: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Quick accept a suggestion"""
    response = SuggestionResponse(
        response=SuggestionResponseType.ACCEPT,
        notes=notes
    )
    return suggestion_service.respond_to_suggestion(
        db, task_id, time_block_id, title, response, current_user.id
    )

@router.post("/{task_id}/{time_block_id}/{title}/reject")
def reject_suggestion(
    task_id: int,
    time_block_id: int,
    title: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Quick reject a suggestion"""
    response = SuggestionResponse(
        response=SuggestionResponseType.REJECT,
        notes=notes
    )
    return suggestion_service.respond_to_suggestion(
        db, task_id, time_block_id, title, response, current_user.id
    )

# ============= SYSTEM ENDPOINTS (for suggestion algorithm) =============

@router.post("/generate", response_model=List[dict])
def create_suggestions(
    suggestions: List[SuggestionCreate],
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create multiple suggestions (called by suggestion algorithm)"""
    return suggestion_service.create_bulk_suggestions(db, suggestions, current_user.id)

@router.post("/cleanup")
def cleanup_expired_suggestions(
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Manually trigger cleanup of expired suggestions"""
    count = suggestion_service.cleanup_expired_suggestions(db, current_user.id)
    return {"message": f"Cleaned up {count} expired suggestions"}