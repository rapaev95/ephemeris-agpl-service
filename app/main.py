"""FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import v1
from app.core.swe import initialize_ephemeris_path
from app.core.errors import create_error_response

# Initialize Swiss Ephemeris path on startup
initialize_ephemeris_path()

# Create FastAPI app
app = FastAPI(
    title="Ephemeris AGPL Service",
    description="HTTP service for astronomical calculations using Swiss Ephemeris (AGPL-3.0)",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
# Allow all origins in development, restrict in production
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(v1.router)


# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unhandled exceptions."""
    return create_error_response(
        code="internal_error",
        message="Internal server error",
        details={"error": str(exc)},
        status_code=500,
    )


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    # Ensure ephemeris path is initialized
    initialize_ephemeris_path()
    print("Ephemeris AGPL Service started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Ephemeris AGPL Service stopped")
