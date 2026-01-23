FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x scripts/startup.sh

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the startup script which handles seeding and starting the server
CMD ["/bin/bash", "scripts/startup.sh"]

