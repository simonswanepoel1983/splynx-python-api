from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..core.database import get_db, User
from ..core.security import get_current_user
from ..services.splynx_service import splynx_service
from pydantic import BaseModel

router = APIRouter()

class UsageData(BaseModel):
    date: datetime
    download_bytes: int
    upload_bytes: int
    total_bytes: int
    service_id: int

class UsageSummary(BaseModel):
    current_period_start: datetime
    current_period_end: datetime
    total_download_gb: float
    total_upload_gb: float
    total_usage_gb: float
    usage_limit_gb: Optional[float]
    usage_percentage: Optional[float]

class UsageHistory(BaseModel):
    date: datetime
    download_gb: float
    upload_gb: float
    total_gb: float

@router.get("/current", response_model=UsageSummary)
async def get_current_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current usage for the billing period"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Get usage data from Splynx
        usage_data = await splynx_service.get_customer_usage(current_user.splynx_customer_id)
        
        # Calculate current period (assuming monthly billing)
        now = datetime.now()
        current_period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_period_end = (current_period_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        # Calculate totals
        total_download = 0
        total_upload = 0
        
        for service_id, service_usage in usage_data.items():
            if isinstance(service_usage, dict) and "data" in service_usage:
                for usage_record in service_usage["data"]:
                    if isinstance(usage_record, dict):
                        total_download += usage_record.get("download_bytes", 0)
                        total_upload += usage_record.get("upload_bytes", 0)
        
        total_usage_gb = (total_download + total_upload) / (1024**3)
        total_download_gb = total_download / (1024**3)
        total_upload_gb = total_upload / (1024**3)
        
        # Get usage limit from customer package
        usage_limit_gb = None
        usage_percentage = None
        
        # This would be retrieved from the customer's package
        # For now, we'll set a default limit
        usage_limit_gb = 1000  # 1TB default
        
        if usage_limit_gb:
            usage_percentage = (total_usage_gb / usage_limit_gb) * 100
        
        return UsageSummary(
            current_period_start=current_period_start,
            current_period_end=current_period_end,
            total_download_gb=round(total_download_gb, 2),
            total_upload_gb=round(total_upload_gb, 2),
            total_usage_gb=round(total_usage_gb, 2),
            usage_limit_gb=usage_limit_gb,
            usage_percentage=round(usage_percentage, 2) if usage_percentage else None
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current usage: {str(e)}"
        )

@router.get("/history", response_model=List[UsageHistory])
async def get_usage_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get usage history for the specified number of days"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get usage data from Splynx
        usage_data = await splynx_service.get_customer_usage(
            current_user.splynx_customer_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Process usage data into daily history
        usage_history = []
        daily_usage = {}
        
        for service_id, service_usage in usage_data.items():
            if isinstance(service_usage, dict) and "data" in service_usage:
                for usage_record in service_usage["data"]:
                    if isinstance(usage_record, dict):
                        date_str = usage_record.get("date", "")
                        if date_str:
                            try:
                                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                date_key = date.date()
                                
                                if date_key not in daily_usage:
                                    daily_usage[date_key] = {
                                        "download": 0,
                                        "upload": 0
                                    }
                                
                                daily_usage[date_key]["download"] += usage_record.get("download_bytes", 0)
                                daily_usage[date_key]["upload"] += usage_record.get("upload_bytes", 0)
                            except ValueError:
                                continue
        
        # Convert to response format
        for date_key, usage in sorted(daily_usage.items()):
            usage_history.append(UsageHistory(
                date=datetime.combine(date_key, datetime.min.time()),
                download_gb=round(usage["download"] / (1024**3), 2),
                upload_gb=round(usage["upload"] / (1024**3), 2),
                total_gb=round((usage["download"] + usage["upload"]) / (1024**3), 2)
            ))
        
        return usage_history
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage history: {str(e)}"
        )

@router.get("/real-time")
async def get_real_time_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time usage data"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # This would typically connect to real-time monitoring systems
        # For now, we'll return simulated data
        return {
            "current_download_speed": 25.5,  # Mbps
            "current_upload_speed": 12.3,    # Mbps
            "current_bandwidth_usage": 45.2,  # %
            "active_connections": 8,
            "last_updated": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get real-time usage: {str(e)}"
        )

@router.get("/limits")
async def get_usage_limits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage limits for the customer's package"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Get customer info from Splynx
        customer_info = await splynx_service.get_customer_info(current_user.splynx_customer_id)
        
        # Extract package information
        package_info = {}
        services = customer_info.get("services", [])
        
        for service in services:
            if service.get("type") == "internet":
                package_info = {
                    "package_name": service.get("name", "Unknown"),
                    "speed_down_mbps": service.get("speed_down", 0),
                    "speed_up_mbps": service.get("speed_up", 0),
                    "data_limit_gb": service.get("data_limit", None),
                    "unlimited_data": service.get("unlimited_data", False)
                }
                break
        
        return package_info
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage limits: {str(e)}"
        )