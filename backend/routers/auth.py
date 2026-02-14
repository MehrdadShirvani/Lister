from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from core.dependencies import get_current_user
from schemas.auth_schemas import UserSignup, Token, TokenData
from schemas.account_schemas import AccountResponse
from services.auth_service import AuthService
from services.account_service import AccountService
from core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

auth_service = AuthService()
account_service = AccountService()

@router.post("/signup", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """Sign up a new user"""
    return account_service.create_account(db, user_data)

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if user.account_status.title != "Active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not active"
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AccountResponse)
def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current user information"""
    return current_user