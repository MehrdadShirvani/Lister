"""
Simple data seeder for initial database setup
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.config import Settings
from core.database import SessionLocal
from models.account_models import AccountRole, AccountStatus
from models.tag_models import Tag
from sqlalchemy.exc import IntegrityError

def seed_account_roles(db):
    """Seed initial account roles"""
    print("Seeding account roles...")
    
    roles = [
        {"name": "User", "description": "Regular user account", "level": 0},
        {"name": "Moderator", "description": "Content moderator", "level": 50},
        {"name": "Admin", "description": "Administrator", "level": 100},
    ]
    
    for role_data in roles:
        existing = db.query(AccountRole).filter_by(name=role_data["name"]).first()
        if not existing:
            role = AccountRole(**role_data)
            db.add(role)
            print(f"  - Added role: {role_data['name']}")
        else:
            print(f"  - Role already exists: {role_data['name']}")
    
    db.commit()

def seed_account_statuses(db):
    """Seed initial account statuses"""
    print("\nSeeding account statuses...")
    
    statuses = [
        {"title": "Active"},
        {"title": "Disabled"},
        {"title": "Not Verified"},
        {"title": "Suspended"},
        {"title": "Banned"},
    ]
    
    for status_data in statuses:
        existing = db.query(AccountStatus).filter_by(title=status_data["title"]).first()
        if not existing:
            status = AccountStatus(**status_data)
            db.add(status)
            print(f"  - Added status: {status_data['title']}")
        else:
            print(f"  - Status already exists: {status_data['title']}")
    
    db.commit()

def seed_public_tags(db):
    """Seed public tags by category"""
    print("\nSeeding public tags...")

    account_id = None
    
    # Tags by type
    tags_by_type = {
        "Mood": [
            "Calm", "Cozy", "Light", "Reflective", "Melancholic",
            "Joyful", "Playful", "Cathartic", "Nostalgic", "Meaningful"
        ],
        "Energy": [
            "Very Low", "Low", "Medium", "High", "Very High"
        ],
        "Vibe": [
            "Slow", "Warm", "Chill", "Minimal", "Intimate",
            "Dark", "Absurd", "Epic"
        ],
        "Context": [
            "Late Night", "After Work", "Weekend", "Rainy Day",
            "Short Break", "Long Session", "Background", "Focused"
        ],
        "Social": [
            "Alone", "With Friends", "With Partner", "Family Friendly",
            "Crowd", "Passive Together"
        ],
        "Commitment": [
            "Zero Commitment", "Low Commitment", "Medium Commitment",
            "High Commitment", "One-shot", "Ongoing"
        ],
        "Subject": [
            "Film", "Series", "Book", "Music", "Podcast",
            "Game", "Documentary", "Art", "Learning-for-fun", "Random"
        ]
    }
    
    tags_added = 0
    tags_skipped = 0
    
    for tag_type, tag_list in tags_by_type.items():
        print(f"\n  Type: {tag_type}")
        for tag_name in tag_list:
            # Check if tag already exists
            existing = db.query(Tag).filter_by(title=tag_name, type=tag_type).first()
            if not existing:
                tag = Tag(
                    title=tag_name,
                    type=tag_type,
                    description=f"Public {tag_type.lower()} tag",
                    account_id=account_id,
                    is_public=True
                )
                db.add(tag)
                tags_added += 1
                print(f"    - Added: {tag_name}")
            else:
                tags_skipped += 1
                print(f"    - Exists: {tag_name}")
    
    db.commit()
    print(f"\n  Total: {tags_added} tags added, {tags_skipped} already existed")

def main():
    """Main seeding function"""
    print("=" * 50)
    print("DATABASE SEEDING SCRIPT")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Seed in order (roles first, then statuses, then tags)
        seed_account_roles(db)
        seed_account_statuses(db)
        
        # A default admin if none exists
        from models.account_models import Account
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        admin_role = db.query(AccountRole).filter_by(name="Admin").first()
        active_status = db.query(AccountStatus).filter_by(title="Active").first()
        
        if admin_role and active_status:
            # Check if admin user exists
            admin_user = db.query(Account).filter_by(account_role_id=admin_role.id).first()
            settings = Settings()
            
            if not admin_user:
                print("\nCreating default admin user...")
                admin_user = Account(
                    first_name=settings.ADMIN_FIRST_NAME,
                    last_name=settings.ADMIN_LAST_NAME,
                    email=settings.ADMIN_EMAIL,
                    account_status_id=active_status.id,
                    account_role_id=admin_role.id,
                    password_hash=pwd_context.hash(settings.ADMIN_PASSWORD)
                )
                db.add(admin_user)
                db.commit()
        
        # Now seed tags
        seed_public_tags(db)
        
        print("\n" + "=" * 50)
        print("SEEDING COMPLETE!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nError during seeding: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()