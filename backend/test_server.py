#!/usr/bin/env python
"""
Comprehensive server diagnostic tool
Run this to test your FastAPI server step by step
"""
import sys
import os
import time
import socket
import subprocess
import threading
import requests
import traceback

print("=" * 60)
print("FASTAPI SERVER DIAGNOSTIC TOOL")
print("=" * 60)

# Step 1: Check Python environment
print("\n[1] CHECKING PYTHON ENVIRONMENT")
print("-" * 40)
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Script location: {__file__}")

# Step 2: Check if port is available
print("\n[2] CHECKING PORT 8000 AVAILABILITY")
print("-" * 40)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    sock.bind(('0.0.0.0', 8000))
    print("✓ Port 8000 is available")
    sock.close()
except Exception as e:
    print(f"✗ Port 8000 is in use or unavailable: {e}")
    # Check what's using it
    if sys.platform == "win32":
        result = subprocess.run(["netstat", "-ano", "|", "findstr", ":8000"], 
                               shell=True, capture_output=True, text=True)
        print(result.stdout)
    else:
        result = subprocess.run(["lsof", "-i", ":8000"], 
                               capture_output=True, text=True)
        print(result.stdout)

# Step 3: Test imports one by one
print("\n[3] TESTING IMPORTS")
print("-" * 40)

def test_import(module_name, import_statement):
    try:
        exec(import_statement)
        print(f"✓ {module_name}")
        return True
    except Exception as e:
        print(f"✗ {module_name}: {e}")
        traceback.print_exc()
        return False

# Test core imports
test_import("core.config", "from core.config import settings")
test_import("core.database", "from core.database import engine, Base")

# Test model imports
test_import("models.account_models", "from models.account_models import AccountStatus, Account")
test_import("models.tag_models", "from models.tag_models import Tag")
test_import("models.note_models", "from models.note_models import Note")
test_import("models.task_models", "from models.task_models import Task, TaskUrl")
test_import("models.list_models", "from models.list_models import List")
test_import("models.plan_models", "from models.plan_models import Plan")
test_import("models.timeblock_models", "from models.timeblock_models import TimeBlock")
test_import("models.notification_models", "from models.notification_models import Notification")

# Test router imports
test_import("routers.auth", "from routers import auth")
test_import("routers.tags", "from routers import tags")
test_import("routers.timeblocks", "from routers import timeblocks")
test_import("routers.tasks", "from routers import tasks")
test_import("routers.lists", "from routers import lists")
test_import("routers.notes", "from routers import notes")
test_import("routers.plans", "from routers import plans")

# Step 4: Test creating the app
print("\n[4] TESTING APP CREATION")
print("-" * 40)
try:
    print("Importing main module...")
    import main
    print("✓ Main module imported")
    print("✓ App created successfully")
except Exception as e:
    print(f"✗ Failed to create app: {e}")
    traceback.print_exc()

# Step 5: Test database connection
print("\n[5] TESTING DATABASE CONNECTION")
print("-" * 40)
try:
    from core.database import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"✓ Database connected: {result.scalar()}")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    traceback.print_exc()

# Step 6: Check environment variables
print("\n[6] ENVIRONMENT VARIABLES")
print("-" * 40)
try:
    from core.config import settings
    print(f"PROJECT_NAME: {settings.PROJECT_NAME}")
    print(f"ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"DB_HOST: {settings.DB_HOST}")
    print(f"DB_NAME: {settings.DB_NAME}")
    print(f"CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")
except Exception as e:
    print(f"✗ Failed to read settings: {e}")

# Step 7: Try running the server for a few seconds
print("\n[7] ATTEMPTING TO START SERVER")
print("-" * 40)
print("Starting server in a separate thread for 5 seconds...")

server_process = None
try:
    # Start server in a subprocess
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(3)
    
    # Test if server responded
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        print(f"✓ Server responded with status {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("✗ Server did not respond - check if it crashed")
        # Get error output
        stdout, stderr = server_process.communicate(timeout=1)
        if stderr:
            print("\nSERVER ERROR OUTPUT:")
            print(stderr)
    except Exception as e:
        print(f"✗ Error testing server: {e}")
        
finally:
    if server_process:
        server_process.terminate()
        print("\nServer process terminated")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)