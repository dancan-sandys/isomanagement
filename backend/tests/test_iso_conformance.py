#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.services.objectives_service_enhanced import ObjectivesServiceEnhanced


def test_iso_6_2_fields_and_review_cadence():
	"""Ensure objective includes required ISO 6.2 fields and review cadence is set."""
	db = SessionLocal()
	try:
		service = ObjectivesServiceEnhanced(db)
		obj = service.create_objective({
			"title": "ISO Conformance Objective",
			"description": "Validate ISO 6.2 required fields",
			"target_value": 10.0,
			"measurement_unit": "percentage",
			"measurement_frequency": "monthly",
			"review_frequency": "quarterly",
			"start_date": datetime.utcnow(),
			"created_by": 1,
			"status": "active",
			"owner_user_id": 1,
			"method_of_evaluation": "trend_analysis",
			"acceptance_criteria": "{""threshold"":90}",
			"resource_plan": "Existing staff and dashboard",
			"communication_plan": "Monthly report to QA",
		})
		assert obj.owner_user_id, "Owner is required"
		assert obj.method_of_evaluation, "Method of evaluation required"
		assert obj.acceptance_criteria, "Acceptance criteria required"
		assert obj.review_frequency, "Review frequency required"
		# next_review_date may be computed elsewhere, but ensure field exists
		assert hasattr(obj, 'next_review_date')
	finally:
		db.close()