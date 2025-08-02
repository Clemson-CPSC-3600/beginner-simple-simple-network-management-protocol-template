#!/usr/bin/env python3
"""
SNMP Manager Implementation
The client that sends requests to SNMP agents

This file focuses on the CLIENT side of network programming:
1. Creating and connecting sockets
2. Packing and sending requests
3. Receiving and unpacking responses
4. Displaying results to the user

IMPORTANT: Command-line parsing and display formatting are PROVIDED
"""

import socket
import sys
import struct
import random
import time
from typing import List, Tuple, Optional, Any

# Import protocol components (you'll implement these in snmp_protocol.py)
from snmp_protocol import (
    PDUType, ValueType, ErrorCode,
    GetRequest, SetRequest, GetBulkRequest, GetResponse,
    receive_complete_message, unpack_message
)

# ============================================================================
# CONSTANTS (PROVIDED - DO NOT MODIFY)
# ============================================================================

DEFAULT_TIMEOUT = 10.0  # Socket timeout in seconds
TIMETICKS_PER_SECOND = 100  # SNMP timeticks are 1/100 second

# ============================================================================
# PROVIDED: Display formatting functions
# ============================================================================

def format_timeticks(ticks: int) -> str:
    """
    PROVIDED: Convert timeticks to human readable format
    
    This handles the display of uptime values in a user-friendly way
    """
    total_seconds = ticks / TIMETICKS_PER_SECOND
    days = int(total_seconds // 86400)
    hours = int((total_seconds % 86400) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days} days")
    if hours > 0:
        parts.append(f"{hours} hours")
    if minutes > 0:
        parts.append(f"{minutes} minutes")
    if seconds > 0 or len(parts) == 0:
        parts.append(f"{seconds:.2f} seconds")
    
    return f"{ticks} ({', '.join(parts)})"

def format_value(value_type: ValueType, value: Any) -> str:
    """
    PROVIDED: Format any value for display based on its type
    """
    if value_type == ValueType.TIMETICKS:
        return format_timeticks(value)
    elif value_type == ValueType.COUNTER:
        # Add thousands separators for readability
        return f"{value:,}"
    else:
        return str(value)

def format_error(error_code: ErrorCode) -> str:
    """
    PROVIDED: Convert error codes to human-readable messages
    """
    error_messages = {
        ErrorCode.NO_SUCH_OID: "No such OID exists",
        ErrorCode.BAD_VALUE: "Bad value for OID type",
        ErrorCode.READ_ONLY: "OID is read-only"
    }
    return error_messages.get(error_code, f"Unknown error ({error_code})")

# ============================================================================
# SNMP MANAGER CLASS
# ============================================================================

class SNMPManager:
    """SNMP Manager for sending requests to agents"""
    
    def __init__(self):
        # Generate random starting request ID
        self.request_id = random.randint(1, 10000)
    
    def _get_next_request_id(self) -> int:
        """
        PROVIDED: Generate unique request IDs for matching responses
        """
        self.request_id += 1
        return self.request_id
    
    # ========================================================================
    # STUDENT IMPLEMENTATION: Core operations
    # ========================================================================
    
    def get(self, host: str, port: int, oids: List[str]) -> None:
        """
        TODO: Send GetRequest and display response
        
        Steps:
        1. Create a TCP socket
        2. Connect to the agent at host:port
        3. Create a GetRequest with unique request ID and OIDs
        4. Pack the request into bytes
        5. Send the request
        6. Receive the complete response (use receive_complete_message)
        7. Unpack the response
        8. Verify it's a GetResponse with matching request ID
        9. Display results or error
        
        Display format:
        - Success: "oid = value" for each OID
        - Error: "Error: <error message>"
        
        Don't forget:
        - Set socket timeout with sock.settimeout()
        - Handle connection errors
        - Always close the socket (use try/finally)
        
        Test: test_manager_get_request
        """
        sock = None
        try:
            # TODO: Create and connect socket
            # TODO: Create and send GetRequest
            # TODO: Receive and process response
            # TODO: Display results
            
            raise NotImplementedError("Implement get operation")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if sock:
                sock.close()
    
    def set(self, host: str, port: int, oid: str, value_type: str, value: str) -> None:
        """
        TODO: Send SetRequest and display response
        
        Steps:
        1. Parse the value_type string to ValueType enum
        2. Convert the value string to appropriate Python type
        3. Create socket and connect
        4. Create SetRequest with OID, type, and value
        5. Send request and receive response
        6. Display success or error
        
        Value type mapping:
        - "integer" -> ValueType.INTEGER (convert value to int)
        - "string" -> ValueType.STRING (use value as-is)
        - "counter" -> ValueType.COUNTER (convert to int)
        - "timeticks" -> ValueType.TIMETICKS (convert to int)
        
        Display format:
        - Success: "Set operation successful:" then "oid = value"
        - Error: "Error: <error message>"
        
        Test: test_manager_set_request
        """
        # Provided: Parse value type
        type_map = {
            'integer': ValueType.INTEGER,
            'string': ValueType.STRING,
            'counter': ValueType.COUNTER,
            'timeticks': ValueType.TIMETICKS
        }
        
        if value_type.lower() not in type_map:
            print(f"Error: Invalid value type '{value_type}'. Must be one of: {', '.join(type_map.keys())}")
            return
        
        vtype = type_map[value_type.lower()]
        
        # TODO: Convert value to appropriate type
        # TODO: Create socket and connect
        # TODO: Send SetRequest
        # TODO: Process response
        
        raise NotImplementedError("Implement set operation")
    
    def bulk(self, host: str, port: int, start_oid: str, max_repetitions: int) -> None:
        """
        TODO: Send GetBulkRequest and display response
        
        GetBulk is used to efficiently retrieve many OIDs at once.
        It returns up to max_repetitions OIDs starting after start_oid.
        
        Steps similar to get(), but:
        - Create GetBulkRequest instead of GetRequest
        - May receive a large response (buffering is critical!)
        - Display all returned OIDs
        
        Display format:
        - Header: "Requesting up to X OIDs starting after Y..."
        - After receive: "Received N OIDs in T seconds (B bytes)"
        - Separator line: "-" * 60
        - Then each OID: "oid = value"
        
        Measure elapsed time for the receive operation to show
        buffering performance.
        
        Test: test_manager_bulk_request
        """
        # TODO: Implement bulk operation
        raise NotImplementedError("Implement bulk operation")
    
    # ========================================================================
    # STUDENT IMPLEMENTATION: Helper methods
    # ========================================================================
    
    def _connect_to_agent(self, host: str, port: int) -> socket.socket:
        """
        TODO: Create a socket and connect to the SNMP agent
        
        Steps:
        1. Create a TCP socket (socket.AF_INET, socket.SOCK_STREAM)
        2. Set a timeout (DEFAULT_TIMEOUT)
        3. Connect to (host, port)
        4. Return the connected socket
        
        Raise ConnectionError if connection fails.
        
        This is a helper method to avoid repeating connection code.
        """
        # TODO: Implement socket connection
        raise NotImplementedError("Implement _connect_to_agent")

# ============================================================================
# PROVIDED: Command-line interface
# ============================================================================

def print_usage():
    """PROVIDED: Print usage information"""
    print("Usage:")
    print("  snmp_manager.py get <host:port> <oid> [<oid> ...]")
    print("  snmp_manager.py set <host:port> <oid> <type> <value>")
    print("  snmp_manager.py bulk <host:port> <start_oid> <max_repetitions>")
    print()
    print("Examples:")
    print("  snmp_manager.py get localhost:1161 1.3.6.1.2.1.1.1.0")
    print("  snmp_manager.py get localhost:1161 1.3.6.1.2.1.1.1.0 1.3.6.1.2.1.1.5.0")
    print("  snmp_manager.py set localhost:1161 1.3.6.1.2.1.1.5.0 string 'new-router-name'")
    print("  snmp_manager.py bulk localhost:1161 1.3.6.1.2.1.2.2.1 50")
    print()
    print("Types: integer, string, counter, timeticks")

def parse_host_port(host_port: str) -> Tuple[str, int]:
    """PROVIDED: Parse host:port string"""
    parts = host_port.split(':')
    if len(parts) != 2:
        raise ValueError("Invalid host:port format. Use 'hostname:port' or 'ip:port'")
    
    host = parts[0]
    try:
        port = int(parts[1])
        if not 1 <= port <= 65535:
            raise ValueError("Port must be between 1 and 65535")
    except ValueError:
        raise ValueError(f"Invalid port number: {parts[1]}")
    
    return host, port

def main():
    """
    PROVIDED: Main entry point with command-line parsing
    
    This handles all the command-line argument parsing so students
    can focus on the networking implementation.
    """
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        host, port = parse_host_port(sys.argv[2])
    except ValueError as e:
        print(f"Error: {e}")
        print_usage()
        sys.exit(1)
    
    manager = SNMPManager()
    
    if command == 'get':
        if len(sys.argv) < 4:
            print("Error: No OIDs specified")
            print_usage()
            sys.exit(1)
        
        oids = sys.argv[3:]
        manager.get(host, port, oids)
        
    elif command == 'set':
        if len(sys.argv) != 6:
            print("Error: Set requires exactly 4 arguments: host:port oid type value")
            print_usage()
            sys.exit(1)
        
        oid = sys.argv[3]
        value_type = sys.argv[4]
        value = sys.argv[5]
        manager.set(host, port, oid, value_type, value)
        
    elif command == 'bulk':
        if len(sys.argv) != 5:
            print("Error: Bulk requires exactly 3 arguments: host:port start_oid max_repetitions")
            print_usage()
            sys.exit(1)
        
        start_oid = sys.argv[3]
        try:
            max_repetitions = int(sys.argv[4])
            if max_repetitions < 1:
                raise ValueError("max_repetitions must be at least 1")
        except ValueError as e:
            print(f"Error: Invalid max_repetitions - {e}")
            sys.exit(1)
        
        manager.bulk(host, port, start_oid, max_repetitions)
        
    else:
        print(f"Error: Unknown command '{command}'")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()