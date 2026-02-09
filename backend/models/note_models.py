from sqlalchemy import Column, Integer, String, BigInteger, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Note(Base):
    """Note table"""
    __tablename__ = "note"
    
    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(Text)
    quality_score = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    account_id = Column(BigInteger, ForeignKey('account.id', ondelete='CASCADE'), nullable=True)
    
    account = relationship("Account", back_populates="notes")
    plans = relationship("Plan", back_populates="note", cascade="all, delete-orphan")