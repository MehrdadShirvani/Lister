from sqlalchemy import Boolean, Column, Integer, BigInteger, String, TIMESTAMP, ForeignKey
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
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    status = Column(String(50))
    account_id = Column(BigInteger, ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    
    task = relationship("Task", back_populates="plans")
    note = relationship("Note", back_populates="plans")
    time_block = relationship("TimeBlock", back_populates="plans")
    account = relationship("Account", back_populates="plans")