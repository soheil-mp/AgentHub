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
- 🔄 **Router Agent** - Smart routing based on user intent
- 📦 **Product Agent** - Product information and inquiries
- 🔧 **Technical Agent** - Technical support and troubleshooting
- 👥 **Customer Service Agent** - General support and billing
- 🤝 **Human Proxy Agent** - Human escalation handling

### Booking Specialists
- ✈️ **Flight Booking Agent** - Air travel reservations
- 🏨 **Hotel Booking Agent** - Accommodation bookings
- 🚗 **Car Rental Agent** - Vehicle rentals
- 🎯 **Excursion Agent** - Activity bookings

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
- Python 3.8 or higher
- Docker Desktop
- Git

### Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/agenthub.git
cd agenthub/backend
```

2. **Set Up Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

3. **Install Dependencies**
```bash
# Install project with development dependencies
pip install -e ".[dev]"
```

4. **Configure Environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings:
# - Add your OpenAI API key
# - Configure Redis and MongoDB settings
# - Adjust other settings as necessary
```

5. **Start Services**
```bash
# Start Redis and MongoDB
docker-compose up -d

# Verify services are running
docker-compose ps
```

6. **Start the API Server**
```bash
uvicorn app.main:app --reload
```

### Verify Installation

After starting the server, you can access:
- API Documentation: http://localhost:8000/docs
- API Information: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

## 💻 Development

### Project Structure
```
.
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints and routes
│   │   │   ├── routes/       # Route definitions
│   │   │   └── middleware/   # Custom middleware
│   │   ├── core/             # Core configurations
│   │   │   ├── config.py     # Settings management
│   │   │   └── exceptions.py # Error handling
│   │   ├── schemas/          # Data models and schemas
│   │   └── services/         # Business logic
│   │       ├── agents/       # Agent implementations
│   │       │   ├── base.py   # Base agent class
│   │       │   ├── booking/  # Booking-related agents
│   │       │   ├── support/  # Support-related agents
│   │       │   └── router.py # Router agent
│   │       ├── cache.py      # Redis service
│   │       ├── database.py   # MongoDB service
│   │       └── graph.py      # Workflow definitions
│   ├── tests/                # Test suites
│   │   ├── unit/            # Unit tests
│   │   ├── integration/     # Integration tests
│   │   ├── performance/     # Performance tests
│   │   └── security/        # Security tests
│   └── docker-compose.yml    # Service definitions
│
└── frontend/
    ├── public/              # Static assets
    ├── src/
    │   ├── components/      # React components
    │   │   ├── Chat/       # Chat interface components
    │   │   └── Graph/      # Graph visualization components
    │   ├── types/          # TypeScript type definitions
    │   ├── App.tsx         # Root component
    │   └── main.tsx        # Entry point
    ├── index.html          # HTML template
    ├── tailwind.config.js  # Tailwind CSS configuration
    └── package.json        # Frontend dependencies
```

### Database Schema
- **MongoDB Collections**
  - `users`: User profiles and preferences
  - `conversations`: Chat history and context
  - `bookings`: Reservation details
  - `metrics`: Performance and usage data

### Key Components
- **Redis**: Session management and caching
- **MongoDB**: Persistent data storage
- **FastAPI**: API framework
- **LangChain**: Agent orchestration
- **Docker**: Service containerization

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/performance/  # Performance tests

# Run with coverage
pytest --cov=app tests/
```

### Test Categories

| Category | Description | Examples |
|----------|-------------|----------|
| Unit Tests | Individual components | Agent behavior, Service functions |
| Integration | Component interaction | API endpoints, Workflows |
| Performance | System efficiency | Load testing, Response times |
| Security | System protection | Input validation, Auth checks |

## 🔧 Maintenance

### Health Monitoring
- **System Health**: `GET /api/v1/health`
- **Database Status**: `GET /api/v1/health/db`
- **Cache Status**: `GET /api/v1/health/cache`
- **Agent Status**: `GET /api/v1/health/agents`

### Logging
- Application logs: `docker-compose logs app`
- MongoDB logs: `docker-compose logs mongodb`
- Redis logs: `docker-compose logs redis`

### Metrics
- System metrics: `GET /api/v1/metrics`
- Agent performance: `GET /api/v1/metrics/agents`
- Response times: `GET /api/v1/metrics/performance`

## 🤝 Contributing

1. **Fork and Clone**
```bash
git clone https://github.com/yourusername/agenthub.git
cd agenthub
```

2. **Set Up Development Environment**
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

3. **Development Guidelines**
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Use type hints
- Add meaningful commit messages

4. **Submit Pull Request**
- Ensure all tests pass
- Update documentation
- Follow code style guidelines
- Include test coverage

## 📄 License

This project is licensed under the CC0 1.0 Universal License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LangChain team for the excellent framework
- OpenAI for their powerful language models
- The open-source community for their contributions
