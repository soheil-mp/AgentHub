# 🤖 AgentHub

<div align="center">

[![CC0 License](https://img.shields.io/badge/License-CC0%201.0-lightgrey.svg)](https://choosealicense.com/licenses/cc0-1.0/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-Powered-orange)](https://github.com/hwchase17/langchain)
[![MongoDB](https://img.shields.io/badge/MongoDB-Ready-green)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/Redis-Enabled-red)](https://redis.io/)

A sophisticated multi-agent system built with LangChain and LangGraph for handling complex customer interactions.

[Features](#-features) •
[Installation](#-installation) •
[Development](#-development) •
[Testing](#-testing) •
[Contributing](#-contributing)

</div>

---

## 🌟 Features

### Multi-Agent Architecture
- 🧠 **Assistant Agent** - Central coordinator for all user interactions
- ✈️ **Flight Booking Agent** - Air travel reservations
- 🏨 **Hotel Booking Agent** - Accommodation bookings
- 🚗 **Car Rental Agent** - Vehicle rentals
- 🎯 **Excursion Agent** - Activity bookings
- 🔒 **Sensitive Workflow Agent** - Secure handling of sensitive operations

### Technical Capabilities
- 📊 **State Management**
  - Redis for caching and session state
  - MongoDB for persistent storage
  - Distributed state handling
- ⚡ **Performance**
  - Rate limiting & request throttling
  - Distributed caching
  - Async operations
  - Load balancing
- 🔄 **Reliability**
  - Error recovery mechanisms
  - Automatic retries
  - Graceful degradation
  - Circuit breakers
- 📈 **Observability**
  - Comprehensive logging
  - Performance metrics
  - Health monitoring
  - Tracing capabilities
- 🔒 **Security**
  - API key validation
  - Input sanitization
  - Rate limiting
  - Data encryption

## 🚀 Installation

### Prerequisites
- Docker Desktop
- Git
- PowerShell (Windows) or Bash (Unix)
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/agenthub.git
cd agenthub
```

2. **Environment Setup**
```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Update backend/.env with your settings
OPENAI_API_KEY=your_key_here
MONGODB_USER=agenthub_user
MONGODB_PASSWORD=password123
MONGODB_DB_NAME=agenthub

# Update frontend/.env with your settings
VITE_API_URL=http://localhost:8001
```

3. **Start the Application**

For development:
```bash
# Start all services in development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Or start specific services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up frontend api

# Rebuild if needed
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

For production:
```bash
# Start all services in production mode
docker-compose up -d
```

4. **Verify Installation**
```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Service Access
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8001/docs
- API Health Check: http://localhost:8001/api/v1/health
- MongoDB: mongodb://localhost:27018
- MongoDB Admin: http://localhost:27018 (if using MongoDB Compass)

### Environment Variables

#### Backend (.env)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# MongoDB Configuration
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_USER=agenthub_user
MONGODB_PASSWORD=password123
MONGODB_DB_NAME=agenthub

# API Configuration
DEBUG=1
LOG_LEVEL=DEBUG
```

#### Frontend (.env)
```bash
# API Configuration
VITE_API_URL=http://localhost:8001

# Development Settings
NODE_ENV=development
HOST=0.0.0.0
PORT=3000
```

### Database Schema
The MongoDB database includes the following collections:

```javascript
users: {
    email: String (unique),
    hashed_password: String,
    created_at: Date,
    updated_at: Date
}

conversations: {
    user_id: String,
    started_at: Date,
    ended_at: Date,
    metadata: Object
}

messages: {
    conversation_id: String,
    role: Enum["user", "assistant", "system"],
    content: String,
    created_at: Date,
    metadata: Object
}

flight_bookings: {
    user_id: String,
    booking_reference: String (unique),
    status: String,
    passenger_details: Object,
    payment_status: String,
    created_at: Date,
    updated_at: Date
}

hotel_bookings: {
    user_id: String,
    booking_reference: String (unique),
    status: String,
    hotel_id: String,
    check_in_date: Date,
    check_out_date: Date,
    room_details: Object,
    guest_details: Object,
    payment_status: String,
    created_at: Date,
    updated_at: Date
}

car_rentals: {
    user_id: String,
    booking_reference: String (unique),
    status: String,
    vehicle_type: String,
    pickup_location: String,
    dropoff_location: String,
    pickup_time: Date,
    dropoff_time: Date,
    driver_details: Object,
    payment_status: String,
    created_at: Date,
    updated_at: Date
}

excursions: {
    user_id: String,
    booking_reference: String (unique),
    status: String,
    activity_id: String,
    activity_date: Date,
    participant_details: Object,
    payment_status: String,
    created_at: Date,
    updated_at: Date
}
```

### Development Tools

#### PowerShell Scripts
- `dev-setup.ps1`: Set up complete development environment
- `verify-setup.ps1`: Verify all services are running correctly
- `check-mongodb-users.ps1`: Check MongoDB users and permissions
- `verify-mongodb.ps1`: Verify MongoDB collections and indexes
- `reset-mongodb.ps1`: Reset MongoDB data and configuration
- `monitor-logs.ps1`: Monitor service logs with filtering

#### Log Monitoring
```powershell
# Monitor all logs
.\scripts\monitor-logs.ps1

# Monitor specific service
.\scripts\monitor-logs.ps1 -service mongodb
.\scripts\monitor-logs.ps1 -service redis
.\scripts\monitor-logs.ps1 -service api

# Monitor by log level
.\scripts\monitor-logs.ps1 -level error
.\scripts\monitor-logs.ps1 -level warning
.\scripts\monitor-logs.ps1 -level info

# Show previous logs
.\scripts\monitor-logs.ps1 -tail 100

# Combine filters
.\scripts\monitor-logs.ps1 -service mongodb -level error -tail 50
```

#### Docker Commands
```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f mongodb

# Rebuild services
docker-compose build --no-cache
docker-compose up -d

# Reset everything
docker-compose down -v
docker volume prune -f
```

### Troubleshooting

#### Log Analysis
```powershell
# Monitor all service logs
.\scripts\monitor-logs.ps1

# Monitor errors only
.\scripts\monitor-logs.ps1 -level error

# Monitor specific service errors
.\scripts\monitor-logs.ps1 -service mongodb -level error

# Check recent logs
.\scripts\monitor-logs.ps1 -tail 100
```

#### Database Issues
```bash
# Reset MongoDB
.\scripts\reset-mongodb.ps1

# Check MongoDB status
.\scripts\verify-mongodb.ps1

# Check MongoDB users
.\scripts\check-mongodb-users.ps1
```

#### API Issues
```bash
# Check API logs
docker-compose logs -f api

# Restart API
docker-compose restart api

# Rebuild API
docker-compose build --no-cache api
docker-compose up -d api
```

#### Redis Issues
```bash
# Check Redis logs
docker-compose logs -f redis

# Test Redis connection
docker exec -it backend-redis-1 redis-cli ping

# Reset Redis
docker-compose restart redis
```

#### Common Issues
1. **MongoDB Authentication Failed**
   - Run `.\scripts\reset-mongodb.ps1` to reset MongoDB
   - Check MongoDB logs: `.\scripts\monitor-logs.ps1 -service mongodb`
   - Monitor authentication issues: `.\scripts\monitor-logs.ps1 -service mongodb -level error`
   - Verify users: `.\scripts\check-mongodb-users.ps1`

2. **Redis Connection Failed**
   - Check Redis is running: `docker-compose ps redis`
   - Monitor Redis logs: `.\scripts\monitor-logs.ps1 -service redis`
   - Check Redis errors: `.\scripts\monitor-logs.ps1 -service redis -level error`
   - Verify Redis connection: `docker exec -it backend-redis-1 redis-cli ping`

3. **API Not Starting**
   - Monitor API logs: `.\scripts\monitor-logs.ps1 -service api`
   - Check API errors: `.\scripts\monitor-logs.ps1 -service api -level error`
   - Verify environment variables
   - Check MongoDB and Redis are running
   - Rebuild API: `docker-compose build --no-cache api`

### Starting the API

#### Option 1: Using Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Or start just the API
docker-compose up -d api

# Monitor API logs
.\scripts\monitor-logs.ps1 -service api

# Monitor API errors only
.\scripts\monitor-logs.ps1 -service api -level error
```

#### Option 2: Running Locally
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix

# Install dependencies
pip install -r requirements.txt

# Start the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Verifying API Status
1. **Check Health Endpoint**:
```bash
curl http://localhost:8000/api/v1/health
```

2. **Visit API Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

3. **Monitor API Status**:
```bash
# Check all services status
.\scripts\verify-setup.ps1

# Monitor API logs
.\scripts\monitor-logs.ps1 -service api
```

#### Troubleshooting API Issues
1. **Check Dependencies**:
   - MongoDB is running and healthy
   - Redis is running and healthy
   - All environment variables are set correctly

2. **Check Logs**:
```bash
# View all API logs
.\scripts\monitor-logs.ps1 -service api

# View only API errors
.\scripts\monitor-logs.ps1 -service api -level error

# View recent logs
.\scripts\monitor-logs.ps1 -service api -tail 100
```

3. **Common Solutions**:
   - Reset and rebuild: `docker-compose down -v && docker-compose up -d`
   - Rebuild API only: `docker-compose build --no-cache api && docker-compose up -d api`
   - Check MongoDB connection: `.\scripts\verify-mongodb.ps1`
   - Verify Redis: `docker exec -it backend-redis-1 redis-cli ping`

### Port Conflicts
If you encounter port conflicts, the following ports are used:
- Frontend: 3000
- API: 8001 (external), 8000 (internal)
- MongoDB: 27018 (external), 27017 (internal)

To change ports, modify the port mappings in docker-compose.yml and update corresponding environment variables.

## 📝 License

This project is licensed under the CC0 1.0 Universal License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LangChain team for the excellent framework
- OpenAI for their powerful language models
- The open-source community for their contributions
