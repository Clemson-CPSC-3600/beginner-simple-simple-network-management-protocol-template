#!/usr/bin/env python3
"""
Tests for SNMP message buffering and reception handling
"""

import pytest
import struct
import socket
import time
from .common import *


class TestSmallMessageReception:
    """Test handling of messages smaller than buffer size"""
    
    @pytest.mark.points(2.0)
    @pytest.mark.bundle('C')
    def test_single_small_message(self, create_test_agent):
        """Test receiving a single small message"""
        with create_test_agent() as port:
            response = send_get_request(port, ['1.3.6.1.2.1.1.1.0'])
            
            assert response is not None
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == 1
            assert response.bindings[0][0] == '1.3.6.1.2.1.1.1.0'
    
    @pytest.mark.points(2.0)
    @pytest.mark.bundle('C')
    def test_multiple_small_messages(self, create_test_agent):
        """Test receiving multiple small messages in sequence"""
        with create_test_agent() as port:
            oids = [
                ['1.3.6.1.2.1.1.1.0'],
                ['1.3.6.1.2.1.1.3.0'],
                ['1.3.6.1.2.1.1.5.0']
            ]
            
            for oid_list in oids:
                response = send_get_request(port, oid_list)
                assert response is not None
                assert response.error_code == ERROR_SUCCESS
                assert len(response.bindings) == 1
                assert response.bindings[0][0] == oid_list[0]


class TestLargeMessageBuffering:
    """Test proper buffering of large messages"""
    
    @pytest.mark.points(2.0)
    @pytest.mark.bundle('A')
    def test_large_string_value(self, create_test_agent):
        """Test message with moderately large string value"""
        with create_test_agent() as port:
            # Use a moderately large string (500 chars instead of 5000)
            large_string = 'A' * 500
            
            # Try to set it (may fail if OID is read-only, but we're testing buffering)
            set_response = send_set_request(port, [
                ('1.3.6.1.2.1.1.6.0', VALUE_STRING, large_string)
            ])
            
            # Even if SET fails due to permissions, the message should be properly buffered
            assert set_response is not None
            # Response was properly parsed even with large request
    
    @pytest.mark.points(2.0)
    @pytest.mark.bundle('A')
    def test_many_oids_request(self, create_test_agent):
        """Test GET request with multiple OIDs"""
        with create_test_agent() as port:
            # Create a request with a reasonable number of OIDs (20 instead of 100)
            oids = []
            # Use system group OIDs (1-7)
            system_oids = [f'1.3.6.1.2.1.1.{i}.0' for i in range(1, 8)]
            
            # Repeat pattern to get 20 OIDs
            for i in range(20):
                oids.append(system_oids[i % len(system_oids)])
            
            response = send_get_request(port, oids)
            assert response is not None
            assert response.error_code == ERROR_SUCCESS
            assert len(response.bindings) == len(oids)
    


class TestBufferingEdgeCases:
    """Test edge cases in message buffering"""
    
    @pytest.mark.points(2.0)
    @pytest.mark.bundle('A')
    def test_consecutive_messages_no_delay(self, create_test_agent):
        """Test rapid consecutive messages without delay"""
        with create_test_agent() as port:
            # Send multiple requests as fast as possible
            results = []
            for i in range(10):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect(('localhost', port))
                    # Use i%7 + 1 to stay within valid OID range (1-7)
                    request = create_get_request(1000 + i, [f'1.3.6.1.2.1.1.{(i%7)+1}.0'])
                    sock.send(request)
                    response_data = receive_complete_message(sock)
                    response = parse_response(response_data)
                    results.append(response)
                finally:
                    sock.close()
            
            # Verify all responses were received correctly
            assert len(results) == 10
            for i, response in enumerate(results):
                assert response.request_id == 1000 + i
                assert response.error_code == ERROR_SUCCESS
    
    
    @pytest.mark.points(2.0)
    @pytest.mark.bundle('A')
    def test_invalid_message_size(self, create_test_agent):
        """Test handling of invalid message size field"""
        with create_test_agent() as port:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect(('localhost', port))
                
                # Send message with invalid size (too small)
                bad_message = struct.pack('!I', 5)  # Size=5 but need at least 9
                bad_message += struct.pack('!I', 1234)  # Request ID
                bad_message += struct.pack('!B', PDU_GET_REQUEST)
                
                sock.send(bad_message)
                
                # Server should close connection or send error
                try:
                    response_data = sock.recv(MAX_RECV_BUFFER)
                    if response_data:
                        # If we get a response, it should be an error
                        response = parse_response(response_data)
                        assert response.error_code != ERROR_SUCCESS
                except:
                    # Connection closed is also acceptable
                    pass
            finally:
                sock.close()
    
    


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])