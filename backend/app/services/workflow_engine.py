from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json

from sqlalchemy.orm import Session

from app.models.production import (
    ProductionProcess, ProcessStage, StageStatus, ProcessStatus,
    StageMonitoringRequirement, MonitoringRequirementType, ProductProcessType
)
from app.models.traceability import Batch


WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / "workflows"


MetricMap: Dict[str, MonitoringRequirementType] = {
    "TEMP": MonitoringRequirementType.TEMPERATURE,
    "HOLD_TIME_SEC": MonitoringRequirementType.TIME,
    "HOLD_TIME_MIN": MonitoringRequirementType.TIME,
    "HOLD_TIME_HR": MonitoringRequirementType.TIME,
    "VOLUME_OUT_KG": MonitoringRequirementType.WEIGHT,
    "PH": MonitoringRequirementType.PH,
    "FLOW": MonitoringRequirementType.PRESSURE,
    "ROOM_TEMP_C": MonitoringRequirementType.TEMPERATURE,
}


class WorkflowEngine:
    def __init__(self, db: Session):
        self.db = db

    def load_workflow(self, product_type: str) -> Dict[str, Any]:
        filename = {
            "fresh_milk": "fresh_milk_workflow.json",
            "yoghurt": "yoghurt_mala_workflow.json",
            "mala": "yoghurt_mala_workflow.json",
            "cheese": "cheese_workflow.json",
        }.get(product_type)
        if not filename:
            raise ValueError(f"Unsupported product_type: {product_type}")
        path = WORKFLOWS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def instantiate_process_from_workflow(
        self,
        batch_id: int,
        product_type: str,
        operator_id: Optional[int],
        initial_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        wf = self.load_workflow(product_type)

        # Create a DRAFT process and stage rows matching workflow order
        process = ProductionProcess(
            batch_id=batch_id,
            process_type=ProductProcessType(product_type),
            operator_id=operator_id,
            spec={"workflow": wf.get("name"), "version": wf.get("version"), "fields": initial_fields or {}},
            status=ProcessStatus.DRAFT,
        )
        self.db.add(process)
        self.db.flush()

        stages_created: List[ProcessStage] = []
        for idx, s in enumerate(wf.get("stages", []), start=1):
            stage = ProcessStage(
                process_id=process.id,
                stage_name=s.get("label") or s["key"],
                stage_description=None,
                sequence_order=idx,
                status=StageStatus.PENDING,
                is_critical_control_point=any(g.get("esign") for g in s.get("gates", [])) if s.get("gates") else False,
                completion_criteria=s.get("conditions"),
                auto_advance=True,
                requires_approval=any(g.get("esign") for g in s.get("gates", [])) if s.get("gates") else False,
            )
            self.db.add(stage)
            self.db.flush()
            stages_created.append(stage)

            # Derive monitoring requirements from conditions where applicable
            for cond in s.get("conditions", []) or []:
                if cond.get("type") in {"min_value", "max_value", "range_value", "min_hold_seconds", "min_hold_minutes", "min_hold_hours", "range_hold_hours", "capture_metric"}:
                    metric = cond.get("metric")
                    if not metric:
                        continue
                    mtype = MetricMap.get(metric)
                    if not mtype:
                        continue
                    req = StageMonitoringRequirement(
                        stage_id=stage.id,
                        requirement_name=cond.get("key") or metric,
                        requirement_type=mtype,
                        is_critical_limit=True if s.get("auto_divert") else False,
                        is_operational_limit=False,
                        target_value=float(cond.get("min") or cond.get("max") or 0) if cond.get("type") != "range_value" else float((cond.get("min") + cond.get("max")) / 2),
                        tolerance_min=float(cond.get("min")) if cond.get("min") is not None else None,
                        tolerance_max=float(cond.get("max")) if cond.get("max") is not None else None,
                        unit_of_measure=self._unit_for_metric(metric),
                        monitoring_frequency=("30_minutes" if (s.get("sampling", {}).get("mode") in {"ONLINE_OR_30MIN", "PERIODIC_30MIN"}) else "per_batch"),
                        is_mandatory=True,
                    )
                    self.db.add(req)

        self.db.commit()

        return {
            "process_id": process.id,
            "stages": [{"id": st.id, "name": st.stage_name, "sequence": st.sequence_order} for st in stages_created],
        }

    def validate_against_workflow(self, process_id: int) -> Dict[str, Any]:
        # Simple dry-run: confirm mandatory monitoring requirements exist for active stage
        stage = (
            self.db.query(ProcessStage)
            .filter(ProcessStage.process_id == process_id)
            .order_by(ProcessStage.sequence_order.asc())
            .first()
        )
        if not stage:
            return {"valid": False, "errors": ["No stages defined"]}
        reqs = self.db.query(StageMonitoringRequirement).filter(StageMonitoringRequirement.stage_id == stage.id).all()
        return {
            "valid": len(reqs) > 0,
            "current_stage": {"id": stage.id, "name": stage.stage_name},
            "requirements": [r.requirement_name for r in reqs],
        }

    def _unit_for_metric(self, metric: str) -> Optional[str]:
        return {
            "TEMP": "C",
            "HOLD_TIME_SEC": "s",
            "HOLD_TIME_MIN": "min",
            "HOLD_TIME_HR": "hr",
            "VOLUME_OUT_KG": "kg",
            "PH": None,
            "FLOW": "lpm",
            "ROOM_TEMP_C": "C",
        }.get(metric)

