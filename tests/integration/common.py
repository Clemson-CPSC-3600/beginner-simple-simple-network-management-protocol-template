#!/usr/bin/env python3
"""
Common test utilities and constants for SNMP protocol tests
"""

import struct
import socket
import sys
import os
import time
import subprocess
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the MIB database
try:
    from mib_database import MIB_DATABASE, MIB_PERMISSIONS
except ImportError:
    print("Warning: mib_database.py not found. Using default MIB.")
    MIB_DATABASE = {
        '1.3.6.1.2.1.1.1.0': ('STRING', 'Router Model X2000 - High Performance Edge Router'),
        '1.3.6.1.2.1.1.3.0': ('TIMETICKS', 0),
        '1.3.6.1.2.1.1.5.0': ('STRING', 'router-main'),
    }
    MIB_PERMISSIONS = {}

# Protocol constants matching the specification
MESSAGE_HEADER_SIZE = 9
RESPONSE_HEADER_SIZE = 10
MAX_RECV_BUFFER = 4096

# PDU Types
PDU_GET_REQUEST = 0xA0
PDU_GET_RESPONSE = 0xA1
PDU_SET_REQUEST = 0xA3

# Value Types
VALUE_INTEGER = 0x02
VALUE_STRING = 0x04
VALUE_COUNTER = 0x41
VALUE_TIMETICKS = 0x43

# Error Codes
ERROR_SUCCESS = 0
ERROR_NO_SUCH_OID = 1
ERROR_WRONG_TYPE = 2
ERROR_READ_ONLY = 3
ERROR_GENERAL = 4

# Test configuration
TEST_AGENT_HOST = '127.0.0.1'
TEST_AGENT_PORT = 20161

# Check if we should use solution files
USE_SOLUTION = os.environ.get('SNMP_TEST_SOLUTION', 'false').lower() == 'true'
SOLUTION_DIR = 'solution'

# Determine paths based on whether we're testing solution or student code
if USE_SOLUTION:
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    solution_path = os.path.join(parent_dir, SOLUTION_DIR)
    if os.path.exists(solution_path):
        MANAGER_PATH = os.path.join(SOLUTION_DIR, 'snmp_manager.py')
        AGENT_PATH = os.path.join(SOLUTION_DIR, 'snmp_agent.py')
        print(f"[TEST MODE] Using solution files from /{SOLUTION_DIR}/")
    else:
        print(f"[WARNING] Solution directory not found, using student files")
        MANAGER_PATH = 'snmp_manager.py'
        AGENT_PATH = 'snmp_agent.py'
else:
    MANAGER_PATH = 'snmp_manager.py'
    AGENT_PATH = 'snmp_agent.py'


# ===== HELPER FUNCTIONS =====

def encode_oid(oid_string: str) -> bytes:
    """Convert OID string to bytes"""
    try:
        return bytes([int(x) for x in oid_string.split('.')])
    except ValueError:
        # For testing invalid OIDs, encode as raw bytes
        return oid_string.encode('utf-8')

def decode_oid(oid_bytes: bytes) -> str:
    """Convert OID bytes to string"""
    return '.'.join(str(b) for b in oid_bytes)

def encode_value(value, value_type: int) -> bytes:
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

def create_get_request(request_id: int, oids: list) -> bytes:
    """Create a GetRequest message"""
    payload = struct.pack('!B', len(oids))
    for oid in oids:
        oid_bytes = encode_oid(oid)
        payload += struct.pack('!B', len(oid_bytes))
        payload += oid_bytes
    
    total_size = 4 + 4 + 1 + len(payload)
    message = struct.pack('!II', total_size, request_id)
    message += struct.pack('!B', PDU_GET_REQUEST)
    message += payload
    return message

def create_set_request(request_id: int, bindings: list) -> bytes:
    """Create a SetRequest message"""
    payload = struct.pack('!B', len(bindings))
    for oid, value_type, value in bindings:
        oid_bytes = encode_oid(oid)
        value_bytes = encode_value(value, value_type)
        
        payload += struct.pack('!B', len(oid_bytes))
        payload += oid_bytes
        payload += struct.pack('!B', value_type)
        payload += struct.pack('!H', len(value_bytes))
        payload += value_bytes
    
    total_size = 4 + 4 + 1 + len(payload)
    message = struct.pack('!II', total_size, request_id)
    message += struct.pack('!B', PDU_SET_REQUEST)
    message += payload
    return message


def receive_complete_message(sock, timeout=5.0) -> bytes:
    """Receive a complete SNMP message with proper buffering"""
    # Set socket timeout
    original_timeout = sock.gettimeout()
    sock.settimeout(timeout)
    
    try:
        received_bytes = b''
        
        # Get message size
        while len(received_bytes) < 4:
            chunk = sock.recv(4 - len(received_bytes))
            if not chunk:
                raise ConnectionError("Connection closed while reading size")
            received_bytes += chunk
        
        message_size = struct.unpack('!I', received_bytes[:4])[0]
        
        # Get rest of message
        while len(received_bytes) < message_size:
            bytes_needed = message_size - len(received_bytes)
            chunk = sock.recv(min(bytes_needed, MAX_RECV_BUFFER))
            if not chunk:
                raise ConnectionError("Connection closed while reading message")
            received_bytes += chunk
        
        return received_bytes
    finally:
        # Restore original timeout
        sock.settimeout(original_timeout)

class SNMPResponse:
    """Parsed SNMP response"""
    def __init__(self, request_id: int, error_code: int, bindings: list):
        self.request_id = request_id
        self.error_code = error_code
        self.bindings = bindings

def parse_response(data: bytes) -> SNMPResponse:
    """Parse a GetResponse message"""
    # Skip size field
    request_id = struct.unpack('!I', data[4:8])[0]
    pdu_type = data[8]
    
    if pdu_type != PDU_GET_RESPONSE:
        raise ValueError(f"Expected GetResponse, got {pdu_type:02X}")
    
    error_code = data[9]
    binding_count = data[10]
    
    offset = 11
    bindings = []
    
    for _ in range(binding_count):
        # Parse OID
        oid_length = data[offset]
        offset += 1
        oid_bytes = data[offset:offset+oid_length]
        offset += oid_length
        oid = decode_oid(oid_bytes)
        
        # Parse value
        value_type = data[offset]
        offset += 1
        value_length = struct.unpack('!H', data[offset:offset+2])[0]
        offset += 2
        value_bytes = data[offset:offset+value_length]
        offset += value_length
        
        # Decode value based on type
        if value_type == VALUE_INTEGER:
            value = struct.unpack('!i', value_bytes)[0]
        elif value_type == VALUE_STRING:
            value = value_bytes.decode('utf-8')
        elif value_type == VALUE_COUNTER:
            value = struct.unpack('!I', value_bytes)[0]
        elif value_type == VALUE_TIMETICKS:
            value = struct.unpack('!I', value_bytes)[0]
        else:
            value = value_bytes
        
        bindings.append((oid, value_type, value))
    
    return SNMPResponse(request_id, error_code, bindings)

def send_get_request(port: int, oids: list, request_id: int = 1234):
    """Send GetRequest and return response"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('localhost', port))
        request = create_get_request(request_id, oids)
        sock.send(request)
        response_data = receive_complete_message(sock)
        return parse_response(response_data)
    finally:
        sock.close()

def send_set_request(port: int, bindings: list, request_id: int = 1234):
    """Send SetRequest and return response"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('localhost', port))
        request = create_set_request(request_id, bindings)
        sock.send(request)
        response_data = receive_complete_message(sock)
        return parse_response(response_data)
    finally:
        sock.close()


def compare_oids(oid1: str, oid2: str) -> int:
    """Compare two OIDs lexicographically per SNMP standard"""
    # SNMP lexicographic ordering compares numeric components, not strings
    # So 1.3.6.1.2.1.2.2.1.2 comes before 1.3.6.1.2.1.2.2.1.10
    parts1 = [int(x) for x in oid1.split('.')]
    parts2 = [int(x) for x in oid2.split('.')]
    
    for i in range(min(len(parts1), len(parts2))):
        if parts1[i] < parts2[i]:
            return -1
        elif parts1[i] > parts2[i]:
            return 1
    
    # If all components match, shorter OID comes first
    return len(parts1) - len(parts2)


# ===== AGENT MANAGEMENT FUNCTIONS =====

def find_free_port() -> int:
    """Find an available port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def wait_for_port(port: int, timeout: float = 5.0) -> bool:
    """Wait for a port to be listening"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            sock.connect(('localhost', port))
            sock.close()
            return True
        except (socket.timeout, ConnectionRefusedError):
            time.sleep(0.1)
    return False


def kill_process_on_port(port: int):
    """Kill any process listening on the given port"""
    if sys.platform == "win32":
        # Windows - more complex, might need admin rights
        try:
            subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True)
        except:
            pass
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

def start_agent(port: int) -> subprocess.Popen:
    """Start the SNMP agent on specified port"""
    env = os.environ.copy()
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    agent_path = os.path.join(parent_dir, AGENT_PATH)
    
    # If using solution, we need to ensure Python imports from solution directory
    if USE_SOLUTION:
        solution_dir = os.path.join(parent_dir, SOLUTION_DIR)
        # Add solution directory to PYTHONPATH so imports work correctly
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = solution_dir + os.pathsep + env['PYTHONPATH']
        else:
            env['PYTHONPATH'] = solution_dir
    
    proc = subprocess.Popen(
        [sys.executable, agent_path, str(port)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for agent to start listening
    if not wait_for_port(port, timeout=5.0):
        proc.terminate()
        stdout, stderr = proc.communicate()
        raise RuntimeError(f"Agent failed to start on port {port}: stdout={stdout.decode()}, stderr={stderr.decode()}")
    
    return proc

@pytest.fixture
def create_test_agent():
    """Fixture to create and cleanup test agent"""
    from contextlib import contextmanager
    
    agents = []
    
    @contextmanager
    def _create_agent():
        port = find_free_port()
        agent = start_agent(port)
        agents.append((agent, port))
        try:
            yield port
        finally:
            # Individual cleanup handled in context manager
            pass
    
    yield _create_agent
    
    # Cleanup all agents at end of test
    for agent, port in agents:
        try:
            agent.terminate()
            agent.wait(timeout=2)
        except:
            agent.kill()