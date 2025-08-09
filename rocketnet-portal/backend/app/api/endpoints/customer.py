"""
Customer profile endpoints
Customer information and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
import structlog

from app.api.endpoints.auth import get_current_customer
from app.schemas.customer import CustomerProfile, CustomerSummary
from app.services.splynx_service import splynx_service
from app.core.exceptions import CustomerNotFoundError, SplynxAPIError

router = APIRouter()
logger = structlog.get_logger()


@router.get("/profile", response_model=CustomerProfile)
async def get_customer_profile(current_customer: dict = Depends(get_current_customer)):
    """
    Get detailed customer profile information
    """
    try:
        customer_profile = await splynx_service.get_customer_profile(
            current_customer["customer_id"]
        )
        return customer_profile
        
    except CustomerNotFoundError as e:
        logger.warning("Customer profile not found", 
                      customer_id=current_customer["customer_id"])
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting customer profile", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting customer profile", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer profile"
        )


@router.get("/summary", response_model=CustomerSummary)
async def get_customer_summary(current_customer: dict = Depends(get_current_customer)):
    """
    Get customer summary for dashboard
    """
    try:
        # Get basic customer profile
        customer_profile = await splynx_service.get_customer_profile(
            current_customer["customer_id"]
        )
        
        # Get current service plan name
        current_plan = None
        if customer_profile.services:
            # Assume first service is the primary one
            current_plan = customer_profile.services[0].get("tariff_name", "Unknown Plan")
        
        # Create summary (in a full implementation, you'd fetch additional data)
        summary = CustomerSummary(
            id=customer_profile.id,
            name=customer_profile.name,
            email=customer_profile.email,
            status=customer_profile.status,
            current_plan=current_plan,
            account_balance=0.0,  # Would fetch from billing
            next_billing_date=None  # Would fetch from billing
        )
        
        return summary
        
    except CustomerNotFoundError as e:
        logger.warning("Customer not found for summary", 
                      customer_id=current_customer["customer_id"])
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting customer summary", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting customer summary", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer summary"
        )


@router.get("/services")
async def get_customer_services(current_customer: dict = Depends(get_current_customer)):
    """
    Get customer's active services
    """
    try:
        customer_profile = await splynx_service.get_customer_profile(
            current_customer["customer_id"]
        )
        
        return {
            "services": customer_profile.services,
            "total_services": len(customer_profile.services)
        }
        
    except CustomerNotFoundError as e:
        logger.warning("Customer not found for services", 
                      customer_id=current_customer["customer_id"])
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting customer services", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting customer services", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer services"
        )