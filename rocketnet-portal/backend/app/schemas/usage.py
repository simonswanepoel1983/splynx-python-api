"""
Usage tracking schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


class UsageDataPoint(BaseModel):
    """Single usage data point"""
    date: date
    download_bytes: int = 0
    upload_bytes: int = 0
    total_bytes: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.total_bytes:
            self.total_bytes = self.download_bytes + self.upload_bytes


class UsageStats(BaseModel):
    """Usage statistics for a period"""
    customer_id: int
    period_start: datetime
    period_end: datetime
    download_bytes: int
    upload_bytes: int
    total_bytes: int
    daily_usage: List[Dict[str, Any]] = []
    
    @property
    def download_gb(self) -> float:
        """Download in GB"""
        return self.download_bytes / (1024 ** 3)
    
    @property
    def upload_gb(self) -> float:
        """Upload in GB"""
        return self.upload_bytes / (1024 ** 3)
    
    @property
    def total_gb(self) -> float:
        """Total usage in GB"""
        return self.total_bytes / (1024 ** 3)
    
    @property
    def average_daily_gb(self) -> float:
        """Average daily usage in GB"""
        days = (self.period_end - self.period_start).days
        return self.total_gb / days if days > 0 else 0
    
    class Config:
        from_attributes = True


class UsageLimits(BaseModel):
    """Usage limits and warnings"""
    monthly_limit_gb: Optional[float] = None
    current_usage_gb: float
    usage_percentage: float
    warning_threshold: float = 80.0  # Warning at 80%
    is_over_limit: bool = False
    is_near_limit: bool = False
    days_remaining: int
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.monthly_limit_gb:
            self.usage_percentage = (self.current_usage_gb / self.monthly_limit_gb) * 100
            self.is_over_limit = self.usage_percentage > 100
            self.is_near_limit = self.usage_percentage >= self.warning_threshold


class UsageOverview(BaseModel):
    """Usage overview for dashboard"""
    current_month: UsageStats
    previous_month: Optional[UsageStats] = None
    limits: Optional[UsageLimits] = None
    peak_usage_day: Optional[date] = None
    peak_usage_gb: Optional[float] = None
    trend: str = "stable"  # increasing, decreasing, stable
    
    class Config:
        from_attributes = True


class UsagePeriodRequest(BaseModel):
    """Request for usage data for a specific period"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    granularity: str = Field(default="daily", regex="^(hourly|daily|weekly|monthly)$")