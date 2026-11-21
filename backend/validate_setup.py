#!/usr/bin/env python3
"""
Setup validation script for AgroScan AI Backend
Checks if all dependencies are installed and model file exists
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor} - FAILED (Need 3.8+)")
        return False


def check_model_file():
    """Check if potatoes.h5 model file exists"""
    print("\n🔍 Checking model file...")
    model_path = Path(__file__).parent.parent / "potatoes.h5"
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"   ✓ Model found at {model_path}")
        print(f"   ✓ Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"   ✗ Model NOT found at {model_path}")
        print(f"   ⓘ Expected location: agriculture/potatoes.h5")
        return False


def check_dependencies():
    """Check if all required packages are installed"""
    print("\n🔍 Checking Python packages...")
    
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'tensorflow': 'tensorflow',
        'PIL': 'Pillow',
        'numpy': 'numpy',
        'multipart': 'python-multipart',
        'dotenv': 'python-dotenv'
    }
    
    all_installed = True
    
    for import_name, pip_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"   ✓ {pip_name} - OK")
        except ImportError:
            print(f"   ✗ {pip_name} - NOT INSTALLED")
            all_installed = False
    
    return all_installed


def check_environment_file():
    """Check if .env file exists"""
    print("\n🔍 Checking configuration...")
    env_path = Path(__file__).parent / ".env"
    
    if env_path.exists():
        print(f"   ✓ .env file found")
        return True
    else:
        print(f"   ⚠ .env file not found (using defaults)")
        return False


def suggest_fixes():
    """Suggest how to fix issues"""
    print("\n" + "="*50)
    print("📋 TO FIX ISSUES:")
    print("="*50)
    print("\n1. Install missing packages:")
    print("   pip install -r requirements.txt")
    print("\n2. Ensure potatoes.h5 is in agriculture/ folder:")
    print("   agriculture/")
    print("   ├── backend/")
    print("   ├── agroscan-ai/")
    print("   └── potatoes.h5  ← Should be here")
    print("\n3. Create .env file (optional):")
    print("   cp .env.example .env  (if available)")
    print("\n4. Run the server:")
    print("   python main.py")


def main():
    """Run all checks"""
    print("\n" + "="*50)
    print("🚀 AgroScan AI Backend - Setup Validator")
    print("="*50 + "\n")
    
    checks = {
        'Python Version': check_python_version,
        'Model File': check_model_file,
        'Dependencies': check_dependencies,
        'Configuration': check_environment_file
    }
    
    results = {}
    for check_name, check_func in checks.items():
        results[check_name] = check_func()
    
    # Summary
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    
    all_passed = all(results.values())
    
    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check_name}: {status}")
    
    if all_passed:
        print("\n✅ All checks passed! Ready to run:")
        print("   python main.py")
        return 0
    else:
        print("\n❌ Some checks failed. See suggestions below.")
        suggest_fixes()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
