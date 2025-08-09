# 🚀 RocketNet Client Portal

A modern, award-winning client portal for RocketNet ISP customers with full Splynx BSS/OSS integration.

## ✨ Features

### 🔐 Authentication & Security
- JWT-based authentication
- Secure password hashing
- Role-based access control
- Session management

### 💰 Billing Management
- Real-time billing information
- Invoice history and details
- Payment processing
- Outstanding balance tracking
- Automated payment reminders

### 📊 Usage Analytics
- Real-time data usage monitoring
- Historical usage charts
- Usage limits and alerts
- Bandwidth consumption tracking
- Usage patterns analysis

### 🏃‍♂️ Speed Testing
- Integrated speed test functionality
- Historical speed test results
- Performance analytics
- Server location selection
- Automatic speed test scheduling

### 📦 Package Management
- Current package information
- Available package upgrades
- Package comparison tools
- Upgrade request processing
- Package recommendations

### 🔄 Retention Management
- Downgrade and cancellation requests
- Retention fee processing
- Request tracking and status
- Payment requirements
- Customer retention analytics

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI
- **Database**: SQLAlchemy with PostgreSQL/SQLite
- **Authentication**: JWT tokens
- **API Integration**: Splynx BSS/OSS
- **Caching**: Redis
- **Task Queue**: Celery

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI)
- **State Management**: React Query
- **Routing**: React Router
- **Animations**: Framer Motion
- **Charts**: Recharts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (optional, SQLite for development)
- Redis (optional for development)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rocketnet-portal
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

5. **Run the backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Application Settings
APP_NAME=RocketNet Client Portal
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///./rocketnet_portal.db
# For PostgreSQL: postgresql://user:password@localhost/rocketnet

# Splynx Integration
SPLYNX_URL=https://splynx.rocketnet.com
SPLYNX_API_KEY=your-api-key
SPLYNX_API_SECRET=your-api-secret
SPLYNX_ADMIN_USERNAME=admin
SPLYNX_ADMIN_PASSWORD=admin-password

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### Splynx API Configuration

1. **Get API credentials** from your Splynx admin panel
2. **Configure API endpoints** in `app/services/splynx_service.py`
3. **Test connection** using the provided examples

## 📁 Project Structure

```
rocketnet-portal/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Configuration settings
│   │   │   ├── database.py        # Database models and setup
│   │   │   └── security.py        # Authentication and security
│   │   ├── routers/
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── billing.py        # Billing management
│   │   │   ├── usage.py          # Usage analytics
│   │   │   ├── speed_tests.py    # Speed test functionality
│   │   │   ├── packages.py       # Package management
│   │   │   └── retentions.py     # Retention requests
│   │   ├── services/
│   │   │   └── splynx_service.py # Splynx API integration
│   │   └── main.py               # FastAPI application
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Layout/
│   │   │       └── Layout.tsx    # Main layout component
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx   # Authentication context
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx     # Dashboard page
│   │   │   ├── Login.tsx         # Login page
│   │   │   ├── Billing.tsx       # Billing page
│   │   │   ├── Usage.tsx         # Usage page
│   │   │   ├── SpeedTests.tsx    # Speed tests page
│   │   │   ├── Packages.tsx      # Packages page
│   │   │   ├── Retentions.tsx    # Retentions page
│   │   │   └── Profile.tsx       # Profile page
│   │   └── App.tsx               # Main application
│   ├── package.json
│   └── public/
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout

### Billing
- `GET /api/billing/history` - Get billing history
- `GET /api/billing/current` - Get current invoice
- `GET /api/billing/outstanding` - Get outstanding invoices
- `GET /api/billing/summary` - Get billing summary
- `POST /api/billing/pay/{invoice_number}` - Process payment

### Usage
- `GET /api/usage/current` - Get current usage
- `GET /api/usage/history` - Get usage history
- `GET /api/usage/real-time` - Get real-time usage
- `GET /api/usage/limits` - Get usage limits

### Speed Tests
- `POST /api/speed-tests/run` - Run speed test
- `GET /api/speed-tests/history` - Get speed test history
- `GET /api/speed-tests/summary` - Get speed test summary
- `GET /api/speed-tests/latest` - Get latest speed test

### Packages
- `GET /api/packages/available` - Get available packages
- `GET /api/packages/current` - Get current package
- `POST /api/packages/upgrade` - Upgrade package
- `GET /api/packages/comparison` - Compare packages

### Retentions
- `POST /api/retentions/request` - Create retention request
- `POST /api/retentions/{request_id}/pay` - Pay retention fee
- `GET /api/retentions/history` - Get retention history
- `GET /api/retentions/{request_id}` - Get retention request
- `GET /api/retentions/fees/calculate` - Calculate retention fees

## 🎨 UI/UX Features

### Modern Design
- Material Design 3 principles
- Responsive design for all devices
- Dark/light theme support
- Smooth animations and transitions
- Accessibility compliant

### User Experience
- Intuitive navigation
- Real-time updates
- Interactive charts and graphs
- Quick actions and shortcuts
- Progressive web app features

### Performance
- Optimized loading times
- Efficient data caching
- Lazy loading components
- Code splitting
- Bundle optimization

## 🔒 Security Features

- JWT token authentication
- Password hashing with bcrypt
- CORS configuration
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

## 🚀 Deployment

### Docker Deployment

1. **Build Docker images**
   ```bash
   docker-compose build
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Production Deployment

1. **Backend deployment**
   - Use Gunicorn with Uvicorn workers
   - Set up reverse proxy (Nginx)
   - Configure SSL certificates
   - Set up monitoring and logging

2. **Frontend deployment**
   - Build production bundle
   - Deploy to CDN or static hosting
   - Configure environment variables
   - Set up CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: support@rocketnet.com
- Documentation: [Wiki](https://wiki.rocketnet.com)
- Issues: [GitHub Issues](https://github.com/rocketnet/portal/issues)

## 🙏 Acknowledgments

- Splynx BSS/OSS for the backend integration
- Material-UI for the component library
- React Query for state management
- Framer Motion for animations
- Recharts for data visualization