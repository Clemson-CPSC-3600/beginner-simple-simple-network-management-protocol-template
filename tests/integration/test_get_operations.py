#!/usr/bin/env python3
"""
Tests for SNMP GET operations
"""

import pytest
import time
from .common import *


class TestGetOperations:
    """Test basic Get request functionality"""
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_single_oid_get(self, create_test_agent):
        """Test GET request with single OID"""
        with create_test_agent() as port:
            response = send_get_request(port, ['1.3.6.1.2.1.1.1.0'])
            
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == 1
            
            oid, value_type, value = response.bindings[0]
            assert oid == '1.3.6.1.2.1.1.1.0'
            assert value_type == VALUE_STRING
            assert isinstance(value, str)
            assert len(value) > 0
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('C')
    def test_multiple_oid_get(self, create_test_agent):
        """Test GET request with multiple OIDs"""
        with create_test_agent() as port:
            oids = [
                '1.3.6.1.2.1.1.1.0',  # sysDescr
                '1.3.6.1.2.1.1.3.0',  # sysUpTime
                '1.3.6.1.2.1.1.5.0'   # sysName
            ]
            response = send_get_request(port, oids)
            
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == 3
            
            # Check each binding
            for i, binding in enumerate(response.bindings):
                oid, value_type, value = binding
                assert oid == oids[i]
                
                if i == 0:  # sysDescr
                    assert value_type == VALUE_STRING
                elif i == 1:  # sysUpTime
                    assert value_type == VALUE_TIMETICKS
                elif i == 2:  # sysName
                    assert value_type == VALUE_STRING
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_non_existent_oid(self, create_test_agent):
        """Test GET request with non-existent OID"""
        with create_test_agent() as port:
            response = send_get_request(port, ['1.2.3.4.5.6.7.8.9'])
            
            assert response.error_code == ERROR_NO_SUCH_OID
            assert len(response.bindings) == 0
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_mixed_valid_invalid_oids(self, create_test_agent):
        """Test GET with mix of valid and invalid OIDs"""
        with create_test_agent() as port:
            oids = [
                '1.3.6.1.2.1.1.1.0',  # Valid
                '1.2.3.4.5',          # Invalid
                '1.3.6.1.2.1.1.5.0'   # Valid
            ]
            response = send_get_request(port, oids)
            
            # Should fail on first invalid OID
            assert response.error_code == ERROR_NO_SUCH_OID
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_empty_oid_list(self, create_test_agent):
        """Test GET request with empty OID list"""
        with create_test_agent() as port:
            response = send_get_request(port, [])
            
            # Should succeed with no bindings
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == 0
    
    @pytest.mark.points(1.5)
    @pytest.mark.bundle('B')
    def test_duplicate_oids(self, create_test_agent):
        """Test GET request with duplicate OIDs"""
        with create_test_agent() as port:
            oids = [
                '1.3.6.1.2.1.1.1.0',
                '1.3.6.1.2.1.1.1.0',  # Duplicate
                '1.3.6.1.2.1.1.5.0'
            ]
            response = send_get_request(port, oids)
            
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == 3
            
            # Both duplicates should return same value
            assert response.bindings[0][2] == response.bindings[1][2]



if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])