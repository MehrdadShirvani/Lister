from sqlalchemy import Boolean, Column, Integer, BigInteger, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Notification(Base):
    """Notification table for user alerts"""
    __tablename__ = "notification"
    
    id = Column(BigInteger, primary_key=True, index=True)
    account_id = Column(BigInteger, ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    seen_at = Column(TIMESTAMP(timezone=True))
    notification_type = Column(String(50), default="info")
    is_read = Column(Boolean, default=False)
    
    account = relationship("Account", back_populates="notifications")