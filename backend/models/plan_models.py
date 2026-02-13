from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP, ForeignKey, Boolean, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class Plan(Base):
    """Plan table"""
    __tablename__ = "plan"
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    task_id = Column(BigInteger, ForeignKey('task.id', ondelete='CASCADE'), nullable=True)
    note_id = Column(BigInteger, ForeignKey('note.id', ondelete='SET NULL'), nullable=True)
    time_block_id = Column(BigInteger, ForeignKey('timeblock.id', ondelete='SET NULL'), nullable=True)
    account_id = Column(BigInteger, ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    
    # Suggestion source (if created from suggestion)
    suggestion_task_id = Column(BigInteger, nullable=True)
    suggestion_time_block_id = Column(BigInteger, nullable=True)
    suggestion_title = Column(String(255), nullable=True)
    
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    actual_start_time = Column(TIMESTAMP(timezone=True))
    actual_end_time = Column(TIMESTAMP(timezone=True))
    
    status = Column(String(50), default="planned")  # planned, in_progress, completed, cancelled, missed
    progress = Column(Integer, default=0)  # 0-100
    
    # Performance metrics
    completion_rate = Column(Float, default=0.0)  # How well it was followed
    notes = Column(Text)
    
    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_parent_id = Column(BigInteger, ForeignKey('plan.id', ondelete='SET NULL'), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="plans")
    note = relationship("Note", back_populates="plans")
    time_block = relationship("TimeBlock", back_populates="plans")
    account = relationship("Account", back_populates="plans")
    
    # Self-referential for recurring
    recurrence_parent = relationship("Plan", remote_side=[id], backref="recurring_children")
    
    # Suggestions that created this plan
    source_suggestions = relationship(
        "Suggestion",
        foreign_keys="[Suggestion.created_plan_id]",
        back_populates="created_plan"
    )