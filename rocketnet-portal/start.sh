#!/bin/bash

# RocketNet Client Portal Startup Script

echo "🚀 Starting RocketNet Client Portal..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# RocketNet Client Portal Environment Variables

# Application Settings
APP_NAME=RocketNet Client Portal
DEBUG=true
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=postgresql://postgres:password@db:5432/rocketnet

# Splynx Integration
SPLYNX_URL=https://splynx.rocketnet.com
SPLYNX_API_KEY=your-api-key
SPLYNX_API_SECRET=your-api-secret
SPLYNX_ADMIN_USERNAME=admin
SPLYNX_ADMIN_PASSWORD=admin-password

# Redis
REDIS_URL=redis://redis:6379

# Frontend URL
FRONTEND_URL=http://localhost:3000
EOF
    echo "✅ .env file created. Please edit it with your actual configuration."
fi

# Create uploads directory
mkdir -p uploads

# Build and start the application
echo "🔨 Building and starting the application..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "🎉 RocketNet Client Portal is starting up!"
echo ""
echo "📊 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "⚠️  Please make sure to:"
echo "   1. Edit the .env file with your actual Splynx configuration"
echo "   2. Wait a few minutes for all services to fully start"
echo "   3. Check the logs with: docker-compose logs -f"
echo ""
echo "🛑 To stop the application, run: docker-compose down"