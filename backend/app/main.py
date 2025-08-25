from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.api.v1.api_minimal import api_router
from app.core.exceptions import setup_exception_handlers

# Import all models to ensure they are registered with SQLAlchemy
from app.models import user, document, haccp, prp, supplier, traceability, notification, rbac, settings as settings_model, audit, nonconformance, training, equipment as equipment_model
from app.models.production import ProductProcessType, ProcessStatus
from app.core.security import verify_token
from app.services import log_audit_event

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_TYPE}")
    
    # Initialize database (only in development/testing)
    if settings.ENVIRONMENT in ["development", "testing"]:
        try:
            init_db()
            logger.info("Database initialized successfully (models metadata created)")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            # Don't crash the app in production - let it continue
    
    yield
    
    # Shutdown
    logger.info("Shutting down ISO 22000 FSMS")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ISO 22000 Food Safety Management System for Dairy Processing",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Setup custom exception handlers
setup_exception_handlers(app)

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
    allowed_hosts=["*"] if settings.DEBUG else ["*"]
)

# Request timing middleware (client-disconnect safe)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:  # Handle client disconnects gracefully
        try:
            import anyio  # type: ignore
            EndOfStream = getattr(anyio, "EndOfStream", None)
        except Exception:
            EndOfStream = None
        import asyncio
        if isinstance(exc, (asyncio.CancelledError, EndOfStream if EndOfStream else Exception)):
            from starlette.responses import Response as _Response
            response = _Response(status_code=204)
        else:
            raise
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    # System-wide audit logging (non-blocking)
    try:
        # Skip docs and health endpoints
        path = request.url.path
        if not (path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json") or path == "/health"):
            user_id = None
            auth = request.headers.get("Authorization")
            if auth and auth.startswith("Bearer "):
                payload = verify_token(auth.split(" ")[1])
                if payload and payload.get("sub"):
                    try:
                        user_id = int(payload.get("sub"))
                    except Exception:
                        user_id = None
            # Derive a simple resource_type from path
            resource_type = "generic"
            if path.startswith("/api/v1/"):
                try:
                    resource_type = path.split("/api/v1/")[1].split("/")[0]
                except Exception:
                    resource_type = "generic"
            # Try to infer a resource_id from path (last segment if int or UUID-like)
            resource_id = None
            try:
                segments = [seg for seg in path.split("/") if seg]
                if segments:
                    cand = segments[-1]
                    # if last segment is not a keyword like 'download', check previous
                    if cand in {"download", "reports", "search", "dashboard", "enhanced", "summary", "templates"} and len(segments) > 1:
                        cand = segments[-2]
                    import re as _re
                    if cand.isdigit() or _re.match(r"^[0-9a-fA-F-]{8,36}$", cand):
                        resource_id = cand
            except Exception:
                resource_id = None
            # Capture safe query params for GET/list endpoints
            qp = None
            try:
                if request.method.upper() == "GET":
                    allowed_keys = {"page", "size", "skip", "limit", "search", "status", "batch_type", "category", "document_type", "date_from", "date_to"}
                    qp_all = dict(request.query_params)
                    qp = {k: v for k, v in qp_all.items() if k in allowed_keys and v is not None}
            except Exception:
                qp = None
            # Persist
            db = SessionLocal()
            log_audit_event(
                db,
                user_id=user_id,
                action=f"{request.method} {path}",
                resource_type=resource_type,
                resource_id=resource_id,
                details={
                    "status": response.status_code,
                    "process_time_ms": int(process_time * 1000),
                    **({"query": qp} if qp else {})
                },
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
            db.close()
    except Exception:
        # Never break response on audit failure
        pass
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
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "timestamp": time.time()
    }

# Debug endpoint
@app.get("/debug")
async def debug():
    return {
        "message": "Debug endpoint working",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "timestamp": time.time()
    }

# Test production endpoints
@app.get("/test-production")
async def test_production():
    """Test endpoint to check production API access"""
    return {
        "message": "Production test endpoint",
        "available_process_types": [pt.value for pt in ProductProcessType],
        "available_statuses": [st.value for st in ProcessStatus],
        "timestamp": time.time()
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Digital Ocean and monitoring"""
    try:
        # Simple health check without database dependency
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "environment": settings.ENVIRONMENT,
            "version": settings.APP_VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time(),
                "environment": settings.ENVIRONMENT
            }
        )

# Catch-all endpoint for debugging (DISABLED)
# @app.get("/{path:path}")
# async def catch_all(path: str):
    """Catch-all endpoint for debugging routing issues"""
    return {
        "message": f"Path '{path}' not found",
        "available_endpoints": ["/", "/health", "/debug", "/api/v1"],
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 