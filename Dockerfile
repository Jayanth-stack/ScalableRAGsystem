# Optimized Dockerfile for Fly.io free tier
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY deployment/free-tier/requirements-minimal.txt .
RUN pip install --no-cache-dir -r deployment/free-tier/requirements-minimal.txt

# Copy application code
COPY code_assistant/ ./code_assistant/
COPY sample_repos/ ./sample_repos/

# Create data directory for SQLite
RUN mkdir -p /data

# Environment variables
ENV DATABASE_URL="sqlite:////data/app.db"
ENV PORT=8080

EXPOSE 8080

# Run the application
CMD ["uvicorn", "code_assistant.api:app", "--host", "0.0.0.0", "--port", "8080"]