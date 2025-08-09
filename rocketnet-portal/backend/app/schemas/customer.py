"""
Customer data schemas
"""

from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class CustomerBase(BaseModel):
    """Base customer schema"""
    login: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=50)


class CustomerLogin(BaseModel):
    """Customer login request"""
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class CustomerProfile(CustomerBase):
    """Customer profile with full details"""
    id: int
    status: str
    services: List[Any] = []
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CustomerSummary(BaseModel):
    """Customer summary for dashboard"""
    id: int
    name: str
    email: EmailStr
    status: str
    current_plan: Optional[str] = None
    account_balance: Optional[float] = None
    next_billing_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True