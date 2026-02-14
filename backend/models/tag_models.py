from sqlalchemy import TIMESTAMP, Column, Integer, String, BigInteger, Text, Boolean, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from core.database import Base

timeblock_tags = Table(
    'timeblock_tags',
    Base.metadata,
    Column('time_block_id', BigInteger, ForeignKey('timeblock.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', BigInteger, ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
)



class Tag(Base):
    """Tag table for categorizing tasks"""
    __tablename__ = "tag"
    
    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    type = Column(String(50))
    description = Column(Text)
    account_id = Column(BigInteger, ForeignKey('account.id', ondelete='SET NULL'), nullable=True)
    is_public = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    account = relationship("Account", back_populates="tags")
    
    tasks = relationship(
        "Task", 
        secondary="task_tags",
        back_populates="tags"
    )
    
    lists = relationship(
        "List",
        secondary="list_tags",
        back_populates="tags"
    )
    
    time_blocks = relationship(
        "TimeBlock",
        secondary=timeblock_tags,
        back_populates="tags"
    )

    notes = relationship(
        "Note",
        secondary="note_tags",
        back_populates="tags"
    )