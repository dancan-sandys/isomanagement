from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, documents, haccp, prp, suppliers, traceability, settings, profile, notifications

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(haccp.router, prefix="/haccp", tags=["haccp"])
api_router.include_router(prp.router, prefix="/prp", tags=["prp"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(traceability.router, prefix="/traceability", tags=["traceability"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"]) 