from sqlalchemy import Column, Integer, String, BigInteger, Text, TIMESTAMP, ForeignKey, Boolean, Table, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

note_tags = Table(
    'note_tags',
    Base.metadata,
    Column('note_id', BigInteger, ForeignKey('note.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', BigInteger, ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
)

note_links = Table(
    'note_links',
    Base.metadata,
    Column('source_note_id', BigInteger, ForeignKey('note.id', ondelete='CASCADE'), primary_key=True),
    Column('target_note_id', BigInteger, ForeignKey('note.id', ondelete='CASCADE'), primary_key=True)
)

class Note(Base):
    """Advanced note table with rich features"""
    __tablename__ = "note"
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Basic info
    title = Column(String(255), nullable=False)
    content = Column(Text)  # Rich text content (Markdown/HTML)
    content_preview = Column(String(500))  # Auto-generated preview
    
    # Metadata
    quality_score = Column(Integer)
    is_pinned = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    
    # Rich formatting (store as JSON for advanced features)
    formatting_data = Column(JSON, default={})  # Store custom formatting
    word_count = Column(Integer, default=0)
    reading_time_minutes = Column(Integer, default=0)
    
    
    is_follow_up = Column(Boolean, default=False)
    parent_note_id = Column(BigInteger, ForeignKey('note.id', ondelete='SET NULL'), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    last_accessed_at = Column(TIMESTAMP(timezone=True))
    
    # Foreign keys
    account_id = Column(BigInteger, ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    plan_id = Column(BigInteger, ForeignKey('plan.id', ondelete='SET NULL'), nullable=True)  
    
    # Relationships
    account = relationship("Account", back_populates="notes")
    plan = relationship("Plan", foreign_keys=[plan_id], back_populates="notes")
    
    # Tags
    tags = relationship(
        "Tag", 
        secondary=note_tags,
        back_populates="notes"
    )
    
    # Note-to-note relationships
    parent_note = relationship(
        "Note", 
        remote_side=[id],
        back_populates="child_notes",
        foreign_keys=[parent_note_id]
    )
    child_notes = relationship(
        "Note", 
        back_populates="parent_note",
        foreign_keys=[parent_note_id],
        cascade="all, delete-orphan"
    )
    
    # Related notes (many-to-many)
    related_notes = relationship(
        "Note",
        secondary=note_links,
        primaryjoin=id == note_links.c.source_note_id,
        secondaryjoin=id == note_links.c.target_note_id,
        backref="related_from"
    )
    
    tasks = relationship(
        "Task",
        secondary="task_notes", 
        back_populates="notes"
    )