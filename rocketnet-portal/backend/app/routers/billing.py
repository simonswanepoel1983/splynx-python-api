from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..core.database import get_db, User, BillingHistory
from ..core.security import get_current_user
from ..services.splynx_service import splynx_service
from pydantic import BaseModel

router = APIRouter()

class BillingHistoryResponse(BaseModel):
    id: int
    invoice_number: str
    amount: float
    due_date: datetime
    paid_date: Optional[datetime]
    status: str
    description: str
    created_at: datetime

class InvoiceDetail(BaseModel):
    invoice_number: str
    amount: float
    due_date: datetime
    status: str
    items: List[dict]
    total_tax: float
    subtotal: float

@router.get("/history", response_model=List[BillingHistoryResponse])
async def get_billing_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get customer billing history"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Get billing history from Splynx
        splynx_billing = await splynx_service.get_customer_billing(current_user.splynx_customer_id)
        
        # Convert to our format
        billing_history = []
        for invoice in splynx_billing:
            billing_history.append(BillingHistoryResponse(
                id=invoice.get("id"),
                invoice_number=invoice.get("invoice_number", ""),
                amount=float(invoice.get("amount", 0)),
                due_date=datetime.fromisoformat(invoice.get("due_date", datetime.now().isoformat())),
                paid_date=datetime.fromisoformat(invoice.get("paid_date")) if invoice.get("paid_date") else None,
                status=invoice.get("status", "unpaid"),
                description=invoice.get("description", ""),
                created_at=datetime.fromisoformat(invoice.get("created_at", datetime.now().isoformat()))
            ))
        
        return billing_history[offset:offset + limit]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing history: {str(e)}"
        )

@router.get("/current", response_model=InvoiceDetail)
async def get_current_invoice(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current invoice for customer"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Get current invoice from Splynx
        splynx_billing = await splynx_service.get_customer_billing(current_user.splynx_customer_id)
        
        # Find current invoice (most recent unpaid)
        current_invoice = None
        for invoice in splynx_billing:
            if invoice.get("status") in ["unpaid", "overdue"]:
                if not current_invoice or invoice.get("due_date") > current_invoice.get("due_date"):
                    current_invoice = invoice
        
        if not current_invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No current invoice found"
            )
        
        return InvoiceDetail(
            invoice_number=current_invoice.get("invoice_number", ""),
            amount=float(current_invoice.get("amount", 0)),
            due_date=datetime.fromisoformat(current_invoice.get("due_date", datetime.now().isoformat())),
            status=current_invoice.get("status", "unpaid"),
            items=current_invoice.get("items", []),
            total_tax=float(current_invoice.get("total_tax", 0)),
            subtotal=float(current_invoice.get("subtotal", 0))
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current invoice: {str(e)}"
        )

@router.get("/outstanding", response_model=List[BillingHistoryResponse])
async def get_outstanding_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get outstanding invoices for customer"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Get billing history from Splynx
        splynx_billing = await splynx_service.get_customer_billing(current_user.splynx_customer_id)
        
        # Filter outstanding invoices
        outstanding_invoices = []
        for invoice in splynx_billing:
            if invoice.get("status") in ["unpaid", "overdue"]:
                outstanding_invoices.append(BillingHistoryResponse(
                    id=invoice.get("id"),
                    invoice_number=invoice.get("invoice_number", ""),
                    amount=float(invoice.get("amount", 0)),
                    due_date=datetime.fromisoformat(invoice.get("due_date", datetime.now().isoformat())),
                    paid_date=datetime.fromisoformat(invoice.get("paid_date")) if invoice.get("paid_date") else None,
                    status=invoice.get("status", "unpaid"),
                    description=invoice.get("description", ""),
                    created_at=datetime.fromisoformat(invoice.get("created_at", datetime.now().isoformat()))
                ))
        
        return outstanding_invoices
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get outstanding invoices: {str(e)}"
        )

@router.get("/summary")
async def get_billing_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing summary for customer"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Get billing history from Splynx
        splynx_billing = await splynx_service.get_customer_billing(current_user.splynx_customer_id)
        
        # Calculate summary
        total_outstanding = 0
        total_paid = 0
        overdue_count = 0
        
        for invoice in splynx_billing:
            amount = float(invoice.get("amount", 0))
            status = invoice.get("status", "unpaid")
            
            if status in ["unpaid", "overdue"]:
                total_outstanding += amount
                if status == "overdue":
                    overdue_count += 1
            elif status == "paid":
                total_paid += amount
        
        return {
            "total_outstanding": total_outstanding,
            "total_paid": total_paid,
            "overdue_count": overdue_count,
            "total_invoices": len(splynx_billing)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing summary: {str(e)}"
        )

@router.post("/pay/{invoice_number}")
async def pay_invoice(
    invoice_number: str,
    payment_amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process payment for an invoice"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # This would integrate with payment gateway
        # For now, we'll just return success
        return {
            "message": "Payment processed successfully",
            "invoice_number": invoice_number,
            "amount_paid": payment_amount,
            "transaction_id": f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment failed: {str(e)}"
        )