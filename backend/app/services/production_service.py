from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.production import (
    ProductionProcess, ProcessStep, ProcessLog, YieldRecord, ColdRoomTransfer, AgingRecord,
    ProductProcessType, ProcessStatus, StepType, LogEvent
)
from app.models.traceability import Batch, BatchStatus, BatchType


class ProductionService:
    def __init__(self, db: Session):
        self.db = db

    def create_process(self, batch_id: int, process_type: ProductProcessType, operator_id: Optional[int], spec: Dict[str, Any]) -> ProductionProcess:
        batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        process = ProductionProcess(
            batch_id=batch_id,
            process_type=process_type,
            operator_id=operator_id,
            spec=spec,
            status=ProcessStatus.IN_PROGRESS,
        )
        self.db.add(process)
        # Create steps from spec
        for seq, step in enumerate(spec.get("steps", []), start=1):
            ps = ProcessStep(
                process=process,
                step_type=StepType(step["type"]),
                sequence=seq,
                target_temp_c=step.get("target_temp_c"),
                target_time_seconds=step.get("target_time_seconds"),
                tolerance_c=step.get("tolerance_c"),
                required=step.get("required", True),
                step_metadata=step.get("metadata"),
            )
            self.db.add(ps)
        self.db.commit()
        self.db.refresh(process)
        return process

    def add_log(self, process_id: int, data: Dict[str, Any]) -> ProcessLog:
        process = self.db.query(ProductionProcess).filter(ProductionProcess.id == process_id).first()
        if not process:
            raise ValueError("Process not found")
        log = ProcessLog(
            process_id=process_id,
            step_id=data.get("step_id"),
            timestamp=data.get("timestamp") or datetime.utcnow(),
            event=LogEvent(data.get("event")),
            measured_temp_c=data.get("measured_temp_c"),
            note=data.get("note"),
            auto_flag=data.get("auto_flag", False),
            source=data.get("source", "manual"),
        )
        self.db.add(log)
        # Validate critical steps (e.g., HTST 72C for 15 sec)
        self._evaluate_diversion(process, log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def record_yield(self, process_id: int, output_qty: float, unit: str, expected_qty: Optional[float] = None) -> YieldRecord:
        yr = YieldRecord(
            process_id=process_id,
            output_qty=output_qty,
            expected_qty=expected_qty,
            unit=unit,
        )
        if expected_qty and expected_qty != 0:
            yr.overrun_percent = ((output_qty - expected_qty) / expected_qty) * 100.0
        self.db.add(yr)
        self.db.commit()
        self.db.refresh(yr)
        return yr

    def record_transfer(self, process_id: int, quantity: float, unit: str, location: Optional[str], lot_number: Optional[str], verified_by: Optional[int]) -> ColdRoomTransfer:
        transfer = ColdRoomTransfer(
            process_id=process_id,
            quantity=quantity,
            unit=unit,
            location=location,
            lot_number=lot_number,
            verified_by=verified_by,
        )
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        return transfer

    def record_aging(self, process_id: int, data: Dict[str, Any]) -> AgingRecord:
        ar = AgingRecord(
            process_id=process_id,
            start_time=data.get("start_time") or datetime.utcnow(),
            end_time=data.get("end_time"),
            room_temperature_c=data.get("room_temperature_c"),
            target_temp_min_c=data.get("target_temp_min_c"),
            target_temp_max_c=data.get("target_temp_max_c"),
            target_days=data.get("target_days"),
            room_location=data.get("room_location"),
            notes=data.get("notes"),
        )
        self.db.add(ar)
        self.db.commit()
        self.db.refresh(ar)
        return ar

    def get_process(self, process_id: int) -> Optional[ProductionProcess]:
        return self.db.query(ProductionProcess).filter(ProductionProcess.id == process_id).first()

    def get_analytics(self, product_type: Optional[ProductProcessType] = None) -> Dict[str, Any]:
        query = self.db.query(YieldRecord)
        if product_type:
            query = query.join(ProductionProcess, ProductionProcess.id == YieldRecord.process_id).filter(ProductionProcess.process_type == product_type)
        yields = query.all()
        total = len(yields)
        overruns = [y for y in yields if (y.overrun_percent or 0) > 0]
        underruns = [y for y in yields if (y.overrun_percent or 0) < 0]
        avg_overrun = sum((y.overrun_percent or 0) for y in yields) / total if total else 0.0
        return {
            "total_records": total,
            "avg_overrun_percent": round(avg_overrun, 2),
            "overruns": len(overruns),
            "underruns": len(underruns),
        }

    # Internal validation
    def _evaluate_diversion(self, process: ProductionProcess, log: ProcessLog) -> None:
        # Applies for Fresh milk HTST: >=72C for 15s; otherwise mark diverted
        try:
            if process.process_type == ProductProcessType.FRESH_MILK:
                # Consider last 20 seconds readings
                window_start = log.timestamp - timedelta(seconds=20)
                logs = self.db.query(ProcessLog).filter(
                    ProcessLog.process_id == process.id,
                    ProcessLog.timestamp >= window_start
                ).order_by(ProcessLog.timestamp.asc()).all()
                # Count consecutive seconds above 72C
                above = 0
                for l in logs:
                    if (l.measured_temp_c or 0) >= 72.0:
                        above += 1
                    else:
                        above = 0
                if above < 15 and any(l.event == LogEvent.READING for l in logs):
                    # Automatically divert
                    divert = ProcessLog(
                        process_id=process.id,
                        step_id=log.step_id,
                        timestamp=datetime.utcnow(),
                        event=LogEvent.DIVERT,
                        measured_temp_c=log.measured_temp_c,
                        note="Auto-divert: HTST criteria not met",
                        auto_flag=True,
                        source="auto",
                    )
                    process.status = ProcessStatus.DIVERTED
                    self.db.add(divert)
        except Exception:
            # Do not block logging on validation errors
            pass

