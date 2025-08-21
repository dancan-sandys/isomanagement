#!/usr/bin/env python3
"""
In-process smoke test for Actions Log flows using TestClient.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db


def main() -> None:
    # Ensure tables exist
    init_db()
    client = TestClient(app)

    # Create interested party with action
    r = client.post('/api/v1/actions/interested-parties', json={
        "stakeholder_name": "Local Regulator",
        "needs_expectations": "Timely compliance reporting",
        "action_to_address": "Establish monthly compliance report",
        "owner_id": 1,
    })
    assert r.status_code == 200, r.text

    # Create SWOT issue with action
    r = client.post('/api/v1/actions/issues/swot', json={
        "issue_type": "weakness",
        "description": "Manual reporting process",
        "required_action": "Automate reporting workflow",
        "owner_id": 1,
    })
    assert r.status_code == 200, r.text

    # Create PESTEL issue with action
    r = client.post('/api/v1/actions/issues/pestel', json={
        "issue_type": "legal",
        "description": "New labeling regulation",
        "required_action": "Update labels to new standard",
        "owner_id": 1,
    })
    assert r.status_code == 200, r.text

    # List actions
    r = client.get('/api/v1/actions/actions-log')
    assert r.status_code == 200, r.text
    actions = r.json()
    assert isinstance(actions, list)
    assert len(actions) >= 3

    print('Actions Log endpoints smoke test passed.')


if __name__ == '__main__':
    main()

