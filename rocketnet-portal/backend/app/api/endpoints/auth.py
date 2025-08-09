"""
Authentication endpoints
Customer login/logout and JWT token management
"""

from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import structlog

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.schemas.customer import CustomerLogin, CustomerProfile
from app.services.splynx_service import splynx_service

router = APIRouter()
security = HTTPBearer()
logger = structlog.get_logger()


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_customer(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated customer from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        customer_id: int = payload.get("sub")
        if customer_id is None:
            raise credentials_exception
        
        # For now, we'll just return the customer_id. In a full implementation,
        # you might want to fetch the customer from the database or cache
        return {"customer_id": customer_id, "login": payload.get("login")}
    except JWTError:
        raise credentials_exception


@router.post("/login")
async def login(login_data: CustomerLogin):
    """
    Customer login endpoint
    Authenticates with Splynx and returns JWT tokens
    """
    try:
        # Authenticate customer with Splynx
        customer = await splynx_service.authenticate_customer(
            login_data.login, 
            login_data.password
        )
        
        if not customer:
            logger.warning("Login failed - invalid credentials", login=login_data.login)
            raise AuthenticationError("Invalid login credentials")
        
        # Create JWT tokens
        access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(customer["id"]), "login": customer["login"]},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": str(customer["id"]), "login": customer["login"]}
        )
        
        logger.info("Customer logged in successfully", 
                   customer_id=customer["id"], 
                   login=customer["login"])
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
            "customer": {
                "id": customer["id"],
                "login": customer["login"],
                "name": customer["name"],
                "email": customer["email"]
            }
        }
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e), login=login_data.login)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )


@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh JWT access token using refresh token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        customer_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if customer_id is None or token_type != "refresh":
            raise credentials_exception
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": customer_id, "login": payload.get("login")},
            expires_delta=access_token_expires
        )
        
        logger.info("Token refreshed", customer_id=customer_id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_MINUTES * 60
        }
        
    except JWTError:
        raise credentials_exception


@router.post("/logout")
async def logout(current_customer: dict = Depends(get_current_customer)):
    """
    Customer logout endpoint
    In a full implementation, you might want to blacklist the token
    """
    logger.info("Customer logged out", customer_id=current_customer["customer_id"])
    
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_customer_info(current_customer: dict = Depends(get_current_customer)):
    """
    Get current customer information
    """
    try:
        customer_profile = await splynx_service.get_customer_profile(
            current_customer["customer_id"]
        )
        return customer_profile
        
    except Exception as e:
        logger.error("Failed to get customer info", 
                    customer_id=current_customer["customer_id"], 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer information"
        )