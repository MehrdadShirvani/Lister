from sqlalchemy import Column, Integer, String, BigInteger, Text, TIMESTAMP, ForeignKey, Table, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class AccountStatus(Base):
    """Account status reference table"""
    __tablename__ = "account_status"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, unique=True, index=True)
    
    accounts = relationship("Account", back_populates="account_status")

class AccountRole(Base):
    """Account role reference table"""
    __tablename__ = "account_role"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text)
    level = Column(Integer, default=0)  # Higher number = more permissions
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    accounts = relationship("Account", back_populates="role")

class Account(Base):
    """Main account table"""
    __tablename__ = "account"
    
    id = Column(BigInteger, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    join_date = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    account_status_id = Column(Integer, ForeignKey('account_status.id'), nullable=False)
    password_hash = Column(Text, nullable=False)
    account_role_id = Column(Integer, ForeignKey('account_role.id'), nullable=False, default=1)

    role = relationship("AccountRole", back_populates="accounts")
    account_status = relationship("AccountStatus", back_populates="accounts")

    lists = relationship("List", back_populates="account", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="account", cascade="all, delete-orphan")
    
    tags = relationship("Tag", back_populates="account", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="account", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="account", cascade="all, delete-orphan")
    time_blocks = relationship("TimeBlock", back_populates="account", cascade="all, delete-orphan")
    plans = relationship("Plan", back_populates="account", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"