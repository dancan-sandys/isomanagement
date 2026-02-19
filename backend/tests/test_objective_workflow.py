#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.services.objectives_service_enhanced import ObjectivesServiceEnhanced
from app.models.user import User


def test_objective_workflow_transitions():
	"""Validate workflow transitions: assign -> submit -> approve -> close"""
	db = SessionLocal()
	try:
		service = ObjectivesServiceEnhanced(db)
		# Pick an existing active user
		user = db.query(User).first()
		assert user is not None, "No user found for testing"

		# Create objective
		obj = service.create_objective({
			"title": "Workflow Test Objective",
			"description": "Ensure workflow transitions operate correctly",
			"target_value": 100.0,
			"measurement_unit": "percentage",
			"measurement_frequency": "monthly",
			"start_date": datetime.utcnow(),
			"created_by": user.id,
			"status": "active"
		})
		assert obj is not None
		assert obj.approval_status in (None, 'draft', ''), f"Unexpected initial status: {obj.approval_status}"

		# Assign owner
		obj = service.assign_owner(obj.id, user.id)
		assert obj.owner_user_id == user.id

		# Submit for approval
		obj = service.submit_for_approval(obj.id, user.id, "Ready for approval")
		assert obj.approval_status == 'pending'
		assert obj.submitted_by_id == user.id
		assert obj.submitted_at is not None

		# Approve
		obj = service.approve(obj.id, user.id, "Approved")
		assert obj.approval_status == 'approved'
		assert obj.approved_by_id == user.id
		assert obj.approved_at is not None

		# Close
		obj = service.close(obj.id, user.id, "Completed work")
		assert obj.approval_status == 'closed'
		assert obj.closed_by_id == user.id
		assert obj.closed_at is not None
	finally:
		db.close()