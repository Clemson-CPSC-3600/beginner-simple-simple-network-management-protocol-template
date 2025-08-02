#!/usr/bin/env python3
"""
Test Runner with Specification Grading Support
Runs tests organized by bundles (C, B, A) and reports grade level achieved.

This script:
- If a 'solution' directory exists: Copies solution files to root, runs tests, 
  then restores original files
- If no 'solution' directory: Runs tests with the existing root implementation
- Groups test results by bundle and shows specification grading progress
"""

import os
import sys
import shutil
import subprocess
import argparse
import tempfile
from pathlib import Path
import time
import re
from collections import defaultdict

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'


class BundleTestRunner:
    def __init__(self, verbose=False):
        self.root_dir = Path(__file__).parent.absolute()
        self.solution_dir = self.root_dir / "solution"
        self.backup_dir = None
        self.verbose = verbose
        self.files_to_backup = [
            "snmp_agent.py",
            "snmp_manager.py", 
            "snmp_protocol.py",
            "mib_database.py"
        ]
        
    def create_backup(self):
        """Backup original root files"""
        self.backup_dir = Path(tempfile.mkdtemp(prefix="snmp_backup_"))
        print(f"Creating backup in: {self.backup_dir}")
        
        for filename in self.files_to_backup:
            src = self.root_dir / filename
            if src.exists():
                dst = self.backup_dir / filename
                shutil.copy2(src, dst)
                if self.verbose:
                    print(f"  Backed up: {filename}")
                    
    def copy_solution_files(self):
        """Copy solution files to root"""
        if not self.solution_dir.exists():
            raise RuntimeError(f"Solution directory not found: {self.solution_dir}")
            
        print("Copying solution files to root directory...")
        for filename in self.files_to_backup:
            src = self.solution_dir / filename
            if src.exists():
                dst = self.root_dir / filename
                shutil.copy2(src, dst)
                if self.verbose:
                    print(f"  Copied: {filename}")
            else:
                print(f"  Warning: {filename} not found in solution directory")
                
    def restore_backup(self):
        """Restore original files from backup"""
        if not self.backup_dir:
            return
            
        print("\nRestoring original files...")
        for filename in self.files_to_backup:
            src = self.backup_dir / filename
            if src.exists():
                dst = self.root_dir / filename
                shutil.copy2(src, dst)
                if self.verbose:
                    print(f"  Restored: {filename}")
                    
        # Clean up backup directory
        shutil.rmtree(self.backup_dir)
        print("Backup cleaned up")
    
    def parse_test_output(self, output):
        """Parse pytest output and organize by bundle"""
        bundles = {'C': defaultdict(list), 'B': defaultdict(list), 'A': defaultdict(list)}
        
        # Debug: let's see what we're getting
        if self.verbose:
            print("\nDEBUG: Parsing test output...")
        
        # Remove ANSI escape codes for easier parsing
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_output = ansi_escape.sub('', output)
        
        # Parse the output line by line
        lines = clean_output.split('\n')
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Handle test output that shows through test_autograder.py
            # The tests show as test_autograder.py but with the actual test class names
            if 'test_autograder.py::' in line and ('PASSED' in line or 'FAILED' in line):
                # Extract test class and name
                # Pattern: tests/integration/test_autograder.py::TestClassName::test_method_name PASSED
                match = re.search(r'test_autograder\.py::(\w+)::(\w+)(?:\[.*\])?\s+(PASSED|FAILED)', line)
                if match:
                    test_class = match.group(1)
                    test_name = match.group(2)
                    status = match.group(3)
                    
                    # Map test class to actual file
                    filename = self.get_filename_from_class(test_class)
                    
                    if self.verbose:
                        print(f"  Found test: {test_class}::{test_name} -> {filename} ({status})")
                    
                    # Determine bundle from our mappings
                    bundle = self.get_bundle_for_test(filename, test_class, test_name)
                    
                    bundles[bundle][filename].append({
                        'name': test_name,
                        'class': test_class,
                        'passed': status == 'PASSED'
                    })
            # Also handle direct test file runs (for when not using autograder)
            elif '.py::' in line and ('PASSED' in line or 'FAILED' in line):
                match = re.search(r'(test_\w+\.py)::(\w+)::(\w+)(?:\[.*\])?\s+(PASSED|FAILED)', line)
                if match:
                    filename = match.group(1)
                    test_class = match.group(2)
                    test_name = match.group(3)
                    status = match.group(4)
                    
                    if self.verbose:
                        print(f"  Found test: {filename}::{test_class}::{test_name} ({status})")
                    
                    # Determine bundle from our mappings
                    bundle = self.get_bundle_for_test(filename, test_class, test_name)
                    
                    bundles[bundle][filename].append({
                        'name': test_name,
                        'class': test_class,
                        'passed': status == 'PASSED'
                    })
        
        if self.verbose:
            print("\nDEBUG: Bundle summary:")
            for bundle, files in bundles.items():
                total = sum(len(tests) for tests in files.values())
                if total > 0:
                    print(f"  {bundle}-level: {total} tests")
        
        return bundles
    
    def get_filename_from_class(self, test_class):
        """Map test class names to their file names"""
        # Map test classes to their files
        class_to_file = {
            # Protocol structure tests
            'TestMessageHeaderStructure': 'test_protocol_structure.py',
            'TestMessageSizeCalculation': 'test_protocol_structure.py',
            'TestOIDEncoding': 'test_protocol_structure.py',
            'TestValueTypeEncoding': 'test_protocol_structure.py',
            # Message buffering tests
            'TestSmallMessageReception': 'test_message_buffering.py',
            'TestLargeMessageBuffering': 'test_message_buffering.py',
            'TestBufferingEdgeCases': 'test_message_buffering.py',
            # Get operations tests
            'TestGetOperations': 'test_get_operations.py',
            # Set operations tests
            'TestValidSetOperations': 'test_set_operations.py',
            'TestSetErrorHandling': 'test_set_operations.py',
            # Error handling tests
            'TestBasicErrors': 'test_error_handling.py',
        }
        
        return class_to_file.get(test_class, 'unknown.py')
    
    def get_bundle_for_test(self, filename, class_name, test_name):
        """Determine bundle for a test based on our bundle assignments"""
        # These mappings match what we added to the test files
        bundle_map = {
            'test_protocol_structure.py': 'C',
            'test_message_buffering.py': {
                'TestSmallMessageReception': 'C',
                'TestLargeMessageBuffering': 'A',
                'TestBufferingEdgeCases': 'A',
            },
            'test_get_operations.py': {
                'test_single_oid_get': 'C',
                'test_multiple_oid_get': 'C',
                'test_non_existent_oid': 'B',
                'test_mixed_valid_invalid_oids': 'B',
                'test_empty_oid_list': 'B',
                'test_duplicate_oids': 'B',
            },
            'test_set_operations.py': 'B',
            'test_error_handling.py': {
                'test_error_code_propagation': 'B',
                'test_request_id_preserved_on_error': 'B',
                'test_recovery_after_error': 'A',
            },
        }
        
        if filename in bundle_map:
            mapping = bundle_map[filename]
            if isinstance(mapping, str):
                return mapping
            elif isinstance(mapping, dict):
                # Check by test name first
                if test_name in mapping:
                    return mapping[test_name]
                # Then by class name
                elif class_name in mapping:
                    return mapping[class_name]
        
        # Default to A if not found
        return 'A'
    
    def run_tests_with_json(self, pytest_args):
        """Run pytest and capture JSON output for parsing"""
        cmd = [sys.executable, "-m", "pytest"]
        cmd.append(str(self.root_dir / "tests"))
        
        # Add JSON output
        cmd.extend([
            "--json-report",
            "--json-report-file=test_results.json",
            "-v",
            "--tb=short",
            "--color=yes",
        ])
        
        if pytest_args:
            cmd.extend(pytest_args)
        
        # Run pytest and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Try to load JSON results
        try:
            import json
            with open('test_results.json', 'r') as f:
                json_data = json.load(f)
            os.remove('test_results.json')
            return result.returncode, json_data
        except:
            # Fallback to parsing text output
            return result.returncode, None
    
    def print_bundle_results(self, bundles_data):
        """Print test results organized by bundle"""
        # Calculate bundle completion
        bundle_status = {}
        for bundle in ['C', 'B', 'A']:
            total = 0
            passed = 0
            for file_tests in bundles_data[bundle].values():
                for test in file_tests:
                    total += 1
                    if test['passed']:
                        passed += 1
            bundle_status[bundle] = {
                'total': total,
                'passed': passed,
                'complete': total > 0 and passed == total
            }
        
        # Determine grade
        grade = 'Not Passing'
        grade_color = RED
        if bundle_status['A']['complete'] and bundle_status['B']['complete'] and bundle_status['C']['complete']:
            grade = 'A'
            grade_color = GREEN
        elif bundle_status['B']['complete'] and bundle_status['C']['complete']:
            grade = 'B'
            grade_color = YELLOW
        elif bundle_status['C']['complete']:
            grade = 'C'
            grade_color = BLUE
        
        # Print header
        print("\n" + "=" * 80)
        print(f"{BOLD}SPECIFICATION GRADING RESULTS{RESET}")
        print("=" * 80)
        print(f"\n{BOLD}Grade Level Achieved: {grade_color}{grade}{RESET}\n")
        
        # Print bundle summaries
        bundle_names = {
            'C': 'C-Level (Basic Implementation)',
            'B': 'B-Level (Full GET/SET)',
            'A': 'A-Level (Production Ready)'
        }
        
        for bundle in ['C', 'B', 'A']:
            status = bundle_status[bundle]
            if status['total'] == 0:
                continue
                
            icon = f"{GREEN}✓{RESET}" if status['complete'] else f"{RED}✗{RESET}"
            completion = f"{status['passed']}/{status['total']}"
            
            print(f"{icon} {BOLD}{bundle_names[bundle]}{RESET}: {completion} tests passed")
            
            if not status['complete'] and self.verbose:
                # Show failing tests
                print(f"  {RED}Failed tests:{RESET}")
                for filename, tests in bundles_data[bundle].items():
                    failed = [t for t in tests if not t['passed']]
                    if failed:
                        for test in failed:
                            print(f"    - {filename}::{test['class']}::{test['name']}")
        
        # Print requirements reminder
        print(f"\n{BOLD}Requirements:{RESET}")
        print("- You must pass ALL tests in a bundle to receive credit")
        print("- Higher bundles require completion of all lower bundles")
        
        # Next steps
        print(f"\n{BOLD}Next Steps:{RESET}")
        if not bundle_status['C']['complete']:
            print("→ Focus on C-level tests (basic GET and protocol structure)")
        elif not bundle_status['B']['complete']:
            print("→ Work on B-level tests (SET operations and error handling)")
        elif not bundle_status['A']['complete']:
            print("→ Complete A-level tests (buffering and edge cases)")
        else:
            print(f"{GREEN}→ Congratulations! All bundles complete!{RESET}")
    
    def run_tests_simple(self, pytest_args):
        """Run tests with simple output parsing"""
        cmd = [sys.executable, "-m", "pytest"]
        cmd.append(str(self.root_dir / "tests"))
        cmd.extend(["-v", "--tb=short", "--color=yes"])
        
        if pytest_args:
            cmd.extend(pytest_args)
            
        print(f"\nRunning: {' '.join(cmd)}")
        print("=" * 80)
        
        # Run pytest and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print the pytest output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Parse the output for bundle information
        bundles_data = self.parse_test_output(result.stdout)
        
        # Print bundle-based results
        self.print_bundle_results(bundles_data)
        
        return result.returncode
        
    def run(self, pytest_args):
        """Main execution method"""
        try:
            print("=" * 80)
            print(f"{BOLD}SNMP Protocol Test Runner{RESET}")
            print("=" * 80)
            print(f"Root directory: {self.root_dir}")
            
            # Check if solution directory exists
            if not self.solution_dir.exists():
                print("\n📁 No solution directory found.")
                print("   Running tests with existing root implementation files.")
                
                # Run tests directly without copying
                exit_code = self.run_tests_simple(pytest_args)
                
                return exit_code
                
            # Solution directory exists - proceed with copying
            print(f"Solution directory: {self.solution_dir}")
            print()
            
            # Create backup
            self.create_backup()
            
            # Copy solution files
            self.copy_solution_files()
            
            print("\n⚠️  Note: Running tests with solution files copied to root directory")
            print("   Original files have been backed up and will be restored after tests")
            
            # Wait a moment for file system to settle
            time.sleep(0.5)
            
            # Run tests
            exit_code = self.run_tests_simple(pytest_args)
            
            return exit_code
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            return 2
        except Exception as e:
            print(f"\nError: {e}")
            return 3
        finally:
            # Restore original files if we created a backup
            if self.backup_dir and self.backup_dir.exists():
                self.restore_backup()


def main():
    parser = argparse.ArgumentParser(
        description="Run tests with specification grading support",
        epilog="""
This script runs tests organized by specification grading bundles:
- C-Level: Basic implementation (GET operations, protocol structure)
- B-Level: Full functionality (SET operations, error handling)
- A-Level: Production ready (buffering, edge cases)

You must pass ALL tests in a bundle to receive credit for that grade level.

Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py -v                 # Verbose output
  python run_tests.py -k test_get        # Run specific tests
  python run_tests.py -m "bundle('C')"   # Run only C-level tests
"""
    )
    
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    
    # Collect remaining arguments for pytest
    args, pytest_args = parser.parse_known_args()
    
    runner = BundleTestRunner(verbose=args.verbose)
    return runner.run(pytest_args)


if __name__ == "__main__":
    sys.exit(main())