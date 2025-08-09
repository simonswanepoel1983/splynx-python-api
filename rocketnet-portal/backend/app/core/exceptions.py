"""
Custom exceptions for RocketNet Portal
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception class for application errors"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.headers = headers
        super().__init__(self.detail)


class AuthenticationError(AppException):
    """Authentication failed"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=401, error_code="AUTH_FAILED")


class AuthorizationError(AppException):
    """Authorization failed"""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail, status_code=403, error_code="AUTH_INSUFFICIENT")


class ValidationError(AppException):
    """Data validation error"""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        error_code = f"VALIDATION_ERROR_{field.upper()}" if field else "VALIDATION_ERROR"
        super().__init__(detail=detail, status_code=422, error_code=error_code)


class NotFoundError(AppException):
    """Resource not found"""
    
    def __init__(self, detail: str = "Resource not found", resource_type: Optional[str] = None):
        error_code = f"{resource_type.upper()}_NOT_FOUND" if resource_type else "NOT_FOUND"
        super().__init__(detail=detail, status_code=404, error_code=error_code)


class ConflictError(AppException):
    """Resource conflict"""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail=detail, status_code=409, error_code="CONFLICT")


class RateLimitError(AppException):
    """Rate limit exceeded"""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(detail=detail, status_code=429, error_code="RATE_LIMIT_EXCEEDED")


# Splynx-specific exceptions
class SplynxAPIError(AppException):
    """Splynx API error"""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=502, error_code="SPLYNX_API_ERROR")


class CustomerNotFoundError(NotFoundError):
    """Customer not found in Splynx"""
    
    def __init__(self, detail: str = "Customer not found"):
        super().__init__(detail=detail, resource_type="customer")


class InvoiceNotFoundError(NotFoundError):
    """Invoice not found"""
    
    def __init__(self, detail: str = "Invoice not found"):
        super().__init__(detail=detail, resource_type="invoice")


class ServiceNotFoundError(NotFoundError):
    """Service not found"""
    
    def __init__(self, detail: str = "Service not found"):
        super().__init__(detail=detail, resource_type="service")


# Speed test specific exceptions
class SpeedTestError(AppException):
    """Speed test error"""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=400, error_code="SPEED_TEST_ERROR")


class SpeedTestLimitExceeded(RateLimitError):
    """Speed test limit exceeded"""
    
    def __init__(self, detail: str = "Daily speed test limit exceeded"):
        super().__init__(detail=detail)


# Retention process exceptions
class RetentionProcessError(AppException):
    """Retention process error"""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=400, error_code="RETENTION_ERROR")


class RetentionPaymentRequired(AppException):
    """Retention payment required"""
    
    def __init__(self, amount: float):
        detail = f"Retention payment of ${amount:.2f} required to proceed"
        super().__init__(detail=detail, status_code=402, error_code="RETENTION_PAYMENT_REQUIRED")