# 🤖 AgentHub

<div align="center">

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-Powered-orange)](https://github.com/hwchase17/langchain)

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
- ✈️ Flight Booking Agent
- 🏨 Hotel Booking Agent
- 🚗 Car Rental Agent
- 🎯 Excursion Agent

### Technical Capabilities
- 📊 State Management with Redis
- ⚡ Rate Limiting & Caching
- 🔄 Error Recovery
- 📈 Metrics Collection
- 📝 Comprehensive Logging

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
# - Configure Redis if needed
# - Adjust other settings as necessary
```

5. **Start Services**

First, ensure Docker Desktop is running, then:
```bash
# Start Redis
docker-compose up -d redis

# Verify Redis is running
docker-compose ps
```

6. **Start the API Server**
```bash
# Make sure you're in the virtual environment
# Windows: venv\Scripts\activate
# Unix/MacOS: source venv/bin/activate

# Start the server with auto-reload
uvicorn app.main:app --reload
```

### Verify Installation

After starting the server, you can access:
- API Documentation: http://localhost:8000/docs
- API Information: http://localhost:8000/api
- Health Check: http://localhost:8000/api/v1/health

## 💻 Development

### Starting the Server
```bash
uvicorn app.main:app --reload
```

API documentation available at: `http://localhost:8000/docs`

## 🧪 Testing

### Running Test Suites

```bash
# All tests
pytest

# Specific categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/performance/  # Performance tests
pytest tests/security/     # Security tests

# With coverage
pytest --cov=app tests/
```

### Test Categories Overview

| Category | Description |
|----------|-------------|
| Unit Tests | Agent behavior, service functionality, base components |
| Integration Tests | API endpoints, agent workflows, chat flows |
| Performance Tests | Load testing, memory usage, rate limiting |
| Security Tests | SQL injection, XSS prevention, input validation |

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core configurations
│   └── services/      # Business logic
│       ├── agents/    # Agent implementations
│       └── graph.py   # Workflow definitions
└── tests/             # Test suites
```

## 🤝 Contributing

1. **Set Up Development Environment**
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

2. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make Changes and Test**
```bash
pytest
pytest --cov=app tests/
```

4. **Submit Pull Request**
- Ensure all tests pass
- Update documentation as needed
- Follow coding standards
- Include test coverage for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
