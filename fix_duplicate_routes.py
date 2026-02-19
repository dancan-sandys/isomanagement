#!/usr/bin/env python3
"""
Script to identify and fix duplicate routes in FastAPI endpoints
"""

import os
import re
from pathlib import Path

def find_duplicate_routes(file_path):
    """Find duplicate route definitions in a file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all route definitions
    route_pattern = r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
    routes = re.findall(route_pattern, content)
    
    # Group by path
    path_groups = {}
    for method, path in routes:
        if path not in path_groups:
            path_groups[path] = []
        path_groups[path].append(method)
    
    # Find duplicates
    duplicates = {}
    for path, methods in path_groups.items():
        if len(methods) > 1:
            duplicates[path] = methods
    
    return duplicates

def main():
    endpoints_dir = Path("backend/app/api/v1/endpoints")
    
    print("Scanning for duplicate routes...")
    print("=" * 50)
    
    for file_path in endpoints_dir.glob("*.py"):
        duplicates = find_duplicate_routes(file_path)
        if duplicates:
            print(f"\nFile: {file_path.name}")
            print("-" * 30)
            for path, methods in duplicates.items():
                print(f"  Path: {path}")
                print(f"  Methods: {methods}")
                print()

if __name__ == "__main__":
    main()
