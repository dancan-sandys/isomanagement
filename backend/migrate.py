#!/usr/bin/env python3
"""
Simple migration script for Digital Ocean deployment
"""
import os
import sys
from alembic.config import Config
from alembic import command

def run_migrations():
    """Run database migrations"""
    try:
        # Get the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create Alembic configuration
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", os.path.join(script_dir, "alembic"))
        alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", ""))
        
        print("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
