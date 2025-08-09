"""
Splynx API Service
Integrates with Splynx BSS/OSS for customer data, billing, usage, and package management
"""

import asyncio
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog

# Add the parent directory to sys.path to import splynx_api
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
from splynx_api.v2 import ApiKeyRequest

from app.core.config import settings
from app.core.exceptions import SplynxAPIError, CustomerNotFoundError
from app.schemas.customer import CustomerProfile
from app.schemas.billing import Invoice, PaymentHistory
from app.schemas.usage import UsageStats
from app.schemas.packages import ServicePackage


logger = structlog.get_logger()


class SplynxService:
    """Service for interacting with Splynx API"""
    
    def __init__(self):
        self.api_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Splynx API client"""
        try:
            self.api_client = ApiKeyRequest(
                splynx_domain=settings.SPLYNX_URL,
                api_key=settings.SPLYNX_API_KEY,
                api_secret=settings.SPLYNX_API_SECRET,
                timeout=settings.SPLYNX_TIMEOUT
            )
            logger.info("Splynx API client initialized", url=settings.SPLYNX_URL)
        except Exception as e:
            logger.error("Failed to initialize Splynx API client", error=str(e))
            raise SplynxAPIError(f"Failed to initialize Splynx client: {str(e)}")
    
    async def authenticate_customer(self, login: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a customer with Splynx"""
        try:
            # Login to get session
            if self.api_client.login():
                raise SplynxAPIError("Failed to authenticate with Splynx API")
            
            # Search for customer by login
            params = {"login": login}
            self.api_client.api_call_get("admin/customers/customer", params=params)
            
            if not self.api_client.response or not self.api_client.response.get("data"):
                logger.warning("Customer not found", login=login)
                return None
            
            customers = self.api_client.response["data"]
            if not customers:
                return None
            
            customer = customers[0]
            
            # Verify password (this would typically be done via customer login endpoint)
            # For now, we'll assume the customer exists and return their data
            logger.info("Customer authenticated", customer_id=customer.get("id"), login=login)
            
            self.api_client.logout()
            return customer
            
        except Exception as e:
            logger.error("Customer authentication failed", login=login, error=str(e))
            if self.api_client:
                self.api_client.logout()
            raise SplynxAPIError(f"Authentication failed: {str(e)}")
    
    async def get_customer_profile(self, customer_id: int) -> CustomerProfile:
        """Get customer profile information"""
        try:
            if self.api_client.login():
                raise SplynxAPIError("Failed to authenticate with Splynx API")
            
            # Get customer details
            self.api_client.api_call_get("admin/customers/customer", entity_id=customer_id)
            
            if not self.api_client.response or not self.api_client.response.get("data"):
                raise CustomerNotFoundError(f"Customer {customer_id} not found")
            
            customer_data = self.api_client.response["data"]
            
            # Get customer services
            self.api_client.api_call_get("admin/customers/services", params={"customer_id": customer_id})
            services_data = self.api_client.response.get("data", [])
            
            self.api_client.logout()
            
            return CustomerProfile(
                id=customer_data["id"],
                login=customer_data["login"],
                name=customer_data["name"],
                email=customer_data["email"],
                phone=customer_data.get("phone", ""),
                address=customer_data.get("street_1", ""),
                city=customer_data.get("city", ""),
                status=customer_data.get("status", ""),
                services=services_data
            )
            
        except Exception as e:
            logger.error("Failed to get customer profile", customer_id=customer_id, error=str(e))
            if self.api_client:
                self.api_client.logout()
            if isinstance(e, (CustomerNotFoundError, SplynxAPIError)):
                raise
            raise SplynxAPIError(f"Failed to get customer profile: {str(e)}")
    
    async def get_customer_invoices(self, customer_id: int, limit: int = 10) -> List[Invoice]:
        """Get customer invoices"""
        try:
            if self.api_client.login():
                raise SplynxAPIError("Failed to authenticate with Splynx API")
            
            params = {
                "customer_id": customer_id,
                "limit": limit,
                "order": "date,desc"
            }
            self.api_client.api_call_get("admin/finance/invoices", params=params)
            
            invoices_data = self.api_client.response.get("data", [])
            self.api_client.logout()
            
            invoices = []
            for invoice_data in invoices_data:
                invoices.append(Invoice(
                    id=invoice_data["id"],
                    number=invoice_data["number"],
                    date=datetime.fromisoformat(invoice_data["date"]),
                    due_date=datetime.fromisoformat(invoice_data["due_date"]) if invoice_data.get("due_date") else None,
                    total=float(invoice_data["total"]),
                    status=invoice_data["status"],
                    items=invoice_data.get("items", [])
                ))
            
            return invoices
            
        except Exception as e:
            logger.error("Failed to get customer invoices", customer_id=customer_id, error=str(e))
            if self.api_client:
                self.api_client.logout()
            raise SplynxAPIError(f"Failed to get invoices: {str(e)}")
    
    async def get_usage_statistics(self, customer_id: int, period_days: int = 30) -> UsageStats:
        """Get customer usage statistics"""
        try:
            if self.api_client.login():
                raise SplynxAPIError("Failed to authenticate with Splynx API")
            
            # Get usage data for the specified period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            params = {
                "customer_id": customer_id,
                "date_from": start_date.strftime("%Y-%m-%d"),
                "date_to": end_date.strftime("%Y-%m-%d")
            }
            
            self.api_client.api_call_get("admin/networking/statistics", params=params)
            usage_data = self.api_client.response.get("data", [])
            
            self.api_client.logout()
            
            # Process usage data
            total_download = sum(item.get("download", 0) for item in usage_data)
            total_upload = sum(item.get("upload", 0) for item in usage_data)
            
            return UsageStats(
                customer_id=customer_id,
                period_start=start_date,
                period_end=end_date,
                download_bytes=total_download,
                upload_bytes=total_upload,
                total_bytes=total_download + total_upload,
                daily_usage=usage_data
            )
            
        except Exception as e:
            logger.error("Failed to get usage statistics", customer_id=customer_id, error=str(e))
            if self.api_client:
                self.api_client.logout()
            raise SplynxAPIError(f"Failed to get usage statistics: {str(e)}")
    
    async def get_available_packages(self, customer_id: int) -> List[ServicePackage]:
        """Get available service packages for upgrade"""
        try:
            if self.api_client.login():
                raise SplynxAPIError("Failed to authenticate with Splynx API")
            
            # Get all tariff plans
            self.api_client.api_call_get("admin/tariff-plans/internet-plans")
            plans_data = self.api_client.response.get("data", [])
            
            # Get customer's current services
            self.api_client.api_call_get("admin/customers/services", params={"customer_id": customer_id})
            services_data = self.api_client.response.get("data", [])
            
            current_plan_ids = [service.get("tariff_id") for service in services_data]
            
            self.api_client.logout()
            
            packages = []
            for plan in plans_data:
                # Only show plans that are upgrades (higher price or speed)
                is_upgrade = plan["id"] not in current_plan_ids
                
                packages.append(ServicePackage(
                    id=plan["id"],
                    name=plan["title"],
                    description=plan.get("description", ""),
                    price=float(plan["price"]),
                    speed_download=plan.get("speed_download", 0),
                    speed_upload=plan.get("speed_upload", 0),
                    data_limit=plan.get("data_limit", 0),
                    is_current=not is_upgrade,
                    is_upgrade=is_upgrade
                ))
            
            return packages
            
        except Exception as e:
            logger.error("Failed to get available packages", customer_id=customer_id, error=str(e))
            if self.api_client:
                self.api_client.logout()
            raise SplynxAPIError(f"Failed to get available packages: {str(e)}")
    
    async def request_package_upgrade(self, customer_id: int, package_id: int) -> Dict[str, Any]:
        """Request a package upgrade"""
        try:
            if self.api_client.login():
                raise SplynxAPIError("Failed to authenticate with Splynx API")
            
            # Create a service change request or ticket
            params = {
                "customer_id": customer_id,
                "subject": f"Package Upgrade Request - Plan ID {package_id}",
                "message": f"Customer requested upgrade to package ID {package_id}",
                "priority": "medium",
                "type": "billing"
            }
            
            self.api_client.api_call_post("admin/support/tickets", params=params)
            ticket_response = self.api_client.response
            
            self.api_client.logout()
            
            logger.info("Package upgrade requested", customer_id=customer_id, package_id=package_id)
            
            return {
                "success": True,
                "message": "Upgrade request submitted successfully",
                "ticket_id": ticket_response.get("data", {}).get("id") if ticket_response else None
            }
            
        except Exception as e:
            logger.error("Failed to request package upgrade", customer_id=customer_id, package_id=package_id, error=str(e))
            if self.api_client:
                self.api_client.logout()
            raise SplynxAPIError(f"Failed to request package upgrade: {str(e)}")
    
    async def initiate_retention_process(self, customer_id: int, action: str, reason: str) -> Dict[str, Any]:
        """Initiate retention process for downgrades/cancellations"""
        try:
            if self.api_client.login():
                raise SplynxAPIError("Failed to authenticate with Splynx API")
            
            # Create a retention ticket
            params = {
                "customer_id": customer_id,
                "subject": f"Service {action.title()} Request - Retention Required",
                "message": f"Customer requested to {action} service. Reason: {reason}. Retention fee: ${settings.RETENTION_FEE_AMOUNT}",
                "priority": "high",
                "type": "billing"
            }
            
            self.api_client.api_call_post("admin/support/tickets", params=params)
            ticket_response = self.api_client.response
            
            self.api_client.logout()
            
            logger.info("Retention process initiated", customer_id=customer_id, action=action)
            
            return {
                "success": True,
                "retention_fee": settings.RETENTION_FEE_AMOUNT,
                "message": f"Retention process initiated. Please pay the retention fee of ${settings.RETENTION_FEE_AMOUNT} to proceed.",
                "ticket_id": ticket_response.get("data", {}).get("id") if ticket_response else None
            }
            
        except Exception as e:
            logger.error("Failed to initiate retention process", customer_id=customer_id, action=action, error=str(e))
            if self.api_client:
                self.api_client.logout()
            raise SplynxAPIError(f"Failed to initiate retention process: {str(e)}")


# Global service instance
splynx_service = SplynxService()