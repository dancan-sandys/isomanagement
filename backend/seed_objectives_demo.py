from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.models.food_safety_objectives import FoodSafetyObjective, ObjectiveTarget, ObjectiveProgress


def seed():
    init_db()
    db: Session = SessionLocal()

    # Create sample objectives
    objectives = [
        {
            "objective_code": "OBJ-001",
            "title": "Reduce NC rate",
            "description": "Reduce non-conformances per 1,000 units",
            "category": "Quality",
            "measurement_unit": "NC/1000",
            "frequency": "monthly",
            "responsible_person_id": None,
            "review_frequency": "quarterly",
            "status": "active",
            "created_by": 1,
        },
        {
            "objective_code": "OBJ-002",
            "title": "Increase PRP completion",
            "description": "Monthly PRP completion rate",
            "category": "PRP",
            "measurement_unit": "%",
            "frequency": "monthly",
            "responsible_person_id": None,
            "review_frequency": "quarterly",
            "status": "active",
            "created_by": 1,
        },
    ]

    for obj in objectives:
        existing = db.query(FoodSafetyObjective).filter(FoodSafetyObjective.objective_code == obj["objective_code"]).first()
        if not existing:
            o = FoodSafetyObjective(**obj)
            db.add(o)
    db.commit()

    # Load IDs
    obj1 = db.query(FoodSafetyObjective).filter(FoodSafetyObjective.objective_code == "OBJ-001").first()
    obj2 = db.query(FoodSafetyObjective).filter(FoodSafetyObjective.objective_code == "OBJ-002").first()

    # Targets for current month
    start = datetime(datetime.utcnow().year, datetime.utcnow().month, 1)
    end = start + timedelta(days=30)

    targets = [
        dict(objective_id=obj1.id, department_id=None, period_start=start, period_end=end,
             target_value=2.0, lower_threshold=None, upper_threshold=3.0, weight=1.0, is_lower_better=True, created_by=1),
        dict(objective_id=obj2.id, department_id=None, period_start=start, period_end=end,
             target_value=95.0, lower_threshold=90.0, upper_threshold=None, weight=1.0, is_lower_better=False, created_by=1),
    ]

    for t in targets:
        exists = db.query(ObjectiveTarget).filter(
            ObjectiveTarget.objective_id == t["objective_id"],
            ObjectiveTarget.period_start == t["period_start"],
        ).first()
        if not exists:
            db.add(ObjectiveTarget(**t))
    db.commit()

    # Progress examples
    progresses = [
        dict(objective_id=obj1.id, department_id=None, period_start=start, period_end=end, actual_value=2.5, evidence="NC log", created_by=1),
        dict(objective_id=obj2.id, department_id=None, period_start=start, period_end=end, actual_value=92.0, evidence="PRP dashboard", created_by=1),
    ]

    for p in progresses:
        prog = ObjectiveProgress(**p)
        # Compute simple attainment
        target = db.query(ObjectiveTarget).filter(ObjectiveTarget.objective_id == prog.objective_id).first()
        if target:
            if target.is_lower_better:
                prog.attainment_percent = min(100.0, (target.target_value / prog.actual_value) * 100.0) if prog.actual_value else 100.0
                prog.status = "on_track" if prog.actual_value <= target.target_value else ("at_risk" if (target.upper_threshold and prog.actual_value <= target.upper_threshold) else "off_track")
            else:
                prog.attainment_percent = (prog.actual_value / target.target_value) * 100.0 if target.target_value else 0.0
                prog.status = "on_track" if prog.attainment_percent >= 100.0 else ("at_risk" if prog.attainment_percent >= 90.0 else "off_track")
        db.add(prog)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()

