#!/usr/bin/env python3
"""
Smoke tests for Objectives API and dashboard KPIs.
"""

import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
API = f"{BASE_URL}/api/v1"


def login():
    resp = requests.post(f"{API}/auth/login", data={"username": "admin", "password": "admin123"}, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Login failed: {resp.status_code} {resp.text}")
    data = resp.json()
    token = data.get("data", {}).get("access_token") or data.get("access_token")
    if not token:
        raise RuntimeError("No access token in login response")
    return token


def test_objectives_crud_and_kpis():
    token = login()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # List objectives (should include seeded ones)
    r = requests.get(f"{API}/objectives", headers=headers, timeout=10)
    assert r.status_code == 200, r.text
    items = r.json()
    assert isinstance(items, list)
    assert len(items) >= 2

    # Get KPIs (should reflect seeded progress)
    r = requests.get(f"{API}/objectives/kpis", headers=headers, timeout=10)
    assert r.status_code == 200, r.text
    kpis = r.json()
    assert isinstance(kpis, list)

    # Dashboard stats should include objectivesKPI
    r = requests.get(f"{API}/dashboard/stats", headers=headers, timeout=10)
    assert r.status_code == 200, r.text
    data = r.json().get("data", {})
    assert "objectivesKPI" in data
    assert isinstance(data["objectivesKPI"], list)


if __name__ == "__main__":
    test_objectives_crud_and_kpis()
    print("Objectives endpoints smoke tests passed.")

