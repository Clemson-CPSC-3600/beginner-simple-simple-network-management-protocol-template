# SNMP Protocol Tests

This directory contains the organized test suite for the SNMP protocol implementation.

## Directory Structure

```
tests/
├── integration/           # Integration tests
│   ├── common.py         # Shared test utilities and constants
│   ├── test_protocol_structure.py    # Message format and encoding tests
│   ├── test_message_buffering.py     # Message reception and buffering tests
│   ├── test_get_operations.py        # GET operation tests
│   ├── test_set_operations.py        # SET operation and permission tests
│   ├── test_error_handling.py        # Error handling and edge case tests
│   ├── test_integration.py           # CLI and server robustness tests
│   └── test_autograder.py           # Main autograder entry point
├── unit/                 # Unit tests (placeholder for future use)
├── helpers/              # Test helper modules
│   └── test_helpers.py   # Additional test utilities
├── fixtures/             # Test fixtures (placeholder for future use)
├── conftest.py          # Pytest configuration
├── run_tests.py         # Main test runner with student-friendly output
└── run_all_tests.py     # Simple script to run all test modules

```

## Running Tests

### Run all tests with detailed output:
```bash
cd tests
python run_tests.py
```

### Test solution files (for instructors):
```bash
# From project root:
python test_solution.py

# Or from tests directory:
cd tests
python run_tests.py --solution

# Or using environment variable:
SNMP_TEST_SOLUTION=true pytest integration/test_autograder.py
```

### Run a specific test module:
```bash
python -m pytest integration/test_get_operations.py -v
```

### Run tests matching a pattern:
```bash
python -m pytest -k "test_get" -v
```

### Run with autograder (for GitHub Classroom):
```bash
python -m pytest integration/test_autograder.py
```

## Test Categories

1. **Protocol Structure Tests** (`test_protocol_structure.py`)
   - Message header format validation
   - Byte ordering (network byte order)
   - OID encoding/decoding
   - Value type encoding

2. **Message Buffering Tests** (`test_message_buffering.py`)
   - Small message handling
   - Large message buffering
   - Consecutive message processing
   - Edge cases (partial messages, invalid sizes)

3. **GET Operations Tests** (`test_get_operations.py`)
   - Single and multiple OID retrieval
   - Non-existent OID handling
   - System uptime testing

4. **SET Operations Tests** (`test_set_operations.py`)
   - Setting different value types
   - Permission checking (read-only vs read-write)
   - Value persistence
   - Error handling for invalid operations

5. **Error Handling Tests** (`test_error_handling.py`)
   - Connection errors
   - Protocol violations
   - Malformed messages
   - Error code propagation

6. **Integration Tests** (`test_integration.py`)
   - Command-line interface testing
   - Server startup/shutdown
   - Concurrent connections
   - Overall system robustness

## Adding New Tests

To add new tests:

1. Choose the appropriate test file based on what you're testing
2. Add your test class/function following the existing patterns
3. Use the utilities from `common.py` for consistency
4. Run your specific test file to verify it works
5. Run the full test suite to ensure no regressions

## Test Utilities

The `common.py` module provides:
- Protocol constants (PDU types, error codes, etc.)
- Message creation functions (GET, SET requests)
- Message parsing functions
- Network utilities (port finding, agent management)
- Pytest fixtures for test agent creation

## Solution Testing (For Instructors)

The test framework supports testing solution files kept in a `/solution` directory (not tracked in git):

1. **Directory Structure:**
   ```
   solution/
   ├── snmp_agent.py
   ├── snmp_manager.py
   └── snmp_protocol.py
   ```

2. **Running Solution Tests:**
   - Use `--solution` flag: `python run_tests.py --solution`
   - Use environment variable: `SNMP_TEST_SOLUTION=true pytest`
   - Use convenience script: `python test_solution.py`

3. **How It Works:**
   - When solution mode is enabled, tests use files from `/solution/` instead of root
   - The `/solution/` directory should NOT be committed to git
   - Tests will indicate they're testing solution files in the output
   - PYTHONPATH is automatically configured so that imports (e.g., `from snmp_protocol import ...`) work correctly within solution files

This allows instructors to maintain and test their solution code separately from student templates.