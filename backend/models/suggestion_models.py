from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP, ForeignKey, Boolean, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class Suggestion(Base):
    """Suggestions for tasks in time blocks"""
    __tablename__ = "suggestions"
    __table_args__ = (
        UniqueConstraint('task_id', 'time_block_id', 'title', name='uq_suggestion_composite'),
    )
    
    task_id = Column(BigInteger, ForeignKey('task.id', ondelete='CASCADE'), primary_key=True)
    time_block_id = Column(BigInteger, ForeignKey('timeblock.id', ondelete='CASCADE'), primary_key=True)
    title = Column(String(255), primary_key=True)
    
    description = Column(Text) 
    confidence_score = Column(Integer, default=50)  # 0-100, how confident the algorithm is
    priority = Column(Integer, default=0)  # 0-10, suggested priority
    
    # Status
    status = Column(String(50), default="pending")  # pending, accepted, rejected, expired
    viewed_at = Column(TIMESTAMP(timezone=True))  # When user viewed it
    responded_at = Column(TIMESTAMP(timezone=True))  # When user responded
    
    # Expiry
    expires_at = Column(TIMESTAMP(timezone=True))  # When suggestion expires
    is_expired = Column(Boolean, default=False)
    
    # Response metadata
    response_notes = Column(Text)  # User's notes on why accepted/rejected
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="suggestions")
    time_block = relationship("TimeBlock", back_populates="suggestions")
    
    created_plan_id = Column(BigInteger, ForeignKey('plan.id', ondelete='SET NULL'), nullable=True)
    created_plan = relationship("Plan", foreign_keys=[created_plan_id])