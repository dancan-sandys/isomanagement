from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, documents, haccp, prp, suppliers, traceability, settings, profile, notifications, dashboard, audits, risk, risk_framework, haccp_risk, complaints, allergen_label, management_review, rbac, websocket, objectives, equipment, production
from app.api.v1.endpoints import change

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
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(audits.router, prefix="/audits", tags=["audits"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(risk_framework.router, prefix="/risk", tags=["risk_framework"])
api_router.include_router(haccp_risk.router, prefix="/haccp", tags=["haccp_risk"])
api_router.include_router(management_review.router, prefix="/management-reviews", tags=["management_reviews"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["complaints"])
api_router.include_router(allergen_label.router, prefix="/allergen-label", tags=["allergen_label"]) 
api_router.include_router(rbac.router, prefix="/rbac", tags=["rbac"])
api_router.include_router(websocket.router, tags=["websocket"])
api_router.include_router(change.router, prefix="/change-requests", tags=["change_requests"])
api_router.include_router(objectives.router, prefix="/objectives-v2", tags=["objectives"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(production.router, prefix="/production", tags=["production"])