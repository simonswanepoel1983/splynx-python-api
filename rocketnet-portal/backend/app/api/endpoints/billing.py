"""
Billing endpoints
Invoice management and payment history
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
import structlog

from app.api.endpoints.auth import get_current_customer
from app.schemas.billing import Invoice, BillingOverview, PaymentHistory
from app.services.splynx_service import splynx_service
from app.core.exceptions import SplynxAPIError

router = APIRouter()
logger = structlog.get_logger()


@router.get("/overview", response_model=BillingOverview)
async def get_billing_overview(current_customer: dict = Depends(get_current_customer)):
    """
    Get billing overview for dashboard
    """
    try:
        # Get recent invoices
        recent_invoices = await splynx_service.get_customer_invoices(
            current_customer["customer_id"], 
            limit=5
        )
        
        # Calculate overview data
        current_balance = 0.0
        overdue_amount = 0.0
        
        for invoice in recent_invoices:
            if invoice.status == "unpaid":
                current_balance += invoice.total
                # Check if overdue (simplified logic)
                if invoice.due_date and invoice.due_date < invoice.date:
                    overdue_amount += invoice.total
        
        overview = BillingOverview(
            current_balance=current_balance,
            next_bill_amount=None,  # Would calculate from upcoming billing
            next_bill_date=None,
            overdue_amount=overdue_amount,
            last_payment_date=None,  # Would fetch from payment history
            last_payment_amount=None,
            recent_invoices=recent_invoices
        )
        
        return overview
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting billing overview", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting billing overview", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve billing overview"
        )


@router.get("/invoices", response_model=List[Invoice])
async def get_invoices(
    current_customer: dict = Depends(get_current_customer),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get customer invoices with pagination
    """
    try:
        invoices = await splynx_service.get_customer_invoices(
            current_customer["customer_id"], 
            limit=limit
        )
        
        # Apply offset (in a full implementation, this would be handled by the API)
        if offset > 0:
            invoices = invoices[offset:]
        
        return invoices
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting invoices", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting invoices", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoices"
        )


@router.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(
    invoice_id: int,
    current_customer: dict = Depends(get_current_customer)
):
    """
    Get specific invoice details
    """
    try:
        # Get all invoices and find the specific one
        # In a full implementation, you'd have a direct API call for this
        invoices = await splynx_service.get_customer_invoices(
            current_customer["customer_id"], 
            limit=100
        )
        
        invoice = next((inv for inv in invoices if inv.id == invoice_id), None)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        return invoice
        
    except HTTPException:
        raise
    except SplynxAPIError as e:
        logger.error("Splynx API error getting invoice", 
                    customer_id=current_customer["customer_id"], 
                    invoice_id=invoice_id,
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting invoice", 
                    customer_id=current_customer["customer_id"], 
                    invoice_id=invoice_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoice"
        )


@router.get("/payment-history", response_model=PaymentHistory)
async def get_payment_history(
    current_customer: dict = Depends(get_current_customer),
    limit: int = Query(default=20, le=100)
):
    """
    Get customer payment history
    """
    try:
        # In a full implementation, you'd fetch actual payment data from Splynx
        # For now, we'll return a placeholder response
        payment_history = PaymentHistory(
            payments=[],
            total_paid=0.0,
            outstanding_balance=0.0
        )
        
        logger.info("Payment history retrieved", 
                   customer_id=current_customer["customer_id"])
        
        return payment_history
        
    except Exception as e:
        logger.error("Unexpected error getting payment history", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment history"
        )


@router.get("/balance")
async def get_account_balance(current_customer: dict = Depends(get_current_customer)):
    """
    Get current account balance
    """
    try:
        # Get recent invoices to calculate balance
        invoices = await splynx_service.get_customer_invoices(
            current_customer["customer_id"], 
            limit=50
        )
        
        # Calculate current balance
        balance = 0.0
        overdue = 0.0
        
        for invoice in invoices:
            if invoice.status == "unpaid":
                balance += invoice.total
                # Simplified overdue calculation
                if invoice.due_date and invoice.due_date < invoice.date:
                    overdue += invoice.total
        
        return {
            "current_balance": balance,
            "overdue_amount": overdue,
            "currency": "USD"
        }
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting balance", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting balance", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account balance"
        )