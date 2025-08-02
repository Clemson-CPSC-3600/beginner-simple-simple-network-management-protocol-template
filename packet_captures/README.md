# Packet Capture Examples

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
