"""
Retention process endpoints
Handles downgrades and cancellations with retention flow
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
import structlog
from datetime import datetime

from app.api.endpoints.auth import get_current_customer
from app.core.config import settings
from app.services.splynx_service import splynx_service
from app.core.exceptions import SplynxAPIError, RetentionProcessError

router = APIRouter()
logger = structlog.get_logger()


class RetentionRequest(BaseModel):
    """Retention process request"""
    action: str  # "downgrade" or "cancel"
    reason: str
    target_package_id: Optional[int] = None  # For downgrades
    notes: Optional[str] = None


class RetentionPayment(BaseModel):
    """Retention payment request"""
    retention_id: str
    payment_method_id: str
    amount: float


@router.post("/initiate")
async def initiate_retention_process(
    retention_request: RetentionRequest,
    current_customer: dict = Depends(get_current_customer)
):
    """
    Initiate retention process for service changes
    """
    customer_id = current_customer["customer_id"]
    
    try:
        # Validate action
        if retention_request.action not in ["downgrade", "cancel"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action must be 'downgrade' or 'cancel'"
            )
        
        # For downgrades, validate target package
        if retention_request.action == "downgrade":
            if not retention_request.target_package_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Target package ID required for downgrades"
                )
            
            # Validate target package exists and is a downgrade
            available_packages = await splynx_service.get_available_packages(customer_id)
            target_package = next(
                (pkg for pkg in available_packages if pkg.id == retention_request.target_package_id),
                None
            )
            
            if not target_package:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target package not found"
                )
        
        # Initiate retention process via Splynx
        result = await splynx_service.initiate_retention_process(
            customer_id,
            retention_request.action,
            retention_request.reason
        )
        
        logger.info("Retention process initiated", 
                   customer_id=customer_id,
                   action=retention_request.action,
                   ticket_id=result.get("ticket_id"))
        
        return {
            "retention_id": f"ret_{customer_id}_{result.get('ticket_id', 'unknown')}",
            "status": "initiated",
            "message": result["message"],
            "retention_fee": result["retention_fee"],
            "action": retention_request.action,
            "ticket_id": result.get("ticket_id"),
            "next_steps": "Please pay the retention fee to proceed with your request"
        }
        
    except HTTPException:
        raise
    except SplynxAPIError as e:
        logger.error("Splynx API error initiating retention process", 
                    customer_id=customer_id, 
                    action=retention_request.action,
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error initiating retention process", 
                    customer_id=customer_id, 
                    action=retention_request.action,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate retention process"
        )


@router.post("/payment")
async def process_retention_payment(
    payment_request: RetentionPayment,
    current_customer: dict = Depends(get_current_customer)
):
    """
    Process retention fee payment
    """
    customer_id = current_customer["customer_id"]
    
    try:
        # Validate retention fee amount
        if payment_request.amount != settings.RETENTION_FEE_AMOUNT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment amount. Expected ${settings.RETENTION_FEE_AMOUNT}"
            )
        
        # In a real implementation, you would:
        # 1. Process payment through payment gateway
        # 2. Update retention status in Splynx
        # 3. Trigger the requested action (downgrade/cancel)
        
        # Simulate payment processing
        logger.info("Processing retention payment", 
                   customer_id=customer_id,
                   retention_id=payment_request.retention_id,
                   amount=payment_request.amount)
        
        # Mock successful payment
        payment_successful = True
        
        if payment_successful:
            return {
                "status": "payment_processed",
                "message": "Retention fee payment successful. Your request will be processed within 1-2 business days.",
                "retention_id": payment_request.retention_id,
                "payment_amount": payment_request.amount,
                "transaction_id": f"txn_{customer_id}_{int(datetime.now().timestamp())}",
                "next_steps": "You will receive email confirmation when your service change is complete"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Payment processing failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error processing retention payment", 
                    customer_id=customer_id, 
                    retention_id=payment_request.retention_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process retention payment"
        )


@router.get("/info")
async def get_retention_info(current_customer: dict = Depends(get_current_customer)):
    """
    Get retention process information and current fee
    """
    try:
        return {
            "retention_fee": settings.RETENTION_FEE_AMOUNT,
            "currency": "USD",
            "policy": {
                "description": "A retention fee is required for service downgrades and cancellations to cover administrative costs and early termination fees.",
                "applies_to": ["downgrade", "cancel"],
                "processing_time": "1-2 business days after payment",
                "refund_policy": "Retention fees are non-refundable"
            },
            "payment_methods": ["credit_card", "debit_card", "bank_transfer"],
            "contact_info": {
                "support_email": "support@rocketnet.com",
                "support_phone": "1-800-ROCKET-NET"
            }
        }
        
    except Exception as e:
        logger.error("Failed to get retention info", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve retention information"
        )


@router.get("/status/{retention_id}")
async def get_retention_status(
    retention_id: str,
    current_customer: dict = Depends(get_current_customer)
):
    """
    Get status of a retention process
    """
    try:
        # In a real implementation, you would query the retention status from your database
        # For now, return a mock status
        
        return {
            "retention_id": retention_id,
            "status": "awaiting_payment",
            "action": "downgrade",
            "retention_fee": settings.RETENTION_FEE_AMOUNT,
            "created_date": "2024-01-15T10:30:00Z",
            "payment_due_date": "2024-01-22T23:59:59Z",
            "estimated_completion": "2024-01-24T17:00:00Z"
        }
        
    except Exception as e:
        logger.error("Failed to get retention status", 
                    retention_id=retention_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve retention status"
        )