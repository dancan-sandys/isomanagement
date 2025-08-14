from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
import sys

from app.core.database import get_db
from app.core.config import settings
from app.core.security import require_permission


router = APIRouter()


def _import_seed_modules():
    try:
        from reset_database import wipe_all_data  # type: ignore
    except Exception:
        # Ensure project root on path
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
        from reset_database import wipe_all_data  # type: ignore

    try:
        from init_database import init_database  # type: ignore
    except Exception:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
        from init_database import init_database  # type: ignore

    try:
        from create_rbac_seed_data import create_permissions, create_default_roles  # type: ignore
    except Exception:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
        from create_rbac_seed_data import create_permissions, create_default_roles  # type: ignore

    try:
        from create_demo_data_engineering import main as seed_engineering  # type: ignore
    except Exception:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
        from create_demo_data_engineering import main as seed_engineering  # type: ignore

    return wipe_all_data, init_database, create_permissions, create_default_roles, seed_engineering


@router.post("/reset", dependencies=[Depends(require_permission(("SETTINGS", "UPDATE")))])
def reset_database_endpoint(db: Session = Depends(get_db)):
    if settings.ENVIRONMENT not in ("development", "staging"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed in this environment")

    wipe_all_data, init_database, _, _, _ = _import_seed_modules()
    try:
        wipe_all_data()
        init_database()
        return {"status": "ok", "message": "Database reset and re-initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {e}")


@router.post("/seed/engineering", dependencies=[Depends(require_permission(("SETTINGS", "UPDATE")))])
def seed_engineering_demo_endpoint(db: Session = Depends(get_db)):
    if settings.ENVIRONMENT not in ("development", "staging"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed in this environment")

    wipe_all_data, init_database, create_permissions, create_default_roles, seed_engineering = _import_seed_modules()

    try:
        # Full reset and seed
        wipe_all_data()
        init_database()
        create_permissions()
        create_default_roles()
        seed_engineering()
        return {"status": "ok", "message": "Engineering demo data loaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {e}")


