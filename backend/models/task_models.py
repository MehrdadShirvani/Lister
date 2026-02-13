from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP, Date, ForeignKey, Text, Boolean, Table, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

list_tasks = Table(
    'list_tasks',
    Base.metadata,
    Column('list_id', BigInteger, ForeignKey('list.id', ondelete='CASCADE'), primary_key=True),
    Column('task_id', BigInteger, ForeignKey('task.id', ondelete='CASCADE'), primary_key=True)
)

task_tags = Table(
    'task_tags',
    Base.metadata,
    Column('task_id', BigInteger, ForeignKey('task.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', BigInteger, ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
)

task_notes = Table(
    'task_notes',
    Base.metadata,
    Column('task_id', BigInteger, ForeignKey('task.id', ondelete='CASCADE'), primary_key=True),
    Column('note_id', BigInteger, ForeignKey('note.id', ondelete='CASCADE'), primary_key=True)
)

class Task(Base):
    """Main task table"""
    __tablename__ = "task"
    
    id = Column(BigInteger, primary_key=True, index=True)
    account_id = Column(BigInteger, ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    list_id = Column(BigInteger, ForeignKey('list.id', ondelete='CASCADE'), nullable=True)
    parent_task_id = Column(BigInteger, ForeignKey('task.id', ondelete='SET NULL'), nullable=True)
    title = Column(String(255), nullable=False)
    type = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    scheduled_date = Column(Date)
    completed_at = Column(TIMESTAMP(timezone=True))
    estimated_duration = Column(Integer)  # in minutes
    priority = Column(Integer)
    status = Column(String(50))
    notes = relationship("Note", secondary=task_notes, back_populates="tasks")

    account = relationship("Account", back_populates="tasks")
    list = relationship("List", back_populates="tasks")
    
    parent_task = relationship(
        "Task", 
        remote_side=[id],
        back_populates="subtasks",
        foreign_keys=[parent_task_id]
    )
    subtasks = relationship(
        "Task", 
        back_populates="parent_task",
        cascade="all, delete-orphan",
        foreign_keys=[parent_task_id]
    )
    
    urls = relationship(
        "TaskUrl",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    tags = relationship(
        "Tag", 
        secondary=task_tags,
        back_populates="tasks"
    )
    
    lists = relationship(
        "List",
        secondary=list_tasks,
        back_populates="contained_tasks"
    )
    
    plans = relationship("Plan", back_populates="task", cascade="all, delete-orphan")
    
    suggestions = relationship("Suggestion", back_populates="task", cascade="all, delete-orphan")


class TaskUrl(Base):
    """Individual URL for a task"""
    __tablename__ = "task_urls"
    
    task_id = Column(BigInteger, ForeignKey('task.id', ondelete='CASCADE'), primary_key=True)
    url = Column(Text, primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    task = relationship("Task", back_populates="urls")
