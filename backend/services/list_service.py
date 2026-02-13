from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func as sql_func
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.list_models import List
from models.task_models import Task
from models.tag_models import Tag
from schemas.list_schemas import ListCreate, ListUpdate, ListFilterParams, TaskHierarchyNode

class ListService:
    
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
    
    def _get_list_stats(self, db: Session, list_id: int, user_id: int) -> Dict[str, Any]:
        """Get statistics for a list"""
        # Get all tasks in this list
        tasks = db.query(Task).filter(
            Task.account_id == user_id,
            Task.list_id == list_id
        ).all()
        
        task_count = len(tasks)
        completed_count = sum(1 for t in tasks if t.status == "completed")
        active_count = task_count - completed_count
        
        # Calculate total estimated duration
        total_duration = sum(t.estimated_duration or 0 for t in tasks)
        
        # Count subtasks (tasks that have a parent in the same list)
        subtask_count = 0
        for task in tasks:
            subtask_count += db.query(Task).filter(
                Task.parent_task_id == task.id
            ).count()
        
        return {
            "task_count": task_count,
            "completed_task_count": completed_count,
            "active_task_count": active_count,
            "total_subtasks": subtask_count,
            "estimated_total_duration": total_duration if total_duration > 0 else None
        }
    
    def _build_task_hierarchy(self, db: Session, list_id: int, user_id: int, parent_id: Optional[int] = None, depth: int = 0) -> List[TaskHierarchyNode]:
        """Build task hierarchy tree for a list"""
        query = db.query(Task).filter(
            Task.account_id == user_id,
            Task.list_id == list_id
        )
        
        if parent_id is None:
            query = query.filter(Task.parent_task_id.is_(None))
        else:
            query = query.filter(Task.parent_task_id == parent_id)
        
        tasks = query.order_by(Task.priority.desc().nullslast(), Task.scheduled_date).all()
        
        result = []
        for task in tasks:
            # Get subtasks for this task
            children = self._build_task_hierarchy(db, list_id, user_id, task.id, depth + 1)
            
            node = TaskHierarchyNode(
                id=task.id,
                title=task.title,
                status=task.status,
                priority=task.priority,
                scheduled_date=task.scheduled_date,
                depth=depth,
                children=children
            )
            result.append(node)
        
        return result
    
    def _get_task_summaries(self, db: Session, list_id: int, user_id: int) -> List[Dict]:
        """Get task summaries for a list"""
        tasks = db.query(Task).filter(
            Task.account_id == user_id,
            Task.list_id == list_id
        ).all()
        
        summaries = []
        for task in tasks:
            subtask_count = db.query(Task).filter(
                Task.parent_task_id == task.id
            ).count()
            
            summaries.append({
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "scheduled_date": task.scheduled_date,
                "has_subtasks": subtask_count > 0,
                "subtask_count": subtask_count
            })
        
        return summaries
    
    # ============= CREATE =============
    
    def create_list(self, db: Session, list_data: ListCreate, user_id: int):
        """Create a new list"""
        
        # Check if list with same name already exists for this user
        existing = db.query(List).filter(
            List.account_id == user_id,
            List.name == list_data.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have a list named '{list_data.name}'"
            )
        
        # Validate tags if provided
        tag_ids = []
        if list_data.tag_ids:
            tag_ids = self._validate_tags(db, list_data.tag_ids, user_id)
        
        # Create list
        new_list = List(
            account_id=user_id,
            name=list_data.name,
            description=list_data.description,
            priority=list_data.priority,
            status=list_data.status.value if list_data.status else "active"
        )
        
        db.add(new_list)
        db.flush()  
        
        # Add tags
        if tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            new_list.tags = tags
        
        db.commit()
        db.refresh(new_list)
        
        return new_list
    
    # ============= READ =============
    
    def get_list(self, db: Session, list_id: int, user_id: int):
        """Get a specific list by ID"""
        list_obj = db.query(List).filter(
            List.id == list_id,
            List.account_id == user_id
        ).first()
        
        if not list_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="List not found"
            )
        
        # Add stats
        stats = self._get_list_stats(db, list_id, user_id)
        for key, value in stats.items():
            setattr(list_obj, key, value)
        
        return list_obj
    
    def get_list_detail(self, db: Session, list_id: int, user_id: int):
        """Get detailed list info with tasks and hierarchy"""
        list_obj = self.get_list(db, list_id, user_id)
        
        # Add task summaries
        list_obj.tasks = self._get_task_summaries(db, list_id, user_id)
        
        # Add task hierarchy
        list_obj.task_hierarchy = self._build_task_hierarchy(db, list_id, user_id)
        
        
        return list_obj
    
    def get_lists(
        self,
        db: Session,
        user_id: int,
        filters: ListFilterParams,
        skip: int = 0,
        limit: int = 100
    ):
        """Get lists with filtering"""
        query = db.query(List).filter(List.account_id == user_id)
        
        # Filter by status
        if filters.status:
            query = query.filter(List.status == filters.status.value)
        
        # Filter by priority range
        if filters.priority_min is not None:
            query = query.filter(List.priority >= filters.priority_min)
        if filters.priority_max is not None:
            query = query.filter(List.priority <= filters.priority_max)
        
        # Filter by tags
        if filters.tag_ids:
            query = query.join(List.tags).filter(Tag.id.in_(filters.tag_ids))
        
        # Search in name/description
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    List.name.ilike(search_term),
                    List.description.ilike(search_term)
                )
            )
        
        # Filter by creation date
        if filters.created_after:
            query = query.filter(List.created_at >= filters.created_after)
        if filters.created_before:
            query = query.filter(List.created_at <= filters.created_before)
        
        # Order by priority and name
        query = query.order_by(
            List.priority.desc().nullslast(),
            List.name.asc()
        )
        
        lists = query.offset(skip).limit(limit).all()
        
        # Add stats to each list
        for list_obj in lists:
            stats = self._get_list_stats(db, list_obj.id, user_id)
            for key, value in stats.items():
                setattr(list_obj, key, value)
        
        # Filter by has_tasks (client-side filtering)
        if filters.has_tasks is not None:
            if filters.has_tasks:
                lists = [l for l in lists if l.task_count > 0]
            else:
                lists = [l for l in lists if l.task_count == 0]
        
        return lists
    
    def get_list_hierarchy(self, db: Session, list_id: int, user_id: int):
        """Get just the task hierarchy for a list"""
        # Verify list exists
        self.get_list(db, list_id, user_id)
        
        return self._build_task_hierarchy(db, list_id, user_id)
    
    # ============= UPDATE =============
    
    def update_list(
        self,
        db: Session,
        list_id: int,
        list_update: ListUpdate,
        user_id: int
    ):
        """Update a list"""
        list_obj = self.get_list(db, list_id, user_id)
        
        update_data = list_update.model_dump(exclude_unset=True)
        
        # Handle status enum
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].value
        
        # Check name uniqueness if changing
        if "name" in update_data and update_data["name"] != list_obj.name:
            existing = db.query(List).filter(
                List.account_id == user_id,
                List.name == update_data["name"],
                List.id != list_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"You already have a list named '{update_data['name']}'"
                )
        
        # Handle tag updates
        if "tag_ids" in update_data:
            # Replace all tags
            tag_ids = self._validate_tags(db, update_data["tag_ids"], user_id)
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            list_obj.tags = tags
            del update_data["tag_ids"]
        else:
            # Handle add/remove tags
            if "add_tag_ids" in update_data:
                add_ids = self._validate_tags(db, update_data["add_tag_ids"], user_id)
                current_tag_ids = [tag.id for tag in list_obj.tags]
                new_ids = set(add_ids) - set(current_tag_ids)
                if new_ids:
                    new_tags = db.query(Tag).filter(Tag.id.in_(new_ids)).all()
                    list_obj.tags.extend(new_tags)
                del update_data["add_tag_ids"]
            
            if "remove_tag_ids" in update_data:
                remove_ids = set(update_data["remove_tag_ids"])
                list_obj.tags = [tag for tag in list_obj.tags if tag.id not in remove_ids]
                del update_data["remove_tag_ids"]
        
        # Update basic fields
        for field, value in update_data.items():
            setattr(list_obj, field, value)
        
        db.commit()
        db.refresh(list_obj)
        
        return list_obj
    
    # ============= DELETE =============
    
    def delete_list(self, db: Session, list_id: int, user_id: int):
        """Delete a list (cascade will handle tasks)"""
        list_obj = self.get_list(db, list_id, user_id)
        
        # Check if list has tasks (optional warning)
        task_count = db.query(Task).filter(Task.list_id == list_id).count()
        if task_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete list with {task_count} tasks. Move or delete tasks first."
            )
        
        db.delete(list_obj)
        db.commit()
        return {"message": "List deleted successfully"}
    
    # ============= LIST OPERATIONS =============
    
    def archive_list(self, db: Session, list_id: int, user_id: int):
        """Archive a list (change status to archived)"""
        list_obj = self.get_list(db, list_id, user_id)
        list_obj.status = "archived"
        db.commit()
        db.refresh(list_obj)
        return list_obj
    
    def get_lists_by_tag(self, db: Session, tag_id: int, user_id: int):
        """Get all lists with a specific tag"""
        lists = db.query(List).join(List.tags).filter(
            List.account_id == user_id,
            Tag.id == tag_id
        ).all()
        
        # Add stats
        for list_obj in lists:
            stats = self._get_list_stats(db, list_obj.id, user_id)
            for key, value in stats.items():
                setattr(list_obj, key, value)
        
        return lists
    
    def move_tasks_to_list(self, db: Session, source_list_id: int, target_list_id: int, user_id: int):
        """Move all tasks from one list to another"""
        # Verify both lists exist
        source = self.get_list(db, source_list_id, user_id)
        target = self.get_list(db, target_list_id, user_id)
        
        if source.id == target.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and target lists are the same"
            )
        
        # Update tasks
        db.query(Task).filter(
            Task.account_id == user_id,
            Task.list_id == source_list_id
        ).update({"list_id": target_list_id})
        
        db.commit()
        
        return {
            "message": f"All tasks moved from '{source.name}' to '{target.name}'",
            "source_list": source.name,
            "target_list": target.name
        }