#!/usr/bin/env python3
"""
Script to fix duplicate routes in FastAPI endpoints by removing duplicates
"""

import os
import re
from pathlib import Path

def fix_duplicate_routes(file_path):
    """Fix duplicate route definitions in a file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all route definitions with line numbers
    route_pattern = r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
    routes = []
    
    for match in re.finditer(route_pattern, content):
        method = match.group(1)
        path = match.group(2)
        start_pos = match.start()
        line_num = content[:start_pos].count('\n') + 1
        routes.append((line_num, method, path, match.group(0)))
    
    # Group by path and method
    path_method_groups = {}
    for line_num, method, path, full_match in routes:
        key = (path, method)
        if key not in path_method_groups:
            path_method_groups[key] = []
        path_method_groups[key].append((line_num, full_match))
    
    # Find duplicates
    duplicates_to_remove = []
    for (path, method), matches in path_method_groups.items():
        if len(matches) > 1:
            # Keep the first occurrence, remove the rest
            for line_num, full_match in matches[1:]:
                duplicates_to_remove.append((line_num, full_match))
    
    if duplicates_to_remove:
        print(f"Found {len(duplicates_to_remove)} duplicate routes in {file_path.name}")
        for line_num, full_match in duplicates_to_remove:
            print(f"  Line {line_num}: {full_match}")
        
        # Remove duplicates (in reverse order to maintain line numbers)
        duplicates_to_remove.sort(key=lambda x: x[0], reverse=True)
        
        for line_num, full_match in duplicates_to_remove:
            # Find the exact line and remove it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if full_match in line:
                    lines.pop(i)
                    break
            
            content = '\n'.join(lines)
        
        # Write back to file
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {len(duplicates_to_remove)} duplicate routes in {file_path.name}")
        return True
    
    return False

def main():
    endpoints_dir = Path("app/api/v1/endpoints")
    
    print("Fixing duplicate routes...")
    print("=" * 50)
    
    fixed_files = []
    for file_path in endpoints_dir.glob("*.py"):
        if fix_duplicate_routes(file_path):
            fixed_files.append(file_path.name)
    
    if fixed_files:
        print(f"\nFixed duplicate routes in {len(fixed_files)} files:")
        for file_name in fixed_files:
            print(f"  - {file_name}")
    else:
        print("\nNo duplicate routes found.")

if __name__ == "__main__":
    main()
