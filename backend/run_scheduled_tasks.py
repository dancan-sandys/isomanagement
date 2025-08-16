#!/usr/bin/env python3
"""
CLI script for running scheduled tasks
Usage:
    python run_scheduled_tasks.py --task=maintenance  # Run all maintenance tasks
    python run_scheduled_tasks.py --task=audit_reminders  # Run audit reminders only
    python run_scheduled_tasks.py --task=all  # Run all tasks
"""

import argparse
import logging
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scheduled_tasks import run_scheduled_maintenance, run_audit_reminders
from app.services.email_service import EmailService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Run scheduled tasks for ISO Management System')
    parser.add_argument(
        '--task',
        choices=['maintenance', 'audit_reminders', 'all'],
        default='all',
        help='Which task to run (default: all)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Starting scheduled task: {args.task}")
    
    try:
        if args.task == 'maintenance':
            results = run_scheduled_maintenance()
            logger.info(f"Maintenance tasks completed: {results}")
            
        elif args.task == 'audit_reminders':
            results = run_audit_reminders()
            logger.info(f"Audit reminders completed: {results}")
            
        elif args.task == 'all':
            # Run maintenance tasks
            maintenance_results = run_scheduled_maintenance()
            logger.info(f"Maintenance tasks completed: {maintenance_results}")
            
            # Run audit reminders
            audit_results = run_audit_reminders()
            logger.info(f"Audit reminders completed: {audit_results}")
            
            # Combine results
            results = {
                "maintenance": maintenance_results,
                "audit_reminders": audit_results
            }
        
        logger.info("Scheduled tasks completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error running scheduled tasks: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
