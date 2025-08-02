# SNMP Protocol Autograder Test Suite

This document describes the automated testing system for the SNMP protocol implementation project.

## Overview

The test suite is designed for GitHub Classroom autograding and provides comprehensive testing of student SNMP implementations. Tests are organized by functionality and aligned with the grading rubric.

## Test Categories and Point Distribution

| Category | Points | Description |
|----------|--------|-------------|
| Protocol Compliance | 25 | Message format, encoding, byte ordering |
| Buffering Implementation | 20 | Handling large messages, proper reassembly |
| Get Operations | 20 | Query functionality with single and multiple OIDs |
| Set Operations | 15 | Configuration changes and persistence |
| Error Handling | 10 | Graceful error recovery |
| Code Quality | 10 | CLI interface, robustness |
| **Total** | **100** | |

## Running Tests Locally

### Basic Test Execution
```bash
# Run all tests
python -m pytest test_autograder.py -v

# Run specific category
python -m pytest test_autograder.py -k "TestMessageHeaderStructure" -v

# Run with detailed output
python -m pytest test_autograder.py -v --tb=short

# Generate test report
python -m pytest test_autograder.py --json-report --json-report-file=results.json
```

### Performance Testing
```bash
# Run with performance monitoring
python -m pytest test_autograder.py -v --durations=10

# Run stress tests
python -m pytest test_autograder.py -k "stress" -v
```

## Test Structure

### Core Protocol Tests (25 points)
- **Message Header Structure** (2.5 points)
  - Validates 4-byte size field
  - Checks request ID placement
  - Verifies PDU type field

- **Byte Ordering** (2.5 points)
  - Ensures big-endian encoding
  - Tests multi-byte integer fields

- **Message Size Calculation** (5 points)
  - Verifies size includes all fields
  - Tests with multiple OIDs

- **OID Encoding** (5 points)
  - String to bytes conversion
  - Bytes to string decoding

- **Value Type Encoding** (10 points)
  - INTEGER: signed 4-byte
  - STRING: UTF-8
  - COUNTER: unsigned 4-byte
  - TIMETICKS: hundredths of seconds

### Buffering Tests (20 points)
- **Small Messages** (5 points)
  - Single recv() messages
  - Exact buffer size

- **Large Messages** (10 points)
  - Multi-recv() handling
  - 5KB+ responses
  - Proper reassembly

- **Edge Cases** (5 points)
  - Consecutive messages
  - Invalid sizes
  - Connection interruption

### Get Tests (20 points)
- **Basic Get** (20 points)
  - Single OID queries
  - Multiple OID queries
  - Non-existent OIDs
  - Empty OID list
  - Duplicate OIDs
  - Uptime updates

### Set Operations Tests (15 points)
- **Valid Sets** (8 points)
  - Writable OIDs
  - Value persistence
  - Type validation

- **Error Cases** (7 points)
  - Read-only OIDs
  - Invalid types
  - Non-existent OIDs

### Error Handling Tests (10 points)
- **Connection Errors** (3 points)
- **Protocol Errors** (4 points)
- **Application Errors** (3 points)

### Code Quality Tests (10 points)
- **Manager CLI** (5 points)
- **Server Robustness** (5 points)

## Common Student Mistakes

1. **Incorrect Byte Order**
   - Using little-endian instead of big-endian
   - Fix: Use `!` prefix in struct.pack/unpack

2. **Incomplete Buffering**
   - Assuming recv() returns complete messages
   - Fix: Loop until message_size bytes received

3. **Size Field Errors**
   - Not including size field itself in total
   - Fix: total_size includes all bytes

4. **String Encoding**
   - Forgetting UTF-8 encoding/decoding
   - Fix: Use .encode('utf-8') and .decode('utf-8')

5. **Socket Reuse**
   - "Address already in use" errors
   - Fix: Set SO_REUSEADDR option

## Debugging Failed Tests

### Enable Detailed Logging
```python
# In student code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use Test Helpers
```python
from test_helpers import format_bytes_hex, compare_messages

# Debug message differences
print(compare_messages(expected, actual))
```

### Run Individual Tests
```bash
# Run single test method
python -m pytest test_autograder.py::TestMessageHeaderStructure::test_header_size_field -v
```

### Check Network Traffic
```bash
# Monitor SNMP traffic
sudo tcpdump -i lo -n port 1161 -X
```

## GitHub Classroom Setup

1. **Import starter code** to GitHub Classroom
2. **Enable autograding** in assignment settings
3. **Configure test command**:
   ```
   python -m pytest test_autograder.py --json-report
   ```
4. **Set passing threshold** (e.g., 60%)
5. **Configure feedback** visibility

## Customizing Tests

### Adjust Point Values
Edit the `@pytest.mark.points()` decorators:
```python
@pytest.mark.points(5)  # Change point value
class TestExample:
    pass
```

### Add New Tests
```python
@pytest.mark.points(2)
@pytest.mark.category('protocol_compliance')
class TestNewFeature:
    def test_something(self, create_test_agent):
        # Test implementation
        pass
```

### Modify Timeouts
```python
@pytest.mark.timeout(60)  # 60 second timeout
def test_long_running():
    pass
```

## Grading Reports

The autograder generates several output files:

- `autograder_results.json` - Detailed results with scores
- `test_results.xml` - JUnit format for CI integration
- `test_results.json` - pytest-json-report format

### Sample Report Structure
```json
{
  "total_score": 85.5,
  "total_possible": 100,
  "percentage": 85.5,
  "categories": {
    "protocol_compliance": {
      "earned": 23.0,
      "possible": 25.0,
      "percentage": 92.0
    },
    ...
  }
}
```

## Troubleshooting

### Tests Hanging
- Add timeouts to all tests
- Check for infinite loops in buffering
- Verify socket cleanup

### Port Conflicts
- Tests use dynamic port allocation
- Check for zombie processes
- Use `lsof -i :1161` to find conflicts

### Platform Issues
- Tests work on Linux/Mac/Windows
- Some features may need platform checks
- Use GitHub Actions for consistent environment

## Contact

For questions or issues with the test suite:
- Check existing GitHub issues
- Contact course instructor
- Review test source code for details