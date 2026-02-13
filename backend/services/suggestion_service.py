from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from backend.schemas.plan_schemas import PlanStatus
from models.suggestion_models import Suggestion
from models.task_models import Task
from models.timeblock_models import TimeBlock
from models.plan_models import Plan
from schemas.suggestion_schemas import (
    SuggestionCreate, 
    SuggestionResponse,
    SuggestionFilterParams,
    SuggestionStatus,
    SuggestionResponseType
)

class SuggestionService:
    
    def _validate_task(self, db: Session, task_id: int, user_id: int):
        """Validate task exists and belongs to user"""
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.account_id == user_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found"
            )
        return task
    
    def _validate_timeblock(self, db: Session, time_block_id: int, user_id: int):
        """Validate timeblock exists and belongs to user"""
        timeblock = db.query(TimeBlock).filter(
            TimeBlock.id == time_block_id,
            TimeBlock.account_id == user_id
        ).first()
        
        if not timeblock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TimeBlock with id {time_block_id} not found"
            )
        return timeblock
    
    def _check_expired(self, suggestion: Suggestion):
        """Check and update expired status"""
        if suggestion.expires_at and suggestion.expires_at < datetime.now():
            if suggestion.status not in [SuggestionStatus.ACCEPTED, SuggestionStatus.REJECTED]:
                suggestion.status = SuggestionStatus.EXPIRED
                suggestion.is_expired = True
                return True
        return False
    
    def _create_plan_from_suggestion(
        self, 
        db: Session, 
        suggestion: Suggestion, 
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Plan:
        """Create a plan from an accepted suggestion"""
        
        # Get task and timeblock for details
        task = db.query(Task).filter(Task.id == suggestion.task_id).first()
        timeblock = db.query(TimeBlock).filter(TimeBlock.id == suggestion.time_block_id).first()
        
        # Create plan
        plan = Plan(
            task_id=suggestion.task_id,
            time_block_id=suggestion.time_block_id,
            account_id=user_id,
            suggestion_task_id=suggestion.task_id,
            suggestion_time_block_id=suggestion.time_block_id,
            suggestion_title=suggestion.title,
            start_time=start_time or timeblock.start_time if timeblock else None,
            end_time=end_time or timeblock.end_time if timeblock else None,
            status=PlanStatus.PLANNED,
            notes=f"Created from suggestion: {suggestion.title}"
        )
        
        db.add(plan)
        db.flush()
        
        # Link suggestion to plan
        suggestion.created_plan_id = plan.id
        
        return plan
    
    # ============= SYSTEM OPERATIONS (for suggestion generation) =============
    
    def create_suggestion(self, db: Session, suggestion_data: SuggestionCreate, user_id: int):
        """Create a new suggestion (called by the suggestion algorithm)"""
        
        # Validate task and timeblock
        task = self._validate_task(db, suggestion_data.task_id, user_id)
        timeblock = self._validate_timeblock(db, suggestion_data.time_block_id, user_id)
        
        # Check if similar suggestion already exists
        existing = db.query(Suggestion).filter(
            Suggestion.task_id == suggestion_data.task_id,
            Suggestion.time_block_id == suggestion_data.time_block_id,
            Suggestion.title == suggestion_data.title,
            Suggestion.status.in_([SuggestionStatus.PENDING, SuggestionStatus.VIEWED])
        ).first()
        
        if existing:
            # Update existing suggestion instead of creating duplicate
            existing.confidence_score = suggestion_data.confidence_score
            existing.priority = suggestion_data.priority
            existing.description = suggestion_data.description
            existing.expires_at = suggestion_data.expires_at
            existing.updated_at = datetime.now()
            db.commit()
            db.refresh(existing)
            return existing
        
        # Set expiry if not provided (default 7 days)
        expires_at = suggestion_data.expires_at or (datetime.now() + timedelta(days=7))
        
        # Create suggestion
        suggestion = Suggestion(
            task_id=suggestion_data.task_id,
            time_block_id=suggestion_data.time_block_id,
            title=suggestion_data.title,
            description=suggestion_data.description,
            confidence_score=suggestion_data.confidence_score,
            priority=suggestion_data.priority,
            expires_at=expires_at,
            status=SuggestionStatus.PENDING
        )
        
        db.add(suggestion)
        db.commit()
        db.refresh(suggestion)
        
        return suggestion
    
    def create_bulk_suggestions(self, db: Session, suggestions_data: List[SuggestionCreate], user_id: int):
        """Create multiple suggestions at once"""
        created = []
        for data in suggestions_data:
            try:
                suggestion = self.create_suggestion(db, data, user_id)
                created.append(suggestion)
            except HTTPException:
                # Skip invalid suggestions
                continue
        return created
    
    # ============= USER OPERATIONS =============
    
    def get_suggestions(
        self,
        db: Session,
        user_id: int,
        filters: SuggestionFilterParams,
        skip: int = 0,
        limit: int = 100
    ):
        """Get suggestions with filters"""
        query = db.query(Suggestion).join(
            Task, Suggestion.task_id == Task.id
        ).filter(
            Task.account_id == user_id  
        )
        
        # Filter by status
        if filters.status:
            query = query.filter(Suggestion.status == filters.status)
        elif filters.is_expired is not None:
            if filters.is_expired:
                query = query.filter(Suggestion.is_expired == True)
            else:
                query = query.filter(
                    or_(
                        Suggestion.is_expired == False,
                        Suggestion.is_expired.is_(None)
                    )
                )
        
        # Filter by task
        if filters.task_id:
            query = query.filter(Suggestion.task_id == filters.task_id)
        
        # Filter by timeblock
        if filters.time_block_id:
            query = query.filter(Suggestion.time_block_id == filters.time_block_id)
        
        # Priority/confidence filters
        if filters.priority_min:
            query = query.filter(Suggestion.priority >= filters.priority_min)
        if filters.confidence_min:
            query = query.filter(Suggestion.confidence_score >= filters.confidence_min)
        
        # Date filters
        if filters.created_after:
            query = query.filter(Suggestion.created_at >= filters.created_after)
        if filters.created_before:
            query = query.filter(Suggestion.created_at <= filters.created_before)
        if filters.expires_before:
            query = query.filter(Suggestion.expires_at <= filters.expires_before)
        
        # Order by priority and confidence
        query = query.order_by(
            Suggestion.priority.desc(),
            Suggestion.confidence_score.desc(),
            Suggestion.created_at.desc()
        )
        
        suggestions = query.offset(skip).limit(limit).all()
        
        # Check for expired and add related data
        result = []
        for suggestion in suggestions:
            self._check_expired(suggestion)
            
            # Add related data for display
            task = db.query(Task).filter(Task.id == suggestion.task_id).first()
            timeblock = db.query(TimeBlock).filter(TimeBlock.id == suggestion.time_block_id).first()
            
            suggestion_dict = {
                "task_id": suggestion.task_id,
                "time_block_id": suggestion.time_block_id,
                "title": suggestion.title,
                "description": suggestion.description,
                "confidence_score": suggestion.confidence_score,
                "priority": suggestion.priority,
                "status": suggestion.status,
                "viewed_at": suggestion.viewed_at,
                "responded_at": suggestion.responded_at,
                "expires_at": suggestion.expires_at,
                "response_notes": suggestion.response_notes,
                "created_at": suggestion.created_at,
                "task_title": task.title if task else None,
                "time_block_title": timeblock.title if timeblock else None,
                "time_block_start": timeblock.start_time if timeblock else None,
                "time_block_end": timeblock.end_time if timeblock else None
            }
            result.append(suggestion_dict)
        
        db.commit()  # Save any expiry updates
        return result
    
    def get_suggestion(self, db: Session, task_id: int, time_block_id: int, title: str, user_id: int):
        """Get a specific suggestion by its composite key"""
        suggestion = db.query(Suggestion).join(
            Task, Suggestion.task_id == Task.id
        ).filter(
            Suggestion.task_id == task_id,
            Suggestion.time_block_id == time_block_id,
            Suggestion.title == title,
            Task.account_id == user_id
        ).first()
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        
        # Check if expired
        self._check_expired(suggestion)
        
        # Mark as viewed if first time
        if not suggestion.viewed_at:
            suggestion.viewed_at = datetime.now()
            suggestion.status = SuggestionStatus.VIEWED
        
        db.commit()
        
        # Add related data
        task = db.query(Task).filter(Task.id == suggestion.task_id).first()
        timeblock = db.query(TimeBlock).filter(TimeBlock.id == suggestion.time_block_id).first()
        
        return {
            "task_id": suggestion.task_id,
            "time_block_id": suggestion.time_block_id,
            "title": suggestion.title,
            "description": suggestion.description,
            "confidence_score": suggestion.confidence_score,
            "priority": suggestion.priority,
            "status": suggestion.status,
            "viewed_at": suggestion.viewed_at,
            "responded_at": suggestion.responded_at,
            "expires_at": suggestion.expires_at,
            "response_notes": suggestion.response_notes,
            "created_at": suggestion.created_at,
            "task_title": task.title if task else None,
            "time_block_title": timeblock.title if timeblock else None,
            "time_block_start": timeblock.start_time if timeblock else None,
            "time_block_end": timeblock.end_time if timeblock else None
        }
    
    def respond_to_suggestion(
        self,
        db: Session,
        task_id: int,
        time_block_id: int,
        title: str,
        response: SuggestionResponse,
        user_id: int
    ):
        """Respond to a suggestion (accept/reject/snooze)"""
        suggestion = db.query(Suggestion).join(
            Task, Suggestion.task_id == Task.id
        ).filter(
            Suggestion.task_id == task_id,
            Suggestion.time_block_id == time_block_id,
            Suggestion.title == title,
            Task.account_id == user_id
        ).first()
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        
        # Check if already responded
        if suggestion.responded_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Suggestion has already been responded to"
            )
        
        # Check if expired
        if self._check_expired(suggestion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Suggestion has expired"
            )
        
        suggestion.responded_at = datetime.now()
        suggestion.response_notes = response.notes
        
        result = {"action": response.response, "plan": None}
        
        if response.response == SuggestionResponseType.ACCEPT:
            # Accept suggestion - create plan
            suggestion.status = SuggestionStatus.ACCEPTED
            plan = self._create_plan_from_suggestion(db, suggestion, user_id)
            result["plan"] = {"id": plan.id, "status": plan.status}
            
        elif response.response == SuggestionResponseType.REJECT:
            # Reject suggestion
            suggestion.status = SuggestionStatus.REJECTED
            
        elif response.response == SuggestionResponseType.SNOOZE:
            # Snooze - create a new suggestion with later expiry
            if not response.snooze_minutes:
                response.snooze_minutes = 60  # Default 1 hour
            
            # Create snoozed copy
            snoozed = Suggestion(
                task_id=suggestion.task_id,
                time_block_id=suggestion.time_block_id,
                title=f"{suggestion.title} (snoozed)",
                description=suggestion.description,
                confidence_score=suggestion.confidence_score,
                priority=suggestion.priority,
                expires_at=datetime.now() + timedelta(minutes=response.snooze_minutes),
                status=SuggestionStatus.PENDING
            )
            db.add(snoozed)
            
            # Mark original as rejected (with snooze note)
            suggestion.status = SuggestionStatus.REJECTED
            suggestion.response_notes = f"Snoozed until {(datetime.now() + timedelta(minutes=response.snooze_minutes)).strftime('%Y-%m-%d %H:%M')}"
        
        db.commit()
        
        return result
    
    def dismiss_suggestion(self, db: Session, task_id: int, time_block_id: int, title: str, user_id: int):
        """Dismiss/view a suggestion without responding"""
        suggestion = db.query(Suggestion).join(
            Task, Suggestion.task_id == Task.id
        ).filter(
            Suggestion.task_id == task_id,
            Suggestion.time_block_id == time_block_id,
            Suggestion.title == title,
            Task.account_id == user_id
        ).first()
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        
        if not suggestion.viewed_at:
            suggestion.viewed_at = datetime.now()
            suggestion.status = SuggestionStatus.VIEWED
            db.commit()
        
        return {"message": "Suggestion marked as viewed"}
    
    # ============= CLEANUP OPERATIONS =============
    
    def cleanup_expired_suggestions(self, db: Session, user_id: Optional[int] = None):
        """Mark expired suggestions as expired"""
        query = db.query(Suggestion).join(
            Task, Suggestion.task_id == Task.id
        )
        
        if user_id:
            query = query.filter(Task.account_id == user_id)
        
        expired = query.filter(
            Suggestion.expires_at < datetime.now(),
            Suggestion.status.in_([SuggestionStatus.PENDING, SuggestionStatus.VIEWED])
        ).all()
        
        for suggestion in expired:
            suggestion.status = SuggestionStatus.EXPIRED
            suggestion.is_expired = True
        
        db.commit()
        return len(expired)