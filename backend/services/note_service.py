from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import re

from models.note_models import Note, note_tags, note_links
from models.tag_models import Tag
from models.task_models import Task, task_notes
from models.plan_models import Plan
from schemas.note_schemas import NoteCreate, NotePreview, NoteUpdate, NoteFilterParams, NoteSortBy

class NoteService:
    
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
                detail=f"Invalid tag IDs: {invalid_ids}"
            )
        
        return valid_ids
    
    def _validate_notes(self, db: Session, note_ids: List[int], user_id: int):
        """Validate that notes exist and belong to user"""
        if not note_ids:
            return []
        
        valid_notes = db.query(Note).filter(
            Note.id.in_(note_ids),
            Note.account_id == user_id
        ).all()
        
        valid_ids = [note.id for note in valid_notes]
        invalid_ids = set(note_ids) - set(valid_ids)
        
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid note IDs: {invalid_ids}"
            )
        
        return valid_ids
    
    def _validate_tasks(self, db: Session, task_ids: List[int], user_id: int):
        """Validate that tasks exist and belong to user"""
        if not task_ids:
            return []
        
        valid_tasks = db.query(Task).filter(
            Task.id.in_(task_ids),
            Task.account_id == user_id
        ).all()
        
        valid_ids = [task.id for task in valid_tasks]
        invalid_ids = set(task_ids) - set(valid_ids)
        
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid task IDs: {invalid_ids}"
            )
        
        return valid_ids
    
    def _generate_preview(self, content: Optional[str], max_length: int = 200) -> Optional[str]:
        """Generate a preview from content"""
        if not content:
            return None
        
        # Strip markdown/HTML and get plain text
        plain_text = re.sub(r'<[^>]+>', '', content)  # Remove HTML tags
        plain_text = re.sub(r'[#*_`\[\]]+', '', plain_text)  # Remove markdown symbols
        
        # Truncate
        if len(plain_text) <= max_length:
            return plain_text
        
        return plain_text[:max_length].rsplit(' ', 1)[0] + '...'
    
    def _calculate_word_count(self, content: Optional[str]) -> int:
        """Calculate word count from content"""
        if not content:
            return 0
        
        # Strip markdown/HTML
        plain_text = re.sub(r'<[^>]+>', '', content)
        plain_text = re.sub(r'[#*_`\[\]]+', '', plain_text)
        
        # Count words
        words = plain_text.split()
        return len(words)
    
    def _calculate_reading_time(self, word_count: int) -> int:
        """Calculate reading time in minutes (average 200 words per minute)"""
        if word_count == 0:
            return 0
        return max(1, round(word_count / 200))
    
    def _update_note_metadata(self, note: Note):
        """Update calculated metadata for a note"""
        note.word_count = self._calculate_word_count(note.content)
        note.reading_time_minutes = self._calculate_reading_time(note.word_count)
        note.content_preview = self._generate_preview(note.content)
    
    def _create_follow_up_note(self, db: Session, plan_id: int, user_id: int) -> Note:
        """Create a follow-up note for a plan"""
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        # Create follow-up note
        follow_up = Note(
            title=f"Follow-up: {plan.task.title if plan.task else 'Plan'}",
            content=f"# Follow-up Notes\n\nPlan details:\n- Time: {plan.start_time}\n- Status: {plan.status}\n\n## Notes:\n",
            account_id=user_id,
            plan_id=plan_id,
            is_follow_up=True
        )
        
        self._update_note_metadata(follow_up)
        db.add(follow_up)
        db.flush()
        
        return follow_up
    
    # ============= CREATE =============
    
    def create_note(self, db: Session, note_data: NoteCreate, user_id: int):
        """Create a new note"""
        
        # Validate parent note if provided
        if note_data.parent_note_id:
            parent = self._validate_notes(db, [note_data.parent_note_id], user_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent note not found"
                )
        
        # Validate tags
        tag_ids = []
        if note_data.tag_ids:
            tag_ids = self._validate_tags(db, note_data.tag_ids, user_id)
        
        # Validate related notes
        related_note_ids = []
        if note_data.related_note_ids:
            related_note_ids = self._validate_notes(db, note_data.related_note_ids, user_id)
        
        # Validate tasks
        task_ids = []
        if note_data.task_ids:
            task_ids = self._validate_tasks(db, note_data.task_ids, user_id)
        
        # Create note
        note = Note(
            account_id=user_id,
            title=note_data.title,
            content=note_data.content,
            quality_score=note_data.quality_score,
            is_pinned=note_data.is_pinned,
            is_favorite=note_data.is_favorite,
            formatting_data=note_data.formatting_data,
            parent_note_id=note_data.parent_note_id,
            plan_id=note_data.plan_id
        )
        
        self._update_note_metadata(note)
        db.add(note)
        db.flush()
        
        # Add tags
        if tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            note.tags = tags
        
        # Add related notes
        if related_note_ids:
            related_notes = db.query(Note).filter(Note.id.in_(related_note_ids)).all()
            note.related_notes = related_notes
        
        # Link tasks
        if task_ids:
            tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
            note.tasks = tasks
        
        # If this is for a plan, mark as follow-up
        if note_data.plan_id:
            note.is_follow_up = True
        
        db.commit()
        db.refresh(note)
        
        return note
    
    # ============= READ =============
    
    def get_note(self, db: Session, note_id: int, user_id: int):
        """Get a specific note by ID"""
        note = db.query(Note).options(
            joinedload(Note.tags),
            joinedload(Note.parent_note),
            joinedload(Note.child_notes),
            joinedload(Note.related_notes),
            joinedload(Note.tasks),
            joinedload(Note.plan)
        ).filter(
            Note.id == note_id,
            Note.account_id == user_id
        ).first()
        
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        # Update last accessed
        note.last_accessed_at = datetime.now()
        db.commit()
        
        return note
    
    def get_notes(
        self,
        db: Session,
        user_id: int,
        filters: NoteFilterParams,
        skip: int = 0,
        limit: int = 100
    ):
        """Get notes with filtering"""
        query = db.query(Note).filter(Note.account_id == user_id)
        
        # Filter by archived status (default to non-archived)
        if filters.is_archived is not None:
            query = query.filter(Note.is_archived == filters.is_archived)
        else:
            query = query.filter(Note.is_archived == False)
        
        # Other boolean filters
        if filters.is_pinned is not None:
            query = query.filter(Note.is_pinned == filters.is_pinned)
        if filters.is_favorite is not None:
            query = query.filter(Note.is_favorite == filters.is_favorite)
        if filters.is_follow_up is not None:
            query = query.filter(Note.is_follow_up == filters.is_follow_up)
        
        # Quality score range
        if filters.quality_score_min is not None:
            query = query.filter(Note.quality_score >= filters.quality_score_min)
        if filters.quality_score_max is not None:
            query = query.filter(Note.quality_score <= filters.quality_score_max)
        
        # Date filters
        if filters.created_after:
            query = query.filter(Note.created_at >= filters.created_after)
        if filters.created_before:
            query = query.filter(Note.created_at <= filters.created_before)
        if filters.updated_after:
            query = query.filter(Note.updated_at >= filters.updated_after)
        
        # Filter by tags
        if filters.tag_ids:
            query = query.join(Note.tags).filter(Tag.id.in_(filters.tag_ids))
        
        # Filter by relationships
        if filters.has_plan is not None:
            if filters.has_plan:
                query = query.filter(Note.plan_id.isnot(None))
            else:
                query = query.filter(Note.plan_id.is_(None))
        
        if filters.has_tasks is not None:
            if filters.has_tasks:
                query = query.join(Note.tasks).distinct()
            else:
                query = query.outerjoin(Note.tasks).filter(Task.id.is_(None))
        
        if filters.has_related_notes is not None:
            if filters.has_related_notes:
                query = query.join(Note.related_notes).distinct()
            else:
                query = query.outerjoin(Note.related_notes).filter(Note.id.is_(None))
        
        # Search in title and content
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Note.title.ilike(search_term),
                    Note.content.ilike(search_term)
                )
            )
        
        # Sorting
        sort_column = {
            NoteSortBy.CREATED_AT: Note.created_at,
            NoteSortBy.UPDATED_AT: Note.updated_at,
            NoteSortBy.TITLE: Note.title,
            NoteSortBy.QUALITY_SCORE: Note.quality_score,
            NoteSortBy.WORD_COUNT: Note.word_count,
            NoteSortBy.READING_TIME: Note.reading_time_minutes
        }.get(filters.sort_by, Note.updated_at)
        
        if filters.sort_desc:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        notes = query.offset(skip).limit(limit).all()
        
        # Convert to preview format
        result = []
        for note in notes:
            preview = NotePreview(
                id=note.id,
                title=note.title,
                content_preview=note.content_preview,
                created_at=note.created_at,
                updated_at=note.updated_at,
                is_pinned=note.is_pinned,
                is_favorite=note.is_favorite,
                word_count=note.word_count,
                reading_time_minutes=note.reading_time_minutes,
                tag_count=len(note.tags),
                has_related_notes=len(note.related_notes) > 0,
                has_tasks=len(note.tasks) > 0
            )
            result.append(preview)
        
        return result
    
    def search_notes(self, db: Session, user_id: int, query: str, limit: int = 20):
        """Full-text search in notes"""
        search_term = f"%{query}%"
        
        notes = db.query(Note).filter(
            Note.account_id == user_id,
            Note.is_archived == False,
            or_(
                Note.title.ilike(search_term),
                Note.content.ilike(search_term)
            )
        ).order_by(
            desc(Note.is_pinned),
            desc(Note.updated_at)
        ).limit(limit).all()
        
        return notes
    
    # ============= UPDATE =============
    
    def update_note(
        self,
        db: Session,
        note_id: int,
        note_update: NoteUpdate,
        user_id: int
    ):
        """Update a note"""
        note = self.get_note(db, note_id, user_id)
        
        update_data = note_update.model_dump(exclude_unset=True)
        
        # Handle basic fields
        basic_fields = ['title', 'content', 'quality_score', 'is_pinned', 
                       'is_archived', 'is_favorite', 'formatting_data']
        
        for field in basic_fields:
            if field in update_data:
                setattr(note, field, update_data[field])
                del update_data[field]
        
        # Update metadata if content changed
        if 'content' in update_data or 'title' in update_data:
            self._update_note_metadata(note)
        
        # Handle tag updates
        if "tag_ids" in update_data:
            tag_ids = self._validate_tags(db, update_data["tag_ids"], user_id)
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            note.tags = tags
            del update_data["tag_ids"]
        else:
            if "add_tag_ids" in update_data:
                add_ids = self._validate_tags(db, update_data["add_tag_ids"], user_id)
                current_ids = [tag.id for tag in note.tags]
                new_ids = set(add_ids) - set(current_ids)
                if new_ids:
                    new_tags = db.query(Tag).filter(Tag.id.in_(new_ids)).all()
                    note.tags.extend(new_tags)
                del update_data["add_tag_ids"]
            
            if "remove_tag_ids" in update_data:
                remove_ids = set(update_data["remove_tag_ids"])
                note.tags = [tag for tag in note.tags if tag.id not in remove_ids]
                del update_data["remove_tag_ids"]
        
        # Handle related notes updates
        if "related_note_ids" in update_data:
            related_ids = self._validate_notes(db, update_data["related_note_ids"], user_id)
            related_notes = db.query(Note).filter(Note.id.in_(related_ids)).all()
            note.related_notes = related_notes
            del update_data["related_note_ids"]
        else:
            if "add_related_note_ids" in update_data:
                add_ids = self._validate_notes(db, update_data["add_related_note_ids"], user_id)
                current_ids = [n.id for n in note.related_notes]
                new_ids = set(add_ids) - set(current_ids)
                if new_ids:
                    new_notes = db.query(Note).filter(Note.id.in_(new_ids)).all()
                    note.related_notes.extend(new_notes)
                del update_data["add_related_note_ids"]
            
            if "remove_related_note_ids" in update_data:
                remove_ids = set(update_data["remove_related_note_ids"])
                note.related_notes = [n for n in note.related_notes if n.id not in remove_ids]
                del update_data["remove_related_note_ids"]
        
        # Handle task updates
        if "task_ids" in update_data:
            task_ids = self._validate_tasks(db, update_data["task_ids"], user_id)
            tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
            note.tasks = tasks
            del update_data["task_ids"]
        else:
            if "add_task_ids" in update_data:
                add_ids = self._validate_tasks(db, update_data["add_task_ids"], user_id)
                current_ids = [t.id for t in note.tasks]
                new_ids = set(add_ids) - set(current_ids)
                if new_ids:
                    new_tasks = db.query(Task).filter(Task.id.in_(new_ids)).all()
                    note.tasks.extend(new_tasks)
                del update_data["add_task_ids"]
            
            if "remove_task_ids" in update_data:
                remove_ids = set(update_data["remove_task_ids"])
                note.tasks = [t for t in note.tasks if t.id not in remove_ids]
                del update_data["remove_task_ids"]
        
        db.commit()
        db.refresh(note)
        
        return note
    
    # ============= DELETE =============
    
    def delete_note(self, db: Session, note_id: int, user_id: int):
        """Delete a note"""
        note = self.get_note(db, note_id, user_id)
        
        # Check if this note has children
        if note.child_notes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete note with {len(note.child_notes)} child notes. Delete children first."
            )
        
        db.delete(note)
        db.commit()
        return {"message": "Note deleted successfully"}
    
    # ============= NOTE OPERATIONS =============
    
    def create_follow_up_for_plan(self, db: Session, plan_id: int, user_id: int):
        """Create a follow-up note for a plan"""
        return self._create_follow_up_note(db, plan_id, user_id)
    
    def get_notes_by_tag(self, db: Session, tag_id: int, user_id: int):
        """Get all notes with a specific tag"""
        notes = db.query(Note).join(Note.tags).filter(
            Note.account_id == user_id,
            Note.is_archived == False,
            Tag.id == tag_id
        ).all()
        
        return notes
    
    def get_notes_by_task(self, db: Session, task_id: int, user_id: int):
        """Get all notes linked to a specific task"""
        notes = db.query(Note).join(Note.tasks).filter(
            Note.account_id == user_id,
            Task.id == task_id
        ).all()
        
        return notes
    
    def toggle_pin(self, db: Session, note_id: int, user_id: int):
        """Toggle pin status of a note"""
        note = self.get_note(db, note_id, user_id)
        note.is_pinned = not note.is_pinned
        db.commit()
        db.refresh(note)
        return note
    
    def toggle_favorite(self, db: Session, note_id: int, user_id: int):
        """Toggle favorite status of a note"""
        note = self.get_note(db, note_id, user_id)
        note.is_favorite = not note.is_favorite
        db.commit()
        db.refresh(note)
        return note
    
    def archive_note(self, db: Session, note_id: int, user_id: int):
        """Archive a note"""
        note = self.get_note(db, note_id, user_id)
        note.is_archived = True
        db.commit()
        db.refresh(note)
        return note
    
    def restore_note(self, db: Session, note_id: int, user_id: int):
        """Restore an archived note"""
        note = db.query(Note).filter(
            Note.id == note_id,
            Note.account_id == user_id,
            Note.is_archived == True
        ).first()
        
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archived note not found"
            )
        
        note.is_archived = False
        db.commit()
        db.refresh(note)
        return note