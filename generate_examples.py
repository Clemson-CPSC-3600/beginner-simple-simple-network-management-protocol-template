#!/usr/bin/env python3
"""
Generate example packet captures and expected outputs for SNMP assignment
This script creates binary packet files and text output examples that students
can use for reference and debugging.
"""

import struct
import os
import sys
import json
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Constants matching the protocol
class PDUType:
    GET_REQUEST = 0xA0
    GET_RESPONSE = 0xA1
    SET_REQUEST = 0xA3
    GET_BULK_REQUEST = 0xA5

class ValueType:
    INTEGER = 0x02
    STRING = 0x04
    COUNTER = 0x41
    TIMETICKS = 0x43

class ErrorCode:
    SUCCESS = 0
    NO_SUCH_OID = 1
    BAD_VALUE = 2
    READ_ONLY = 3

def encode_oid(oid_string: str) -> bytes:
    """Convert OID string to bytes"""
    return bytes([int(x) for x in oid_string.split('.')])

def create_directories():
    """Create necessary directories for examples"""
    dirs = ['packet_captures', 'examples']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"Created/verified directory: {dir_name}/")

# ============================================================================
# PACKET CAPTURE GENERATION
# ============================================================================

def generate_get_request_packet(request_id: int, oids: list) -> bytes:
    """Generate a GetRequest packet"""
    # Build payload
    payload = struct.pack('!B', len(oids))  # oid_count
    for oid in oids:
        oid_bytes = encode_oid(oid)
        payload += struct.pack('!B', len(oid_bytes))
        payload += oid_bytes
    
    # Build message
    total_size = 9 + len(payload)
    message = struct.pack('!IIB', total_size, request_id, PDUType.GET_REQUEST)
    message += payload
    
    return message

def generate_get_response_packet(request_id: int, error_code: int, bindings: list) -> bytes:
    """Generate a GetResponse packet"""
    # Build payload
    payload = struct.pack('!B', len(bindings))  # binding_count
    
    for oid, value_type, value in bindings:
        oid_bytes = encode_oid(oid)
        
        # Encode value based on type
        if value_type == ValueType.INTEGER:
            value_bytes = struct.pack('!i', value)
        elif value_type == ValueType.STRING:
            value_bytes = value.encode('utf-8') if isinstance(value, str) else value
        elif value_type == ValueType.COUNTER:
            value_bytes = struct.pack('!I', value)
        elif value_type == ValueType.TIMETICKS:
            value_bytes = struct.pack('!I', value)
        else:
            value_bytes = b''
        
        # Add to payload
        payload += struct.pack('!B', len(oid_bytes))
        payload += oid_bytes
        payload += struct.pack('!B', value_type)
        payload += struct.pack('!H', len(value_bytes))
        payload += value_bytes
    
    # Build message
    total_size = 10 + len(payload)
    message = struct.pack('!IIB', total_size, request_id, PDUType.GET_RESPONSE)
    message += struct.pack('!B', error_code)
    message += payload
    
    return message

def generate_set_request_packet(request_id: int, bindings: list) -> bytes:
    """Generate a SetRequest packet"""
    # Build payload
    payload = struct.pack('!B', len(bindings))  # oid_count
    
    for oid, value_type, value in bindings:
        oid_bytes = encode_oid(oid)
        
        # Encode value
        if value_type == ValueType.INTEGER:
            value_bytes = struct.pack('!i', value)
        elif value_type == ValueType.STRING:
            value_bytes = value.encode('utf-8') if isinstance(value, str) else value
        elif value_type == ValueType.COUNTER:
            value_bytes = struct.pack('!I', value)
        elif value_type == ValueType.TIMETICKS:
            value_bytes = struct.pack('!I', value)
        else:
            value_bytes = b''
        
        # Add to payload
        payload += struct.pack('!B', len(oid_bytes))
        payload += oid_bytes
        payload += struct.pack('!B', value_type)
        payload += struct.pack('!H', len(value_bytes))
        payload += value_bytes
    
    # Build message
    total_size = 9 + len(payload)
    message = struct.pack('!IIB', total_size, request_id, PDUType.SET_REQUEST)
    message += payload
    
    return message

def generate_bulk_request_packet(request_id: int, start_oid: str, max_repetitions: int) -> bytes:
    """Generate a GetBulkRequest packet"""
    oid_bytes = encode_oid(start_oid)
    
    # Build payload
    payload = struct.pack('!B', len(oid_bytes))
    payload += oid_bytes
    payload += struct.pack('!H', max_repetitions)
    
    # Build message
    total_size = 9 + len(payload)
    message = struct.pack('!IIB', total_size, request_id, PDUType.GET_BULK_REQUEST)
    message += payload
    
    return message

def create_packet_captures():
    """Create example packet capture files"""
    print("\nGenerating packet captures...")
    
    # Example 1: Simple GetRequest for system description
    packet = generate_get_request_packet(1001, ['1.3.6.1.2.1.1.1.0'])
    filename = 'packet_captures/get_request_single_oid.bin'
    with open(filename, 'wb') as f:
        f.write(packet)
    print(f"  Created: {filename} ({len(packet)} bytes)")
    
    # Example 2: GetRequest for multiple OIDs
    packet = generate_get_request_packet(1002, [
        '1.3.6.1.2.1.1.1.0',  # sysDescr
        '1.3.6.1.2.1.1.3.0',  # sysUpTime
        '1.3.6.1.2.1.1.5.0'   # sysName
    ])
    filename = 'packet_captures/get_request_multiple_oids.bin'
    with open(filename, 'wb') as f:
        f.write(packet)
    print(f"  Created: {filename} ({len(packet)} bytes)")
    
    # Example 3: GetResponse with success
    packet = generate_get_response_packet(1001, ErrorCode.SUCCESS, [
        ('1.3.6.1.2.1.1.1.0', ValueType.STRING, 'Router Model X2000 - High Performance Edge Router')
    ])
    filename = 'packet_captures/get_response_success.bin'
    with open(filename, 'wb') as f:
        f.write(packet)
    print(f"  Created: {filename} ({len(packet)} bytes)")
    
    # Example 4: GetResponse with error
    packet = generate_get_response_packet(1003, ErrorCode.NO_SUCH_OID, [])
    filename = 'packet_captures/get_response_error.bin'
    with open(filename, 'wb') as f:
        f.write(packet)
    print(f"  Created: {filename} ({len(packet)} bytes)")
    
    # Example 5: SetRequest
    packet = generate_set_request_packet(2001, [
        ('1.3.6.1.2.1.1.5.0', ValueType.STRING, 'new-router-name')
    ])
    filename = 'packet_captures/set_request.bin'
    with open(filename, 'wb') as f:
        f.write(packet)
    print(f"  Created: {filename} ({len(packet)} bytes)")
    
    # Example 6: GetBulkRequest
    packet = generate_bulk_request_packet(3001, '1.3.6.1.2.1.2.2.1.10', 50)
    filename = 'packet_captures/get_bulk_request.bin'
    with open(filename, 'wb') as f:
        f.write(packet)
    print(f"  Created: {filename} ({len(packet)} bytes)")
    
    # Example 7: Large GetBulkResponse (for testing buffering)
    bindings = []
    for i in range(1, 51):
        oid = f'1.3.6.1.2.1.2.2.1.10.{i}'
        value = 1000000 * i  # Some counter value
        bindings.append((oid, ValueType.COUNTER, value))
    
    packet = generate_get_response_packet(3001, ErrorCode.SUCCESS, bindings)
    filename = 'packet_captures/get_bulk_response_large.bin'
    with open(filename, 'wb') as f:
        f.write(packet)
    print(f"  Created: {filename} ({len(packet)} bytes) - Tests buffering!")

# ============================================================================
# EXPECTED OUTPUT GENERATION
# ============================================================================

def create_expected_outputs():
    """Create expected output examples for different operations"""
    print("\nGenerating expected outputs...")
    
    outputs = []
    
    # Example 1: GET single OID
    outputs.append({
        'command': 'python snmp_manager.py get localhost:1161 1.3.6.1.2.1.1.1.0',
        'output': '1.3.6.1.2.1.1.1.0 = Router Model X2000 - High Performance Edge Router'
    })
    
    # Example 2: GET multiple OIDs
    outputs.append({
        'command': 'python snmp_manager.py get localhost:1161 1.3.6.1.2.1.1.1.0 1.3.6.1.2.1.1.3.0 1.3.6.1.2.1.1.5.0',
        'output': '''1.3.6.1.2.1.1.1.0 = Router Model X2000 - High Performance Edge Router
1.3.6.1.2.1.1.3.0 = 452300 (1 hours, 15 minutes, 23.00 seconds)
1.3.6.1.2.1.1.5.0 = router-main'''
    })
    
    # Example 3: GET non-existent OID
    outputs.append({
        'command': 'python snmp_manager.py get localhost:1161 1.3.6.1.2.1.1.99.0',
        'output': 'Error: No such OID exists'
    })
    
    # Example 4: SET operation (success)
    outputs.append({
        'command': 'python snmp_manager.py set localhost:1161 1.3.6.1.2.1.1.5.0 string "new-router-name"',
        'output': '''Set operation successful:
1.3.6.1.2.1.1.5.0 = new-router-name'''
    })
    
    # Example 5: SET operation (read-only error)
    outputs.append({
        'command': 'python snmp_manager.py set localhost:1161 1.3.6.1.2.1.1.3.0 integer 0',
        'output': 'Error: OID is read-only'
    })
    
    # Example 6: BULK operation
    outputs.append({
        'command': 'python snmp_manager.py bulk localhost:1161 1.3.6.1.2.1.2.2.1.10 5',
        'output': '''Requesting up to 5 OIDs starting after 1.3.6.1.2.1.2.2.1.10...
Received 5 OIDs in 0.012 seconds (156 bytes)
------------------------------------------------------------
1.3.6.1.2.1.2.2.1.10.1 = 3,456,789,012
1.3.6.1.2.1.2.2.1.10.2 = 1,876,543,210
1.3.6.1.2.1.2.2.1.10.3 = 567,890
1.3.6.1.2.1.2.2.1.11.1 = 23,456,789
1.3.6.1.2.1.2.2.1.11.2 = 8,765,432'''
    })
    
    # Write to file
    filename = 'examples/expected_outputs.txt'
    with open(filename, 'w') as f:
        f.write("SNMP Manager Expected Outputs\n")
        f.write("=" * 80 + "\n\n")
        
        for i, example in enumerate(outputs, 1):
            f.write(f"Example {i}:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Command: {example['command']}\n")
            f.write(f"Output:\n{example['output']}\n\n")
    
    print(f"  Created: {filename}")
    
    # Create JSON version for programmatic use
    filename = 'examples/expected_outputs.json'
    with open(filename, 'w') as f:
        json.dump(outputs, f, indent=2)
    print(f"  Created: {filename}")

# ============================================================================
# PACKET ANALYSIS FILES
# ============================================================================

def create_packet_analysis():
    """Create human-readable packet analysis files"""
    print("\nGenerating packet analysis files...")
    
    filename = 'packet_captures/README.md'
    with open(filename, 'w') as f:
        f.write("""# Packet Capture Examples

This directory contains example SNMP packets in binary format. These can be used to:
1. Understand the correct packet format
2. Test your parsing code
3. Debug your implementation

## File Descriptions

### get_request_single_oid.bin
A simple GetRequest for one OID (system description).
- Request ID: 1001
- OID: 1.3.6.1.2.1.1.1.0

**Hex dump:**
```
00 00 00 16  # Total size: 22 bytes
00 00 03 e9  # Request ID: 1001
a0           # PDU Type: GET_REQUEST
01           # OID count: 1
09           # OID length: 9
01 03 06 01 02 01 01 01 00  # OID: 1.3.6.1.2.1.1.1.0
```

### get_request_multiple_oids.bin
GetRequest for three OIDs.
- Request ID: 1002
- OIDs: sysDescr, sysUpTime, sysName

### get_response_success.bin
Successful GetResponse with system description.
- Request ID: 1001
- Error: SUCCESS (0)
- Contains one OID/value binding

### get_response_error.bin
GetResponse indicating OID not found.
- Request ID: 1003
- Error: NO_SUCH_OID (1)
- No bindings

### set_request.bin
SetRequest to change system name.
- Request ID: 2001
- OID: 1.3.6.1.2.1.1.5.0
- Value: "new-router-name" (STRING)

### get_bulk_request.bin
GetBulkRequest for interface statistics.
- Request ID: 3001
- Start OID: 1.3.6.1.2.1.2.2.1.10
- Max repetitions: 50

### get_bulk_response_large.bin
Large GetBulkResponse with 50 OIDs.
- Tests message buffering (>4KB)
- Contains interface counter values

## How to Use These Files

### Reading in Python:
```python
with open('packet_captures/get_request_single_oid.bin', 'rb') as f:
    packet_data = f.read()
    
# Now parse it with your code
message = unpack_message(packet_data)
```

### Viewing hex dump:
```bash
# Linux/Mac
hexdump -C get_request_single_oid.bin

# Or use Python
with open('get_request_single_oid.bin', 'rb') as f:
    data = f.read()
    print(' '.join(f'{b:02x}' for b in data))
```

### Testing your parser:
```python
# Test that you can parse all example packets
import glob

for filename in glob.glob('packet_captures/*.bin'):
    with open(filename, 'rb') as f:
        data = f.read()
    try:
        msg = unpack_message(data)
        print(f"✓ Successfully parsed {filename}")
    except Exception as e:
        print(f"✗ Failed to parse {filename}: {e}")
```
""")
    print(f"  Created: {filename}")

def create_hex_dumps():
    """Create hex dump files for each packet"""
    print("\nGenerating hex dumps...")
    
    import glob
    
    for bin_file in glob.glob('packet_captures/*.bin'):
        if 'README' in bin_file:
            continue
            
        hex_file = bin_file.replace('.bin', '.hex')
        
        with open(bin_file, 'rb') as f:
            data = f.read()
        
        with open(hex_file, 'w') as f:
            # Write header
            f.write(f"Hex dump of {os.path.basename(bin_file)}\n")
            f.write(f"Size: {len(data)} bytes\n")
            f.write("=" * 70 + "\n\n")
            
            # Write hex dump with ASCII
            for i in range(0, len(data), 16):
                # Hex part
                hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
                # ASCII part
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
                # Format line
                f.write(f"{i:08x}  {hex_str:<48}  |{ascii_str}|\n")
            
            f.write("\n")
            
            # Add protocol analysis
            f.write("Protocol Analysis:\n")
            f.write("-" * 40 + "\n")
            
            if len(data) >= 9:
                total_size = struct.unpack('!I', data[0:4])[0]
                request_id = struct.unpack('!I', data[4:8])[0]
                pdu_type = data[8]
                
                f.write(f"Total Size: {total_size} bytes\n")
                f.write(f"Request ID: {request_id}\n")
                f.write(f"PDU Type: 0x{pdu_type:02x}")
                
                pdu_names = {
                    0xA0: "GET_REQUEST",
                    0xA1: "GET_RESPONSE",
                    0xA3: "SET_REQUEST",
                    0xA5: "GET_BULK_REQUEST"
                }
                if pdu_type in pdu_names:
                    f.write(f" ({pdu_names[pdu_type]})")
                f.write("\n")
                
                if pdu_type == 0xA1 and len(data) >= 10:
                    error_code = data[9]
                    error_names = {
                        0: "SUCCESS",
                        1: "NO_SUCH_OID",
                        2: "BAD_VALUE",
                        3: "READ_ONLY"
                    }
                    f.write(f"Error Code: {error_code}")
                    if error_code in error_names:
                        f.write(f" ({error_names[error_code]})")
                    f.write("\n")
        
        print(f"  Created: {hex_file}")

# ============================================================================
# TEST DATA GENERATION
# ============================================================================

def create_test_vectors():
    """Create test vectors for students to verify their implementation"""
    print("\nGenerating test vectors...")
    
    test_vectors = {
        'oid_encoding': [
            {'input': '1.3.6.1.2.1.1.1.0', 
             'output': '010306010201010100',
             'description': 'System description OID'},
            {'input': '1.3.6.1.2.1.1.3.0',
             'output': '010306010201010300',
             'description': 'System uptime OID'},
            {'input': '1.3.6.1.2.1.2.2.1.10.1',
             'output': '0103060102010202010a01',
             'description': 'Interface 1 input octets'}
        ],
        'value_encoding': [
            {'type': 'INTEGER', 'value': 42, 'output': '0000002a',
             'description': 'Positive integer'},
            {'type': 'INTEGER', 'value': -1, 'output': 'ffffffff',
             'description': 'Negative integer'},
            {'type': 'STRING', 'value': 'test', 'output': '74657374',
             'description': 'Simple string'},
            {'type': 'COUNTER', 'value': 1234567890, 'output': '499602d2',
             'description': 'Large counter'},
            {'type': 'TIMETICKS', 'value': 360000, 'output': '00057e40',
             'description': 'One hour in timeticks'}
        ]
    }
    
    filename = 'examples/test_vectors.json'
    with open(filename, 'w') as f:
        json.dump(test_vectors, f, indent=2)
    print(f"  Created: {filename}")
    
    # Create human-readable version
    filename = 'examples/test_vectors.md'
    with open(filename, 'w') as f:
        f.write("# Test Vectors for SNMP Implementation\n\n")
        f.write("Use these test cases to verify your encoding/decoding functions.\n\n")
        
        f.write("## OID Encoding Tests\n\n")
        f.write("| Input OID | Expected Hex Output | Description |\n")
        f.write("|-----------|-------------------|-------------|\n")
        for test in test_vectors['oid_encoding']:
            f.write(f"| `{test['input']}` | `{test['output']}` | {test['description']} |\n")
        
        f.write("\n## Value Encoding Tests\n\n")
        f.write("| Type | Value | Expected Hex | Description |\n")
        f.write("|------|-------|--------------|-------------|\n")
        for test in test_vectors['value_encoding']:
            f.write(f"| {test['type']} | {test['value']} | `{test['output']}` | {test['description']} |\n")
    
    print(f"  Created: {filename}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all example files"""
    print("SNMP Example Generator")
    print("=" * 80)
    
    # Create directories
    create_directories()
    
    # Generate packet captures
    create_packet_captures()
    create_hex_dumps()
    create_packet_analysis()
    
    # Generate expected outputs
    create_expected_outputs()
    
    # Generate test vectors
    create_test_vectors()
    
    print("\n" + "=" * 80)
    print("✓ All example files generated successfully!")
    print("\nStudents can now:")
    print("  1. Examine packet_captures/*.bin to understand the protocol")
    print("  2. Read packet_captures/*.hex for human-readable format")
    print("  3. Check examples/expected_outputs.txt for correct program behavior")
    print("  4. Use examples/test_vectors.json to verify their functions")

if __name__ == "__main__":
    main()