#!/usr/bin/env python3
"""
The Gatekeeper - Main Application Entry Point
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from starlette.responses import Response
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="The Gatekeeper",
    description="AI System API",
    version="1.0.0"
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'gatekeeper_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'gatekeeper_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# ──────────────────────────────────────────────────────────────
# Health Check Endpoints
# ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "gatekeeper",
        "version": "1.0.0"
    }

@app.get("/health/ready")
async def readiness_check():
    """Readiness check for container orchestration"""
    # Add checks for dependencies (Redis, DB, etc.)
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "redis": "connected",  # Placeholder
            "database": "connected"  # Placeholder
        }
    }

@app.get("/health/live")
async def liveness_check():
    """Liveness check for container orchestration"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

# ──────────────────────────────────────────────────────────────
# Metrics Endpoint
# ──────────────────────────────────────────────────────────────

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# ──────────────────────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "The Gatekeeper",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }

@app.get("/api/v1/status")
async def get_status():
    """Get system status"""
    return {
        "system": "operational",
        "uptime": "unknown",  # Implement uptime tracking
        "environment": os.getenv('OMEGA_ENV', 'development'),
        "timestamp": datetime.utcnow().isoformat()
    }

# ──────────────────────────────────────────────────────────────
# Error Handlers
# ──────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if os.getenv('OMEGA_ENV') == 'development' else "An error occurred"
        }
    )

# ──────────────────────────────────────────────────────────────
# Startup & Shutdown Events
# ──────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("🚀 The Gatekeeper is starting up...")
    logger.info(f"Environment: {os.getenv('OMEGA_ENV', 'development')}")
    logger.info(f"Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("🛑 The Gatekeeper is shutting down...")

# ──────────────────────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("OMEGA_ENV") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
