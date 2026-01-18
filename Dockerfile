# Gatekeeper/Omega System Docker Image
# ======================================
# Multi-stage build for optimized image size

# Stage 1: Base image with Python and system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Audio libraries
    ffmpeg \
    libsndfile1 \
    libasound2-dev \
    portaudio19-dev \
    # Build tools
    build-essential \
    git \
    curl \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 2: Dependencies installation
FROM base as dependencies

# Copy requirements files
COPY requirements.txt requirements_enhanced.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements_enhanced.txt

# Stage 3: Application
FROM base as application

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p \
    /app/omega_voice \
    /app/omega_agents \
    /app/omega_security \
    /app/omega_swarm \
    /app/conversations \
    /app/logs

# Expose ports
EXPOSE 5000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Default command
CMD ["python", "omega_web_ide.py", "--host", "0.0.0.0", "--port", "5000"]

LABEL Name=thegatekeeper Version=1.0.0 \
      Description="Gatekeeper/Omega AI System" \
      Maintainer="The Gatekeeper Project"
