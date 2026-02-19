from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.food_safety_objectives import FoodSafetyObjective, ObjectiveTarget, ObjectiveProgress


class ObjectivesService:
    def __init__(self, db: Session):
        self.db = db

    # CRUD for objectives
    def create_objective(self, data: Dict[str, Any]) -> FoodSafetyObjective:
        objective = FoodSafetyObjective(**data)
        self.db.add(objective)
        self.db.commit()
        self.db.refresh(objective)
        return objective

    def update_objective(self, objective_id: int, updates: Dict[str, Any]) -> Optional[FoodSafetyObjective]:
        obj = self.db.query(FoodSafetyObjective).filter(FoodSafetyObjective.id == objective_id).first()
        if not obj:
            return None
        for k, v in updates.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_objective(self, objective_id: int) -> Optional[FoodSafetyObjective]:
        return self.db.query(FoodSafetyObjective).filter(FoodSafetyObjective.id == objective_id).first()

    def list_objectives(self) -> List[FoodSafetyObjective]:
        return self.db.query(FoodSafetyObjective).all()

    # Targets
    def upsert_target(self, data: Dict[str, Any]) -> ObjectiveTarget:
        existing = self.db.query(ObjectiveTarget).filter(
            ObjectiveTarget.objective_id == data["objective_id"],
            ObjectiveTarget.department_id == data.get("department_id"),
            ObjectiveTarget.period_start == data["period_start"],
        ).first()
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        target = ObjectiveTarget(**data)
        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)
        return target

    def list_targets(self, objective_id: int) -> List[ObjectiveTarget]:
        return self.db.query(ObjectiveTarget).filter(ObjectiveTarget.objective_id == objective_id).all()

    # Progress
    def upsert_progress(self, data: Dict[str, Any]) -> ObjectiveProgress:
        progress = ObjectiveProgress(**data)
        # Compute attainment and status if possible
        self._compute_attainment(progress)
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def list_progress(self, objective_id: int) -> List[ObjectiveProgress]:
        return self.db.query(ObjectiveProgress).filter(ObjectiveProgress.objective_id == objective_id).all()

    # KPIs
    def get_kpis(self, objective_id: Optional[int] = None, department_id: Optional[int] = None,
                 period_start: Optional[datetime] = None, period_end: Optional[datetime] = None) -> List[Dict[str, Any]]:
        query = self.db.query(ObjectiveProgress).join(FoodSafetyObjective, ObjectiveProgress.objective_id == FoodSafetyObjective.id)
        if objective_id:
            query = query.filter(ObjectiveProgress.objective_id == objective_id)
        if department_id:
            query = query.filter(ObjectiveProgress.department_id == department_id)
        if period_start:
            query = query.filter(ObjectiveProgress.period_start >= period_start)
        if period_end:
            query = query.filter(ObjectiveProgress.period_end <= period_end)

        results = []
        for p in query.all():
            results.append({
                "objective_id": p.objective_id,
                "department_id": p.department_id,
                "period_start": p.period_start,
                "period_end": p.period_end,
                "actual_value": p.actual_value,
                "attainment_percent": p.attainment_percent,
                "status": p.status,
            })
        return results

    # Helpers
    def _compute_attainment(self, progress: ObjectiveProgress) -> None:
        # Find matching target
        target = self.db.query(ObjectiveTarget).filter(
            ObjectiveTarget.objective_id == progress.objective_id,
            ObjectiveTarget.department_id == progress.department_id,
            ObjectiveTarget.period_start <= progress.period_start,
            ObjectiveTarget.period_end >= progress.period_end
        ).order_by(ObjectiveTarget.period_start.desc()).first()

        if not target:
            progress.attainment_percent = None
            progress.status = None
            return

        if target.is_lower_better:
            # Lower actual is better; attainment = target/actual * 100 (cap at 100)
            if progress.actual_value <= 0:
                progress.attainment_percent = 100.0
            else:
                progress.attainment_percent = min(100.0, (target.target_value / progress.actual_value) * 100.0)
        else:
            # Higher actual is better; attainment = actual/target * 100 (cap at 120 for visibility)
            if target.target_value == 0:
                progress.attainment_percent = 0.0
            else:
                progress.attainment_percent = (progress.actual_value / target.target_value) * 100.0

        # Determine status using thresholds when available
        status = "on_track"
        if target.is_lower_better:
            # For lower-is-better: compare actual against thresholds
            if target.upper_threshold is not None and progress.actual_value > target.upper_threshold:
                status = "off_track"
            elif target.target_value is not None and progress.actual_value > target.target_value:
                status = "at_risk"
        else:
            # For higher-is-better: compare attainment against thresholds
            if target.lower_threshold is not None and progress.attainment_percent < (target.lower_threshold / max(target.target_value, 1e-6) * 100.0):
                status = "off_track"
            elif target.target_value is not None and progress.attainment_percent < 90.0:
                status = "at_risk"
        progress.status = status

