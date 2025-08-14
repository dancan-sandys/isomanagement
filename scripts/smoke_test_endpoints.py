#!/usr/bin/env python3
"""
End-to-end API smoke test: logs in and calls representative frontend endpoints.

This script simulates the frontend's API calls to the FastAPI backend to quickly
catch obvious implementation or integration errors. It focuses on safe GET endpoints
and minimal auth flows used broadly across the app.
"""

import sys
import time
from typing import Dict, Tuple, Callable, Optional

import requests


API_BASE = "http://127.0.0.1:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"


def login(username: str, password: str) -> Tuple[Optional[str], Optional[str], Dict]:
    """Perform OAuth2 form login and return (access_token, refresh_token, raw_json)."""
    url = f"{API_BASE}/auth/login"
    try:
        resp = requests.post(
            url,
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        if resp.status_code == 200 and data.get("success"):
            payload = data.get("data") or {}
            return payload.get("access_token"), payload.get("refresh_token"), data
        return None, None, {"status": resp.status_code, "body": data}
    except Exception as exc:
        return None, None, {"error": str(exc)}


def call_get(path: str, token: Optional[str]) -> Tuple[int, str]:
    """Call a GET endpoint with optional bearer token; return (status_code, error_or_empty)."""
    url = f"{API_BASE}{path if path.startswith('/') else '/' + path}"
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.get(url, headers=headers, timeout=15)
        # Consider 200 OK as pass; 401/403 are failures under admin context
        if r.status_code == 200:
            return 200, ""
        return r.status_code, r.text[:500]
    except Exception as exc:
        return 0, str(exc)


def main() -> int:
    start = time.time()
    print("API Smoke Test (frontend -> backend simulation)")
    print("=" * 72)

    # 1) Login to get tokens
    print("\nAuthenticating...")
    access_token, refresh_token, info = login(USERNAME, PASSWORD)
    if not access_token:
        print(f"❌ Login failed: {info}")
        return 1
    print("✅ Login successful; token acquired")

    # 2) Define representative endpoints from frontend services (safe GETs)
    tests: Dict[str, str] = {
        # Auth & User
        "auth.me": "/auth/me",
        "users.list": "/users",
        "users.dashboard": "/users/dashboard",

        # Dashboard
        "dashboard.stats": "/dashboard/stats",
        "dashboard.recent": "/dashboard/recent-activity",
        "dashboard.compliance": "/dashboard/compliance-metrics",
        "dashboard.system-status": "/dashboard/system-status",

        # Documents
        "documents.list": "/documents",
        "documents.stats.overview": "/documents/stats/overview",

        # HACCP
        "haccp.products": "/haccp/products",
        "haccp.dashboard": "/haccp/dashboard",
        "haccp.dashboard.enhanced": "/haccp/dashboard/enhanced",

        # PRP
        "prp.programs": "/prp/programs",
        "prp.dashboard.enhanced": "/prp/dashboard/enhanced",

        # Suppliers
        "suppliers.list": "/suppliers",
        "suppliers.dashboard.stats": "/suppliers/dashboard/stats",

        # Traceability
        "traceability.batches": "/traceability/batches",
        "traceability.dashboard.enhanced": "/traceability/dashboard/enhanced",

        # Notifications
        "notifications.list": "/notifications",
        "notifications.unread": "/notifications/unread",
        "notifications.summary": "/notifications/summary",

        # Settings
        "settings.preferences.me": "/settings/preferences/me",
        "settings.system-info": "/settings/system-info",
        "settings.backup-status": "/settings/backup-status",

        # Audits
        "audits.list": "/audits",
        "audits.stats": "/audits/stats",

        # Risk & Opportunity
        "risk.stats.overview": "/risk/stats/overview",

        # Complaints
        "complaints.list": "/complaints",
        "complaints.trends": "/complaints/reports/trends",

        # Training
        "training.programs": "/training/programs",
        # Training matrix for current user
        "training.matrix.me": "/training/matrix/me",
    }

    failures: Dict[str, Tuple[int, str]] = {}
    for name, path in tests.items():
        status, err = call_get(path, access_token)
        if status == 200:
            print(f"✅ {name}: 200 OK")
        else:
            print(f"❌ {name}: {status} {('- ' + err) if err else ''}")
            failures[name] = (status, err)

    duration_ms = int((time.time() - start) * 1000)
    print("\n" + "-" * 72)
    print(f"Completed in {duration_ms} ms")
    if failures:
        print(f"Failures: {len(failures)}")
        for name, (code, err) in failures.items():
            snippet = (err or "").replace("\n", " ")[:200]
            print(f" - {name}: {code} {snippet}")
        return 2
    print("All tested endpoints returned 200 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())


