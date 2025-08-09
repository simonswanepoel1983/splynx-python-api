"""
Speed test endpoints
Internet speed testing functionality
"""

import asyncio
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
import structlog

from app.api.endpoints.auth import get_current_customer
from app.core.config import settings
from app.core.exceptions import SpeedTestError, SpeedTestLimitExceeded

router = APIRouter()
logger = structlog.get_logger()

# In-memory storage for speed test results (use Redis in production)
speed_test_results = {}
speed_test_counts = {}


@router.post("/run")
async def run_speed_test(current_customer: dict = Depends(get_current_customer)):
    """
    Run a speed test
    """
    customer_id = current_customer["customer_id"]
    
    try:
        # Check if speed testing is enabled
        if not settings.ENABLE_SPEED_TEST:
            raise SpeedTestError("Speed testing is currently disabled")
        
        # Check daily limit
        today = datetime.now().date()
        customer_tests_today = speed_test_counts.get(f"{customer_id}_{today}", 0)
        
        if customer_tests_today >= settings.MAX_SPEED_TESTS_PER_DAY:
            raise SpeedTestLimitExceeded(
                f"Daily speed test limit of {settings.MAX_SPEED_TESTS_PER_DAY} exceeded"
            )
        
        # Simulate speed test execution
        logger.info("Starting speed test", customer_id=customer_id)
        
        # In a real implementation, you would:
        # 1. Trigger actual speed test using Ookla, Fast.com, or custom implementation
        # 2. Monitor the test progress
        # 3. Return real results
        
        # Simulate test execution time
        await asyncio.sleep(2)
        
        # Generate realistic speed test results (replace with actual implementation)
        download_speed = random.uniform(50, 200)  # Mbps
        upload_speed = random.uniform(10, 50)     # Mbps
        ping = random.uniform(10, 50)             # ms
        jitter = random.uniform(1, 10)            # ms
        
        test_result = {
            "id": f"test_{customer_id}_{int(datetime.now().timestamp())}",
            "customer_id": customer_id,
            "timestamp": datetime.now().isoformat(),
            "download_mbps": round(download_speed, 2),
            "upload_mbps": round(upload_speed, 2),
            "ping_ms": round(ping, 2),
            "jitter_ms": round(jitter, 2),
            "server_location": "Local Server",
            "test_provider": settings.SPEED_TEST_PROVIDER,
            "status": "completed"
        }
        
        # Store result
        if customer_id not in speed_test_results:
            speed_test_results[customer_id] = []
        speed_test_results[customer_id].append(test_result)
        
        # Update daily count
        speed_test_counts[f"{customer_id}_{today}"] = customer_tests_today + 1
        
        logger.info("Speed test completed", 
                   customer_id=customer_id,
                   download=download_speed,
                   upload=upload_speed,
                   ping=ping)
        
        return test_result
        
    except (SpeedTestError, SpeedTestLimitExceeded):
        raise
    except Exception as e:
        logger.error("Speed test failed", customer_id=customer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Speed test failed due to server error"
        )


@router.get("/history")
async def get_speed_test_history(
    current_customer: dict = Depends(get_current_customer),
    limit: int = 10
):
    """
    Get speed test history for the customer
    """
    customer_id = current_customer["customer_id"]
    
    try:
        customer_results = speed_test_results.get(customer_id, [])
        
        # Sort by timestamp (most recent first) and apply limit
        sorted_results = sorted(
            customer_results, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )[:limit]
        
        return {
            "results": sorted_results,
            "total_tests": len(customer_results),
            "daily_limit": settings.MAX_SPEED_TESTS_PER_DAY,
            "tests_today": speed_test_counts.get(f"{customer_id}_{datetime.now().date()}", 0)
        }
        
    except Exception as e:
        logger.error("Failed to get speed test history", 
                    customer_id=customer_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve speed test history"
        )


@router.get("/status")
async def get_speed_test_status(current_customer: dict = Depends(get_current_customer)):
    """
    Get speed test service status and limits
    """
    customer_id = current_customer["customer_id"]
    today = datetime.now().date()
    
    try:
        tests_today = speed_test_counts.get(f"{customer_id}_{today}", 0)
        
        return {
            "enabled": settings.ENABLE_SPEED_TEST,
            "provider": settings.SPEED_TEST_PROVIDER,
            "daily_limit": settings.MAX_SPEED_TESTS_PER_DAY,
            "tests_used_today": tests_today,
            "tests_remaining": max(0, settings.MAX_SPEED_TESTS_PER_DAY - tests_today),
            "can_run_test": settings.ENABLE_SPEED_TEST and tests_today < settings.MAX_SPEED_TESTS_PER_DAY
        }
        
    except Exception as e:
        logger.error("Failed to get speed test status", 
                    customer_id=customer_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve speed test status"
        )


@router.get("/latest")
async def get_latest_speed_test(current_customer: dict = Depends(get_current_customer)):
    """
    Get the most recent speed test result
    """
    customer_id = current_customer["customer_id"]
    
    try:
        customer_results = speed_test_results.get(customer_id, [])
        
        if not customer_results:
            return None
        
        # Return the most recent result
        latest_result = max(customer_results, key=lambda x: x["timestamp"])
        return latest_result
        
    except Exception as e:
        logger.error("Failed to get latest speed test", 
                    customer_id=customer_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve latest speed test"
        )