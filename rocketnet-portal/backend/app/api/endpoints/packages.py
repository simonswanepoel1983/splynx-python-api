"""
Package management endpoints
Service package upgrades and changes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import structlog

from app.api.endpoints.auth import get_current_customer
from app.schemas.packages import (
    ServicePackage, PackageComparison, PackageUpgradeRequest, 
    PackageUpgradeResponse, ServiceChange
)
from app.services.splynx_service import splynx_service
from app.core.exceptions import SplynxAPIError

router = APIRouter()
logger = structlog.get_logger()


@router.get("/available", response_model=List[ServicePackage])
async def get_available_packages(current_customer: dict = Depends(get_current_customer)):
    """
    Get available service packages for upgrade
    """
    try:
        packages = await splynx_service.get_available_packages(
            current_customer["customer_id"]
        )
        return packages
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting available packages", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting available packages", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available packages"
        )


@router.get("/comparison", response_model=PackageComparison)
async def get_package_comparison(current_customer: dict = Depends(get_current_customer)):
    """
    Get package comparison with current plan
    """
    try:
        all_packages = await splynx_service.get_available_packages(
            current_customer["customer_id"]
        )
        
        # Find current package
        current_package = next((pkg for pkg in all_packages if pkg.is_current), None)
        if not current_package and all_packages:
            # If no current package found, use the first one as a fallback
            current_package = all_packages[0]
            current_package.is_current = True
        
        # Get recommended packages (upgrades with better value)
        recommended_packages = [
            pkg for pkg in all_packages 
            if pkg.is_upgrade and pkg.price > (current_package.price if current_package else 0)
        ]
        
        comparison = PackageComparison(
            current_package=current_package,
            recommended_packages=recommended_packages[:3],  # Top 3 recommendations
            all_packages=all_packages
        )
        
        return comparison
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting package comparison", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting package comparison", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve package comparison"
        )


@router.post("/upgrade", response_model=PackageUpgradeResponse)
async def request_package_upgrade(
    upgrade_request: PackageUpgradeRequest,
    current_customer: dict = Depends(get_current_customer)
):
    """
    Request a package upgrade
    """
    try:
        # Validate that the package exists and is available
        available_packages = await splynx_service.get_available_packages(
            current_customer["customer_id"]
        )
        
        target_package = next(
            (pkg for pkg in available_packages if pkg.id == upgrade_request.package_id), 
            None
        )
        
        if not target_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or not available"
            )
        
        if not target_package.is_upgrade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected package is not an upgrade"
            )
        
        # Submit upgrade request to Splynx
        result = await splynx_service.request_package_upgrade(
            current_customer["customer_id"],
            upgrade_request.package_id
        )
        
        response = PackageUpgradeResponse(
            success=result["success"],
            message=result["message"],
            ticket_id=result.get("ticket_id"),
            estimated_completion="1-2 business days"
        )
        
        logger.info("Package upgrade requested", 
                   customer_id=current_customer["customer_id"],
                   package_id=upgrade_request.package_id,
                   ticket_id=result.get("ticket_id"))
        
        return response
        
    except HTTPException:
        raise
    except SplynxAPIError as e:
        logger.error("Splynx API error requesting package upgrade", 
                    customer_id=current_customer["customer_id"], 
                    package_id=upgrade_request.package_id,
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error requesting package upgrade", 
                    customer_id=current_customer["customer_id"], 
                    package_id=upgrade_request.package_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request package upgrade"
        )


@router.get("/current")
async def get_current_package(current_customer: dict = Depends(get_current_customer)):
    """
    Get customer's current service package
    """
    try:
        packages = await splynx_service.get_available_packages(
            current_customer["customer_id"]
        )
        
        current_package = next((pkg for pkg in packages if pkg.is_current), None)
        
        if not current_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Current package not found"
            )
        
        return current_package
        
    except HTTPException:
        raise
    except SplynxAPIError as e:
        logger.error("Splynx API error getting current package", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting current package", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve current package"
        )