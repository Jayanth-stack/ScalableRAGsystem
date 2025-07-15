"""Main FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from ..core.config import Settings
from .routers import analysis, search, documentation, metrics
from .middleware import RateLimitMiddleware

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Code Assistant API...")
    # Initialize resources
    yield
    # Cleanup
    logger.info("Shutting down Code Assistant API...")

# Create FastAPI app
app = FastAPI(
    title="Code Documentation Assistant API",
    description="AI-powered code analysis and documentation generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
# app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# Include routers
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(documentation.router, prefix="/api/v1/documentation", tags=["documentation"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Code Documentation Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 