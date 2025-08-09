import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from splynx_api.v2 import CustomerRequest, AdministratorRequest, ApiKeyRequest
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta

from ..core.config import settings

logger = logging.getLogger(__name__)

class SplynxService:
    def __init__(self):
        self.splynx_url = settings.splynx_url
        self.api_key = settings.splynx_api_key
        self.api_secret = settings.splynx_api_secret
        self.admin_client = None
        self.customer_client = None
        
    def _get_admin_client(self) -> AdministratorRequest:
        """Get admin client for Splynx API"""
        if not self.admin_client:
            self.admin_client = AdministratorRequest(
                self.splynx_url,
                settings.splynx_admin_username,
                settings.splynx_admin_password
            )
            if self.admin_client.login():
                raise Exception("Failed to login to Splynx admin API")
        return self.admin_client
    
    def _get_customer_client(self, username: str, password: str) -> CustomerRequest:
        """Get customer client for Splynx API"""
        customer_client = CustomerRequest(self.splynx_url, username, password)
        if customer_client.login():
            raise Exception("Failed to login to Splynx customer API")
        return customer_client
    
    def _get_api_key_client(self) -> ApiKeyRequest:
        """Get API key client for Splynx API"""
        if not self.api_key or not self.api_secret:
            raise Exception("API key and secret not configured")
        
        api_client = ApiKeyRequest(self.splynx_url, self.api_key, self.api_secret)
        if api_client.login():
            raise Exception("Failed to login to Splynx API with key")
        return api_client
    
    async def get_customer_info(self, customer_id: int) -> Dict[str, Any]:
        """Get customer information from Splynx"""
        try:
            admin_client = self._get_admin_client()
            admin_client.api_call_get("admin/customers/customer", customer_id)
            
            if not admin_client.result:
                raise Exception(f"Failed to get customer info: {admin_client.response}")
            
            return admin_client.response
        except Exception as e:
            logger.error(f"Error getting customer info: {e}")
            raise
    
    async def get_customer_billing(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get customer billing history from Splynx"""
        try:
            admin_client = self._get_admin_client()
            admin_client.api_call_get("admin/finance/invoices", params={
                "customer_id": customer_id,
                "limit": 50
            })
            
            if not admin_client.result:
                raise Exception(f"Failed to get billing info: {admin_client.response}")
            
            return admin_client.response.get("data", [])
        except Exception as e:
            logger.error(f"Error getting billing info: {e}")
            raise
    
    async def get_customer_usage(self, customer_id: int, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get customer usage data from Splynx"""
        try:
            admin_client = self._get_admin_client()
            
            # Get customer's internet service
            admin_client.api_call_get("admin/customers/customer", customer_id)
            if not admin_client.result:
                raise Exception(f"Failed to get customer info: {admin_client.response}")
            
            customer_data = admin_client.response
            services = customer_data.get("services", [])
            
            usage_data = {}
            for service in services:
                if service.get("type") == "internet":
                    service_id = service.get("id")
                    # Get usage for this service
                    admin_client.api_call_get(f"admin/customers/internet/{service_id}/usage", params={
                        "start_date": start_date,
                        "end_date": end_date
                    })
                    
                    if admin_client.result:
                        usage_data[service_id] = admin_client.response
            
            return usage_data
        except Exception as e:
            logger.error(f"Error getting usage info: {e}")
            raise
    
    async def get_available_packages(self) -> List[Dict[str, Any]]:
        """Get available internet packages from Splynx"""
        try:
            admin_client = self._get_admin_client()
            admin_client.api_call_get("admin/customers/internet", params={
                "limit": 100
            })
            
            if not admin_client.result:
                raise Exception(f"Failed to get packages: {admin_client.response}")
            
            return admin_client.response.get("data", [])
        except Exception as e:
            logger.error(f"Error getting packages: {e}")
            raise
    
    async def upgrade_package(self, customer_id: int, new_package_id: int) -> Dict[str, Any]:
        """Upgrade customer package"""
        try:
            admin_client = self._get_admin_client()
            
            # Get current customer info
            admin_client.api_call_get("admin/customers/customer", customer_id)
            if not admin_client.result:
                raise Exception(f"Failed to get customer info: {admin_client.response}")
            
            customer_data = admin_client.response
            
            # Find current internet service
            current_service = None
            for service in customer_data.get("services", []):
                if service.get("type") == "internet":
                    current_service = service
                    break
            
            if not current_service:
                raise Exception("No internet service found for customer")
            
            # Update the service with new package
            update_data = {
                "internet_service_id": new_package_id
            }
            
            admin_client.api_call_put(
                f"admin/customers/internet/{current_service['id']}",
                current_service['id'],
                update_data
            )
            
            if not admin_client.result:
                raise Exception(f"Failed to upgrade package: {admin_client.response}")
            
            return admin_client.response
        except Exception as e:
            logger.error(f"Error upgrading package: {e}")
            raise
    
    async def create_retention_request(self, customer_id: int, request_type: str, reason: str) -> Dict[str, Any]:
        """Create a retention request for customer"""
        try:
            admin_client = self._get_admin_client()
            
            # Create retention request in Splynx
            retention_data = {
                "customer_id": customer_id,
                "type": request_type,
                "reason": reason,
                "status": "pending"
            }
            
            admin_client.api_call_post("admin/customers/retention", retention_data)
            
            if not admin_client.result:
                raise Exception(f"Failed to create retention request: {admin_client.response}")
            
            return admin_client.response
        except Exception as e:
            logger.error(f"Error creating retention request: {e}")
            raise
    
    async def process_retention_payment(self, retention_id: int, amount: float) -> Dict[str, Any]:
        """Process payment for retention request"""
        try:
            admin_client = self._get_admin_client()
            
            # Update retention request with payment
            payment_data = {
                "amount_paid": amount,
                "status": "paid"
            }
            
            admin_client.api_call_put("admin/customers/retention", retention_id, payment_data)
            
            if not admin_client.result:
                raise Exception(f"Failed to process retention payment: {admin_client.response}")
            
            return admin_client.response
        except Exception as e:
            logger.error(f"Error processing retention payment: {e}")
            raise
    
    async def get_speed_test_results(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get speed test results for customer"""
        try:
            admin_client = self._get_admin_client()
            admin_client.api_call_get("admin/customers/speed_tests", params={
                "customer_id": customer_id,
                "limit": 20
            })
            
            if not admin_client.result:
                raise Exception(f"Failed to get speed test results: {admin_client.response}")
            
            return admin_client.response.get("data", [])
        except Exception as e:
            logger.error(f"Error getting speed test results: {e}")
            raise
    
    async def create_speed_test(self, customer_id: int, speed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new speed test result"""
        try:
            admin_client = self._get_admin_client()
            
            speed_test_data = {
                "customer_id": customer_id,
                "download_speed": speed_data.get("download_speed"),
                "upload_speed": speed_data.get("upload_speed"),
                "ping": speed_data.get("ping"),
                "jitter": speed_data.get("jitter"),
                "test_date": datetime.now().isoformat(),
                "server_location": speed_data.get("server_location", "Auto"),
                "test_type": speed_data.get("test_type", "manual")
            }
            
            admin_client.api_call_post("admin/customers/speed_tests", speed_test_data)
            
            if not admin_client.result:
                raise Exception(f"Failed to create speed test: {admin_client.response}")
            
            return admin_client.response
        except Exception as e:
            logger.error(f"Error creating speed test: {e}")
            raise

# Global instance
splynx_service = SplynxService()