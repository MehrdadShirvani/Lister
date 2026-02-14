from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class AccountBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class AccountCreate(AccountBase):
    password: str

class AccountResponse(AccountBase):
    id: int
    join_date: datetime
    account_status_id: int
    account_role_id: int
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"