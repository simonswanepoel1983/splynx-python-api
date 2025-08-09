from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from .config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    splynx_customer_id = Column(Integer, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SpeedTest(Base):
    __tablename__ = "speed_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    download_speed = Column(Float)
    upload_speed = Column(Float)
    ping = Column(Float)
    jitter = Column(Float)
    test_date = Column(DateTime, default=datetime.utcnow)
    server_location = Column(String)
    test_type = Column(String)  # 'manual' or 'automatic'

class BillingHistory(Base):
    __tablename__ = "billing_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    invoice_number = Column(String, unique=True, index=True)
    amount = Column(Float)
    due_date = Column(DateTime)
    paid_date = Column(DateTime, nullable=True)
    status = Column(String)  # 'paid', 'unpaid', 'overdue'
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Package(Base):
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    speed_down = Column(Integer)  # Mbps
    speed_up = Column(Integer)  # Mbps
    price = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RetentionRequest(Base):
    __tablename__ = "retention_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    request_type = Column(String)  # 'downgrade', 'cancel'
    reason = Column(Text)
    amount_paid = Column(Float, nullable=True)
    status = Column(String, default='pending')  # 'pending', 'approved', 'rejected'
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)