FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including network tools and graphviz
RUN apt-get update && apt-get install -y \
    build-essential \
    iputils-ping \
    net-tools \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 