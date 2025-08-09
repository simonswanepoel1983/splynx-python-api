from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db, User, RetentionRequest
from ..core.security import get_current_user
from ..services.splynx_service import splynx_service
from pydantic import BaseModel

router = APIRouter()

class RetentionRequestCreate(BaseModel):
    request_type: str  # 'downgrade' or 'cancel'
    reason: str
    amount_paid: Optional[float] = None

class RetentionRequestResponse(BaseModel):
    id: int
    request_type: str
    reason: str
    amount_paid: Optional[float]
    status: str
    created_at: datetime
    processed_at: Optional[datetime]

class RetentionPaymentRequest(BaseModel):
    amount: float
    payment_method: str = "credit_card"

@router.post("/request", response_model=RetentionRequestResponse)
async def create_retention_request(
    retention_request: RetentionRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new retention request (downgrade or cancellation)"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Validate request type
        if retention_request.request_type not in ["downgrade", "cancel"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request type must be 'downgrade' or 'cancel'"
            )
        
        # Check if user already has a pending request
        existing_request = db.query(RetentionRequest).filter(
            RetentionRequest.user_id == current_user.id,
            RetentionRequest.status == "pending"
        ).first()
        
        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending retention request"
            )
        
        # Calculate required payment amount based on request type
        required_amount = _calculate_retention_fee(retention_request.request_type)
        
        # Create retention request in database
        new_request = RetentionRequest(
            user_id=current_user.id,
            request_type=retention_request.request_type,
            reason=retention_request.reason,
            amount_paid=retention_request.amount_paid,
            status="pending"
        )
        
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        
        # Also create in Splynx
        try:
            await splynx_service.create_retention_request(
                current_user.splynx_customer_id,
                retention_request.request_type,
                retention_request.reason
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to create retention request in Splynx: {e}")
        
        return RetentionRequestResponse(
            id=new_request.id,
            request_type=new_request.request_type,
            reason=new_request.reason,
            amount_paid=new_request.amount_paid,
            status=new_request.status,
            created_at=new_request.created_at,
            processed_at=new_request.processed_at
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create retention request: {str(e)}"
        )

@router.post("/{request_id}/pay", response_model=RetentionRequestResponse)
async def pay_retention_fee(
    request_id: int,
    payment_request: RetentionPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process payment for retention request"""
    try:
        # Get retention request
        retention_request = db.query(RetentionRequest).filter(
            RetentionRequest.id == request_id,
            RetentionRequest.user_id == current_user.id
        ).first()
        
        if not retention_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retention request not found"
            )
        
        if retention_request.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Retention request is not pending"
            )
        
        # Calculate required amount
        required_amount = _calculate_retention_fee(retention_request.request_type)
        
        if payment_request.amount < required_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient payment amount. Required: ${required_amount}"
            )
        
        # Process payment (this would integrate with payment gateway)
        # For now, we'll simulate successful payment
        
        # Update retention request
        retention_request.amount_paid = payment_request.amount
        retention_request.status = "paid"
        retention_request.processed_at = datetime.now()
        
        db.commit()
        db.refresh(retention_request)
        
        # Update in Splynx
        try:
            await splynx_service.process_retention_payment(
                retention_request.id,
                payment_request.amount
            )
        except Exception as e:
            print(f"Failed to update retention payment in Splynx: {e}")
        
        return RetentionRequestResponse(
            id=retention_request.id,
            request_type=retention_request.request_type,
            reason=retention_request.reason,
            amount_paid=retention_request.amount_paid,
            status=retention_request.status,
            created_at=retention_request.created_at,
            processed_at=retention_request.processed_at
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment failed: {str(e)}"
        )

@router.get("/history", response_model=List[RetentionRequestResponse])
async def get_retention_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get retention request history for the user"""
    try:
        retention_requests = db.query(RetentionRequest).filter(
            RetentionRequest.user_id == current_user.id
        ).order_by(RetentionRequest.created_at.desc()).all()
        
        return [
            RetentionRequestResponse(
                id=req.id,
                request_type=req.request_type,
                reason=req.reason,
                amount_paid=req.amount_paid,
                status=req.status,
                created_at=req.created_at,
                processed_at=req.processed_at
            )
            for req in retention_requests
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get retention history: {str(e)}"
        )

@router.get("/{request_id}", response_model=RetentionRequestResponse)
async def get_retention_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific retention request details"""
    try:
        retention_request = db.query(RetentionRequest).filter(
            RetentionRequest.id == request_id,
            RetentionRequest.user_id == current_user.id
        ).first()
        
        if not retention_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retention request not found"
            )
        
        return RetentionRequestResponse(
            id=retention_request.id,
            request_type=retention_request.request_type,
            reason=retention_request.reason,
            amount_paid=retention_request.amount_paid,
            status=retention_request.status,
            created_at=retention_request.created_at,
            processed_at=retention_request.processed_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get retention request: {str(e)}"
        )

@router.get("/fees/calculate")
async def calculate_retention_fees(
    request_type: str,
    current_user: User = Depends(get_current_user)
):
    """Calculate retention fees for different request types"""
    try:
        if request_type not in ["downgrade", "cancel"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request type must be 'downgrade' or 'cancel'"
            )
        
        required_amount = _calculate_retention_fee(request_type)
        
        return {
            "request_type": request_type,
            "required_amount": required_amount,
            "currency": "USD",
            "description": f"Retention fee for {request_type} request"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate retention fees: {str(e)}"
        )

def _calculate_retention_fee(request_type: str) -> float:
    """Calculate retention fee based on request type"""
    if request_type == "downgrade":
        return 25.00  # $25 for downgrade
    elif request_type == "cancel":
        return 50.00  # $50 for cancellation
    else:
        return 0.00