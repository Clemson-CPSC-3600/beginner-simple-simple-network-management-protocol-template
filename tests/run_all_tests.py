#!/usr/bin/env python3
"""
Simple test runner to verify the reorganized test structure works correctly
"""

import subprocess
import sys
import os

def run_test_file(test_file):
    """Run a single test file and return results"""
    print(f"\n{'='*60}")
    print(f"Running {test_file}...")
    print('='*60)
    
    cmd = [sys.executable, '-m', 'pytest', test_file, '-v']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def main():
    """Run all test files in the integration directory"""
    test_files = [
        'integration/test_protocol_structure.py',
        'integration/test_message_buffering.py', 
        'integration/test_get_operations.py',
        'integration/test_set_operations.py',
        'integration/test_error_handling.py'
    ]
    
    print("Running all modularized tests...")
    all_passed = True
    
    for test_file in test_files:
        if os.path.exists(test_file):
            passed = run_test_file(test_file)
            if not passed:
                all_passed = False
        else:
            print(f"WARNING: {test_file} not found!")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ All test modules completed successfully!")
    else:
        print("❌ Some test modules failed or were not found")
    print('='*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())