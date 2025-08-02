# Specification Grading for SNMP Protocol Implementation

This course uses **specification grading** (or "specs grading"), which means:
- Each assignment component is graded as **satisfactory/unsatisfactory** (pass/fail)
- You must pass **ALL** tests in a bundle to receive credit for that bundle
- Your final grade is determined by which bundles you complete
- No partial credit within bundles - your code either meets the specification or it doesn't

## Grade Bundles

To earn each grade level, you must pass **100% of the tests** in that bundle AND all lower bundles.

### C-Level: Basic SNMP Implementation
**Learning Goal**: Implement a basic SNMP agent and manager that can handle simple GET requests.

You must pass ALL tests in these categories:
- **Protocol Structure** - Correct message format, encoding, and OID handling
- **Basic GET Operations** - Single and multiple OID queries with correct responses
- **Basic Code Quality** - Server starts, accepts connections, and handles basic requests

**What you'll implement**:
- TCP server that listens on port 1161
- Binary protocol encoding/decoding using struct
- GET request processing for single and multiple OIDs
- Basic MIB database lookups

### B-Level: Full GET/SET Implementation  
**Learning Goal**: Add SET operations and comprehensive error handling.

You must ALSO pass ALL tests in:
- **Complete GET Operations** - Handle error cases like non-existent OIDs
- **SET Operations** - Modify values, check permissions, ensure persistence
- **Basic Error Handling** - Return correct error codes and preserve request IDs

**What you'll add**:
- SET request processing with permission checking
- Proper error responses for invalid operations
- State persistence across requests
- Complete GET operation edge cases

### A-Level: Production-Ready Implementation
**Learning Goal**: Handle real-world networking challenges like message fragmentation.

You must ALSO pass ALL tests in:
- **Message Buffering** - Handle messages larger than socket buffer
- **Advanced Error Handling** - Gracefully handle malformed messages and connection errors
- **Complete Code Quality** - All robustness and edge case tests

**What you'll add**:
- Proper message buffering for large responses
- Robust error recovery
- Handling of edge cases and malformed input
- Production-quality code

## Resubmission Policy

- You start with **3 resubmission tokens**
- Each token allows you to resubmit your entire project after receiving feedback
- Use tokens wisely - test thoroughly before submitting!
- Tokens do not carry over between projects

## How to Check Your Progress

Run the test script to see your current grade level:
```bash
python run_tests.py          # See your grade and bundle status
python run_tests.py -v       # See detailed test results by bundle
```

You can also run tests for specific bundles:
```bash
python run_tests.py -m "bundle('C')"   # Run only C-level tests
python run_tests.py -m "bundle('B')"   # Run only B-level tests
python run_tests.py -m "bundle('A')"   # Run only A-level tests
```

## Tips for Success

1. **Start with C-level** - Get basic functionality working before moving up
2. **Test frequently** - Run tests after each feature implementation
3. **Read test descriptions** - Tests document expected behavior
4. **Use the autograder** - Check your progress before submitting
5. **Ask for help** - Office hours are available for debugging

## Common Pitfalls

- **Trying to do everything at once** - Focus on one bundle at a time
- **Not reading error messages** - Test failures explain what's wrong
- **Skipping edge cases** - Every test must pass, including edge cases
- **Poor testing locally** - Always run the full test suite before submitting

Remember: In the real world, software either works correctly or it doesn't. This grading system prepares you for professional software development where "mostly working" isn't acceptable.