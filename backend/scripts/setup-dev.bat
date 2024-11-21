@echo off

:: Create logs directory
mkdir logs 2>nul
echo Created logs directory

:: Create necessary directories
mkdir app\services\agents\booking 2>nul
mkdir app\services\agents\support 2>nul

:: Make sure we're in the backend directory
cd /d "%~dp0\.."

:: Stop and remove existing containers
docker-compose down -v

:: Remove existing volumes
docker volume prune -f

:: Start services
docker-compose up -d

:: Wait for MongoDB to initialize
echo Waiting for MongoDB to initialize...
timeout /t 15 /nobreak

:: Check services health
echo Checking services health...
docker-compose ps

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment and install dependencies
call venv\Scripts\activate
pip install --upgrade pip
pip install -e .[dev]

echo Setup complete! You can now start the application with:
echo uvicorn app.main:app --reload 