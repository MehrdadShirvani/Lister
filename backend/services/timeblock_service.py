from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from models.timeblock_models import TimeBlock
from models.tag_models import Tag
from schemas.timeblock_schemas import TimeBlockCreate, TimeBlockUpdate, TimeBlockFilterParams

class TimeBlockService:
    
    # Energy levels mapping
    ENERGY_LEVELS = ["Very Low", "Low", "Medium", "High", "Very High"]
    
    def _get_energy_tags(self, db: Session, user_id: int):
        """Get all energy tags available to user (public + user's private)"""
        return db.query(Tag).filter(
            Tag.type == "Energy",
            or_(
                Tag.is_public == True,
                Tag.account_id == user_id
            )
        ).all()
    
    def _validate_energy_tags(self, db: Session, energy_tag_ids: List[int], user_id: int):
        """Validate that provided tag IDs are actually energy tags"""
        if not energy_tag_ids:
            return []
        
        energy_tags = self._get_energy_tags(db, user_id)
        valid_ids = [tag.id for tag in energy_tags]
        
        for tag_id in energy_tag_ids:
            if tag_id not in valid_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tag ID {tag_id} is not a valid energy tag"
                )
        return energy_tag_ids
    
    def _validate_other_tags(self, db: Session, other_tag_ids: List[int], user_id: int):
        """Validate other tags (public + user's private)"""
        if not other_tag_ids:
            return []
        
        valid_tags = db.query(Tag).filter(
            Tag.id.in_(other_tag_ids),
            or_(
                Tag.is_public == True,
                Tag.account_id == user_id
            )
        ).all()
        
        valid_ids = [tag.id for tag in valid_tags]
        invalid_ids = set(other_tag_ids) - set(valid_ids)
        
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tag IDs: {invalid_ids}"
            )
        
        return valid_ids
    
    def _organize_tags(self, db: Session, timeblock: TimeBlock):
        """Organize tags into energy and other categories"""
        result = {
            "energy_tag": None,
            "other_tags": []
        }
        
        for tag in timeblock.tags:
            tag_info = {
                "id": tag.id,
                "title": tag.title,
                "type": tag.type,
                "is_public": tag.is_public
            }
            
            if tag.type == "Energy":
                result["energy_tag"] = {
                    "level": tag.title,
                    "tag_id": tag.id
                }
            else:
                result["other_tags"].append(tag_info)
        
        return result
    
    # ============= CREATE =============
    
    def create_timeblock(
        self, 
        db: Session, 
        timeblock_data: TimeBlockCreate, 
        user_id: int
    ):
        """Create a new time block"""
        
        # Validate energy tags
        energy_tag_ids = []
        if timeblock_data.energy_tag_ids:
            energy_tag_ids = self._validate_energy_tags(
                db, timeblock_data.energy_tag_ids, user_id
            )
        
        # Validate other tags
        other_tag_ids = []
        if timeblock_data.other_tag_ids:
            other_tag_ids = self._validate_other_tags(
                db, timeblock_data.other_tag_ids, user_id
            )
        
        # Create time block
        timeblock = TimeBlock(
            account_id=user_id,
            title=timeblock_data.title,
            description=timeblock_data.description,
            start_time=timeblock_data.start_time,
            end_time=timeblock_data.end_time,
            block_type=timeblock_data.block_type.value if timeblock_data.block_type else "general",
            status=timeblock_data.status.value if timeblock_data.status else "planned",
            is_recurring=timeblock_data.is_recurring,
            recurrence_rule=timeblock_data.recurrence_rule.value if timeblock_data.recurrence_rule else None,
            day_of_week=timeblock_data.day_of_week
        )
        
        db.add(timeblock)
        db.flush()  
        
        # Add tags
        all_tag_ids = energy_tag_ids + other_tag_ids
        if all_tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(all_tag_ids)).all()
            timeblock.tags = tags
        
        db.commit()
        db.refresh(timeblock)
        
        # Organize tags for response
        tag_info = self._organize_tags(db, timeblock)
        timeblock.energy_tag = tag_info["energy_tag"]
        timeblock.other_tags = tag_info["other_tags"]
        
        return timeblock
    
    # ============= READ =============
    
    def get_timeblock(self, db: Session, timeblock_id: int, user_id: int):
        """Get a specific time block"""
        timeblock = db.query(TimeBlock).filter(
            TimeBlock.id == timeblock_id,
            TimeBlock.account_id == user_id
        ).first()
        
        if not timeblock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time block not found"
            )
        
        # Organize tags
        tag_info = self._organize_tags(db, timeblock)
        timeblock.energy_tag = tag_info["energy_tag"]
        timeblock.other_tags = tag_info["other_tags"]
        
        return timeblock
    
    def get_timeblocks(
        self,
        db: Session,
        user_id: int,
        filters: TimeBlockFilterParams,
        skip: int = 0,
        limit: int = 100
    ):
        """Get time blocks with filtering"""
        query = db.query(TimeBlock).filter(TimeBlock.account_id == user_id)
        
        # Filter by date range
        if filters.start_date:
            query = query.filter(TimeBlock.start_time >= filters.start_date)
        if filters.end_date:
            query = query.filter(TimeBlock.end_time <= filters.end_date)
        
        # Filter by block type
        if filters.block_type:
            query = query.filter(TimeBlock.block_type == filters.block_type.value)
        
        # Filter by status
        if filters.status:
            query = query.filter(TimeBlock.status == filters.status.value)
        
        # Filter by recurring
        if filters.is_recurring is not None:
            query = query.filter(TimeBlock.is_recurring == filters.is_recurring)
        
        # Filter by energy level
        if filters.energy_level:
            # Find energy tag with that level
            energy_tag = db.query(Tag).filter(
                Tag.type == "Energy",
                Tag.title == filters.energy_level,
                or_(
                    Tag.is_public == True,
                    Tag.account_id == user_id
                )
            ).first()
            
            if energy_tag:
                query = query.join(TimeBlock.tags).filter(Tag.id == energy_tag.id)
            else:
                # No time blocks with that energy level
                return []
        
        # Filter by tag IDs
        if filters.tag_ids:
            query = query.join(TimeBlock.tags).filter(Tag.id.in_(filters.tag_ids))
        
        # Search in title/description
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    TimeBlock.title.ilike(search_term),
                    TimeBlock.description.ilike(search_term)
                )
            )
        
        # Order by start time
        query = query.order_by(TimeBlock.start_time)
        
        # Get results
        timeblocks = query.offset(skip).limit(limit).all()
        
        # Organize tags for each timeblock
        for tb in timeblocks:
            tag_info = self._organize_tags(db, tb)
            tb.energy_tag = tag_info["energy_tag"]
            tb.other_tags = tag_info["other_tags"]
        
        return timeblocks
    
    # ============= UPDATE =============
    
    def update_timeblock(
        self,
        db: Session,
        timeblock_id: int,
        timeblock_update: TimeBlockUpdate,
        user_id: int
    ):
        """Update a time block"""
        timeblock = db.query(TimeBlock).filter(
            TimeBlock.id == timeblock_id,
            TimeBlock.account_id == user_id
        ).first()
        
        if not timeblock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time block not found"
            )
        
        update_data = timeblock_update.model_dump(exclude_unset=True)
        
        # Handle enum conversions
        if "block_type" in update_data and update_data["block_type"]:
            update_data["block_type"] = update_data["block_type"].value
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].value
        if "recurrence_rule" in update_data and update_data["recurrence_rule"]:
            update_data["recurrence_rule"] = update_data["recurrence_rule"].value
        
        # Handle tag updates separately
        tag_ids_to_update = []
        if "energy_tag_ids" in update_data or "other_tag_ids" in update_data:
            energy_ids = update_data.pop("energy_tag_ids", []) or []
            other_ids = update_data.pop("other_tag_ids", []) or []
            
            # Validate tags
            if energy_ids:
                energy_ids = self._validate_energy_tags(db, energy_ids, user_id)
            if other_ids:
                other_ids = self._validate_other_tags(db, other_ids, user_id)
            
            tag_ids_to_update = energy_ids + other_ids
        
        # Update basic fields
        for field, value in update_data.items():
            setattr(timeblock, field, value)
        
        # Update tags if needed
        if tag_ids_to_update:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids_to_update)).all()
            timeblock.tags = tags
        
        db.commit()
        db.refresh(timeblock)
        
        tag_info = self._organize_tags(db, timeblock)
        timeblock.energy_tag = tag_info["energy_tag"]
        timeblock.other_tags = tag_info["other_tags"]
        
        return timeblock
    
    # ============= DELETE =============
    
    def delete_timeblock(self, db: Session, timeblock_id: int, user_id: int):
        """Delete a time block"""
        timeblock = db.query(TimeBlock).filter(
            TimeBlock.id == timeblock_id,
            TimeBlock.account_id == user_id
        ).first()
        
        if not timeblock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time block not found"
            )
        
        db.delete(timeblock)
        db.commit()
        return {"message": "Time block deleted successfully"}
    
    # ============= UTILITY =============
    
    def get_energy_levels(self, db: Session, user_id: int):
        """Get available energy levels with tag info"""
        energy_tags = self._get_energy_tags(db, user_id)
        
        return [
            {
                "level": tag.title,
                "tag_id": tag.id,
                "description": tag.description,
                "is_public": tag.is_public
            }
            for tag in energy_tags
        ]
    
    def get_upcoming_timeblocks(self, db: Session, user_id: int, days: int = 7):
        """Get time blocks for the next X days"""
        now = datetime.now()
        end_date = datetime.now().replace(
            hour=23, minute=59, second=59
        ) + timedelta(days=days)
        
        return self.get_timeblocks(
            db, user_id,
            TimeBlockFilterParams(
                start_date=now,
                end_date=end_date
            )
        )