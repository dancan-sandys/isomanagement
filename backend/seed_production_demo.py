from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.models.traceability import Batch, BatchType, BatchStatus
from app.models.production import ProductProcessType, StepType
from app.services.production_service import ProductionService


def seed():
    init_db()
    db: Session = SessionLocal()
    svc = ProductionService(db)

    # Always create a fresh demo batch (avoids legacy enum rows read)
    batch = Batch(
        batch_number=f"BATCH-{datetime.utcnow().strftime('%Y%m%d')}-DEMO",
        batch_type=BatchType.FINAL_PRODUCT,
        status=BatchStatus.IN_PRODUCTION,
        product_name="Pasteurized Milk",
        quantity=1000.0,
        unit="L",
        production_date=datetime.utcnow(),
        created_by=1,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    # Fresh milk HTST spec
    spec = {
        "steps": [
            {"type": StepType.HEAT.value, "target_temp_c": 72.0, "target_time_seconds": 15, "tolerance_c": 0.5},
            {"type": StepType.COOL.value, "target_temp_c": 4.0},
            {"type": StepType.TRANSFER_COLD_ROOM.value},
        ]
    }

    proc = svc.create_process(batch.id, ProductProcessType.FRESH_MILK, operator_id=1, spec=spec)

    # Simulate readings
    now = datetime.utcnow()
    for i in range(20):
        svc.add_log(proc.id, {
            "event": "reading",
            "timestamp": now + timedelta(seconds=i),
            "measured_temp_c": 72.2 if i >= 2 else 70.0,
            "source": "manual"
        })

    # Record yield
    svc.record_yield(proc.id, output_qty=990.0, unit="L", expected_qty=1000.0)
    # Transfer to cold room
    svc.record_transfer(proc.id, quantity=990.0, unit="L", location="Cold Room A", lot_number=batch.lot_number, verified_by=1)

    db.close()


if __name__ == "__main__":
    seed()

