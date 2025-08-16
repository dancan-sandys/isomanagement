from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)


class AuditAccessDeniedException(HTTPException):
    """Custom exception for audit access denied scenarios"""
    def __init__(self, detail: Union[str, Dict[str, Any]], audit_id: int = None, user_id: int = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        self.audit_id = audit_id
        self.user_id = user_id


class FileUploadException(HTTPException):
    """Custom exception for file upload failures"""
    def __init__(self, detail: Union[str, Dict[str, Any]], filename: str = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        self.filename = filename


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with enhanced logging and response format"""
    
    # Log the error with context
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} "
        f"for {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # For 403 errors, add additional context
    if exc.status_code == 403:
        logger.warning(
            f"Access denied: User attempted to access {request.method} {request.url.path} "
            f"with insufficient permissions"
        )
    
    # For 413 errors (file too large), add file context
    if exc.status_code == 413:
        logger.warning(f"File upload rejected due to size limit: {request.url.path}")
    
    # For 400 errors (bad request), add validation context
    if exc.status_code == 400:
        logger.warning(f"Bad request: {request.method} {request.url.path} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with detailed error information"""
    
    logger.warning(
        f"Validation Error: {request.method} {request.url.path} - {len(exc.errors())} validation errors"
    )
    
    # Format validation errors for better readability
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "status_code": 422,
            "detail": "Request validation failed",
            "errors": formatted_errors,
            "path": request.url.path,
            "method": request.method
        }
    )


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions"""
    
    logger.warning(
        f"Starlette HTTP Exception: {exc.status_code} - {exc.detail} "
        f"for {request.method} {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method
        }
    )


def setup_exception_handlers(app):
    """Setup custom exception handlers for the FastAPI app"""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    
    logger.info("Custom exception handlers configured")
