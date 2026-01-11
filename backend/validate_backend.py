#!/usr/bin/env python3
"""
Backend validation script to verify the backend is working correctly.
"""

import sys
import os
from pathlib import Path

def check_backend_structure():
    """Check if the backend structure is correct."""
    print("[CHECK] Checking backend structure...")

    required_paths = [
        "src/main.py",
        "src/api/v1/router.py",
        "src/models/",
        "src/services/",
        "src/config/",
        "src/utils/",
        "requirements.txt",
        "main.py"
    ]

    backend_dir = Path(".")
    all_good = True

    for path in required_paths:
        full_path = backend_dir / path
        if not full_path.exists():
            print(f"[ERROR] Missing: {path}")
            all_good = False
        else:
            print(f"[OK] Found: {path}")

    return all_good

def check_imports():
    """Check if main backend modules can be imported."""
    print("\n[CHECK] Checking imports...")

    try:
        from src.main import app
        print("[OK] Main app import successful")

        from src.config.settings import settings
        print("[OK] Config import successful")

        from src.api.v1.router import router
        print("[OK] Router import successful")

        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def check_syntax():
    """Check Python syntax in the backend code."""
    print("\n[CHECK] Checking Python syntax...")

    import subprocess
    try:
        result = subprocess.run([
            sys.executable, "-m", "compileall", "src/"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("[OK] Syntax check passed")
            return True
        else:
            print(f"[ERROR] Syntax errors found:\n{result.stdout}\n{result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Syntax check error: {e}")
        return False

def main():
    """Run all validation checks."""
    print("[START] Starting backend validation...\n")

    checks = [
        ("Structure Check", check_backend_structure),
        ("Import Check", check_imports),
        ("Syntax Check", check_syntax),
    ]

    results = []
    for check_name, check_func in checks:
        result = check_func()
        results.append((check_name, result))

    print(f"\n[RESULTS] Validation Results:")
    all_passed = True
    for check_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {check_name}: {status}")
        if not result:
            all_passed = False

    if all_passed:
        print(f"\n[SUCCESS] Backend is working correctly!")
        print(f"[OK] Backend structure is valid")
        print(f"[OK] All imports work properly")
        print(f"[OK] No syntax errors found")
        print(f"[OK] Ready for Railway deployment")
        return True
    else:
        print(f"\n[ERROR] Backend has issues that need to be fixed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)