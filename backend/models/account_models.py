from sqlalchemy import Column, Integer, String, BigInteger, Text, TIMESTAMP, ForeignKey, Table, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

account_timezones = Table(
    'account_timezones',
    Base.metadata,
    Column('account_id', BigInteger, ForeignKey('account.id', ondelete='CASCADE'), primary_key=True),
    Column('time_zone', String(100), primary_key=True)
)

class AccountStatus(Base):
    """Account status reference table"""
    __tablename__ = "account_status"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, unique=True, index=True)
    
    accounts = relationship("Account", back_populates="account_status")


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
    
    account_status = relationship("AccountStatus", back_populates="accounts")
    timezones = relationship(
        "AccountTimezone", 
        secondary=account_timezones,
        back_populates="accounts"
    )
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