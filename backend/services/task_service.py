from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, not_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, date
from models.task_models import Task, TaskUrl
from models.tag_models import Tag
from models.list_models import List
from models.plan_models import Plan
from schemas.task_schemas import TaskCreate, TaskUpdate, TaskFilterParams

class TaskService:
    
    def _validate_tags(self, db: Session, tag_ids: List[int], user_id: int):
        """Validate that tags exist and are accessible by user"""
        if not tag_ids:
            return []
        
        valid_tags = db.query(Tag).filter(
            Tag.id.in_(tag_ids),
            or_(
                Tag.is_public == True,
                Tag.account_id == user_id
            )
        ).all()
        
        valid_ids = [tag.id for tag in valid_tags]
        invalid_ids = set(tag_ids) - set(valid_ids)
        
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tag IDs (not found or no permission): {invalid_ids}"
            )
        
        return valid_ids
    
    def _validate_parent_task(self, db: Session, task_id: Optional[int], parent_id: Optional[int], user_id: int):
        """Validate parent task relationship"""
        if not parent_id:
            return True
        
        # Check if parent exists and belongs to user
        parent = db.query(Task).filter(
            Task.id == parent_id,
            Task.account_id == user_id
        ).first()
        
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent task not found"
            )
        
        # Check for circular reference
        if task_id:  # When updating existing task
            if task_id == parent_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task cannot be its own parent"
                )
            
            # Check if parent is actually a descendant (would create cycle)
            current = parent
            while current.parent_task_id:
                if current.parent_task_id == task_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot set parent that would create a circular reference"
                    )
                current = db.query(Task).get(current.parent_task_id)
        
        return True
    
    def _validate_list(self, db: Session, list_id: Optional[int], user_id: int):
        """Validate that list exists and belongs to user"""
        if not list_id:
            return True
        
        list_obj = db.query(List).filter(
            List.id == list_id,
            List.account_id == user_id
        ).first()
        
        if not list_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="List not found"
            )
        
        return True
    
    def _process_urls(self, db: Session, task: Task, urls: List[str]):
        """Add URLs to task"""
        if not urls:
            return
        
        for url in urls:
            # Check if URL already exists for this task
            existing = db.query(TaskUrl).filter(
                TaskUrl.task_id == task.id,
                TaskUrl.url == url
            ).first()
            
            if not existing:
                task_url = TaskUrl(task_id=task.id, url=url)
                db.add(task_url)
    
    def _remove_urls(self, db: Session, task: Task, urls: List[str]):
        """Remove specific URLs from task"""
        if not urls:
            return
        
        db.query(TaskUrl).filter(
            TaskUrl.task_id == task.id,
            TaskUrl.url.in_(urls)
        ).delete(synchronize_session=False)
    
    def _get_task_hierarchy(self, db: Session, task: Task, visited=None):
        """Build task hierarchy tree, checking for cycles"""
        if visited is None:
            visited = set()
        
        if task.id in visited:
            return None  # Cycle detected
        
        visited.add(task.id)
        
        result = {
            "id": task.id,
            "title": task.title,
            "type": task.type,
            "status": task.status,
            "priority": task.priority,
            "scheduled_date": task.scheduled_date,
            "children": []
        }
        
        # Load subtasks
        subtasks = db.query(Task).filter(
            Task.parent_task_id == task.id,
            Task.account_id == task.account_id
        ).all()
        
        for subtask in subtasks:
            child = self._get_task_hierarchy(db, subtask, visited.copy())
            if child:
                result["children"].append(child)
        
        return result
    
    # ============= CREATE =============
    
    def create_task(self, db: Session, task_data: TaskCreate, user_id: int):
        """Create a new task"""
        
        # Validate parent task
        self._validate_parent_task(db, None, task_data.parent_task_id, user_id)
        
        # Validate list
        self._validate_list(db, task_data.list_id, user_id)
        
        # Validate tags
        tag_ids = []
        if task_data.tag_ids:
            tag_ids = self._validate_tags(db, task_data.tag_ids, user_id)
        
        # Create task
        task = Task(
            account_id=user_id,
            title=task_data.title,
            type=task_data.type.value if task_data.type else "task",
            list_id=task_data.list_id,
            parent_task_id=task_data.parent_task_id,
            scheduled_date=task_data.scheduled_date,
            estimated_duration=task_data.estimated_duration,
            priority=task_data.priority,
            status=task_data.status.value if task_data.status else "not_started"
        )
        
        db.add(task)
        db.flush()
        
        # Add tags
        if tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            task.tags = tags
        
        # Add URLs
        if task_data.urls:
            self._process_urls(db, task, task_data.urls)
        
        db.commit()
        db.refresh(task)
        
        return task
    
    # ============= READ =============
    
    def get_task(self, db: Session, task_id: int, user_id: int):
        """Get a specific task by ID"""
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.account_id == user_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return task
    
    def get_task_detail(self, db: Session, task_id: int, user_id: int):
        """Get detailed task info with relationships"""
        task = db.query(Task).options(
            joinedload(Task.tags),
            joinedload(Task.urls),
            joinedload(Task.subtasks),
            joinedload(Task.parent_task),
            joinedload(Task.lists)
        ).filter(
            Task.id == task_id,
            Task.account_id == user_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return task
    
    def get_tasks(
        self,
        db: Session,
        user_id: int,
        filters: TaskFilterParams,
        skip: int = 0,
        limit: int = 100
    ):
        """Get tasks with filtering"""
        query = db.query(Task).filter(Task.account_id == user_id)
        
        # Filter by list
        if filters.list_id is not None:
            query = query.filter(Task.list_id == filters.list_id)
        
        # Filter by status
        if filters.status:
            query = query.filter(Task.status == filters.status.value)
        
        # Filter by type
        if filters.type:
            query = query.filter(Task.type == filters.type.value)
        
        # Filter by priority range
        if filters.priority_min is not None:
            query = query.filter(Task.priority >= filters.priority_min)
        if filters.priority_max is not None:
            query = query.filter(Task.priority <= filters.priority_max)
        
        # Filter by scheduled date
        if filters.scheduled_after:
            query = query.filter(Task.scheduled_date >= filters.scheduled_after)
        if filters.scheduled_before:
            query = query.filter(Task.scheduled_date <= filters.scheduled_before)
        
        # Filter by parent relationship
        if filters.has_parent is not None:
            if filters.has_parent:
                query = query.filter(Task.parent_task_id.isnot(None))
            else:
                query = query.filter(Task.parent_task_id.is_(None))
        
        if filters.parent_task_id is not None:
            query = query.filter(Task.parent_task_id == filters.parent_task_id)
        
        # Filter by completion
        if filters.is_completed is not None:
            if filters.is_completed:
                query = query.filter(Task.completed_at.isnot(None))
            else:
                query = query.filter(Task.completed_at.is_(None))
        
        # Filter by future plans
        if filters.is_planned is not None:
            if filters.is_planned:
                # Tasks that have plans in the future
                future_plans = db.query(Plan.plan_id).filter(
                    Plan.start_time > datetime.now()
                ).subquery()
                query = query.join(Plan).filter(Plan.id.in_(future_plans))
            else:
                # Tasks with no plans or only past plans
                query = query.outerjoin(Plan).filter(
                    or_(
                        Plan.id.is_(None),
                        Plan.start_time <= datetime.now()
                    )
                )
        
        # Filter by tags
        if filters.tag_ids:
            query = query.join(Task.tags).filter(Tag.id.in_(filters.tag_ids))
        
        # Search in title
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(Task.title.ilike(search_term))
        
        # Order by priority and scheduled date
        query = query.order_by(
            Task.priority.desc().nullslast(),
            Task.scheduled_date.asc().nullslast()
        )
        
        tasks = query.offset(skip).limit(limit).all()
        
        # Add additional info
        for task in tasks:
            task.subtask_count = db.query(Task).filter(
                Task.parent_task_id == task.id
            ).count()
        
        return tasks
    
    def get_task_hierarchy(self, db: Session, user_id: int, root_task_id: Optional[int] = None):
        """Get task hierarchy tree"""
        if root_task_id:
            # Get specific root
            root = self.get_task(db, root_task_id, user_id)
            if root.parent_task_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task is not a root task (has a parent)"
                )
            return self._get_task_hierarchy(db, root)
        else:
            # Get all root tasks
            roots = db.query(Task).filter(
                Task.account_id == user_id,
                Task.parent_task_id.is_(None)
            ).order_by(Task.priority.desc().nullslast()).all()
            
            return [self._get_task_hierarchy(db, root) for root in roots]
    
    # ============= UPDATE =============
    
    def update_task(
        self,
        db: Session,
        task_id: int,
        task_update: TaskUpdate,
        user_id: int
    ):
        """Update a task"""
        task = self.get_task(db, task_id, user_id)
        
        update_data = task_update.model_dump(exclude_unset=True)
        
        # Handle special fields
        if "type" in update_data and update_data["type"]:
            update_data["type"] = update_data["type"].value
        
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].value
            # Auto-set completed_at if status is completed
            if update_data["status"] == "completed" and not task.completed_at:
                update_data["completed_at"] = datetime.now()
            elif update_data["status"] != "completed" and task.completed_at:
                update_data["completed_at"] = None
        
        # Validate parent task if changing
        if "parent_task_id" in update_data:
            self._validate_parent_task(db, task_id, update_data["parent_task_id"], user_id)
        
        # Validate list if changing
        if "list_id" in update_data:
            self._validate_list(db, update_data["list_id"], user_id)
        
        # Handle tag updates
        if "tag_ids" in update_data:
            # Replace all tags
            tag_ids = self._validate_tags(db, update_data["tag_ids"], user_id)
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            task.tags = tags
            del update_data["tag_ids"]
        else:
            # Handle add/remove tags
            if "add_tag_ids" in update_data:
                add_ids = self._validate_tags(db, update_data["add_tag_ids"], user_id)
                current_tag_ids = [tag.id for tag in task.tags]
                new_ids = set(add_ids) - set(current_tag_ids)
                if new_ids:
                    new_tags = db.query(Tag).filter(Tag.id.in_(new_ids)).all()
                    task.tags.extend(new_tags)
                del update_data["add_tag_ids"]
            
            if "remove_tag_ids" in update_data:
                remove_ids = set(update_data["remove_tag_ids"])
                task.tags = [tag for tag in task.tags if tag.id not in remove_ids]
                del update_data["remove_tag_ids"]
        
        # Handle URL updates
        if "urls" in update_data:
            # Replace all URLs
            # First delete all existing URLs
            db.query(TaskUrl).filter(TaskUrl.task_id == task.id).delete()
            # Then add new ones
            if update_data["urls"]:
                self._process_urls(db, task, update_data["urls"])
            del update_data["urls"]
        else:
            # Handle add/remove URLs
            if "add_urls" in update_data and update_data["add_urls"]:
                self._process_urls(db, task, update_data["add_urls"])
                del update_data["add_urls"]
            
            if "remove_urls" in update_data and update_data["remove_urls"]:
                self._remove_urls(db, task, update_data["remove_urls"])
                del update_data["remove_urls"]
        
        # Update basic fields
        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        
        return task
    
    # ============= DELETE =============
    
    def delete_task(self, db: Session, task_id: int, user_id: int):
        """Delete a task (cascade delete will handle related records)"""
        task = self.get_task(db, task_id, user_id)
        
        # Check if this task has children
        child_count = db.query(Task).filter(Task.parent_task_id == task_id).count()
        if child_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete task with {child_count} subtasks. Delete subtasks first or reassign them."
            )
        
        db.delete(task)
        db.commit()
        return {"message": "Task deleted successfully"}
    
    # ============= TASK OPERATIONS =============
    
    def complete_task(self, db: Session, task_id: int, user_id: int):
        """Mark a task as completed"""
        task = self.get_task(db, task_id, user_id)
        
        if task.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is already completed"
            )
        
        task.status = "completed"
        task.completed_at = datetime.now()
        
        db.commit()
        db.refresh(task)
        
        return task
    
    def get_incomplete_tasks_with_future_plans(self, db: Session, user_id: int):
        """Get tasks that are not done and have future plans"""
        future_plans = db.query(Plan.plan_id).filter(
            Plan.start_time > datetime.now()
        ).subquery()
        
        tasks = db.query(Task).join(Plan).filter(
            Task.account_id == user_id,
            Task.completed_at.is_(None),
            Plan.id.in_(future_plans)
        ).all()
        
        return tasks
    
    def get_tasks_by_tag(self, db: Session, tag_id: int, user_id: int):
        """Get all tasks with a specific tag"""
        tasks = db.query(Task).join(Task.tags).filter(
            Task.account_id == user_id,
            Tag.id == tag_id
        ).all()
        
        return tasks