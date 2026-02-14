from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import sys
import os
import traceback

# Add debug logging
print("=" * 60)
print("MAIN.PY DEBUG STARTUP")
print("=" * 60)
print(f"Step 0: Script started at {datetime.now()}")

try:
    print("Step 1: Importing settings...")
    from core.config import settings
    print(f"  ✓ Settings loaded: DEBUG={settings.DEBUG}")
except Exception as e:
    print(f"  ✗ Error: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("Step 2: Importing database...")
    from core.database import engine, Base
    print("  ✓ Database imports successful")
except Exception as e:
    print(f"  ✗ Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("Step 3: Importing models...")
try:
    from models.account_models import AccountStatus, Account
    print("  ✓ account_models")
except Exception as e:
    print(f"  ✗ account_models: {e}")

try:
    from models.tag_models import Tag
    print("  ✓ tag_models")
except Exception as e:
    print(f"  ✗ tag_models: {e}")

try:
    from models.note_models import Note
    print("  ✓ note_models")
except Exception as e:
    print(f"  ✗ note_models: {e}")

try:
    from models.task_models import Task, TaskUrl
    print("  ✓ task_models")
except Exception as e:
    print(f"  ✗ task_models: {e}")

try:
    from models.list_models import List
    print("  ✓ list_models")
except Exception as e:
    print(f"  ✗ list_models: {e}")

try:
    from models.plan_models import Plan
    print("  ✓ plan_models")
except Exception as e:
    print(f"  ✗ plan_models: {e}")

try:
    from models.timeblock_models import TimeBlock
    print("  ✓ timeblock_models")
except Exception as e:
    print(f"  ✗ timeblock_models: {e}")

try:
    from models.notification_models import Notification
    print("  ✓ notification_models")
except Exception as e:
    print(f"  ✗ notification_models: {e}")

print("Step 4: Importing routers...")
try:
    from routers import auth, tags, timeblocks, tasks, lists, notes, plans
    print("  ✓ All routers imported")
except Exception as e:
    print(f"  ✗ Router import error: {e}")
    traceback.print_exc()

print("Step 5: Importing fastapi utilities...")
try:
    from fastapi.openapi.utils import get_openapi
    print("  ✓ get_openapi imported")
except Exception as e:
    print(f"  ✗ {e}")

print("Step 6: Creating lifespan function...")
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("  ✓ Lifespan STARTED")
        print(f"  Starting {settings.PROJECT_NAME} v{settings.VERSION}")
        print(f"  Environment: {settings.ENVIRONMENT}")
        
        if settings.ENVIRONMENT != "production":
            print("  Creating database tables...")
            try:
                Base.metadata.create_all(bind=engine)
                print("  ✓ Tables created")
            except Exception as e:
                print(f"  ✗ Table creation error: {e}")
                traceback.print_exc()
            
            print("  Seeding data...")
            try:
                from seed_data import main as seed_main
                seed_main()
                print("  ✓ Seeding complete")
            except ImportError:
                print("  Seed script not found")
            except Exception as e:
                print(f"  ✗ Seeding error: {e}")
                traceback.print_exc()
        
        print("  ✓ Lifespan startup complete")
        yield
    except Exception as e:
        print(f"  ✗ Fatal error in lifespan: {e}")
        traceback.print_exc()
        raise
    finally:
        print("  Shutting down...")

print("Step 7: Creating FastAPI app...")
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Lister",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    lifespan=lifespan,
)
print("  ✓ FastAPI app created")

print("Step 8: Setting up CORS...")
if settings.BACKEND_CORS_ORIGINS:
    origins = settings.BACKEND_CORS_ORIGINS
    if isinstance(origins, str):
        origins = [origin.strip() for origin in origins.split(",")]
    print(f"  CORS origins: {origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("  ✓ CORS middleware added")

print("Step 9: Setting up OpenAPI...")
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Task management system",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi
print("  ✓ OpenAPI configured")

print("Step 10: Including routers...")
try:
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    print("  ✓ auth router")
except Exception as e:
    print(f"  ✗ auth router error: {e}")

try:
    app.include_router(lists.router, prefix=settings.API_V1_STR)
    print("  ✓ lists router")
except Exception as e:
    print(f"  ✗ lists router error: {e}")

try:
    app.include_router(tasks.router, prefix=settings.API_V1_STR)
    print("  ✓ tasks router")
except Exception as e:
    print(f"  ✗ tasks router error: {e}")

try:
    app.include_router(tags.router, prefix=settings.API_V1_STR)
    print("  ✓ tags router")
except Exception as e:
    print(f"  ✗ tags router error: {e}")

try:
    app.include_router(timeblocks.router, prefix=settings.API_V1_STR)
    print("  ✓ timeblocks router")
except Exception as e:
    print(f"  ✗ timeblocks router error: {e}")

try:
    app.include_router(notes.router, prefix=settings.API_V1_STR)
    print("  ✓ notes router")
except Exception as e:
    print(f"  ✗ notes router error: {e}")

try:
    app.include_router(plans.router, prefix=settings.API_V1_STR)
    print("  ✓ plans router")
except Exception as e:
    print(f"  ✗ plans router error: {e}")

print("Step 11: Adding health endpoints...")

@app.get("/")
async def root():
    return {"message": "Working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

print("Step 12: Setup complete -", datetime.now())
print("=" * 60)
print("READY TO START SERVER")
print("=" * 60)

if __name__ == "__main__":
    print("Starting uvicorn...")
    uvicorn.run(
        "main_debug:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Turn off reload for debugging
        log_level="debug"
    )