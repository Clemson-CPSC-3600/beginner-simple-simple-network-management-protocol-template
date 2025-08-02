#!/usr/bin/env python3
"""
Simple test runner for SNMP protocol implementation
Helps students run tests locally before submission
"""

import subprocess
import sys
import os
import argparse
import json
from pathlib import Path


def check_requirements(use_solution=False):
    """Check if required files exist"""
    # Check in parent directory since we're now in tests/
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if use_solution:
        # Check solution directory
        solution_dir = os.path.join(parent_dir, 'solution')
        if not os.path.exists(solution_dir):
            print("❌ Solution directory not found!")
            return False
        required_files = ['snmp_agent.py', 'snmp_manager.py', 'snmp_protocol.py']
        missing = []
        for file in required_files:
            file_path = os.path.join(solution_dir, file)
            if not os.path.exists(file_path):
                missing.append(f"solution/{file}")
    else:
        # Check student files
        required_files = ['snmp_agent.py', 'snmp_manager.py', 'snmp_protocol.py', 'mib_database.py']
        missing = []
        for file in required_files:
            file_path = os.path.join(parent_dir, file)
            if not os.path.exists(file_path):
                missing.append(file)
    
    if missing:
        print("❌ Missing required files:")
        for file in missing:
            print(f"   - {file}")
        return False
    
    location = "solution" if use_solution else "student"
    print(f"✅ All required {location} files found")
    return True


def install_dependencies():
    """Install test dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        req_file = os.path.join(parent_dir, 'requirements.txt')
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_file, '--quiet'], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Try running: pip install -r requirements.txt")
        return False


def run_syntax_check(use_solution=False):
    """Check Python syntax"""
    print("\n🔍 Checking syntax...")
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if use_solution:
        files_to_check = [os.path.join(parent_dir, 'solution', f) for f in ['snmp_agent.py', 'snmp_manager.py', 'snmp_protocol.py']]
    else:
        files_to_check = [os.path.join(parent_dir, f) for f in ['snmp_agent.py', 'snmp_manager.py', 'snmp_protocol.py']]
    
    for file in files_to_check:
        try:
            subprocess.run([sys.executable, '-m', 'py_compile', file], check=True, capture_output=True)
            print(f"✅ {file} - syntax OK")
        except subprocess.CalledProcessError as e:
            print(f"❌ {file} - syntax error")
            print(f"   {e.stderr.decode()}")
            return False
    
    return True


def run_tests(category=None, verbose=False, use_solution=False):
    """Run the test suite"""
    location = "solution" if use_solution else "student"
    print(f"\n🧪 Running tests on {location} code...")
    
    cmd = [sys.executable, '-m', 'pytest', 'integration/test_autograder.py']
    
    if use_solution:
        cmd.append('--solution')
    
    if verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    if category:
        cmd.extend(['-k', category])
    
    cmd.extend([
        '--tb=short',
        '--json-report',
        '--json-report-file=test_results.json',
        '--timeout=300'
    ])
    
    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # Parse and display results
    if os.path.exists('autograder_results.json'):
        try:
            with open('autograder_results.json', 'r') as f:
                results = json.load(f)
            display_results(results)
        except:
            pass
    
    return result.returncode == 0


def display_results(results):
    """Display test results in a friendly format"""
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    score = results.get('total_score', 0)
    total = results.get('total_possible', 100)
    percentage = results.get('percentage', 0)
    
    # Determine grade and emoji
    if percentage >= 90:
        grade, emoji = 'A', '🌟'
    elif percentage >= 80:
        grade, emoji = 'B', '✨'
    elif percentage >= 70:
        grade, emoji = 'C', '👍'
    elif percentage >= 60:
        grade, emoji = 'D', '📝'
    else:
        grade, emoji = 'F', '❌'
    
    print(f"\n{emoji} Total Score: {score:.1f}/{total:.1f} ({percentage:.1f}%)")
    print(f"📑 Letter Grade: {grade}")
    
    if 'categories' in results:
        print("\n📋 Category Breakdown:")
        print("-" * 50)
        for cat, data in results['categories'].items():
            cat_name = cat.replace('_', ' ').title()
            cat_percentage = data['percentage']
            
            # Progress bar
            bar_length = 20
            filled = int(bar_length * cat_percentage / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            print(f"{cat_name:.<30} [{bar}] {data['earned']:.1f}/{data['possible']:.1f}")
    
    print("\n" + "="*60)
    
    # Provide feedback based on score
    if percentage >= 90:
        print("🎉 Excellent work! Your implementation is outstanding!")
    elif percentage >= 80:
        print("👏 Great job! Your implementation is very good.")
    elif percentage >= 70:
        print("👍 Good work! Your implementation meets most requirements.")
    elif percentage >= 60:
        print("📝 Passing grade, but there's room for improvement.")
    else:
        print("❌ Your implementation needs more work. Review the failed tests.")
    
    print("\nRun with --verbose to see detailed test output")


def run_specific_test(test_name, use_solution=False):
    """Run a specific test by name"""
    location = "solution" if use_solution else "student"
    print(f"\n🎯 Running specific test on {location} code: {test_name}")
    
    cmd = [
        sys.executable, '-m', 'pytest', 
        f'integration/test_autograder.py::{test_name}',
        '-v', '--tb=short'
    ]
    
    if use_solution:
        cmd.append('--solution')
    
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description='Run SNMP autograder tests')
    parser.add_argument('--category', '-c', choices=[
        'protocol', 'buffering', 'get', 'set', 'error', 'quality'
    ], help='Run tests for a specific category')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Show detailed test output')
    parser.add_argument('--test', '-t', help='Run a specific test by name')
    parser.add_argument('--install', '-i', action='store_true',
                       help='Install dependencies only')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Quick check: syntax only')
    parser.add_argument('--solution', '-s', action='store_true',
                       help='Test solution files instead of student files')
    
    args = parser.parse_args()
    
    print("🚀 SNMP Protocol Test Runner")
    print("="*60)
    
    if args.solution:
        print("📁 Testing SOLUTION files")
    else:
        print("📁 Testing STUDENT files")
    
    # Check files
    if not check_requirements(args.solution):
        sys.exit(1)
    
    # Install dependencies if requested
    if args.install:
        install_dependencies()
        sys.exit(0)
    
    # Syntax check
    if not run_syntax_check(args.solution):
        print("\n⚠️  Fix syntax errors before running tests")
        sys.exit(1)
    
    if args.quick:
        print("\n✅ Quick check passed!")
        sys.exit(0)
    
    # Try to check if pytest is available by running it
    try:
        result = subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"\n✅ Found pytest: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n⚠️  Warning: Could not verify pytest installation")
        print("   If tests fail, install dependencies with:")
        print(f"   {sys.executable} -m pip install -r requirements.txt")
        print("\n   Attempting to run tests anyway...")
    
    # Run specific test if requested
    if args.test:
        run_specific_test(args.test, args.solution)
    else:
        # Run tests
        success = run_tests(category=args.category, verbose=args.verbose, use_solution=args.solution)
        
        if not success:
            print("\n💡 Tips for debugging:")
            print("   1. Run with --verbose to see detailed output")
            print("   2. Check TESTING.md for common issues")
            print("   3. Run specific categories with --category")
            print("   4. Test your agent manually with: python snmp_agent.py")
            sys.exit(1)
        else:
            print("\n✅ All tests passed! Ready to submit.")


if __name__ == '__main__':
    main()