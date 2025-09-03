#!/usr/bin/env python3
"""
Test script to check if the actions_log_service module can be imported correctly
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.services.actions_log_service import ActionsLogService
    print("✅ Successfully imported ActionsLogService")
    
    # Try to access the PESTELAnalysis model
    from app.models.actions_log import PESTELAnalysis
    print("✅ Successfully imported PESTELAnalysis model")
    
    # Check what attributes PESTELAnalysis has
    print(f"PESTELAnalysis attributes: {[attr for attr in dir(PESTELAnalysis) if not attr.startswith('_')]}")
    
    # Check if status attribute exists
    if hasattr(PESTELAnalysis, 'status'):
        print("✅ PESTELAnalysis has 'status' attribute")
    else:
        print("❌ PESTELAnalysis does NOT have 'status' attribute")
    
    # Check if is_active attribute exists
    if hasattr(PESTELAnalysis, 'is_active'):
        print("❌ PESTELAnalysis still has 'is_active' attribute")
    else:
        print("✅ PESTELAnalysis does NOT have 'is_active' attribute")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()

