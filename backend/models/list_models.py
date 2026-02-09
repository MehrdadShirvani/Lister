from sqlalchemy import Column, Integer, String, Text, BigInteger, TIMESTAMP, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

list_tags = Table(
    'list_tags',
    Base.metadata,
    Column('list_id', BigInteger, ForeignKey('list.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', BigInteger, ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
)


class List(Base):
    """List table for organizing tasks"""
    __tablename__ = "list"
    
    id = Column(BigInteger, primary_key=True, index=True)
    account_id = Column(BigInteger, ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(Integer)
    status = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    account = relationship("Account", back_populates="lists")
    tasks = relationship("Task", back_populates="list", cascade="all, delete-orphan")
    
    tags = relationship(
        "Tag", 
        secondary=list_tags,
        back_populates="lists"
    )
    
    contained_tasks = relationship(
        "Task",
        secondary="list_tasks",
        back_populates="lists"
    )