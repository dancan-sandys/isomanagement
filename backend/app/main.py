from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.api.v1.api_minimal import api_router

# Import all models to ensure they are registered with SQLAlchemy
from app.models import user, document, haccp, prp, supplier, traceability, notification, rbac, settings as settings_model, audit, nonconformance, training, equipment as equipment_model
from app.core.security import verify_token
from app.services import log_audit_event

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ISO 22000 Food Safety Management System for Dairy Processing",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add CORS middleware (explicit origins when credentials are allowed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ALLOWED_CREDENTIALS else ["*"],
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

    # Initialize database (dev convenience). Ensure models are imported above.
    try:
        init_db()
        print("Database initialized successfully (models metadata created)")
    except Exception as e:
        print(f"Database initialization error: {e}")

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