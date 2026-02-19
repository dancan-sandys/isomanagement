#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import asyncio
import httpx
from httpx import ASGITransport

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User


def get_auth_headers():
	s = SessionLocal()
	try:
		user = s.query(User).first()
		assert user is not None
		token = create_access_token({"sub": str(user.id)})
		return {"Authorization": f"Bearer {token}"}
	finally:
		s.close()


async def run_baseline(iterations: int = 20):
	transport = ASGITransport(app=app)
	headers = get_auth_headers()
	async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
		# Warmup
		await client.get("/api/v1/objectives-v2/dashboard/summary", headers=headers)
		latencies = []
		for _ in range(iterations):
			start = time.perf_counter()
			resp1 = await client.get("/api/v1/objectives-v2/dashboard/summary", headers=headers)
			resp2 = await client.get("/api/v1/objectives-v2/", headers=headers, follow_redirects=True)
			resp1.raise_for_status(); resp2.raise_for_status()
			latencies.append((time.perf_counter() - start) * 1000)
		print(f"OK {len(latencies)} requests avg={sum(latencies)/len(latencies):.1f}ms p95={sorted(latencies)[int(0.95*len(latencies))-1]:.1f}ms")


if __name__ == "__main__":
	asyncio.run(run_baseline())