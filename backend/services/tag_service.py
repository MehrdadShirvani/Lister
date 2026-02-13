from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import List, Optional
from models.tag_models import Tag
from models.account_models import Account, AccountRole
from schemas.tag_schemas import UserTagCreate, PublicTagCreate, TagUpdate

class TagService:
    
    # ============= USER-MADE TAGS =============
    def create_user_tag(self, db: Session, tag_data: UserTagCreate, user_id: int):
        """Create a new private tag for the authenticated user"""
        # Check if tag with same title already exists for this user
        existing_tag = db.query(Tag).filter(
            Tag.title == tag_data.title,
            Tag.account_id == user_id,
            Tag.is_public == False
        ).first()
        
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a tag with this name"
            )
        
        # Create new tag
        new_tag = Tag(
            title=tag_data.title,
            type=tag_data.type,
            description=tag_data.description,
            account_id=user_id,
            is_public=False
        )
        
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag
    
    def update_user_tag(self, db: Session, tag_id: int, tag_update: TagUpdate, user_id: int):
        """Update a user's private tag"""
        # Find the tag and verify ownership
        tag = db.query(Tag).filter(
            Tag.id == tag_id,
            Tag.account_id == user_id,
            Tag.is_public == False
        ).first()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found or you don't have permission to edit it"
            )
        
        # If title is being updated, check for duplicates
        if tag_update.title and tag_update.title != tag.title:
            duplicate = db.query(Tag).filter(
                Tag.title == tag_update.title,
                Tag.account_id == user_id,
                Tag.is_public == False,
                Tag.id != tag_id
            ).first()
            
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You already have a tag with this name"
                )
        
        # Update fields
        update_data = tag_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)
        
        db.commit()
        db.refresh(tag)
        return tag
    
    def delete_user_tag(self, db: Session, tag_id: int, user_id: int):
        """Delete a user's private tag"""
        tag = db.query(Tag).filter(
            Tag.id == tag_id,
            Tag.account_id == user_id,
            Tag.is_public == False
        ).first()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found or you don't have permission to delete it"
            )
        
        db.delete(tag)
        db.commit()
        return {"message": "Tag deleted successfully"}
    
    # ============= PUBLIC TAGS (Admin only) =============
    
    def _check_admin(self, db: Session, user_id: int):
        """Check if user is admin"""
        user = db.query(Account).filter(Account.id == user_id).first()
        if not user or user.role.name != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can perform this action"
            )
        return True
    
    def create_public_tag(self, db: Session, tag_data: PublicTagCreate, admin_id: int):
        """Create a new public tag (admin only)"""
        # Verify admin
        self._check_admin(db, admin_id)
        
        # Check if public tag with same title exists
        existing_tag = db.query(Tag).filter(
            Tag.title == tag_data.title,
            Tag.is_public == True
        ).first()
        
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A public tag with this name already exists"
            )
        
        # Create public tag
        new_tag = Tag(
            title=tag_data.title,
            type=tag_data.type,
            description=tag_data.description,
            account_id=admin_id,  
            is_public=True
        )
        
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag
    
    def update_public_tag(self, db: Session, tag_id: int, tag_update: TagUpdate, admin_id: int):
        """Update a public tag (admin only)"""
        # Verify admin
        self._check_admin(db, admin_id)
        
        # Find public tag
        tag = db.query(Tag).filter(
            Tag.id == tag_id,
            Tag.is_public == True
        ).first()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Public tag not found"
            )
        
        # Check for duplicate title
        if tag_update.title and tag_update.title != tag.title:
            duplicate = db.query(Tag).filter(
                Tag.title == tag_update.title,
                Tag.is_public == True,
                Tag.id != tag_id
            ).first()
            
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A public tag with this name already exists"
                )
        
        update_data = tag_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)
        
        db.commit()
        db.refresh(tag)
        return tag
    
    def delete_public_tag(self, db: Session, tag_id: int, admin_id: int):
        """Delete a public tag (admin only)"""
        # Verify admin
        self._check_admin(db, admin_id)
        
        # Find public tag
        tag = db.query(Tag).filter(
            Tag.id == tag_id,
            Tag.is_public == True
        ).first()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Public tag not found"
            )
        
        db.delete(tag)
        db.commit()
        return {"message": "Public tag deleted successfully"}
    
    # ============= TAG FILTERING AND LISTING =============
    
    def get_tags(
        self, 
        db: Session, 
        user_id: int,
        tag_type: Optional[str] = None,
        is_public: Optional[bool] = None,
        search: Optional[str] = None,
        created_by_me: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ):
        """Get tags with various filters"""
        query = db.query(Tag)
        
        # Filter by type
        if tag_type:
            query = query.filter(Tag.type == tag_type)
        
        # Filter by public/private
        if is_public is not None:
            query = query.filter(Tag.is_public == is_public)
        
        # Search by title
        if search:
            query = query.filter(Tag.title.ilike(f"%{search}%"))
        
        # Filter by ownership
        if created_by_me is not None:
            if created_by_me:
                query = query.filter(Tag.account_id == user_id)
            else:
                query = query.filter(
                    or_(
                        Tag.account_id != user_id,
                        Tag.account_id.is_(None)
                    )
                )
        
        if not is_public and not created_by_me and not search:
            query = query.filter(
                or_(
                    Tag.is_public == True,
                    Tag.account_id == user_id
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def get_tag_types(self, db: Session) -> List[str]:
        """Get all distinct tag types"""
        types = db.query(Tag.type).distinct().filter(Tag.type.isnot(None)).all()
        return [t[0] for t in types if t[0]]