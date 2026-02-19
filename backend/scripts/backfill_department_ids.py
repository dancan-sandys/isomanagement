#!/usr/bin/env python3
"""
Backfill users.department_id from users.department_name by matching departments.name.
Also creates an index on users.department_id if not present.

Usage: python backend/scripts/backfill_department_ids.py
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.departments import Department


def backfill_department_ids() -> None:
    session: Session = SessionLocal()
    try:
        # Build name -> id mapping (case-insensitive)
        departments = session.query(Department.id, Department.name).all()
        name_to_id = { (name or '').strip().lower(): did for (did, name) in departments }

        updated = 0
        users = session.query(User).all()
        for user in users:
            # If user has department_id already, ensure name is synced for legacy display
            if getattr(user, 'department_id', None):
                # Sync name if empty and match exists
                if not getattr(user, 'department_name', None):
                    dep = session.query(Department).filter(Department.id == user.department_id).first()
                    if dep:
                        user.department_name = dep.name
                        updated += 1
                continue
            # If no department_id but a department_name exists, try to map
            dept_name = (getattr(user, 'department_name', None) or getattr(user, 'department', None) or '').strip()
            if dept_name:
                dep_id = name_to_id.get(dept_name.lower())
                if dep_id:
                    user.department_id = dep_id
                    updated += 1

        if updated:
            session.commit()
            print(f"Updated {updated} users with department_id or department_name.")
        else:
            print("No user updates required.")

        # Create index if not exists (SQLite and Postgres compatible IF NOT EXISTS)
        try:
            session.execute(text("CREATE INDEX IF NOT EXISTS ix_users_department_id ON users (department_id)"))
            session.commit()
            print("Ensured index ix_users_department_id exists.")
        except Exception as e:
            print(f"Index creation skipped/failed: {e}")
            session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    backfill_department_ids()

