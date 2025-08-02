#!/usr/bin/env python3
"""
Tests for basic SNMP error handling
Simplified version focusing on essential error cases only
"""

import pytest
import socket
from .common import *


class TestBasicErrors:
    """Test basic application-level error handling"""
    
    @pytest.mark.points(2.0)
    @pytest.mark.bundle('B')
    def test_error_code_propagation(self, create_test_agent):
        """Test that basic error codes are properly returned"""
        with create_test_agent() as port:
            # Test non-existent OID
            response = send_get_request(port, ['9.9.9.9.9'])
            assert response.error_code == ERROR_NO_SUCH_OID
            assert len(response.bindings) == 0  # No bindings on error
            
            # Test SET on read-only OID (sysUpTime)
            readonly_oid = '1.3.6.1.2.1.1.3.0'
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect(('localhost', port))
                request = create_set_request(1002, [(readonly_oid, VALUE_INTEGER, 0)])
                sock.send(request)
                response_data = receive_complete_message(sock)
                response = parse_response(response_data)
                
                assert response.error_code == ERROR_READ_ONLY
                assert len(response.bindings) == 0  # No bindings on error
            finally:
                sock.close()
    
    @pytest.mark.points(1.0)
    @pytest.mark.bundle('B')
    def test_request_id_preserved_on_error(self, create_test_agent):
        """Test that request ID is preserved in error responses"""
        with create_test_agent() as port:
            test_ids = [1, 12345, 0x7FFFFFFF]
            
            for req_id in test_ids:
                # Create request that will cause error (non-existent OID)
                response = send_get_request(port, ['invalid.oid'], request_id=req_id)
                
                assert response.request_id == req_id
                assert response.error_code == ERROR_NO_SUCH_OID
    
    @pytest.mark.points(1.0)
    @pytest.mark.bundle('A')
    def test_recovery_after_error(self, create_test_agent):
        """Test that agent continues working normally after handling errors"""
        with create_test_agent() as port:
            # First, cause an error with non-existent OID
            error_response = send_get_request(port, ['invalid.oid'])
            assert error_response.error_code == ERROR_NO_SUCH_OID
            
            # Then, send a valid request
            valid_response = send_get_request(port, ['1.3.6.1.2.1.1.1.0'])
            assert valid_response.error_code == ERROR_SUCCESS
            assert len(valid_response.bindings) == 1
            
            # Verify agent continues working normally
            response = send_get_request(port, ['1.3.6.1.2.1.1.5.0'])
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])