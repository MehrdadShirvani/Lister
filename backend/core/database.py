from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from core.config import settings

database_url = settings.sqlalchemy_database_url

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  
    echo=settings.DB_ECHO, 
    echo_pool=settings.DEBUG, 
    future=True,  
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()
from models.account_models import AccountStatus, Account, AccountRole
from models.list_models import List
from models.task_models import Task, TaskUrl, Suggestion
from models.tag_models import Tag
from models.notification_models import Notification
from models.note_models import Note
from models.plan_models import Plan
from models.timeblock_models import TimeBlock
from models.task_models import TaskUrl, list_tasks, task_tags, task_notes
from models.list_models import list_tags
from models.tag_models import timeblock_tags

def get_db():
    """
    Dependency to provide a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if settings.DB_ECHO and settings.DEBUG:
    print(f"Database URL: {settings.sqlalchemy_database_url}")
    print(f"Database host: {settings.DB_HOST}")
    print(f"Database name: {settings.DB_NAME}")