#!/usr/bin/env python3
"""
In-process smoke tests for Production endpoints using FastAPI TestClient.
This avoids external server requirements and seeds a demo batch directly.
"""

from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal, init_db
from app.models.traceability import Batch, BatchType, BatchStatus


def seed_batch() -> int:
    init_db()
    db = SessionLocal()
    try:
        batch = Batch(
            batch_number=f"BATCH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-SMOKE",
            batch_type=BatchType.FINAL_PRODUCT,
            status=BatchStatus.IN_PRODUCTION,
            product_name="Pasteurized Milk",
            quantity=500.0,
            unit="L",
            production_date=datetime.utcnow(),
            created_by=1,
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        return batch.id
    finally:
        db.close()


def main() -> None:
    client = TestClient(app)
    batch_id = seed_batch()

    # Create process
    spec = {
        "steps": [
            {"type": "heat", "target_temp_c": 72.0, "target_time_seconds": 15, "tolerance_c": 0.5},
            {"type": "cool", "target_temp_c": 4.0},
            {"type": "transfer_cold_room"},
        ]
    }
    resp = client.post("/api/v1/production/process", json={
        "batch_id": batch_id,
        "process_type": "fresh_milk",
        "operator_id": 1,
        "spec": spec,
    })
    assert resp.status_code == 200, resp.text
    process = resp.json()
    process_id = process["id"]

    # Add logs: simulate 20 seconds at 72.2C (should be on track, no diversion),
    # then a reading that may cause diversion to be logged by validation if insufficient.
    now = datetime.utcnow()
    for i in range(20):
        r = client.post(f"/api/v1/production/{process_id}/log", json={
            "event": "reading",
            "timestamp": (now + timedelta(seconds=i)).isoformat(),
            "measured_temp_c": 72.2,
        })
        assert r.status_code == 200, r.text

    # Record yield
    r = client.post(f"/api/v1/production/{process_id}/yield", json={
        "output_qty": 495.0,
        "expected_qty": 500.0,
        "unit": "L",
    })
    assert r.status_code == 200, r.text
    yr = r.json()
    assert yr["overrun_percent"] == ((495.0 - 500.0) / 500.0) * 100

    # Analytics
    r = client.get("/api/v1/production/analytics")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "total_records" in data

    print("Production endpoints smoke test passed.")


if __name__ == "__main__":
    main()

