from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class TimeBlock(Base):
    """Time block for scheduling"""
    __tablename__ = "timeblock"
    
    id = Column(BigInteger, primary_key=True, index=True)
    account_id = Column(BigInteger, ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    day_of_week = Column(Integer)  
    is_recurring = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    account = relationship("Account", back_populates="time_blocks")
    plans = relationship("Plan", back_populates="time_block", cascade="all, delete-orphan")
    
    tags = relationship(
        "Tag",
        secondary="timeblock_tags",
        back_populates="time_blocks"
    )
    
    suggestions = relationship("Suggestion", back_populates="time_block", cascade="all, delete-orphan")