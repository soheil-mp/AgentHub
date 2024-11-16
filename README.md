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
- Docker and Docker Compose
- Redis

### Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/agenthub.git
cd agenthub/backend
```

2. **Set Up Virtual Environment**
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

3. **Install Dependencies**
```bash
pip install -e ".[dev]"
```

4. **Configure Environment**
```bash
cp .env.example .env
```

Required variables in `.env`:
```ini
OPENAI_API_KEY=your_api_key_here
REDIS_HOST=localhost
REDIS_PASSWORD=your_password_here  # if needed
```

5. **Start Redis**
```bash
docker-compose up -d redis
```

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

---

<div align="center">
Made with ❤️ by the AgentHub Team
</div>