"""
Service package schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ServicePackage(BaseModel):
    """Service package/tariff plan"""
    id: int
    name: str
    description: Optional[str] = None
    price: float
    speed_download: int  # Mbps
    speed_upload: int   # Mbps
    data_limit: Optional[int] = None  # GB, None for unlimited
    features: List[str] = []
    is_current: bool = False
    is_upgrade: bool = False
    is_available: bool = True
    
    @property
    def speed_display(self) -> str:
        """Human-readable speed display"""
        if self.speed_download == self.speed_upload:
            return f"{self.speed_download} Mbps"
        return f"{self.speed_download}/{self.speed_upload} Mbps"
    
    @property
    def data_limit_display(self) -> str:
        """Human-readable data limit display"""
        if self.data_limit is None:
            return "Unlimited"
        if self.data_limit >= 1000:
            return f"{self.data_limit // 1000} TB"
        return f"{self.data_limit} GB"
    
    class Config:
        from_attributes = True


class PackageComparison(BaseModel):
    """Package comparison for upgrades"""
    current_package: ServicePackage
    recommended_packages: List[ServicePackage] = []
    all_packages: List[ServicePackage] = []


class PackageUpgradeRequest(BaseModel):
    """Package upgrade request"""
    package_id: int
    effective_date: Optional[str] = None  # "immediate" or YYYY-MM-DD
    notes: Optional[str] = None


class PackageUpgradeResponse(BaseModel):
    """Package upgrade response"""
    success: bool
    message: str
    ticket_id: Optional[int] = None
    estimated_completion: Optional[str] = None


class ServiceChange(BaseModel):
    """Service change record"""
    id: int
    customer_id: int
    old_package_id: Optional[int] = None
    new_package_id: int
    change_type: str  # upgrade, downgrade, change
    requested_date: str
    effective_date: Optional[str] = None
    status: str  # pending, approved, completed, cancelled
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True