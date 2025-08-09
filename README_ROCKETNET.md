# RocketNet Client Portal

A modern, award-winning customer portal for RocketNet ISP customers, built with React and FastAPI, integrating seamlessly with Splynx BSS/OSS.

## Features

### 🎯 Core Functionality
- **Customer Authentication** - Secure login with Splynx integration
- **Billing Dashboard** - View invoices, payment history, and outstanding balances
- **Usage Analytics** - Real-time data consumption and usage patterns
- **Speed Testing** - Integrated speed test capabilities
- **Package Management** - View current plan and upgrade options
- **Retention Flow** - Smart downgrade/cancellation process with retention steps

### 🎨 Award-Winning UX Design
- **Modern UI** - Clean, intuitive design with RocketNet branding
- **Responsive Design** - Seamless experience across all devices
- **Accessibility** - WCAG 2.1 compliant
- **Performance** - Optimized loading and interactions
- **Dark/Light Themes** - User preference support

### 🔒 Security & Compliance
- **API Key Management** - Secure Splynx API integration
- **Data Encryption** - End-to-end encryption for sensitive data
- **Session Management** - Secure customer sessions
- **GDPR Compliance** - Privacy-first data handling

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI       │    │   Splynx BSS    │
│   (TypeScript)  │◄──►│   Backend       │◄──►│   (API)         │
│                 │    │   (Python)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│                      │                      │
├─ Dashboard          ├─ Authentication      ├─ Customer Data
├─ Billing            ├─ API Integration     ├─ Billing Info
├─ Usage Analytics    ├─ Speed Test Proxy    ├─ Usage Data
├─ Speed Tests        ├─ Retention Logic     ├─ Service Plans
├─ Package Upgrades   ├─ Payment Processing  ├─ Tariffs
└─ Retention Flow     └─ Session Management  └─ Invoices
```

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for utility-first styling
- **Framer Motion** for smooth animations
- **React Query** for data management
- **React Router** for navigation
- **Chart.js** for usage analytics
- **React Hook Form** for form management

### Backend
- **FastAPI** for high-performance API
- **SQLAlchemy** for database ORM
- **Pydantic** for data validation
- **JWT** for authentication
- **Redis** for caching and sessions
- **Celery** for background tasks
- **PostgreSQL** for data storage

### DevOps
- **Docker** for containerization
- **Docker Compose** for local development
- **GitHub Actions** for CI/CD
- **Nginx** for reverse proxy
- **Let's Encrypt** for SSL certificates

## Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL
- Redis

### Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd rocketnet-portal

# Start all services
docker-compose up -d

# The portal will be available at http://localhost:3000
# API documentation at http://localhost:8000/docs
```

### Development Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your Splynx API credentials

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your API endpoints

# Start the development server
npm run dev
```

## Configuration

### Environment Variables

#### Backend (.env)
```env
# Splynx Configuration
SPLYNX_URL=https://your-splynx-domain.com
SPLYNX_API_KEY=your_api_key
SPLYNX_API_SECRET=your_api_secret

# Database
DATABASE_URL=postgresql://user:password@localhost/rocketnet_portal

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Features
ENABLE_SPEED_TEST=true
RETENTION_FEE_AMOUNT=25.00
```

#### Frontend (.env.local)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=RocketNet Portal
VITE_ENABLE_ANALYTICS=true
```

## API Documentation

The FastAPI backend provides comprehensive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints
- `POST /auth/login` - Customer authentication
- `GET /customer/profile` - Customer information
- `GET /billing/invoices` - Billing history
- `GET /usage/stats` - Usage analytics
- `POST /speedtest/run` - Initiate speed test
- `GET /packages/available` - Available upgrades
- `POST /retention/initiate` - Start retention process

## Deployment

### Production Deployment with Docker

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Environment-specific Configs
- **Development**: `docker-compose.yml`
- **Staging**: `docker-compose.staging.yml`
- **Production**: `docker-compose.prod.yml`

## Security Considerations

1. **API Security**: All Splynx API calls use secure API keys
2. **Data Encryption**: Sensitive data encrypted at rest and in transit
3. **Authentication**: JWT-based authentication with refresh tokens
4. **Rate Limiting**: API rate limiting to prevent abuse
5. **CORS**: Properly configured CORS policies
6. **Input Validation**: Comprehensive input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software for RocketNet ISP.

## Support

For technical support, contact:
- **Development Team**: dev@rocketnet.com
- **Documentation**: [Internal Wiki](link-to-internal-docs)
- **Issue Tracking**: [GitHub Issues](link-to-issues)