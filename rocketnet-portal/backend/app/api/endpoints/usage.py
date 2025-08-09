"""
Usage tracking endpoints
Data usage statistics and monitoring
"""

from typing import Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
import structlog

from app.api.endpoints.auth import get_current_customer
from app.schemas.usage import UsageStats, UsageOverview, UsagePeriodRequest
from app.services.splynx_service import splynx_service
from app.core.exceptions import SplynxAPIError

router = APIRouter()
logger = structlog.get_logger()


@router.get("/overview", response_model=UsageOverview)
async def get_usage_overview(current_customer: dict = Depends(get_current_customer)):
    """
    Get usage overview for dashboard
    """
    try:
        # Get current month usage
        current_month_stats = await splynx_service.get_usage_statistics(
            current_customer["customer_id"], 
            period_days=30
        )
        
        # Get previous month usage
        previous_month_stats = await splynx_service.get_usage_statistics(
            current_customer["customer_id"], 
            period_days=60  # Last 60 days, we'll filter for the previous month
        )
        
        # Calculate peak usage day (simplified)
        peak_usage_day = None
        peak_usage_gb = 0.0
        
        for daily_data in current_month_stats.daily_usage:
            daily_total = daily_data.get("download", 0) + daily_data.get("upload", 0)
            daily_gb = daily_total / (1024 ** 3)
            if daily_gb > peak_usage_gb:
                peak_usage_gb = daily_gb
                peak_usage_day = datetime.fromisoformat(daily_data.get("date", "")).date()
        
        # Determine trend (simplified)
        trend = "stable"
        if current_month_stats.total_gb > previous_month_stats.total_gb * 1.1:
            trend = "increasing"
        elif current_month_stats.total_gb < previous_month_stats.total_gb * 0.9:
            trend = "decreasing"
        
        overview = UsageOverview(
            current_month=current_month_stats,
            previous_month=previous_month_stats,
            limits=None,  # Would calculate based on customer plan
            peak_usage_day=peak_usage_day,
            peak_usage_gb=peak_usage_gb,
            trend=trend
        )
        
        return overview
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting usage overview", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting usage overview", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage overview"
        )


@router.get("/statistics", response_model=UsageStats)
async def get_usage_statistics(
    current_customer: dict = Depends(get_current_customer),
    period_days: int = Query(default=30, ge=1, le=365),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None)
):
    """
    Get usage statistics for a specific period
    """
    try:
        # If dates are provided, calculate period_days
        if start_date and end_date:
            period_days = (end_date - start_date).days
            if period_days <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date must be after start date"
                )
        
        usage_stats = await splynx_service.get_usage_statistics(
            current_customer["customer_id"], 
            period_days=period_days
        )
        
        return usage_stats
        
    except HTTPException:
        raise
    except SplynxAPIError as e:
        logger.error("Splynx API error getting usage statistics", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting usage statistics", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage statistics"
        )


@router.get("/current-month", response_model=UsageStats)
async def get_current_month_usage(current_customer: dict = Depends(get_current_customer)):
    """
    Get usage statistics for the current month
    """
    try:
        # Calculate days from start of month
        today = date.today()
        start_of_month = today.replace(day=1)
        days_in_month = (today - start_of_month).days + 1
        
        usage_stats = await splynx_service.get_usage_statistics(
            current_customer["customer_id"], 
            period_days=days_in_month
        )
        
        return usage_stats
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting current month usage", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting current month usage", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve current month usage"
        )


@router.get("/daily")
async def get_daily_usage(
    current_customer: dict = Depends(get_current_customer),
    days: int = Query(default=7, ge=1, le=90)
):
    """
    Get daily usage breakdown
    """
    try:
        usage_stats = await splynx_service.get_usage_statistics(
            current_customer["customer_id"], 
            period_days=days
        )
        
        # Process daily usage data for chart display
        daily_usage = []
        for daily_data in usage_stats.daily_usage:
            daily_usage.append({
                "date": daily_data.get("date"),
                "download_gb": daily_data.get("download", 0) / (1024 ** 3),
                "upload_gb": daily_data.get("upload", 0) / (1024 ** 3),
                "total_gb": (daily_data.get("download", 0) + daily_data.get("upload", 0)) / (1024 ** 3)
            })
        
        return {
            "period_days": days,
            "total_download_gb": usage_stats.download_gb,
            "total_upload_gb": usage_stats.upload_gb,
            "total_usage_gb": usage_stats.total_gb,
            "average_daily_gb": usage_stats.average_daily_gb,
            "daily_breakdown": daily_usage
        }
        
    except SplynxAPIError as e:
        logger.error("Splynx API error getting daily usage", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
        
    except Exception as e:
        logger.error("Unexpected error getting daily usage", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily usage"
        )