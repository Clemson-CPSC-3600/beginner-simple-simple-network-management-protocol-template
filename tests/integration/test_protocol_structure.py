#!/usr/bin/env python3
"""
Tests for SNMP protocol message structure, encoding, and basic format
"""

import pytest
import struct
from .common import *


class TestMessageHeaderStructure:
    """Tests for basic message header structure"""
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_header_format(self):
        """Test that message header follows the specified format"""
        request_id = 0x12345678
        pdu_type = PDU_GET_REQUEST
        oids = ['1.3.6.1.2.1.1.1.0']
        
        message = create_get_request(request_id, oids)
        
        # Check minimum size
        assert len(message) >= MESSAGE_HEADER_SIZE
        
        # Verify header fields
        size, req_id, pdu = struct.unpack('!IIB', message[:9])
        assert size == len(message)
        assert req_id == request_id
        assert pdu == pdu_type
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_size_field(self):
        """Test that size field correctly represents total message size"""
        for num_oids in [1, 3, 5]:
            oids = [f'1.3.6.1.2.1.1.{i}.0' for i in range(num_oids)]
            message = create_get_request(1234, oids)
            
            size_field = struct.unpack('!I', message[:4])[0]
            assert size_field == len(message)
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_request_id_field(self):
        """Test that request ID is preserved correctly"""
        test_ids = [0, 1, 0x7FFFFFFF, 0xFFFFFFFF]
        
        for req_id in test_ids:
            message = create_get_request(req_id, ['1.3.6.1.2.1.1.1.0'])
            stored_id = struct.unpack('!I', message[4:8])[0]
            assert stored_id == req_id
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_pdu_type_field(self):
        """Test PDU type field for different message types"""
        # Test GET request
        get_msg = create_get_request(1234, ['1.3.6.1.2.1.1.1.0'])
        assert get_msg[8] == PDU_GET_REQUEST
        
        # Test SET request
        set_msg = create_set_request(1234, [('1.3.6.1.2.1.1.5.0', VALUE_STRING, 'test')])
        assert set_msg[8] == PDU_SET_REQUEST




class TestMessageSizeCalculation:
    """Test message size calculations"""
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_single_oid_size(self):
        """Test size calculation with single OID"""
        oid = '1.3.6.1.2.1.1.1.0'
        message = create_get_request(1234, [oid])
        
        expected_size = (
            4 +  # Size field
            4 +  # Request ID
            1 +  # PDU type
            1 +  # Binding count
            1 +  # OID length
            len(encode_oid(oid))  # OID bytes
        )
        
        assert len(message) == expected_size
        assert struct.unpack('!I', message[:4])[0] == expected_size
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_multiple_oid_size(self):
        """Test size calculation with multiple OIDs"""
        oids = ['1.3.6.1.2.1.1.1.0', '1.3.6.1.2.1.1.3.0', '1.3.6.1.2.1.1.5.0']
        message = create_get_request(1234, oids)
        
        expected_size = 9 + 1  # Header + binding count
        for oid in oids:
            expected_size += 1 + len(encode_oid(oid))
        
        assert len(message) == expected_size
        assert struct.unpack('!I', message[:4])[0] == expected_size
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_set_request_size(self):
        """Test size calculation for SET requests"""
        bindings = [
            ('1.3.6.1.2.1.1.5.0', VALUE_STRING, 'hostname'),
            ('1.3.6.1.2.1.1.6.0', VALUE_INTEGER, 42)
        ]
        message = create_set_request(1234, bindings)
        
        expected_size = 9 + 1  # Header + binding count
        for oid, vtype, value in bindings:
            value_bytes = encode_value(value, vtype)
            expected_size += (
                1 + len(encode_oid(oid)) +  # OID length + OID
                1 +  # Value type
                2 +  # Value length field
                len(value_bytes)  # Value
            )
        
        assert len(message) == expected_size
        assert struct.unpack('!I', message[:4])[0] == expected_size


class TestOIDEncoding:
    """Test OID string to bytes conversion"""
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_simple_oid_encoding(self):
        """Test encoding of simple OIDs"""
        test_cases = [
            ('1.3.6.1', bytes([1, 3, 6, 1])),
            ('1.3.6.1.2.1.1.1.0', bytes([1, 3, 6, 1, 2, 1, 1, 1, 0])),
            ('0.0', bytes([0, 0])),
            ('255.255.255', bytes([255, 255, 255]))
        ]
        
        for oid_str, expected in test_cases:
            assert encode_oid(oid_str) == expected
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_oid_decoding(self):
        """Test OID bytes to string conversion"""
        test_cases = [
            (bytes([1, 3, 6, 1]), '1.3.6.1'),
            (bytes([1, 3, 6, 1, 2, 1, 1, 1, 0]), '1.3.6.1.2.1.1.1.0'),
            (bytes([0]), '0'),
            (bytes([255, 0, 128]), '255.0.128')
        ]
        
        for oid_bytes, expected in test_cases:
            assert decode_oid(oid_bytes) == expected
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_oid_length_encoding(self):
        """Test that OID length is encoded correctly"""
        oids = [
            '1',  # 1 byte
            '1.3.6.1.2.1',  # 6 bytes
            '1.3.6.1.2.1.1.1.0.0.0.0.0.0.0'  # 15 bytes
        ]
        
        for oid in oids:
            message = create_get_request(1234, [oid])
            # OID length is at offset 10 (after header and binding count)
            oid_length = message[10]
            assert oid_length == len(encode_oid(oid))


class TestValueTypeEncoding:
    """Test encoding of different value types"""
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_integer_encoding(self):
        """Test INTEGER value type encoding"""
        test_values = [-2147483648, -1, 0, 1, 2147483647]
        
        for value in test_values:
            encoded = encode_value(value, VALUE_INTEGER)
            assert len(encoded) == 4
            decoded = struct.unpack('!i', encoded)[0]
            assert decoded == value
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_string_encoding(self):
        """Test STRING value type encoding"""
        test_strings = [
            '',
            'test',
            'A' * 255,
            'Special chars: !@#$%',
            'Unicode: café'
        ]
        
        for string in test_strings:
            encoded = encode_value(string, VALUE_STRING)
            assert encoded == string.encode('utf-8')
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_counter_encoding(self):
        """Test COUNTER value type encoding"""
        test_values = [0, 1, 1000000, 4294967295]
        
        for value in test_values:
            encoded = encode_value(value, VALUE_COUNTER)
            assert len(encoded) == 4
            decoded = struct.unpack('!I', encoded)[0]
            assert decoded == value
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_timeticks_encoding(self):
        """Test TIMETICKS value type encoding"""
        test_values = [0, 100, 360000, 4294967295]
        
        for value in test_values:
            encoded = encode_value(value, VALUE_TIMETICKS)
            assert len(encoded) == 4
            decoded = struct.unpack('!I', encoded)[0]
            assert decoded == value
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_value_type_in_message(self):
        """Test that value types are correctly included in SET messages"""
        bindings = [
            ('1.3.6.1.2.1.1.1.0', VALUE_STRING, 'test'),
            ('1.3.6.1.2.1.1.2.0', VALUE_INTEGER, 42),
            ('1.3.6.1.2.1.1.3.0', VALUE_COUNTER, 1000),
            ('1.3.6.1.2.1.1.4.0', VALUE_TIMETICKS, 360000)
        ]
        
        message = create_set_request(1234, bindings)
        
        # Parse message to verify value types
        offset = 10  # Skip header and binding count
        
        for oid, expected_type, value in bindings:
            oid_len = message[offset]
            offset += 1 + oid_len  # Skip OID length and OID
            
            actual_type = message[offset]
            assert actual_type == expected_type
            
            offset += 1  # Skip value type
            value_len = struct.unpack('!H', message[offset:offset+2])[0]
            offset += 2 + value_len  # Skip value length and value


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])