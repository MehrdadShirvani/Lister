from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from models.plan_models import Plan
from models.task_models import Task
from models.note_models import Note
from models.timeblock_models import TimeBlock
from schemas.plan_schemas import (
    PlanCreate,
    PlanUpdate,
    PlanFromSuggestion,
    PlanAction,
    PlanFilterParams,
    PlanStatus
)

class PlanService:
    
    def _validate_task(self, db: Session, task_id: Optional[int], user_id: int):
        """Validate task exists and belongs to user"""
        if not task_id:
            return None
        
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
    
    def _validate_note(self, db: Session, note_id: Optional[int], user_id: int):
        """Validate note exists and belongs to user"""
        if not note_id:
            return None
        
        note = db.query(Note).filter(
            Note.id == note_id,
            Note.account_id == user_id
        ).first()
        
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note with id {note_id} not found"
            )
        return note
    
    def _validate_timeblock(self, db: Session, time_block_id: Optional[int], user_id: int):
        """Validate timeblock exists and belongs to user"""
        if not time_block_id:
            return None
        
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
    
    def _add_related_data(self, db: Session, plan: Plan) -> dict:
        """Add related data to plan for response"""
        plan_dict = {
            "id": plan.id,
            "account_id": plan.account_id,
            "task_id": plan.task_id,
            "note_id": plan.note_id,
            "time_block_id": plan.time_block_id,
            "start_time": plan.start_time,
            "end_time": plan.end_time,
            "actual_start_time": plan.actual_start_time,
            "actual_end_time": plan.actual_end_time,
            "status": plan.status,
            "progress": plan.progress,
            "notes": plan.notes,
            "created_at": plan.created_at,
            "updated_at": plan.updated_at,
            "completion_rate": plan.completion_rate,
            "from_suggestion": plan.suggestion_task_id is not None
        }
        
        # Add related titles
        if plan.task:
            plan_dict["task_title"] = plan.task.title
            plan_dict["task_status"] = plan.task.status
        
        if plan.note:
            plan_dict["note_title"] = plan.note.title
        
        if plan.time_block:
            plan_dict["time_block_title"] = plan.time_block.title
        
        # Add suggestion details if from suggestion
        if plan.from_suggestion:
            plan_dict["suggestion_details"] = {
                "task_id": plan.suggestion_task_id,
                "time_block_id": plan.suggestion_time_block_id,
                "title": plan.suggestion_title
            }
        
        return plan_dict
    
    # ============= CREATE =============
    
    def create_plan(self, db: Session, plan_data: PlanCreate, user_id: int):
        """Create a new plan manually"""
        
        # Validate relationships
        self._validate_task(db, plan_data.task_id, user_id)
        self._validate_note(db, plan_data.note_id, user_id)
        self._validate_timeblock(db, plan_data.time_block_id, user_id)
        
        # Create plan
        plan = Plan(
            account_id=user_id,
            task_id=plan_data.task_id,
            note_id=plan_data.note_id,
            time_block_id=plan_data.time_block_id,
            start_time=plan_data.start_time,
            end_time=plan_data.end_time,
            status=plan_data.status.value if plan_data.status else "planned",
            progress=plan_data.progress,
            notes=plan_data.notes
        )
        
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        return self._add_related_data(db, plan)
    
    def create_plan_from_suggestion(self, db: Session, plan_data: PlanFromSuggestion, user_id: int):
        """Create a plan from a suggestion (called when suggestion accepted)"""
        
        # Validate that the suggestion exists and belongs to user
        from models.suggestion_models import Suggestion
        
        suggestion = db.query(Suggestion).join(
            Task, Suggestion.task_id == Task.id
        ).filter(
            Suggestion.task_id == plan_data.suggestion_task_id,
            Suggestion.time_block_id == plan_data.suggestion_time_block_id,
            Suggestion.title == plan_data.suggestion_title,
            Task.account_id == user_id
        ).first()
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        
        # Get task and timeblock
        task = self._validate_task(db, plan_data.suggestion_task_id, user_id)
        timeblock = self._validate_timeblock(db, plan_data.suggestion_time_block_id, user_id)
        
        # Create plan
        plan = Plan(
            account_id=user_id,
            task_id=plan_data.suggestion_task_id,
            time_block_id=plan_data.suggestion_time_block_id,
            suggestion_task_id=plan_data.suggestion_task_id,
            suggestion_time_block_id=plan_data.suggestion_time_block_id,
            suggestion_title=plan_data.suggestion_title,
            start_time=plan_data.start_time or timeblock.start_time,
            end_time=plan_data.end_time or timeblock.end_time,
            status=PlanStatus.PLANNED,
            notes=plan_data.notes or f"Created from suggestion: {suggestion.title}"
        )
        
        db.add(plan)
        db.flush()
        
        # Update suggestion to link to plan
        suggestion.created_plan_id = plan.id
        suggestion.status = "accepted"
        
        db.commit()
        db.refresh(plan)
        
        return self._add_related_data(db, plan)
    
    # ============= READ =============
    
    def get_plan(self, db: Session, plan_id: int, user_id: int):
        """Get a specific plan by ID"""
        plan = db.query(Plan).options(
            joinedload(Plan.task),
            joinedload(Plan.note),
            joinedload(Plan.time_block)
        ).filter(
            Plan.id == plan_id,
            Plan.account_id == user_id
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        return self._add_related_data(db, plan)
    
    def get_plans(
        self,
        db: Session,
        user_id: int,
        filters: PlanFilterParams,
        skip: int = 0,
        limit: int = 100
    ):
        """Get plans with filters"""
        query = db.query(Plan).options(
            joinedload(Plan.task),
            joinedload(Plan.note),
            joinedload(Plan.time_block)
        ).filter(Plan.account_id == user_id)
        
        # Filter by status
        if filters.status:
            query = query.filter(Plan.status == filters.status)
        
        # Filter by task
        if filters.task_id:
            query = query.filter(Plan.task_id == filters.task_id)
        
        # Filter by timeblock
        if filters.time_block_id:
            query = query.filter(Plan.time_block_id == filters.time_block_id)
        
        # Filter by note presence
        if filters.has_note is not None:
            if filters.has_note:
                query = query.filter(Plan.note_id.isnot(None))
            else:
                query = query.filter(Plan.note_id.is_(None))
        
        # Date range
        if filters.date_from:
            query = query.filter(Plan.start_time >= filters.date_from)
        if filters.date_to:
            query = query.filter(Plan.end_time <= filters.date_to)
        
        # Recurring
        if filters.is_recurring is not None:
            query = query.filter(Plan.is_recurring == filters.is_recurring)
        
        # Progress range
        if filters.progress_min is not None:
            query = query.filter(Plan.progress >= filters.progress_min)
        if filters.progress_max is not None:
            query = query.filter(Plan.progress <= filters.progress_max)
        
        # From suggestion
        if filters.from_suggestion is not None:
            if filters.from_suggestion:
                query = query.filter(Plan.suggestion_task_id.isnot(None))
            else:
                query = query.filter(Plan.suggestion_task_id.is_(None))
        
        # Order by start time
        query = query.order_by(Plan.start_time.asc().nullslast())
        
        plans = query.offset(skip).limit(limit).all()
        
        return [self._add_related_data(db, plan) for plan in plans]
    
    def get_today_plans(self, db: Session, user_id: int):
        """Get plans for today"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59)
        
        return self.get_plans(
            db, user_id,
            PlanFilterParams(
                date_from=today_start,
                date_to=today_end
            )
        )
    
    def get_upcoming_plans(self, db: Session, user_id: int, days: int = 7):
        """Get plans for the next X days"""
        now = datetime.now()
        future = now + timedelta(days=days)
        
        return self.get_plans(
            db, user_id,
            PlanFilterParams(
                date_from=now,
                date_to=future,
                status=PlanStatus.PLANNED
            )
        )
    
    # ============= UPDATE =============
    
    def update_plan(
        self,
        db: Session,
        plan_id: int,
        plan_update: PlanUpdate,
        user_id: int
    ):
        """Update a plan"""
        plan = db.query(Plan).filter(
            Plan.id == plan_id,
            Plan.account_id == user_id
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        update_data = plan_update.model_dump(exclude_unset=True)
        
        # Validate relationships if being updated
        if "task_id" in update_data:
            self._validate_task(db, update_data["task_id"], user_id)
        
        if "note_id" in update_data:
            self._validate_note(db, update_data["note_id"], user_id)
        
        if "time_block_id" in update_data:
            self._validate_timeblock(db, update_data["time_block_id"], user_id)
        
        # Handle status enum
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].value
        
        # Update fields
        for field, value in update_data.items():
            setattr(plan, field, value)
        
        # Calculate completion rate if status changed to completed
        if plan.status == "completed" and plan.start_time and plan.end_time:
            if plan.actual_start_time and plan.actual_end_time:
                planned_duration = (plan.end_time - plan.start_time).total_seconds()
                actual_duration = (plan.actual_end_time - plan.actual_start_time).total_seconds()
                if planned_duration > 0:
                    plan.completion_rate = min(100, (actual_duration / planned_duration) * 100)
        
        db.commit()
        db.refresh(plan)
        
        return self._add_related_data(db, plan)
    
    def plan_action(self, db: Session, plan_id: int, action: PlanAction, user_id: int):
        """Perform an action on a plan (start, complete, etc.)"""
        plan = db.query(Plan).filter(
            Plan.id == plan_id,
            Plan.account_id == user_id
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        action_time = action.timestamp or datetime.now()
        
        if action.action == "start":
            if plan.status != "planned":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot start plan with status {plan.status}"
                )
            plan.status = "in_progress"
            plan.actual_start_time = action_time
            if action.notes:
                plan.notes = (plan.notes or "") + f"\nStarted: {action.notes}"
        
        elif action.action == "pause":
            if plan.status != "in_progress":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only pause in-progress plans"
                )
            plan.status = "paused"
        
        elif action.action == "resume":
            if plan.status != "paused":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only resume paused plans"
                )
            plan.status = "in_progress"
        
        elif action.action == "complete":
            if plan.status not in ["in_progress", "planned", "paused"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot complete plan with status {plan.status}"
                )
            plan.status = "completed"
            plan.actual_end_time = action_time
            plan.progress = 100
            
            # Calculate completion rate
            if plan.start_time and plan.actual_start_time:
                planned_duration = (plan.end_time - plan.start_time).total_seconds() if plan.end_time else 3600
                actual_duration = (action_time - plan.actual_start_time).total_seconds()
                if planned_duration > 0:
                    plan.completion_rate = min(100, (actual_duration / planned_duration) * 100)
            
            if action.notes:
                plan.notes = (plan.notes or "") + f"\nCompleted: {action.notes}"
        
        elif action.action == "cancel":
            plan.status = "cancelled"
            if action.notes:
                plan.notes = (plan.notes or "") + f"\nCancelled: {action.notes}"
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown action: {action.action}"
            )
        
        db.commit()
        db.refresh(plan)
        
        return self._add_related_data(db, plan)
    
    # ============= DELETE =============
    
    def delete_plan(self, db: Session, plan_id: int, user_id: int):
        """Delete a plan"""
        plan = db.query(Plan).filter(
            Plan.id == plan_id,
            Plan.account_id == user_id
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        db.delete(plan)
        db.commit()
        return {"message": "Plan deleted successfully"}