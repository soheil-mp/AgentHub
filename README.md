# AgentHub Backend

A sophisticated multi-agent system built with LangChain and LangGraph for handling complex customer interactions.

## Features

- Multi-agent architecture with specialized agents:
  - Router Agent: Smart routing based on user intent
  - Product Agent: Product information and inquiries
  - Technical Agent: Technical support and troubleshooting
  - Customer Service Agent: General support and billing
  - Human Proxy Agent: Human escalation handling
  - Booking Agents:
    - Flight Booking Agent
    - Hotel Booking Agent
    - Car Rental Agent
    - Excursion Agent

- Advanced Features:
  - State Management with Redis
  - Rate Limiting
  - Caching
  - Error Recovery
  - Metrics Collection
  - Comprehensive Logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agenthub.git
cd agenthub/backend
```

2. Set up virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

3. Install the package in development mode:
```bash
# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Required variables:
# - OPENAI_API_KEY
# - REDIS_HOST
# - REDIS_PASSWORD (if needed)
```

5. Start Redis:
```bash
docker-compose up -d redis
```

## Development

1. Start development server:
```bash
uvicorn app.main:app --reload
```

2. Access API documentation:
```
http://localhost:8000/docs
```

## Running Tests

The project includes comprehensive test suites:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
pytest tests/security/

# Run with coverage
pytest --cov=app tests/
```

### Test Categories

1. Unit Tests
- Agent Tests: Individual agent behavior
- Service Tests: Core service functionality
- Base Component Tests: Shared functionality

2. Integration Tests
- API Endpoint Tests
- Agent Workflow Tests
- Chat Flow Tests

3. Performance Tests
- Load Testing
- Memory Usage
- Rate Limiting

4. Security Tests
- SQL Injection Prevention
- XSS Prevention
- Input Validation
- Error Message Safety

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── middleware.py
│   └── services/
│       ├── agents/
│       │   ├── booking/
│       │   └── support/
│       ├── cache.py
│       ├── graph.py
│       └── state.py
└── tests/
    ├── unit/
    ├── integration/
    ├── performance/
    └── security/
```

## Contributing

1. Create a new virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

4. Make your changes and run tests:
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

5. Submit a pull request

## License

MIT License - see LICENSE file for details