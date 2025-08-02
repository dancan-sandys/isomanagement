from fastapi import APIRouter

from app.api.v1.endpoints import auth, dashboard, documents

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"]) 