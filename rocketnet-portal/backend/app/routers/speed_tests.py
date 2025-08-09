from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json

from ..core.database import get_db, User, SpeedTest
from ..core.security import get_current_user
from ..services.splynx_service import splynx_service
from pydantic import BaseModel

router = APIRouter()

class SpeedTestRequest(BaseModel):
    server_location: Optional[str] = "Auto"
    test_type: str = "manual"

class SpeedTestResult(BaseModel):
    id: int
    download_speed: float
    upload_speed: float
    ping: float
    jitter: float
    test_date: datetime
    server_location: str
    test_type: str

class SpeedTestSummary(BaseModel):
    average_download: float
    average_upload: float
    average_ping: float
    average_jitter: float
    total_tests: int
    last_test_date: Optional[datetime]

@router.post("/run", response_model=SpeedTestResult)
async def run_speed_test(
    test_request: SpeedTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run a new speed test"""
    try:
        if not current_user.splynx_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID not found"
            )
        
        # Run speed test using external service (e.g., Speedtest.net API)
        speed_results = await _run_speed_test_external(test_request.server_location)
        
        # Save results to database
        speed_test = SpeedTest(
            user_id=current_user.id,
            download_speed=speed_results["download_speed"],
            upload_speed=speed_results["upload_speed"],
            ping=speed_results["ping"],
            jitter=speed_results["jitter"],
            test_date=datetime.now(),
            server_location=test_request.server_location,
            test_type=test_request.test_type
        )
        
        db.add(speed_test)
        db.commit()
        db.refresh(speed_test)
        
        # Also save to Splynx if configured
        try:
            await splynx_service.create_speed_test(
                current_user.splynx_customer_id,
                {
                    "download_speed": speed_results["download_speed"],
                    "upload_speed": speed_results["upload_speed"],
                    "ping": speed_results["ping"],
                    "jitter": speed_results["jitter"],
                    "server_location": test_request.server_location,
                    "test_type": test_request.test_type
                }
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to save speed test to Splynx: {e}")
        
        return SpeedTestResult(
            id=speed_test.id,
            download_speed=speed_test.download_speed,
            upload_speed=speed_test.upload_speed,
            ping=speed_test.ping,
            jitter=speed_test.jitter,
            test_date=speed_test.test_date,
            server_location=speed_test.server_location,
            test_type=speed_test.test_type
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speed test failed: {str(e)}"
        )

@router.get("/history", response_model=List[SpeedTestResult])
async def get_speed_test_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get speed test history for the user"""
    try:
        # Get from local database
        speed_tests = db.query(SpeedTest).filter(
            SpeedTest.user_id == current_user.id
        ).order_by(SpeedTest.test_date.desc()).offset(offset).limit(limit).all()
        
        # Also try to get from Splynx
        splynx_tests = []
        if current_user.splynx_customer_id:
            try:
                splynx_tests = await splynx_service.get_speed_test_results(current_user.splynx_customer_id)
            except Exception as e:
                print(f"Failed to get speed tests from Splynx: {e}")
        
        # Combine and format results
        results = []
        for test in speed_tests:
            results.append(SpeedTestResult(
                id=test.id,
                download_speed=test.download_speed,
                upload_speed=test.upload_speed,
                ping=test.ping,
                jitter=test.jitter,
                test_date=test.test_date,
                server_location=test.server_location,
                test_type=test.test_type
            ))
        
        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get speed test history: {str(e)}"
        )

@router.get("/summary", response_model=SpeedTestSummary)
async def get_speed_test_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get speed test summary for the specified number of days"""
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get speed tests from database
        speed_tests = db.query(SpeedTest).filter(
            SpeedTest.user_id == current_user.id,
            SpeedTest.test_date >= start_date,
            SpeedTest.test_date <= end_date
        ).all()
        
        if not speed_tests:
            return SpeedTestSummary(
                average_download=0,
                average_upload=0,
                average_ping=0,
                average_jitter=0,
                total_tests=0,
                last_test_date=None
            )
        
        # Calculate averages
        total_download = sum(test.download_speed for test in speed_tests)
        total_upload = sum(test.upload_speed for test in speed_tests)
        total_ping = sum(test.ping for test in speed_tests)
        total_jitter = sum(test.jitter for test in speed_tests)
        
        count = len(speed_tests)
        last_test = max(speed_tests, key=lambda x: x.test_date)
        
        return SpeedTestSummary(
            average_download=round(total_download / count, 2),
            average_upload=round(total_upload / count, 2),
            average_ping=round(total_ping / count, 2),
            average_jitter=round(total_jitter / count, 2),
            total_tests=count,
            last_test_date=last_test.test_date
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get speed test summary: {str(e)}"
        )

@router.get("/latest", response_model=SpeedTestResult)
async def get_latest_speed_test(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the latest speed test result"""
    try:
        latest_test = db.query(SpeedTest).filter(
            SpeedTest.user_id == current_user.id
        ).order_by(SpeedTest.test_date.desc()).first()
        
        if not latest_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No speed test results found"
            )
        
        return SpeedTestResult(
            id=latest_test.id,
            download_speed=latest_test.download_speed,
            upload_speed=latest_test.upload_speed,
            ping=latest_test.ping,
            jitter=latest_test.jitter,
            test_date=latest_test.test_date,
            server_location=latest_test.server_location,
            test_type=latest_test.test_type
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get latest speed test: {str(e)}"
        )

async def _run_speed_test_external(server_location: str = "Auto") -> dict:
    """Run speed test using external service"""
    # This is a simplified implementation
    # In production, you would integrate with a real speed test service
    # like Speedtest.net API or similar
    
    # Simulate speed test results
    import random
    import time
    
    # Simulate test duration
    await asyncio.sleep(2)
    
    # Generate realistic speed test results
    download_speed = random.uniform(50, 500)  # Mbps
    upload_speed = download_speed * random.uniform(0.1, 0.3)  # Typically 10-30% of download
    ping = random.uniform(5, 50)  # ms
    jitter = random.uniform(1, 10)  # ms
    
    return {
        "download_speed": round(download_speed, 2),
        "upload_speed": round(upload_speed, 2),
        "ping": round(ping, 2),
        "jitter": round(jitter, 2),
        "server_location": server_location,
        "test_date": datetime.now().isoformat()
    }