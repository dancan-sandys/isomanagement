#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
import pytest
import httpx
from httpx import ASGITransport

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.rbac import Permission, PermissionType, Module, UserPermission


transport = ASGITransport(app=app)


@pytest.fixture
def anyio_backend():
	return 'asyncio'


def _auth_headers(db):
	user = db.query(User).first()
	assert user is not None, "No user"
	token = create_access_token({"sub": str(user.id)})
	return {"Authorization": f"Bearer {token}"}


def _ensure_objectives_permissions(db, user_id: int):
	needed = [
		(Module.OBJECTIVES, PermissionType.CREATE),
		(Module.OBJECTIVES, PermissionType.UPDATE),
		(Module.OBJECTIVES, PermissionType.VIEW),
		(Module.OBJECTIVES, PermissionType.APPROVE),
		(Module.OBJECTIVES, PermissionType.ASSIGN),
	]
	for module, action in needed:
		perm = db.query(Permission).filter(Permission.module == module, Permission.action == action).first()
		if not perm:
			perm = Permission(module=module, action=action, description=f"Test perm {module.value}:{action.value}")
			db.add(perm)
			db.commit(); db.refresh(perm)
		link = db.query(UserPermission).filter(UserPermission.user_id == user_id, UserPermission.permission_id == perm.id).first()
		if not link:
			db.add(UserPermission(user_id=user_id, permission_id=perm.id, granted=True))
			db.commit()


@pytest.mark.anyio("asyncio")
async def test_workflow_endpoints_happy_path():
	db = SessionLocal()
	try:
		user = db.query(User).first(); assert user is not None
		_ensure_objectives_permissions(db, user.id)
		h = _auth_headers(db)
		async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
			# Create objective
			payload = {
				"title": "API Workflow Objective",
				"description": "API flow",
				"target_value": 5,
				"measurement_unit": "percentage",
				"measurement_frequency": "monthly",
				"start_date": datetime.utcnow().isoformat(),
			}
			res = await client.post("/api/v1/objectives-v2/", json=payload, headers=h)
			assert res.status_code in (200, 201), res.text
			obj = res.json()
			obj_id = obj["id"] if isinstance(obj, dict) else obj.get("id")
			assert obj_id

			# Assign
			res = await client.post(f"/api/v1/objectives-v2/{obj_id}/assign", params={"owner_user_id": user.id}, headers=h)
			assert res.status_code == 200, res.text

			# Submit
			res = await client.post(f"/api/v1/objectives-v2/{obj_id}/submit", params={"notes": "please approve"}, headers=h)
			assert res.status_code == 200, res.text
			assert res.json()["approval_status"] == "pending"

			# Approve
			res = await client.post(f"/api/v1/objectives-v2/{obj_id}/approve", params={"notes": "ok"}, headers=h)
			assert res.status_code == 200, res.text
			assert res.json()["approval_status"] == "approved"

			# Close
			res = await client.post(f"/api/v1/objectives-v2/{obj_id}/close", params={"reason": "done"}, headers=h)
			assert res.status_code == 200, res.text
			assert res.json()["approval_status"] == "closed"
	finally:
		db.close()