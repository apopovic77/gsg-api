"""
GSG API - Gravity Sports Group Product API
Main FastAPI Application
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .core.config import get_settings
from .routers import products, brands

# Static files path
STATIC_DIR = Path(__file__).parent / "static"

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)
app.include_router(brands.router)

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/console", tags=["UI"], include_in_schema=False)
async def console():
    """Dev Console UI"""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/", tags=["Health"])
async def root():
    """API root - health check"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    from .core.database import db

    # Test database connection
    try:
        result = db.execute_scalar("SELECT 1")
        db_status = "connected" if result == 1 else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "version": settings.api_version,
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "gsg_api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )
