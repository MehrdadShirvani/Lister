from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.database import get_db
from services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
auth_service = AuthService()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Dependency to get current authenticated user"""
    return auth_service.get_current_user(db, token)

def get_current_active_user(current_user = Depends(get_current_user)):
    """Dependency to ensure user is active"""
    if current_user.account_status.title != "Active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user