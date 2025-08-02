#!/usr/bin/env python3
"""
Script to fix bcrypt installation issues
"""

import subprocess
import sys

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 Fixing bcrypt installation...")
    
    # Step 1: Uninstall existing bcrypt
    print("1. Uninstalling existing bcrypt...")
    success, stdout, stderr = run_command("pip uninstall bcrypt -y")
    if not success:
        print(f"Warning: Could not uninstall bcrypt: {stderr}")
    
    # Step 2: Uninstall passlib
    print("2. Uninstalling passlib...")
    success, stdout, stderr = run_command("pip uninstall passlib -y")
    if not success:
        print(f"Warning: Could not uninstall passlib: {stderr}")
    
    # Step 3: Install bcrypt first
    print("3. Installing bcrypt...")
    success, stdout, stderr = run_command("pip install bcrypt==4.3.0")
    if not success:
        print(f"Error installing bcrypt: {stderr}")
        return False
    
    # Step 4: Install passlib with bcrypt
    print("4. Installing passlib with bcrypt...")
    success, stdout, stderr = run_command("pip install 'passlib[bcrypt]==1.7.4'")
    if not success:
        print(f"Error installing passlib: {stderr}")
        return False
    
    # Step 5: Test bcrypt
    print("5. Testing bcrypt...")
    test_code = """
import bcrypt
password = b"test_password"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print("bcrypt test successful!")
"""
    
    success, stdout, stderr = run_command(f'python -c "{test_code}"')
    if success:
        print("✅ bcrypt installation successful!")
        return True
    else:
        print(f"❌ bcrypt test failed: {stderr}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 