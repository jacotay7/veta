#!/usr/bin/env python3
"""
Test runner script for the veta package.
This script runs all tests and generates coverage reports.
"""
import subprocess
import sys
import os

def main():
    """Run tests with coverage reporting"""
    
    # Change to the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    print("🧪 Running veta package tests...")
    print("=" * 50)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=veta",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-report=xml:coverage.xml",
        "-v",
        "--tb=short",
        "tests/"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("\n📊 Coverage reports generated:")
        print("  - HTML report: htmlcov/index.html")
        print("  - XML report: coverage.xml")
        print("  - Terminal output above")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
