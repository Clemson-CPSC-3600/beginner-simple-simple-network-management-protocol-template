"""
SNMP Protocol Implementation
Contains message classes and encoding/decoding logic for simplified SNMP
"""

import struct
import logging
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
from enum import IntEnum

# Protocol Constants
MESSAGE_HEADER_SIZE = 9  # total_size(4) + request_id(4) + pdu_type(1)
RESPONSE_HEADER_SIZE = 10  # MESSAGE_HEADER_SIZE + error_code(1)
MAX_RECV_BUFFER = 4096  # Maximum bytes to receive at once
MIN_MESSAGE_SIZE = 9  # Minimum valid message size
MAX_MESSAGE_SIZE = 65536  # Maximum message size (64KB) to prevent memory exhaustion
SIZE_FIELD_LENGTH = 4  # Length of the size field in bytes
REQUEST_ID_LENGTH = 4  # Length of request ID field
PDU_TYPE_LENGTH = 1  # Length of PDU type field in bytes
ERROR_CODE_LENGTH = 1  # Length of error code field in bytes
OID_COUNT_LENGTH = 1  # Length of OID count field in bytes
OID_LENGTH_FIELD = 1  # Length of OID length field in bytes
VALUE_TYPE_LENGTH = 1  # Length of value type field in bytes
VALUE_LENGTH_FIELD = 2  # Length of value length field in bytes
MAX_REPETITIONS_LENGTH = 2  # Length of max repetitions field in bytes
OID_COUNT_MAX = 255  # Maximum OIDs in a single request
MAX_REPETITIONS_MAX = 65535  # Maximum repetitions for bulk request
PDU_TYPE_OFFSET = 8  # Offset where PDU type is located in message
REQUEST_ID_OFFSET = 4  # Offset where request ID starts in message

# Configure module logger
logger = logging.getLogger('snmp.protocol')

# PDU Types
class PDUType(IntEnum):
    GET_REQUEST = 0xA0
    GET_RESPONSE = 0xA1
    SET_REQUEST = 0xA3
    GET_BULK_REQUEST = 0xA5

# Value Types
class ValueType(IntEnum):
    INTEGER = 0x02
    STRING = 0x04
    COUNTER = 0x41
    TIMETICKS = 0x43

# Error Codes
class ErrorCode(IntEnum):
    SUCCESS = 0
    NO_SUCH_OID = 1
    BAD_VALUE = 2
    READ_ONLY = 3

def encode_oid(oid_string: str) -> bytes:
    """
    TODO: Convert OID string to bytes
    
    Example: "1.3.6.1.2.1.1.5.0" → b'\x01\x03\x06\x01\x02\x01\x01\x05\x00'
    
    Steps:
    1. Split the string by '.'
    2. Convert each part to an integer
    3. Convert the list of integers to bytes
    
    Hint: Python's bytes() constructor can take a list of integers (0-255)
    See README section 3.2.4 for OID encoding details
    
    Test: test_oid_encoding will verify your implementation
    """
    # TODO: Implement OID encoding
    raise NotImplementedError("Implement encode_oid")

def decode_oid(oid_bytes: bytes) -> str:
    """
    TODO: Convert OID bytes back to string
    
    Example: b'\x01\x03\x06\x01\x02\x01\x01\x05\x00' → "1.3.6.1.2.1.1.5.0"
    
    Steps:
    1. Convert each byte to its integer value
    2. Join them with '.' as a string
    
    Test: test_oid_decoding will verify your implementation
    """
    # TODO: Implement OID decoding
    raise NotImplementedError("Implement decode_oid")

def encode_value(value: Any, value_type: ValueType) -> bytes:
    """Encode a value based on its type"""
    if value_type == ValueType.INTEGER:
        return struct.pack('!i', value)
    elif value_type == ValueType.STRING:
        if isinstance(value, str):
            return value.encode('utf-8')
        return value
    elif value_type == ValueType.COUNTER:
        return struct.pack('!I', value)
    elif value_type == ValueType.TIMETICKS:
        return struct.pack('!I', value)
    else:
        raise ValueError(f"Unknown value type: {value_type}")

def decode_value(value_bytes: bytes, value_type: ValueType) -> Any:
    """Decode a value based on its type"""
    if value_type == ValueType.INTEGER:
        return struct.unpack('!i', value_bytes)[0]
    elif value_type == ValueType.STRING:
        return value_bytes.decode('utf-8')
    elif value_type == ValueType.COUNTER:
        return struct.unpack('!I', value_bytes)[0]
    elif value_type == ValueType.TIMETICKS:
        return struct.unpack('!I', value_bytes)[0]
    else:
        raise ValueError(f"Unknown value type: {value_type}")

class SNMPMessage(ABC):
    """Base class for all SNMP messages"""
    
    def __init__(self, request_id: int, pdu_type: PDUType):
        self.request_id = request_id
        self.pdu_type = pdu_type
    
    @abstractmethod
    def pack(self) -> bytes:
        """Convert message to bytes for transmission"""
        pass
    
    @classmethod
    @abstractmethod
    def unpack(cls, data: bytes) -> 'SNMPMessage':
        """Create message instance from received bytes"""
        pass

class GetRequest(SNMPMessage):
    """SNMP GetRequest message"""
    
    def __init__(self, request_id: int, oids: List[str]):
        super().__init__(request_id, PDUType.GET_REQUEST)
        self.oids = oids
    
    def pack(self) -> bytes:
        """
        TODO: Pack this GetRequest into bytes for transmission
        
        Message format (see README section 3.3.1):
        - total_size (4 bytes, big-endian): Total message size including header
        - request_id (4 bytes, big-endian): Unique request identifier
        - pdu_type (1 byte): PDUType.GET_REQUEST (0xA0)
        - payload:
            - oid_count (1 byte): Number of OIDs
            - For each OID:
                - oid_length (1 byte): Length of this OID in bytes
                - oid_bytes (variable): The encoded OID
        
        Steps:
        1. Build the payload first (oid_count + all OIDs with lengths)
        2. Calculate total_size (header + payload size)
        3. Pack the complete message
        
        Hints:
        - Use struct.pack('!I', value) for 4-byte big-endian integers
        - Use struct.pack('!B', value) for single bytes
        - Build payload as bytes, then prepend header
        
        Test: test_get_request_encoding will verify this
        """
        # TODO: Implement GetRequest packing
        raise NotImplementedError("Implement GetRequest.pack()")
    
    @classmethod
    def unpack(cls, data: bytes) -> 'GetRequest':
        """
        TODO: Create GetRequest from received bytes
        
        Reverse the packing process:
        1. Skip the header (we know it's a GetRequest from PDU type)
        2. Extract request_id from bytes 4-8
        3. Start parsing payload at byte 9
        4. Read oid_count, then read each OID
        
        Remember to decode OIDs from bytes to strings!
        
        Test: test_get_request_decoding will verify this
        """
        # TODO: Implement GetRequest unpacking
        raise NotImplementedError("Implement GetRequest.unpack()")

class SetRequest(SNMPMessage):
    """SNMP SetRequest message"""
    
    def __init__(self, request_id: int, bindings: List[Tuple[str, ValueType, Any]]):
        super().__init__(request_id, PDUType.SET_REQUEST)
        self.bindings = bindings  # List of (oid, value_type, value)
    
    def pack(self) -> bytes:
        """
        TODO: Pack this SetRequest into bytes
        
        Similar to GetRequest, but payload includes values (see README 3.3.2):
        - Header same as GetRequest
        - Payload:
            - oid_count (1 byte)
            - For each binding:
                - oid_length (1 byte)
                - oid_bytes (variable)
                - value_type (1 byte): Type from ValueType enum
                - value_length (2 bytes, big-endian): Length of value data
                - value_data (variable): Encoded value
        
        Use the provided encode_value() function for value encoding!
        
        Test: test_set_request_encoding will verify this
        """
        # TODO: Implement SetRequest packing
        raise NotImplementedError("Implement SetRequest.pack()")
    
    @classmethod
    def unpack(cls, data: bytes) -> 'SetRequest':
        """
        TODO: Create SetRequest from received bytes
        
        Parse both OIDs and their associated values.
        Use decode_value() to decode the value data.
        
        Test: test_set_request_decoding will verify this
        """
        # TODO: Implement SetRequest unpacking
        raise NotImplementedError("Implement SetRequest.unpack()")

class GetBulkRequest(SNMPMessage):
    """SNMP GetBulkRequest message"""
    
    def __init__(self, request_id: int, oid: str, max_repetitions: int):
        super().__init__(request_id, PDUType.GET_BULK_REQUEST)
        self.oid = oid
        self.max_repetitions = max_repetitions
    
    def pack(self) -> bytes:
        """
        TODO: Pack this GetBulkRequest into bytes
        
        Format (see README section 3.3.4):
        - Standard header
        - Payload:
            - oid_length (1 byte)
            - oid_bytes (variable)
            - max_repetitions (2 bytes, big-endian)
        
        Test: test_bulk_request_encoding will verify this
        """
        # TODO: Implement GetBulkRequest packing
        raise NotImplementedError("Implement GetBulkRequest.pack()")
    
    @classmethod
    def unpack(cls, data: bytes) -> 'GetBulkRequest':
        """
        TODO: Create GetBulkRequest from received bytes
        
        Test: test_bulk_request_decoding will verify this
        """
        # TODO: Implement GetBulkRequest unpacking
        raise NotImplementedError("Implement GetBulkRequest.unpack()")

class GetResponse(SNMPMessage):
    """SNMP GetResponse message"""
    
    def __init__(self, request_id: int, error_code: ErrorCode, 
                 bindings: List[Tuple[str, ValueType, Any]]):
        super().__init__(request_id, PDUType.GET_RESPONSE)
        self.error_code = error_code
        self.bindings = bindings  # List of (oid, value_type, value)
    
    def pack(self) -> bytes:
        """
        TODO: Pack this GetResponse into bytes
        
        Format (see README section 3.3.3):
        - total_size (4 bytes)
        - request_id (4 bytes)
        - pdu_type (1 byte): PDUType.GET_RESPONSE (0xA1)
        - error_code (1 byte): Error code from ErrorCode enum
        - Payload (same as SetRequest payload - OIDs with values)
        
        Note: GetResponse has an extra error_code field after pdu_type!
        
        Test: test_get_response_encoding will verify this
        """
        # TODO: Implement GetResponse packing
        raise NotImplementedError("Implement GetResponse.pack()")
    
    @classmethod
    def unpack(cls, data: bytes) -> 'GetResponse':
        """
        TODO: Create GetResponse from received bytes
        
        Remember to extract the error_code field!
        
        Test: test_get_response_decoding will verify this
        """
        # TODO: Implement GetResponse unpacking
        raise NotImplementedError("Implement GetResponse.unpack()")

def unpack_message(data: bytes) -> SNMPMessage:
    """Unpack any SNMP message based on PDU type"""
    if len(data) < MIN_MESSAGE_SIZE:
        logger.error("Message too short: %d bytes, minimum %d", len(data), MIN_MESSAGE_SIZE)
        raise ValueError(f"Message too short: {len(data)} bytes, minimum {MIN_MESSAGE_SIZE}")
    
    pdu_type = struct.unpack('!B', data[PDU_TYPE_OFFSET:PDU_TYPE_OFFSET+PDU_TYPE_LENGTH])[0]
    logger.debug("Unpacking message with PDU type 0x%02X", pdu_type)
    
    if pdu_type == PDUType.GET_REQUEST:
        return GetRequest.unpack(data)
    elif pdu_type == PDUType.SET_REQUEST:
        return SetRequest.unpack(data)
    elif pdu_type == PDUType.GET_BULK_REQUEST:
        return GetBulkRequest.unpack(data)
    elif pdu_type == PDUType.GET_RESPONSE:
        return GetResponse.unpack(data)
    else:
        logger.error("Unknown PDU type: 0x%02X", pdu_type)
        raise ValueError(f"Unknown PDU type: {pdu_type}")

def receive_complete_message(sock) -> bytes:
    """
    TODO: Receive a complete SNMP message handling buffering
    
    This is a CRITICAL function that demonstrates proper network buffering!
    
    The challenge: When receiving from a socket, you might get:
    - Less data than expected (partial message)
    - Exactly the amount you need
    - More than one message (if you read too much)
    
    Algorithm (see README section 4 for details):
    1. First, receive exactly 4 bytes to get the message size
       - May take multiple recv() calls!
    2. Decode message size from these 4 bytes (big-endian unsigned int)
    3. Continue receiving until you have exactly message_size bytes total
       - Track how many bytes you've received so far
       - Calculate how many more you need
       - NEVER request more than the remaining bytes!
    
    Common mistakes to avoid:
    - Assuming recv() returns all requested data
    - Reading past the end of the message
    - Not handling the case where recv() returns 0 (connection closed)
    
    Pseudocode:
        received = b''
        # Get message size (first 4 bytes)
        while len(received) < 4:
            chunk = sock.recv(4 - len(received))
            if not chunk:
                raise ConnectionError("Connection closed")
            received += chunk
        
        message_size = unpack size from first 4 bytes
        
        # Get rest of message
        while len(received) < message_size:
            remaining = message_size - len(received)
            chunk = sock.recv(min(remaining, 4096))
            ...
    
    Test: test_message_buffering will verify this handles partial receives
    Test: test_large_bulk_response will verify this handles large messages
    """
    # TODO: Implement complete message buffering
    raise NotImplementedError("Implement receive_complete_message")