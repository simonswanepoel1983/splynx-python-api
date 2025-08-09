from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from .routers import auth, billing, usage, speed_tests, packages, retentions
from .core.config import settings
from .core.database import init_db
from .core.security import get_current_user

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="RocketNet Client Portal",
    description="Modern client portal for RocketNet ISP customers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://portal.rocketnet.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])
app.include_router(usage.router, prefix="/api/usage", tags=["Usage"])
app.include_router(speed_tests.router, prefix="/api/speed-tests", tags=["Speed Tests"])
app.include_router(packages.router, prefix="/api/packages", tags=["Packages"])
app.include_router(retentions.router, prefix="/api/retentions", tags=["Retentions"])

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RocketNet Client Portal</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; text-align: center; }
            h1 { font-size: 3em; margin-bottom: 20px; }
            p { font-size: 1.2em; margin-bottom: 30px; }
            .api-link { display: inline-block; background: rgba(255,255,255,0.2); padding: 15px 30px; border-radius: 10px; text-decoration: none; color: white; margin: 10px; transition: all 0.3s ease; }
            .api-link:hover { background: rgba(255,255,255,0.3); transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 RocketNet Client Portal</h1>
            <p>Welcome to the RocketNet Client Portal API</p>
            <a href="/docs" class="api-link">📚 API Documentation</a>
            <a href="/redoc" class="api-link">📖 ReDoc Documentation</a>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "RocketNet Client Portal"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )