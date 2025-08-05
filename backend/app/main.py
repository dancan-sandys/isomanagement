from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api_minimal import api_router

# Import all models to ensure they are registered with SQLAlchemy
from app.models import user, document, haccp, prp, supplier, traceability, notification, rbac, settings as settings_model

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ISO 22000 Food Safety Management System for Dairy Processing",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOWED_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ISO 22000 FSMS API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database: {settings.DATABASE_TYPE}")

    # Initialize database - commented out to avoid model import issues
    # try:
    #     init_db()
    #     print("Database initialized successfully")
    # except Exception as e:
    #     print(f"Database initialization error: {e}")
    
    print("Database tables should be created manually or via Alembic")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down ISO 22000 FSMS")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 