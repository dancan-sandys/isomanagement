#!/usr/bin/env python3
"""
Script to fix traceability endpoint enum handling issues.
This script updates the traceability endpoints to handle enum values properly.
"""

import os
import shutil
from datetime import datetime

def backup_file():
    """Create a backup of the traceability endpoints file"""
    source_file = "app/api/v1/endpoints/traceability.py"
    backup_name = f"traceability_endpoints_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(source_file):
        shutil.copy2(source_file, backup_name)
        print(f"Backup created: {backup_name}")
        return backup_name
    else:
        print(f"Source file not found: {source_file}")
        return None

def fix_enum_handling():
    """Fix the enum handling in traceability endpoints"""
    file_path = "app/api/v1/endpoints/traceability.py"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the enum handling in the list_recalls endpoint
    # Replace r.recall_type.value with str(r.recall_type)
    # Replace r.status.value with str(r.status)
    
    # Find and replace the problematic lines
    old_content = """                "recall_type": r.recall_type.value,
                "status": r.status.value,"""
    
    new_content = """                "recall_type": str(r.recall_type),
                "status": str(r.status),"""
    
    if old_content in content:
        content = content.replace(old_content, new_content)
        print("Fixed recall_type and status enum handling in list_recalls endpoint")
    else:
        print("Could not find the exact pattern to replace")
        return False
    
    # Also fix the get_recall endpoint
    old_content2 = """                "recall_type": recall.recall_type.value,
                "status": recall.status.value,"""
    
    new_content2 = """                "recall_type": str(recall.recall_type),
                "status": str(recall.status),"""
    
    if old_content2 in content:
        content = content.replace(old_content2, new_content2)
        print("Fixed recall_type and status enum handling in get_recall endpoint")
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Traceability endpoints file updated successfully")
    return True

def main():
    """Main function"""
    print("Fixing Traceability Endpoint Enum Handling...")
    print("=" * 50)
    
    # Backup the file
    backup_file_path = backup_file()
    if not backup_file_path:
        return False
    
    # Fix the enum handling
    if not fix_enum_handling():
        return False
    
    print("\nEnum handling fixes completed!")
    print(f"Backup saved as: {backup_file_path}")
    print("\nNext steps:")
    print("1. Restart the backend server")
    print("2. Test traceability endpoints")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
