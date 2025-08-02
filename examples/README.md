# Examples Directory

This directory contains reference materials to help you understand and test your SNMP implementation.

## Files in This Directory

### 📝 expected_outputs.txt
Human-readable examples showing the expected output for various SNMP manager commands. Use this to verify your manager's display format is correct.

**Example usage:**
```bash
# Compare your output with the expected output
python snmp_manager.py get localhost:1161 1.3.6.1.2.1.1.1.0
# Then check expected_outputs.txt to see if your output matches
```

### 📊 expected_outputs.json
Same as above but in JSON format for programmatic testing. You can write scripts to automatically verify your output.

### 🧪 Testing Your Basic Functions
To test your encoding/decoding functions, use the built-in test suite:

```bash
# Test OID encoding/decoding
pytest tests/ -k "test_oid" -v

# Test value encoding
pytest tests/ -k "test_value_type" -v

# Test message structure
pytest tests/ -k "test_header" -v
```

These tests will verify your basic functions work correctly before you move on to full protocol implementation.

## Quick Testing Script

You can test your implementation against the example packets:

```python
# Test that you can parse all example packets
import glob
from snmp_protocol import unpack_message

for filename in glob.glob('packet_captures/*.bin'):
    with open(filename, 'rb') as f:
        data = f.read()
    try:
        msg = unpack_message(data)
        print(f"✓ Successfully parsed {filename}")
    except Exception as e:
        print(f"✗ Failed to parse {filename}: {e}")
```

## Packet Captures

See the `packet_captures/` directory for:
- Binary packet files (`.bin`) - Real SNMP packet data
- Hex dumps (`.hex`) - Human-readable packet analysis
- README with detailed packet descriptions

## Using These Examples

### Step 1: Start with Test Vectors
Begin by implementing the basic encoding functions and verify them against `test_vectors.md`.

### Step 2: Parse Example Packets
Try parsing the packets in `packet_captures/*.bin` with your implementation.

### Step 3: Match Expected Outputs
Run your manager with the commands shown in `expected_outputs.txt` and verify your output matches.

### Step 4: Handle Edge Cases
The examples include error cases (non-existent OIDs, read-only errors) to test your error handling.

## Regenerating Examples

If you need to regenerate these examples (e.g., if you modify the protocol), run:

```bash
python3 generate_examples.py
```

This will recreate all example files with fresh data.

## Tips

1. **Start Small**: Begin with the single OID examples before moving to multiple OIDs or bulk requests
2. **Check Byte Order**: Many issues come from incorrect byte ordering - the hex dumps help debug this
3. **Use the JSON Files**: Write automated tests using the JSON files for faster development
4. **Compare Hex Values**: When debugging, convert your bytes to hex and compare with the expected values character by character

Good luck with your implementation! 🚀