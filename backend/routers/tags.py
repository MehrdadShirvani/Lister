from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.dependencies import get_current_active_user
from models.account_models import Account
from models.tag_models import Tag
from schemas.tag_schemas import (
    UserTagCreate, 
    PublicTagCreate, 
    TagUpdate, 
    TagResponse,
    TagFilterParams
)
from services.tag_service import TagService

router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)

tag_service = TagService()

# ============= USER-MADE TAGS (Private) =============

@router.post("/user", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_user_tag(
    tag_data: UserTagCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create a new private tag (for authenticated user only)"""
    return tag_service.create_user_tag(db, tag_data, current_user.id)

@router.put("/user/{tag_id}", response_model=TagResponse)
def update_user_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Update a user's private tag"""
    return tag_service.update_user_tag(db, tag_id, tag_update, current_user.id)

@router.delete("/user/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Delete a user's private tag"""
    result = tag_service.delete_user_tag(db, tag_id, current_user.id)
    return None

# ============= PUBLIC TAGS (Admin only) =============

@router.post("/public", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_public_tag(
    tag_data: PublicTagCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Create a new public tag (Admin only)"""
    return tag_service.create_public_tag(db, tag_data, current_user.id)

@router.put("/public/{tag_id}", response_model=TagResponse)
def update_public_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Update a public tag (Admin only)"""
    return tag_service.update_public_tag(db, tag_id, tag_update, current_user.id)

@router.delete("/public/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_public_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Delete a public tag (Admin only)"""
    result = tag_service.delete_public_tag(db, tag_id, current_user.id)
    return None

# ============= TAG LISTING AND FILTERING =============

@router.get("/", response_model=List[TagResponse])
def get_tags(
    tag_type: Optional[str] = Query(None, description="Filter by tag type"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    search: Optional[str] = Query(None, description="Search by title"),
    created_by_me: Optional[bool] = Query(None, description="Show only tags created by me"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get tags with filtering options"""
    return tag_service.get_tags(
        db, 
        current_user.id,
        tag_type,
        is_public,
        search,
        created_by_me,
        skip,
        limit
    )

@router.get("/types", response_model=List[str])
def get_tag_types(
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get all distinct tag types"""
    return tag_service.get_tag_types(db)

@router.get("/{tag_id}", response_model=TagResponse)
def get_tag_by_id(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_user)
):
    """Get a specific tag by ID"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check permissions: can only see public tags or your own private tags
    if not tag.is_public and tag.account_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this tag"
        )
    
    return tag