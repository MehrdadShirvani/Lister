from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.account_models import Account, AccountRole, AccountStatus
from schemas.account_schemas import AccountCreate
from services.auth_service import AuthService

auth_service = AuthService()

class AccountService:
    def create_account(self, db: Session, account_data: AccountCreate):
        """Create a new user account"""
        # Check if email already exists
        existing_user = db.query(Account).filter(Account.email == account_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Get default role (User) and status (Active)
        user_role = db.query(AccountRole).filter(AccountRole.name == "User").first()
        active_status = db.query(AccountStatus).filter(AccountStatus.title == "Active").first()
        
        if not user_role or not active_status:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="System configuration error"
            )
        
        # Create account
        hashed_password = auth_service.hash_password(account_data.password)
        db_account = Account(
            first_name=account_data.first_name,
            last_name=account_data.last_name,
            email=account_data.email,
            account_status_id=active_status.id,
            account_role_id=user_role.id,
            password_hash=hashed_password
        )
        
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account
    
    def get_account_by_id(self, db: Session, account_id: int):
        """Get account by ID"""
        return db.query(Account).filter(Account.id == account_id).first()
    
    def get_account_by_email(self, db: Session, email: str):
        """Get account by email"""
        return db.query(Account).filter(Account.email == email).first()