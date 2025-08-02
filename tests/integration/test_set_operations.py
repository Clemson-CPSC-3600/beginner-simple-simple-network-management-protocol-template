#!/usr/bin/env python3
"""
Tests for SNMP SET operations
"""

import pytest
from .common import *


class TestValidSetOperations:
    """Test successful SET operations"""
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_set_string_value(self, create_test_agent):
        """Test SET operation with STRING value"""
        with create_test_agent() as port:
            # Find a writable string OID from MIB_PERMISSIONS
            writable_oid = None
            for oid, perm in MIB_PERMISSIONS.items():
                if perm == 'read-write' and MIB_DATABASE.get(oid, ('', ''))[0] == 'STRING':
                    writable_oid = oid
                    break
            
            if not writable_oid:
                pytest.skip("No writable STRING OID in MIB")
            
            # Set new value
            new_value = "TestHostName123"
            response = send_set_request(port, [(writable_oid, VALUE_STRING, new_value)])
            
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == 1
            
            # Verify the value was set
            oid, value_type, value = response.bindings[0]
            assert oid == writable_oid
            assert value_type == VALUE_STRING
            assert value == new_value
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_set_integer_value(self, create_test_agent):
        """Test SET operation with INTEGER value"""
        with create_test_agent() as port:
            # Find a writable integer OID
            writable_oid = None
            for oid, perm in MIB_PERMISSIONS.items():
                if perm == 'read-write' and MIB_DATABASE.get(oid, ('', ''))[0] == 'INTEGER':
                    writable_oid = oid
                    break
            
            if not writable_oid:
                pytest.skip("No writable INTEGER OID in MIB")
            
            # Set new value
            new_value = 42
            response = send_set_request(port, [(writable_oid, VALUE_INTEGER, new_value)])
            
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == 1
            
            # Verify the value was set
            oid, value_type, value = response.bindings[0]
            assert oid == writable_oid
            assert value_type == VALUE_INTEGER
            assert value == new_value
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_set_persistence(self, create_test_agent):
        """Test that SET values persist across GET requests"""
        with create_test_agent() as port:
            # Find a writable OID
            writable_oid = None
            for oid, perm in MIB_PERMISSIONS.items():
                if perm == 'read-write':
                    writable_oid = oid
                    break
            
            if not writable_oid:
                pytest.skip("No writable OID in MIB")
            
            # Determine value type and new value
            original_type, _ = MIB_DATABASE.get(writable_oid, ('STRING', ''))
            if original_type == 'STRING':
                new_value = "PersistentValue"
                value_type = VALUE_STRING
            elif original_type == 'INTEGER':
                new_value = 999
                value_type = VALUE_INTEGER
            else:
                pytest.skip(f"Unsupported type for testing: {original_type}")
            
            # Set the value
            set_response = send_set_request(port, [(writable_oid, value_type, new_value)])
            assert set_response.error_code == ERROR_SUCCESS
            
            # Get the value back
            get_response = send_get_request(port, [writable_oid])
            assert get_response.error_code == ERROR_SUCCESS
            assert len(get_response.bindings) == 1
            
            # Verify it matches what we set
            _, _, retrieved_value = get_response.bindings[0]
            assert retrieved_value == new_value
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_multiple_set_operations(self, create_test_agent):
        """Test SET with multiple variable bindings"""
        with create_test_agent() as port:
            # Find multiple writable OIDs
            writable_bindings = []
            for oid, perm in MIB_PERMISSIONS.items():
                if perm == 'read-write' and len(writable_bindings) < 3:
                    vtype, _ = MIB_DATABASE.get(oid, ('STRING', ''))
                    if vtype == 'STRING':
                        writable_bindings.append((oid, VALUE_STRING, f"Value{len(writable_bindings)}"))
                    elif vtype == 'INTEGER':
                        writable_bindings.append((oid, VALUE_INTEGER, 100 + len(writable_bindings)))
            
            if len(writable_bindings) < 2:
                pytest.skip("Not enough writable OIDs for multi-SET test")
            
            # Set multiple values
            response = send_set_request(port, writable_bindings)
            
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == len(writable_bindings)
            
            # Verify all values were set
            for i, (expected_oid, expected_type, expected_value) in enumerate(writable_bindings):
                oid, value_type, value = response.bindings[i]
                assert oid == expected_oid
                assert value == expected_value


class TestSetErrorHandling:
    """Test error handling in SET operations"""
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_set_readonly_oid(self, create_test_agent):
        """Test SET on read-only OID returns error"""
        with create_test_agent() as port:
            # Find a read-only OID
            readonly_oid = None
            for oid, perm in MIB_PERMISSIONS.items():
                if perm == 'read-only':
                    readonly_oid = oid
                    break
            
            if not readonly_oid:
                # If no explicit read-only in permissions, use a system OID
                readonly_oid = '1.3.6.1.2.1.1.3.0'  # sysUpTime is always read-only
            
            response = send_set_request(port, [(readonly_oid, VALUE_INTEGER, 0)])
            
            assert response.error_code == ERROR_READ_ONLY
            assert len(response.bindings) == 0
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_set_wrong_type(self, create_test_agent):
        """Test SET with wrong value type"""
        with create_test_agent() as port:
            # Find a writable OID with known type
            test_oid = None
            correct_type = None
            wrong_type = None
            wrong_value = None
            
            for oid, perm in MIB_PERMISSIONS.items():
                if perm == 'read-write':
                    vtype, _ = MIB_DATABASE.get(oid, (None, None))
                    if vtype == 'STRING':
                        test_oid = oid
                        correct_type = 'STRING'
                        wrong_type = VALUE_INTEGER
                        wrong_value = 12345
                        break
                    elif vtype == 'INTEGER':
                        test_oid = oid
                        correct_type = 'INTEGER'
                        wrong_type = VALUE_STRING
                        wrong_value = "NotANumber"
                        break
            
            if not test_oid:
                pytest.skip("No suitable writable OID for type mismatch test")
            
            response = send_set_request(port, [(test_oid, wrong_type, wrong_value)])
            
            assert response.error_code == ERROR_WRONG_TYPE
            assert len(response.bindings) == 0
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_set_non_existent_oid(self, create_test_agent):
        """Test SET on non-existent OID"""
        with create_test_agent() as port:
            response = send_set_request(port, [
                ('9.9.9.9.9.9.9', VALUE_STRING, 'test')
            ])
            
            assert response.error_code == ERROR_NO_SUCH_OID
            assert len(response.bindings) == 0
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_set_empty_string(self, create_test_agent):
        """Test SET with empty string value"""
        with create_test_agent() as port:
            # Find a writable string OID
            writable_oid = None
            for oid, perm in MIB_PERMISSIONS.items():
                if perm == 'read-write' and MIB_DATABASE.get(oid, ('', ''))[0] == 'STRING':
                    writable_oid = oid
                    break
            
            if not writable_oid:
                pytest.skip("No writable STRING OID in MIB")
            
            # Set empty string
            response = send_set_request(port, [(writable_oid, VALUE_STRING, '')])
            
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == 1
            assert response.bindings[0][2] == ''
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_set_boundary_integer_values(self, create_test_agent):
        """Test SET with boundary integer values"""
        with create_test_agent() as port:
            # Find a writable integer OID
            writable_oid = None
            for oid, perm in MIB_PERMISSIONS.items():
                if perm == 'read-write' and MIB_DATABASE.get(oid, ('', ''))[0] == 'INTEGER':
                    writable_oid = oid
                    break
            
            if not writable_oid:
                pytest.skip("No writable INTEGER OID in MIB")
            
            # Test boundary values
            test_values = [-2147483648, -1, 0, 1, 2147483647]
            
            for test_value in test_values:
                response = send_set_request(port, [(writable_oid, VALUE_INTEGER, test_value)])
                assert response.error_code == ERROR_SUCCESS
                assert response.bindings[0][2] == test_value
    
    


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])