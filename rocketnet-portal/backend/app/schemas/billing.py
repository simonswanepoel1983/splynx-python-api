"""
Billing data schemas
"""

from typing import List, Optional, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    """Invoice line item"""
    description: str
    quantity: float = 1.0
    unit_price: float
    total: float


class Invoice(BaseModel):
    """Invoice schema"""
    id: int
    number: str
    date: datetime
    due_date: Optional[datetime] = None
    total: float
    status: str
    items: List[InvoiceItem] = []
    
    class Config:
        from_attributes = True


class PaymentMethod(BaseModel):
    """Payment method"""
    id: str
    type: str  # card, bank_account, paypal, etc.
    last_four: Optional[str] = None
    brand: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    is_default: bool = False


class Payment(BaseModel):
    """Payment record"""
    id: int
    invoice_id: Optional[int] = None
    amount: float
    date: datetime
    method: str
    status: str
    transaction_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaymentHistory(BaseModel):
    """Payment history"""
    payments: List[Payment]
    total_paid: float
    outstanding_balance: float


class BillingOverview(BaseModel):
    """Billing overview for dashboard"""
    current_balance: float
    next_bill_amount: Optional[float] = None
    next_bill_date: Optional[datetime] = None
    overdue_amount: float = 0.0
    last_payment_date: Optional[datetime] = None
    last_payment_amount: Optional[float] = None
    recent_invoices: List[Invoice] = []
    
    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    """Payment request"""
    amount: float = Field(..., gt=0)
    payment_method_id: str
    invoice_id: Optional[int] = None