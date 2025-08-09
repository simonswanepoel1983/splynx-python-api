from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db, User, Package
from ..core.security import get_current_user
from ..services.splynx_service import splynx_service
from pydantic import BaseModel

router = APIRouter()

class PackageInfo(BaseModel):
    id: int
    name: str
    description: str
    speed_down: int
    speed_up: int
    price: float
    is_active: bool

class PackageUpgradeRequest(BaseModel):
    new_package_id: int
    upgrade_date: Optional[datetime] = None

class PackageComparison(BaseModel):
    current_package: Optional[PackageInfo]
    available_packages: List[PackageInfo]
    recommended_upgrades: List[PackageInfo]

@router.get("/available", response_model=List[PackageInfo])
async def get_available_packages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available packages"""
    try:
        # Get packages from Splynx
        splynx_packages = await splynx_service.get_available_packages()
        
        # Convert to our format
        packages = []
        for package in splynx_packages:
            packages.append(PackageInfo(
                id=package.get("id"),
                name=package.get("name", ""),
                description=package.get("description", ""),
                speed_down=package.get("speed_down", 0),
                speed_up=package.get("speed_up", 0),
                price=float(package.get("price", 0)),
                is_active=package.get("is_active", True)
            ))
        
        return packages
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available packages: {str(e)}"
        )

@router.get("/current", response_model=PackageInfo)
async def get_current_package(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current package for the user"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Get customer info from Splynx
        customer_info = await splynx_service.get_customer_info(current_user.splynx_customer_id)
        
        # Find current internet service
        current_package = None
        services = customer_info.get("services", [])
        
        for service in services:
            if service.get("type") == "internet":
                current_package = PackageInfo(
                    id=service.get("id"),
                    name=service.get("name", "Unknown"),
                    description=service.get("description", ""),
                    speed_down=service.get("speed_down", 0),
                    speed_up=service.get("speed_up", 0),
                    price=float(service.get("price", 0)),
                    is_active=service.get("is_active", True)
                )
                break
        
        if not current_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No current package found"
            )
        
        return current_package
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current package: {str(e)}"
        )

@router.post("/upgrade", response_model=dict)
async def upgrade_package(
    upgrade_request: PackageUpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade customer package"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Validate package exists
        available_packages = await splynx_service.get_available_packages()
        package_exists = any(pkg.get("id") == upgrade_request.new_package_id for pkg in available_packages)
        
        if not package_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid package ID"
            )
        
        # Get current package for comparison
        current_package = await get_current_package(current_user, db)
        
        # Check if it's actually an upgrade
        new_package = next(pkg for pkg in available_packages if pkg.get("id") == upgrade_request.new_package_id)
        
        if new_package.get("speed_down", 0) <= current_package.speed_down:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected package is not an upgrade"
            )
        
        # Process upgrade in Splynx
        upgrade_result = await splynx_service.upgrade_package(
            current_user.splynx_customer_id,
            upgrade_request.new_package_id
        )
        
        return {
            "message": "Package upgrade successful",
            "old_package": current_package.name,
            "new_package": new_package.get("name"),
            "upgrade_date": upgrade_request.upgrade_date or datetime.now(),
            "speed_increase": new_package.get("speed_down", 0) - current_package.speed_down
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Package upgrade failed: {str(e)}"
        )

@router.get("/comparison", response_model=PackageComparison)
async def compare_packages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare current package with available packages"""
    try:
        # Get current package
        current_package = None
        try:
            current_package = await get_current_package(current_user, db)
        except HTTPException:
            # User might not have a current package
            pass
        
        # Get available packages
        available_packages = await get_available_packages(current_user, db)
        
        # Find recommended upgrades (packages with higher speeds)
        recommended_upgrades = []
        if current_package:
            for package in available_packages:
                if package.speed_down > current_package.speed_down and package.is_active:
                    recommended_upgrades.append(package)
            
            # Sort by speed increase
            recommended_upgrades.sort(key=lambda x: x.speed_down - current_package.speed_down, reverse=True)
        
        return PackageComparison(
            current_package=current_package,
            available_packages=available_packages,
            recommended_upgrades=recommended_upgrades[:5]  # Top 5 recommendations
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare packages: {str(e)}"
        )

@router.get("/{package_id}", response_model=PackageInfo)
async def get_package_details(
    package_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific package"""
    try:
        # Get packages from Splynx
        splynx_packages = await splynx_service.get_available_packages()
        
        # Find the specific package
        package = next((pkg for pkg in splynx_packages if pkg.get("id") == package_id), None)
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found"
            )
        
        return PackageInfo(
            id=package.get("id"),
            name=package.get("name", ""),
            description=package.get("description", ""),
            speed_down=package.get("speed_down", 0),
            speed_up=package.get("speed_up", 0),
            price=float(package.get("price", 0)),
            is_active=package.get("is_active", True)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get package details: {str(e)}"
        )