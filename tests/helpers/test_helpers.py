#!/usr/bin/env python3
"""
Test Helper Functions for SNMP Autograder
Shared utilities for testing SNMP implementations
"""

import struct
import socket
import subprocess
import time
import os
import sys
import threading
import random
from typing import List, Tuple, Any, Optional, Dict
import json

# Protocol constants
PDU_GET_REQUEST = 0xA0
PDU_GET_RESPONSE = 0xA1
PDU_SET_REQUEST = 0xA3

VALUE_INTEGER = 0x02
VALUE_STRING = 0x04
VALUE_COUNTER = 0x41
VALUE_TIMETICKS = 0x43

ERROR_SUCCESS = 0
ERROR_NO_SUCH_OID = 1
ERROR_BAD_VALUE = 2
ERROR_READ_ONLY = 3

MAX_RECV_BUFFER = 4096


class MockSNMPAgent:
    """Mock SNMP agent for controlled testing"""
    
    def __init__(self, port: int, mib_data: Optional[Dict] = None):
        self.port = port
        self.mib_data = mib_data or self._default_mib()
        self.server_socket = None
        self.running = False
        self.thread = None
        self.connections_handled = 0
        self.requests_received = []
        
    def _default_mib(self) -> Dict:
        """Create a simple default MIB for testing"""
        return {
            '1.3.6.1.2.1.1.1.0': ('STRING', 'Test SNMP Agent'),
            '1.3.6.1.2.1.1.3.0': ('TIMETICKS', 12345),
            '1.3.6.1.2.1.1.5.0': ('STRING', 'test-agent'),
        }
    
    def start(self):
        """Start the mock agent"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('localhost', self.port))
        self.server_socket.listen(5)
        self.running = True
        
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the mock agent"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if self.thread:
            self.thread.join(timeout=1)
    
    def _run(self):
        """Run the agent server loop"""
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                self._handle_client(client_sock)
                self.connections_handled += 1
            except Exception:
                if self.running:
                    raise
    
    def _handle_client(self, sock):
        """Handle a client connection"""
        try:
            while True:
                # Receive message
                data = self._receive_message(sock)
                if not data:
                    break
                
                # Process request
                response = self._process_request(data)
                if response:
                    sock.send(response)
        finally:
            sock.close()
    
    def _receive_message(self, sock) -> bytes:
        """Receive a complete SNMP message"""
        # Similar to the real implementation
        received = b''
        
        # Get size
        while len(received) < 4:
            chunk = sock.recv(4 - len(received))
            if not chunk:
                return b''
            received += chunk
        
        size = struct.unpack('!I', received[:4])[0]
        
        # Get rest
        while len(received) < size:
            chunk = sock.recv(min(size - len(received), 4096))
            if not chunk:
                return b''
            received += chunk
        
        return received
    
    def _process_request(self, data: bytes) -> bytes:
        """Process an SNMP request and return response"""
        # Record the request
        self.requests_received.append(data)
        
        # Parse request
        request_id = struct.unpack('!I', data[4:8])[0]
        pdu_type = data[8]
        
        if pdu_type == PDU_GET_REQUEST:
            return self._handle_get_request(data, request_id)
        # Add other PDU types as needed
        
        return b''
    
    def _handle_get_request(self, data: bytes, request_id: int) -> bytes:
        """Handle a GetRequest"""
        # Simple implementation for testing
        # In reality, would parse OIDs and look them up
        
        # Create a simple response
        response_bindings = [(
            '1.3.6.1.2.1.1.1.0',
            VALUE_STRING,
            'Mock Agent Response'
        )]
        
        return create_get_response(request_id, ERROR_SUCCESS, response_bindings)


class DelayedResponseAgent(MockSNMPAgent):
    """Agent that delays responses for buffering tests"""
    
    def __init__(self, port: int, delay: float = 0.1):
        super().__init__(port)
        self.delay = delay
    
    def _process_request(self, data: bytes) -> bytes:
        """Process request with delay"""
        time.sleep(self.delay)
        return super()._process_request(data)


class FragmentedResponseAgent(MockSNMPAgent):
    """Agent that sends responses in fragments"""
    
    def __init__(self, port: int, fragment_size: int = 100):
        super().__init__(port)
        self.fragment_size = fragment_size
    
    def _handle_client(self, sock):
        """Handle client with fragmented responses"""
        try:
            while True:
                data = self._receive_message(sock)
                if not data:
                    break
                
                response = self._process_request(data)
                if response:
                    # Send in fragments
                    for i in range(0, len(response), self.fragment_size):
                        sock.send(response[i:i+self.fragment_size])
                        time.sleep(0.01)  # Small delay between fragments
        finally:
            sock.close()


def create_get_response(request_id: int, error_code: int, 
                       bindings: List[Tuple[str, int, Any]]) -> bytes:
    """Create a GetResponse message"""
    payload = struct.pack('!B', len(bindings))
    
    for oid, value_type, value in bindings:
        oid_bytes = encode_oid(oid)
        value_bytes = encode_value(value, value_type)
        
        payload += struct.pack('!B', len(oid_bytes))
        payload += oid_bytes
        payload += struct.pack('!B', value_type)
        payload += struct.pack('!H', len(value_bytes))
        payload += value_bytes
    
    total_size = 4 + 4 + 1 + 1 + len(payload)
    message = struct.pack('!II', total_size, request_id)
    message += struct.pack('!B', PDU_GET_RESPONSE)
    message += struct.pack('!B', error_code)
    message += payload
    
    return message


def encode_oid(oid_string: str) -> bytes:
    """Convert OID string to bytes"""
    return bytes([int(x) for x in oid_string.split('.')])


def decode_oid(oid_bytes: bytes) -> str:
    """Convert OID bytes to string"""
    return '.'.join(str(b) for b in oid_bytes)


def encode_value(value: Any, value_type: int) -> bytes:
    """Encode a value based on its type"""
    if value_type == VALUE_INTEGER:
        return struct.pack('!i', value)
    elif value_type == VALUE_STRING:
        if isinstance(value, str):
            return value.encode('utf-8')
        return value
    elif value_type == VALUE_COUNTER:
        return struct.pack('!I', value)
    elif value_type == VALUE_TIMETICKS:
        return struct.pack('!I', value)
    else:
        raise ValueError(f"Unknown value type: {value_type}")


def decode_value(value_bytes: bytes, value_type: int) -> Any:
    """Decode a value based on its type"""
    if value_type == VALUE_INTEGER:
        return struct.unpack('!i', value_bytes)[0]
    elif value_type == VALUE_STRING:
        return value_bytes.decode('utf-8')
    elif value_type == VALUE_COUNTER:
        return struct.unpack('!I', value_bytes)[0]
    elif value_type == VALUE_TIMETICKS:
        return struct.unpack('!I', value_bytes)[0]
    else:
        return value_bytes


def generate_large_response(num_bindings: int = 100) -> bytes:
    """Generate a large GetResponse for buffering tests"""
    bindings = []
    for i in range(num_bindings):
        oid = f"1.3.6.1.4.1.99.{i}.0"
        value = f"This is a long test value number {i} designed to test message buffering " * 5
        bindings.append((oid, VALUE_STRING, value))
    
    return create_get_response(1234, ERROR_SUCCESS, bindings)


def wait_for_port(port: int, timeout: float = 5.0) -> bool:
    """Wait for a port to become available"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(('localhost', port))
            sock.close()
            return True
        except (ConnectionRefusedError, socket.error):
            time.sleep(0.1)
    return False


def kill_process_on_port(port: int):
    """Kill any process listening on the given port"""
    if sys.platform == "win32":
        # Windows
        subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True)
        # More complex on Windows, might need admin rights
    else:
        # Unix-like
        try:
            result = subprocess.run(
                f"lsof -ti:{port}",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                pid = result.stdout.strip()
                subprocess.run(f"kill -9 {pid}", shell=True)
        except:
            pass


def create_malformed_messages() -> List[bytes]:
    """Create various malformed messages for testing"""
    messages = []
    
    # Message with size too small
    msg = struct.pack('!I', 5)  # Size less than minimum
    msg += struct.pack('!I', 1234)
    msg += struct.pack('!B', PDU_GET_REQUEST)
    messages.append(msg)
    
    # Message with size too large
    msg = struct.pack('!I', 999999)  # Unreasonably large
    msg += struct.pack('!I', 1234)
    msg += struct.pack('!B', PDU_GET_REQUEST)
    messages.append(msg)
    
    # Message with invalid PDU type
    msg = struct.pack('!I', 13)
    msg += struct.pack('!I', 1234)
    msg += struct.pack('!B', 0xFF)  # Invalid PDU
    msg += b'\x00' * 4
    messages.append(msg)
    
    # Truncated message
    msg = struct.pack('!I', 20)  # Says 20 bytes
    msg += struct.pack('!I', 1234)
    msg += struct.pack('!B', PDU_GET_REQUEST)
    # But don't include the rest
    messages.append(msg)
    
    return messages


def format_bytes_hex(data: bytes, width: int = 16) -> str:
    """Format bytes as hex dump for debugging"""
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"{i:04x}: {hex_part:<{width*3-1}} {ascii_part}")
    return '\n'.join(lines)


def compare_messages(expected: bytes, actual: bytes) -> str:
    """Compare two messages and return detailed diff"""
    if expected == actual:
        return "Messages match"
    
    diff = []
    diff.append(f"Expected length: {len(expected)}, Actual length: {len(actual)}")
    diff.append("\nExpected:")
    diff.append(format_bytes_hex(expected))
    diff.append("\nActual:")
    diff.append(format_bytes_hex(actual))
    
    # Find first difference
    for i in range(min(len(expected), len(actual))):
        if expected[i] != actual[i]:
            diff.append(f"\nFirst difference at byte {i}: expected 0x{expected[i]:02x}, got 0x{actual[i]:02x}")
            break
    
    return '\n'.join(diff)


class ExecutionLogger:
    """Logger for test execution details"""
    
    def __init__(self, filename: str = "test_execution.log"):
        self.filename = filename
        self.start_time = time.time()
        
    def log(self, message: str):
        """Log a message with timestamp"""
        elapsed = time.time() - self.start_time
        with open(self.filename, 'a') as f:
            f.write(f"[{elapsed:.3f}s] {message}\n")
    
    def log_request(self, request_type: str, data: bytes):
        """Log an SNMP request"""
        self.log(f"Request: {request_type}")
        self.log(f"Data:\n{format_bytes_hex(data)}")
    
    def log_response(self, data: bytes):
        """Log an SNMP response"""
        self.log("Response received")
        self.log(f"Data:\n{format_bytes_hex(data)}")


def measure_response_time(func, *args, **kwargs) -> Tuple[Any, float]:
    """Measure execution time of a function"""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed


def create_performance_report(results: Dict[str, List[float]]) -> str:
    """Create a performance report from timing results"""
    report = ["Performance Report", "=" * 40]
    
    for test_name, times in results.items():
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            report.append(f"\n{test_name}:")
            report.append(f"  Average: {avg_time:.3f}s")
            report.append(f"  Min: {min_time:.3f}s")
            report.append(f"  Max: {max_time:.3f}s")
    
    return '\n'.join(report)


def generate_test_oids(count: int, prefix: str = "1.3.6.1.2.1") -> List[str]:
    """Generate a list of test OIDs"""
    oids = []
    for i in range(count):
        # Create varied OIDs
        group = i % 10
        subgroup = (i // 10) % 10
        instance = i % 3
        oids.append(f"{prefix}.{group}.{subgroup}.{i}.{instance}")
    return oids


def simulate_network_conditions(sock: socket.socket, 
                              delay: float = 0, 
                              jitter: float = 0,
                              loss_rate: float = 0):
    """Simulate various network conditions on a socket"""
    # This would need to be implemented with a proxy or wrapper
    # For now, it's a placeholder for future enhancement
    pass