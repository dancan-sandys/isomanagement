#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility to erase all application data from the database (for demo resets).

WARNING: This irreversibly deletes all rows from all application tables.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from sqlalchemy.engine import Connection
from app.core.database import engine


def _sqlite_reset(conn: Connection):
    # Disable foreign key checks for bulk deletes
    conn.execute(text("PRAGMA foreign_keys=OFF"))
    # Collect table names excluding alembic_version
    rows = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"))
    tables = [r[0] for r in rows if r[0] != 'alembic_version']
    for table in tables:
        conn.execute(text(f"DELETE FROM {table}"))
    conn.execute(text("PRAGMA foreign_keys=ON"))


def _generic_reset(conn: Connection):
    # Best-effort generic reset for PostgreSQL or others
    # Disable constraints
    try:
        conn.execute(text("SET session_replication_role = 'replica'"))
    except Exception:
        pass
    # Fetch table list
    tables = []
    try:
        res = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        tables = [r[0] for r in res if r[0] != 'alembic_version']
    except Exception:
        pass
    for table in tables:
        conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    try:
        conn.execute(text("SET session_replication_role = 'origin'"))
    except Exception:
        pass


def wipe_all_data():
    print("⚠️  Wiping all database data...")
    with engine.begin() as conn:
        url = str(getattr(getattr(conn, 'engine', None), 'url', ''))
        if url.startswith('sqlite'):
            _sqlite_reset(conn)
        else:
            _generic_reset(conn)
    print("✅ Database wiped successfully.")


if __name__ == "__main__":
    wipe_all_data()


