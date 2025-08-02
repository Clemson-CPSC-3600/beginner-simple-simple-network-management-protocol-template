#!/usr/bin/env python3
"""
SNMP Protocol Autograder Test Suite
For GitHub Classroom automatic grading

This file now imports and runs all the modularized test files.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import all test modules
from .test_protocol_structure import *
from .test_message_buffering import *
from .test_get_operations import *
from .test_set_operations import *
from .test_error_handling import *

# The tests are now organized in separate files:
# - test_protocol_structure.py: Message structure, encoding, byte ordering
# - test_message_buffering.py: Message reception and buffering
# - test_get_operations.py: GET operations
# - test_set_operations.py: SET operations and permissions
# - test_error_handling.py: Basic error handling (non-existent OIDs, read-only errors)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])