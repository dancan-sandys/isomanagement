#!/usr/bin/env python3
"""
Dynamic endpoint tester using the OpenAPI (Swagger) spec.
Discovers all endpoints and tests safe GET routes across modules.
Saves a detailed JSON report with coverage metrics per tag/module.
"""

import requests
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple


BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"
OPENAPI_URL = f"{BASE_URL}/openapi.json"


@dataclass
class EndpointResult:
    method: str
    path: str
    tag: Optional[str]
    tested: bool
    status: str  # PASS/FAIL/SKIPPED
    http_status: Optional[int]
    error: Optional[str]


class OpenAPITester:
    def __init__(self, api_base: str = API_BASE, openapi_url: str = OPENAPI_URL):
        self.api_base = api_base
        self.openapi_url = openapi_url
        self.session = requests.Session()
        self.results: List[EndpointResult] = []
        self.token: Optional[str] = None

    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        try:
            resp = self.session.post(
                f"{self.api_base}/auth/login",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json() or {}
                token = None
                if data.get("success") and data.get("data"):
                    token = data["data"].get("access_token")
                else:
                    token = data.get("access_token")
                if token:
                    self.token = token
                    self.session.headers.update({"Authorization": f"Bearer {token}"})
                    return True
            return False
        except Exception:
            return False

    def fetch_openapi(self) -> Dict:
        resp = self.session.get(self.openapi_url, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _has_path_params(self, path: str) -> bool:
        return "{" in path and "}" in path

    def _fill_path_params(self, path: str) -> Tuple[str, bool]:
        # Very simple heuristic replacements for common ids
        # Returns (filled_path, can_test)
        can_test = True
        filled = path
        try:
            # Replace any {param} by 1 (safe GET should 200 or 404; we prefer to skip unknowns)
            import re
            def repl(m):
                name = m.group(1)
                if name.lower().endswith("_id") or name.lower() in {"id", "user_id", "product_id", "hazard_id", "ccp_id"}:
                    return "1"
                # Unknown param types; mark untestable
                nonlocal can_test
                can_test = False
                return m.group(0)
            filled = re.sub(r"\{([^{}]+)\}", repl, path)
        except Exception:
            can_test = False
        return filled, can_test

    def test_get(self, path: str) -> EndpointResult:
        # Use host base + raw path from OpenAPI to avoid double /api/v1 prefixing
        full_url = f"{BASE_URL}{path}"
        try:
            resp = self.session.get(full_url, timeout=10)
            if resp.status_code == 200:
                return EndpointResult("GET", path, None, True, "PASS", resp.status_code, None)
            return EndpointResult("GET", path, None, True, "FAIL", resp.status_code, resp.text)
        except Exception as e:
            return EndpointResult("GET", path, None, True, "FAIL", None, str(e))

    def run(self) -> Dict:
        # Ensure backend reachable
        try:
            health = self.session.get(f"{BASE_URL}/health", timeout=5)
            health.raise_for_status()
        except Exception as e:
            return {"error": f"Backend not reachable: {e}"}

        if not self.login():
            # Continue without token; many endpoints will 401
            pass

        spec = self.fetch_openapi()
        paths: Dict[str, Dict] = spec.get("paths", {})
        total_discovered = 0
        total_considered = 0
        total_tested = 0

        per_tag: Dict[str, Dict[str, int]] = {}

        for raw_path, methods in paths.items():
            # Limit to API base
            if not raw_path.startswith("/api/v1/"):
                continue
            for method, op in methods.items():
                m = method.upper()
                total_discovered += 1
                tags = op.get("tags") or []
                tag = tags[0] if tags else None
                per_tag.setdefault(tag or "untagged", {"discovered": 0, "considered": 0, "tested": 0, "passed": 0, "failed": 0, "skipped": 0})
                per_tag[tag or "untagged"]["discovered"] += 1

                # For now, only test safe GET endpoints
                if m != "GET":
                    self.results.append(EndpointResult(m, raw_path, tag, False, "SKIPPED", None, "non-GET"))
                    per_tag[tag or "untagged"]["skipped"] += 1
                    continue

                total_considered += 1
                per_tag[tag or "untagged"]["considered"] += 1

                # Skip GETs with unfilled required path params
                if self._has_path_params(raw_path):
                    filled, can_test = self._fill_path_params(raw_path)
                    if not can_test:
                        self.results.append(EndpointResult(m, raw_path, tag, False, "SKIPPED", None, "requires path params"))
                        per_tag[tag or "untagged"]["skipped"] += 1
                        continue
                    res = self.test_get(filled)
                else:
                    res = self.test_get(raw_path)

                # record tag
                res.tag = tag
                self.results.append(res)
                total_tested += 1
                per_tag[tag or "untagged"]["tested"] += 1
                if res.status == "PASS":
                    per_tag[tag or "untagged"]["passed"] += 1
                else:
                    per_tag[tag or "untagged"]["failed"] += 1

        summary = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.api_base,
            "discovered": total_discovered,
            "considered": total_considered,
            "tested": total_tested,
            "per_tag": per_tag,
        }

        # Save detailed results
        filename = f"api_test_results_openapi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump({
                "summary": summary,
                "results": [
                    {
                        "method": r.method,
                        "path": r.path,
                        "tag": r.tag,
                        "tested": r.tested,
                        "status": r.status,
                        "http_status": r.http_status,
                        "error": r.error,
                    }
                    for r in self.results
                ],
            }, f, indent=2)

        return summary


def main() -> None:
    tester = OpenAPITester()
    summary = tester.run()
    print("Dynamic OpenAPI Endpoint Testing")
    print("=" * 72)
    if "error" in summary:
        print(f"❌ {summary['error']}")
        return
    print(f"Discovered: {summary['discovered']}")
    print(f"Considered (GET): {summary['considered']}")
    print(f"Tested: {summary['tested']}")
    # Print quick per-tag stats
    for tag, stats in sorted(summary.get("per_tag", {}).items()):
        print(f"- {tag}: discovered={stats['discovered']} considered={stats['considered']} tested={stats['tested']} passed={stats['passed']} failed={stats['failed']} skipped={stats['skipped']}")


if __name__ == "__main__":
    main()


