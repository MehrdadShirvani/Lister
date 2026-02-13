from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from core.database import engine, Base
# from routers import accounts, lists, tasks, tags, notifications, notes, plans, suggestions
from routers import auth, tags
from models.account_models import AccountStatus, Account
from models.list_models import List
from models.task_models import Task, TaskUrl, Suggestion
from models.tag_models import Tag
from models.notification_models import Notification
from models.note_models import Note
from models.plan_models import Plan
from models.timeblock_models import TimeBlock

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    
    if settings.ENVIRONMENT != "production":
        print("Creating/updating database tables...")
        Base.metadata.create_all(bind=engine)
        
        seed_initial_data()
    else:
        print("Production environment detected - skipping auto table creation")
        print("Use migrations for production: alembic upgrade head")
    
    yield
    print("Shutting down application...")

def seed_initial_data():
    """Seed initial data"""
    try:
        from seed_data import main as seed_main
        seed_main()
    except ImportError:
        print("Seed script not found, skipping data seeding")
    except Exception as e:
        print(f"Error during seeding: {e}")

# Create FastAPI app 
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Lister",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# # Include all routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
# app.include_router(accounts.router, prefix=settings.API_V1_STR)
# app.include_router(lists.router, prefix=settings.API_V1_STR)
# app.include_router(tasks.router, prefix=settings.API_V1_STR)
app.include_router(tags.router, prefix=settings.API_V1_STR)
# app.include_router(notifications.router, prefix=settings.API_V1_STR)
# app.include_router(notes.router, prefix=settings.API_V1_STR)
# app.include_router(plans.router, prefix=settings.API_V1_STR)
# app.include_router(suggestions.router, prefix=settings.API_V1_STR)

# Health check endpoints
@app.get("/")
async def root():
    return {
        "message": f"{settings.PROJECT_NAME} is running",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else None,
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    from sqlalchemy import text
    
    db_status = "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": {
            "status": db_status,
            "host": settings.DB_HOST,
            "name": settings.DB_NAME,
        },
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/config")
async def get_config():
    """Get current configuration"""
    if not settings.DEBUG:
        return {"message": "Configuration endpoint disabled in production"}
    
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database": {
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "name": settings.DB_NAME,
            "pool_size": settings.DB_POOL_SIZE,
        },
        "api": {
            "v1_prefix": settings.API_V1_STR,
            "cors_origins": settings.BACKEND_CORS_ORIGINS,
        },
        "security": {
            "token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )