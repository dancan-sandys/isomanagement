from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.haccp import Product
from app.models.supplier import Supplier
from app.schemas.common import ResponseModel


router = APIRouter()


@router.get("/smart", response_model=ResponseModel)
async def smart_search(
    q: str = Query("", min_length=1),
    user_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        query = q.strip()
        results: List[dict] = []

        if not query:
            return ResponseModel(success=True, message="No query provided", data={"results": [], "suggestions": []})

        # Documents
        docs = (
            db.query(Document)
            .filter((Document.title.ilike(f"%{query}%")) | (Document.document_number.ilike(f"%{query}%")))
            .limit(limit)
            .all()
        )
        for d in docs:
            results.append(
                {
                    "id": d.id,
                    "title": d.title,
                    "description": d.description or "Document",
                    "category": "Documents",
                    "path": f"/documents/{d.id}",
                    "priority": 8,
                    "last_used": d.updated_at.isoformat() if d.updated_at else None,
                }
            )

        # HACCP Products
        products = (
            db.query(Product)
            .filter((Product.name.ilike(f"%{query}%")) | (Product.product_code.ilike(f"%{query}%")))
            .limit(limit)
            .all()
        )
        for p in products:
            results.append(
                {
                    "id": p.id,
                    "title": p.name,
                    "description": f"HACCP Product - {p.product_type}",
                    "category": "HACCP",
                    "path": f"/haccp/products/{p.id}",
                    "priority": 9,
                }
            )

        # Suppliers
        suppliers = (
            db.query(Supplier)
            .filter((Supplier.name.ilike(f"%{query}%")) | (Supplier.supplier_code.ilike(f"%{query}%")))
            .limit(limit)
            .all()
        )
        for s in suppliers:
            results.append(
                {
                    "id": s.id,
                    "title": s.name,
                    "description": f"Supplier - {s.supplier_type}",
                    "category": "Suppliers",
                    "path": f"/suppliers/{s.id}",
                    "priority": 7,
                }
            )

        results = results[:limit]
        suggestions = [
            {
                "id": "1",
                "text": f"Create new {query}",
                "category": "Quick Actions",
                "action_type": "create",
            }
        ]

        return ResponseModel(success=True, message="Search completed", data={"results": results, "suggestions": suggestions})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/analytics", response_model=ResponseModel)
async def track_search(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # For now, accept payload and return success; extend to persist analytics if needed
        return ResponseModel(success=True, message="Search analytics recorded")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record search analytics: {str(e)}")


