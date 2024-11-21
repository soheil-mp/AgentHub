@echo off

:: Make sure we're in the backend directory
cd /d "%~dp0\.."

:: Stop MongoDB container
docker-compose stop mongodb

:: Remove MongoDB volume
docker volume rm backend_mongodb_data

:: Start MongoDB container
docker-compose up -d mongodb

:: Wait for MongoDB to be ready
echo Waiting for MongoDB to initialize...
timeout /t 10 /nobreak

echo MongoDB reset complete! 