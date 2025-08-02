#!/usr/bin/env python3
"""
Script to fix bcrypt compatibility issues on deployment.
This script ensures the correct versions of bcrypt and passlib are installed.
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def fix_bcrypt_issue():
    """Fix bcrypt compatibility issues"""
    print("🔧 Fixing bcrypt compatibility issues...")
    
    # Check current bcrypt version
    bcrypt_version = run_command("pip show bcrypt")
    if bcrypt_version:
        print(f"Current bcrypt: {bcrypt_version.split('Version: ')[1].split()[0] if 'Version: ' in bcrypt_version else 'Unknown'}")
    
    # Uninstall current bcrypt and passlib
    print("🗑️ Uninstalling current bcrypt and passlib...")
    run_command("pip uninstall -y bcrypt passlib")
    
    # Install compatible versions
    print("📥 Installing compatible versions...")
    run_command("pip install bcrypt==4.3.0")
    run_command("pip install passlib[bcrypt]==1.7.4")
    
    # Verify installation
    print("✅ Verifying installation...")
    bcrypt_version = run_command("pip show bcrypt")
    passlib_version = run_command("pip show passlib")
    
    if bcrypt_version and passlib_version:
        print("✅ bcrypt and passlib installed successfully!")
        print(f"bcrypt: {bcrypt_version.split('Version: ')[1].split()[0] if 'Version: ' in bcrypt_version else 'Unknown'}")
        print(f"passlib: {passlib_version.split('Version: ')[1].split()[0] if 'Version: ' in passlib_version else 'Unknown'}")
    else:
        print("❌ Installation verification failed!")

if __name__ == "__main__":
    print("🚀 ISO 22000 FSMS - bcrypt Fix Script")
    print("=" * 50)
    fix_bcrypt_issue()
    print("=" * 50)
    print("✅ Fix completed! You can now restart your server.") 