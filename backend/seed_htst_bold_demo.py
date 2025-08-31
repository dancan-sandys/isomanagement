from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.models.traceability import Batch, BatchType, BatchStatus
from app.services.workflow_engine import WorkflowEngine
from app.services.production_service import ProductionService
from app.services.batch_progression_service import BatchProgressionService, TransitionType
from app.models.production import ProductProcessType, ProcessStage, StageStatus, ProcessLog, LogEvent


def run_demo():
    init_db()
    db: Session = SessionLocal()

    # Create fresh batch
    batch = Batch(
        batch_number=f"DEMO-HTST-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        batch_type=BatchType.FINAL_PRODUCT,
        status=BatchStatus.IN_PRODUCTION,
        product_name="Fresh Milk",
        quantity=1000.0,
        unit="kg",
        production_date=datetime.utcnow(),
        created_by=1,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    # Instantiate workflow into stages
    engine = WorkflowEngine(db)
    inst = engine.instantiate_process_from_workflow(batch.id, "fresh_milk", operator_id=1, initial_fields={"start_qty_kg": 1000.0, "start_temp_c": 6.0})
    process_id = inst["process_id"]

    # Start the process and simulate 10-min HTST with 10s dip
    ps = ProductionService(db)
    ps.start_process(process_id, operator_id=1, start_notes="HTST demo start")

    start_time = datetime.utcnow()
    # 5 minutes steady >=72C
    for i in range(300):
        ps.add_log(process_id, {
            "event": "reading",
            "timestamp": start_time + timedelta(seconds=i),
            "measured_temp_c": 72.5,
            "source": "manual",
        })
    # 10-second dip to 70C (should trigger auto-divert)
    for i in range(300, 310):
        ps.add_log(process_id, {
            "event": "reading",
            "timestamp": start_time + timedelta(seconds=i),
            "measured_temp_c": 70.0,
            "source": "manual",
        })
    # Recover to >=72C for 2 minutes
    for i in range(310, 430):
        ps.add_log(process_id, {
            "event": "reading",
            "timestamp": start_time + timedelta(seconds=i),
            "measured_temp_c": 72.3,
            "source": "manual",
        })

    # Verify auto-divert log exists
    divert_logs = db.query(ProcessLog).filter(ProcessLog.process_id == process_id, ProcessLog.event == LogEvent.DIVERT).all()
    print(f"DIVERT_LOGS: {len(divert_logs)}")

    # Initiate rework on current stage
    active_stage = db.query(ProcessStage).filter(ProcessStage.process_id == process_id, ProcessStage.status == StageStatus.IN_PROGRESS).first()
    if active_stage:
        bps = BatchProgressionService(db)
        bps.request_stage_transition(
            process_id=process_id,
            current_stage_id=active_stage.id,
            user_id=1,
            transition_type=TransitionType.REWORK,
            transition_data={
                "reason": "Auto-divert HTST criteria not met",
                "notes": "Rework pasteurization",
                "rework_reason": "Temperature dip"
            }
        )
        print(f"REWORK_INITIATED_FOR_STAGE: {active_stage.id}")

    # Record yield and transfer
    ps.record_yield(process_id, output_qty=950.0, unit="kg", expected_qty=1000.0)
    ps.record_transfer(process_id, quantity=950.0, unit="kg", location="Cold Room A", lot_number=batch.lot_number, verified_by=1)

    db.close()


if __name__ == "__main__":
    run_demo()

