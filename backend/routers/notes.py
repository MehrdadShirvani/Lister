from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from core.database import get_db
from core.dependencies import get_current_active_user
from models.account_models import Account
from schemas.note_schemas import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NotePreview,
    NoteFilterParams,
    NoteSortBy
)
from services.note_service import NoteService

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
)

note_service = NoteService()

# ============= CRUD ENDPOINTS =============

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create a new note"""
    return note_service.create_note(db, note_data, current_user.id)

@router.get("/", response_model=List[NotePreview])
def get_notes(
    # Filter parameters
    search: Optional[str] = Query(None, description="Search in title and content"),
    tag_ids: Optional[List[int]] = Query(None, description="Filter by tag IDs"),
    is_pinned: Optional[bool] = Query(None, description="Filter pinned notes"),
    is_favorite: Optional[bool] = Query(None, description="Filter favorite notes"),
    is_archived: Optional[bool] = Query(None, description="Filter archived notes"),
    is_follow_up: Optional[bool] = Query(None, description="Filter follow-up notes"),
    has_plan: Optional[bool] = Query(None, description="Notes with/without linked plans"),
    has_tasks: Optional[bool] = Query(None, description="Notes with/without linked tasks"),
    has_related_notes: Optional[bool] = Query(None, description="Notes with/without related notes"),
    quality_score_min: Optional[int] = Query(None, ge=0, le=10),
    quality_score_max: Optional[int] = Query(None, ge=0, le=10),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    updated_after: Optional[datetime] = Query(None),
    sort_by: NoteSortBy = Query(NoteSortBy.UPDATED_AT),
    sort_desc: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all notes with filters"""
    filters = NoteFilterParams(
        search=search,
        tag_ids=tag_ids,
        is_pinned=is_pinned,
        is_favorite=is_favorite,
        is_archived=is_archived,
        is_follow_up=is_follow_up,
        has_plan=has_plan,
        has_tasks=has_tasks,
        has_related_notes=has_related_notes,
        quality_score_min=quality_score_min,
        quality_score_max=quality_score_max,
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        sort_by=sort_by,
        sort_desc=sort_desc
    )
    
    return note_service.get_notes(db, current_user.id, filters, skip, limit)

@router.get("/search", response_model=List[NotePreview])
def search_notes(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Full-text search in notes"""
    return note_service.search_notes(db, current_user.id, q, limit)

@router.get("/by-tag/{tag_id}", response_model=List[NotePreview])
def get_notes_by_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all notes with a specific tag"""
    return note_service.get_notes_by_tag(db, tag_id, current_user.id)

@router.get("/by-task/{task_id}", response_model=List[NoteResponse])
def get_notes_by_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all notes linked to a specific task"""
    return note_service.get_notes_by_task(db, task_id, current_user.id)

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get a specific note by ID"""
    return note_service.get_note(db, note_id, current_user.id)

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Update a note"""
    return note_service.update_note(db, note_id, note_update, current_user.id)

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Delete a note"""
    result = note_service.delete_note(db, note_id, current_user.id)
    return None

# ============= NOTE OPERATIONS =============

@router.post("/{note_id}/pin", response_model=NoteResponse)
def toggle_pin(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Toggle pin status of a note"""
    return note_service.toggle_pin(db, note_id, current_user.id)

@router.post("/{note_id}/favorite", response_model=NoteResponse)
def toggle_favorite(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Toggle favorite status of a note"""
    return note_service.toggle_favorite(db, note_id, current_user.id)

@router.post("/{note_id}/archive", response_model=NoteResponse)
def archive_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Archive a note"""
    return note_service.archive_note(db, note_id, current_user.id)

@router.post("/{note_id}/restore", response_model=NoteResponse)
def restore_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Restore an archived note"""
    return note_service.restore_note(db, note_id, current_user.id)

# ============= PLAN FOLLOW-UP =============

@router.post("/from-plan/{plan_id}", response_model=NoteResponse)
def create_follow_up_for_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create a follow-up note for a plan"""
    return note_service.create_follow_up_for_plan(db, plan_id, current_user.id)

# ============= BULK OPERATIONS =============

@router.post("/bulk", response_model=List[NoteResponse])
def create_multiple_notes(
    notes_data: List[NoteCreate],
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create multiple notes at once"""
    created = []
    for data in notes_data:
        created.append(note_service.create_note(db, data, current_user.id))
    return created

@router.post("/{note_id}/duplicate", response_model=NoteResponse)
def duplicate_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Duplicate a note"""
    original = note_service.get_note(db, note_id, current_user.id)
    
    duplicate_data = NoteCreate(
        title=f"{original.title} (copy)",
        content=original.content,
        quality_score=original.quality_score,
        is_pinned=False,  
        is_favorite=False,
        formatting_data=original.formatting_data,
        tag_ids=[tag.id for tag in original.tags],
        related_note_ids=[n.id for n in original.related_notes],
        task_ids=[t.id for t in original.tasks]
    )
    
    return note_service.create_note(db, duplicate_data, current_user.id)