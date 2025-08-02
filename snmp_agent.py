#!/usr/bin/env python3
"""
SNMP Agent Implementation
The server that listens for SNMP requests and responds with data

This file focuses on the SERVER side of network programming:
1. Socket server setup - CREATE YOUR OWN SERVER!
2. Receiving and parsing network messages
3. Processing different message types
4. Sending responses back to clients

IMPORTANT: You'll implement the complete server socket setup to learn
how network servers work from the ground up
"""

import socket
import sys
import struct
import time
import signal
from typing import Dict, Any, List, Tuple, Optional

# Import protocol components (you'll implement these in snmp_protocol.py)
from snmp_protocol import (
    PDUType, ValueType, ErrorCode,
    GetRequest, SetRequest, GetResponse,
    unpack_message, receive_complete_message,
    encode_oid, decode_oid
)

# ============================================================================
# CONSTANTS (PROVIDED - DO NOT MODIFY)
# ============================================================================

DEFAULT_PORT = 1161  # We use 1161 instead of standard 161 (no root required)
LISTEN_BACKLOG = 5   # Maximum pending connections
TIMEOUT_SECONDS = 10.0  # Socket timeout
TIMETICKS_PER_SECOND = 100  # SNMP timeticks are 1/100 second

# ============================================================================
# MIB DATABASE (PROVIDED - DO NOT MODIFY)
# ============================================================================

# Import the MIB database (Management Information Base)
# This contains all the data our agent can serve
try:
    from mib_database import MIB_DATABASE, MIB_PERMISSIONS
except ImportError:
    # Fallback MIB for testing if mib_database.py doesn't exist
    MIB_DATABASE = {
        '1.3.6.1.2.1.1.1.0': ('STRING', 'Router Model X2000'),
        '1.3.6.1.2.1.1.3.0': ('TIMETICKS', 0),  # System uptime
        '1.3.6.1.2.1.1.5.0': ('STRING', 'router-main'),
        '1.3.6.1.2.1.1.7.0': ('INTEGER', 72),
        # Interface data
        '1.3.6.1.2.1.2.2.1.10.1': ('COUNTER', 1234567890),
        '1.3.6.1.2.1.2.2.1.10.2': ('COUNTER', 987654321),
        '1.3.6.1.2.1.2.2.1.10.3': ('COUNTER', 456789),
    }
    
    MIB_PERMISSIONS = {
        '1.3.6.1.2.1.1.1.0': 'read-only',
        '1.3.6.1.2.1.1.3.0': 'read-only',
        '1.3.6.1.2.1.1.5.0': 'read-write',
        '1.3.6.1.2.1.1.7.0': 'read-only',
    }

# ============================================================================
# SNMP AGENT CLASS
# ============================================================================

class SNMPAgent:
    """SNMP Agent that responds to management requests"""
    
    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.mib = dict(MIB_DATABASE)  # Create a mutable copy
        self.start_time = time.time()
        self.server_socket = None
        self.running = True
    
    # ========================================================================
    # STUDENT IMPLEMENTATION: Socket setup and server loop
    # ========================================================================
    
    def start(self):
        """
        TODO: Start the SNMP agent server
        
        This is where you implement the SERVER side of socket programming!
        
        Steps:
        1. Create a TCP socket (AF_INET, SOCK_STREAM)
        2. Set socket option SO_REUSEADDR to 1 (prevents "Address already in use")
        3. Bind the socket to all interfaces ('') on self.port
        4. Start listening with LISTEN_BACKLOG connections
        5. Print "SNMP Agent listening on port {port}..."
        6. Main server loop:
           - Accept incoming connections
           - Print connection info
           - Call _handle_client() for each connection
           - Handle KeyboardInterrupt for graceful shutdown
        7. Always close the server socket when done
        
        Important:
        - Use try/finally to ensure socket cleanup
        - Handle KeyboardInterrupt to allow Ctrl+C shutdown
        - The server should run forever until interrupted
        
        Socket methods you'll need:
        - socket.socket() - create socket
        - sock.setsockopt() - set options
        - sock.bind() - bind to address
        - sock.listen() - start listening
        - sock.accept() - accept connections
        - sock.close() - cleanup
        
        Test: test_agent_starts_and_accepts_connections
        """
        # TODO: Create server socket
        # TODO: Set SO_REUSEADDR option
        # TODO: Bind to address
        # TODO: Start listening
        # TODO: Main accept loop
        # TODO: Handle shutdown
        
        raise NotImplementedError("Implement start() - server socket setup")
    
    # ========================================================================
    # STUDENT IMPLEMENTATION: Message handling
    # ========================================================================
    
    def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        """
        TODO: Handle a client connection
        
        This method is called for each client that connects. You need to:
        1. Set a timeout on the client socket (use client_socket.settimeout)
        2. Receive messages from the client (use receive_complete_message)
        3. Unpack and process each message
        4. Send appropriate responses
        5. Handle errors gracefully
        6. Close the connection when done
        
        The connection should stay open for multiple requests until:
        - The client closes the connection
        - A timeout occurs
        - An unrecoverable error happens
        
        Hints:
        - Use try/except/finally to ensure the socket is always closed
        - Remember to handle ConnectionError and socket.timeout
        - Each request should get a response (even if it's an error)
        
        Test: test_agent_handles_multiple_requests will verify this
        """
        try:
            # TODO: Set socket timeout
            # TODO: Loop to handle multiple requests
            # TODO: Receive and process messages
            # TODO: Send responses
            
            raise NotImplementedError("Implement _handle_client")
            
        finally:
            client_socket.close()
    
    def _process_message(self, message_bytes: bytes) -> bytes:
        """
        TODO: Process a received message and return response bytes
        
        Steps:
        1. Unpack the message to determine its type
        2. Call the appropriate handler based on message type
        3. Return the response as bytes
        
        This is the main dispatcher that routes messages to handlers.
        
        Test: Various tests will verify different message types
        """
        # TODO: Unpack message
        # TODO: Route to appropriate handler
        # TODO: Return response bytes
        
        raise NotImplementedError("Implement _process_message")
    
    # ========================================================================
    # STUDENT IMPLEMENTATION: Protocol handlers
    # ========================================================================
    
    def _handle_get_request(self, request: GetRequest) -> GetResponse:
        """
        TODO: Process GetRequest and return GetResponse
        
        For each OID in the request:
        1. Check if it exists in self.mib
        2. If it exists, add its value to the response
        3. If any OID doesn't exist, return error code NO_SUCH_OID
        
        Remember to:
        - Update dynamic values (like uptime) before responding
        - Use the correct value types from the MIB
        
        Test: test_get_single_oid and test_get_multiple_oids
        """
        # TODO: Update dynamic values (like uptime)
        self._update_dynamic_values()
        
        # TODO: Process each OID
        # TODO: Build and return GetResponse
        
        raise NotImplementedError("Implement _handle_get_request")
    
    def _handle_set_request(self, request: SetRequest) -> GetResponse:
        """
        TODO: Process SetRequest and return GetResponse
        
        For each OID/value binding in the request:
        1. Check if OID exists (error: NO_SUCH_OID)
        2. Check if OID is writable (error: READ_ONLY)
        3. Validate value type matches MIB (error: BAD_VALUE)
        4. If all checks pass, update the value
        
        Important: Only update values if ALL bindings are valid!
        
        Test: test_set_request and test_set_read_only_fails
        """
        # TODO: Validate all bindings first
        # TODO: Update values only if all valid
        # TODO: Return appropriate response
        
        raise NotImplementedError("Implement _handle_set_request")
    
    
    # ========================================================================
    # STUDENT IMPLEMENTATION: Helper methods
    # ========================================================================
    
    def _update_dynamic_values(self):
        """
        TODO: Update dynamic MIB values like system uptime
        
        Some MIB values change over time:
        - System uptime (1.3.6.1.2.1.1.3.0) - time since agent started
        
        Calculate uptime as:
        - Current time - self.start_time
        - Convert to timeticks (hundredths of seconds)
        - Update in self.mib
        
        Test: test_agent_uptime_increases
        """
        # TODO: Calculate and update uptime
        raise NotImplementedError("Implement _update_dynamic_values")
    
    def _get_value_type(self, type_str: str) -> ValueType:
        """
        PROVIDED: Convert MIB type string to ValueType enum
        """
        mapping = {
            'INTEGER': ValueType.INTEGER,
            'STRING': ValueType.STRING,
            'COUNTER': ValueType.COUNTER,
            'TIMETICKS': ValueType.TIMETICKS,
        }
        return mapping.get(type_str, ValueType.STRING)
    
    def _get_next_oids(self, start_oid: str, max_count: int) -> List[str]:
        """
        TODO: Get the next OIDs in lexicographic order
        
        Lexicographic ordering for OIDs means:
        - 1.2.3 comes before 1.2.4
        - 1.2 comes before 1.2.0
        - 1.2.3 comes before 1.3
        
        Algorithm:
        1. Get all OIDs from self.mib
        2. Sort them using OID comparison rules
        3. Find OIDs greater than start_oid
        4. Return up to max_count of them
        
        Hint: Implement _compare_oids to help with sorting
        """
        # TODO: Get and sort OIDs
        # TODO: Find OIDs after start_oid
        # TODO: Return up to max_count
        
        raise NotImplementedError("Implement _get_next_oids")
    
    def _compare_oids(self, oid1: str, oid2: str) -> int:
        """
        TODO: Compare two OIDs lexicographically
        
        Returns:
        - -1 if oid1 < oid2
        - 0 if oid1 == oid2
        - 1 if oid1 > oid2
        
        Example comparisons:
        - "1.2.3" < "1.2.4" (compare each number)
        - "1.2" < "1.2.0" (shorter is less)
        - "1.2.3" < "1.3" (compare left to right)
        
        Hint: Split by '.', convert to integers, compare lists
        """
        # TODO: Implement OID comparison
        raise NotImplementedError("Implement _compare_oids")

# ============================================================================
# MAIN ENTRY POINT (PROVIDED)
# ============================================================================

def main():
    """
    PROVIDED: Main entry point with command-line parsing
    """
    # Parse command line arguments
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            if not 1 <= port <= 65535:
                print(f"Error: Port must be between 1 and 65535")
                sys.exit(1)
        except ValueError:
            print(f"Error: Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    # Create and start the agent
    agent = SNMPAgent(port)
    try:
        agent.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()