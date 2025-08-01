# Simplified SNMP Protocol Implementation
**CPSC 3600 - Networks and Network Programming**  
**Fall 2025**

---
# 1. Introduction
In this project, you will implement a simplified version of the Simple Network Management Protocol (SNMP), the industry-standard protocol used to monitor and manage network devices worldwide. Every router, switch, server, and network-enabled printer uses SNMP for monitoring and configuration. Your implementation will allow network administrators to 1) query device information (uptime, system name, traffic statistics, etc), 2) modify device configurations, 3) and efficiently retrieve bulk data from network interfaces.

There is a lot of information in this document that you need to understand how this protocol works, however it maps to a fairly small amount of code that you will need to right. The bulk of the detail discussed in this document is in the *data* (which we provide you with), not the *code* required to access it.

## Learning Objectives
By building this protocol from scratch, you will master essential network programming skills including:

1. **Design binary network protocols** using `struct.pack()` and `struct.unpack()`
2. **Implement message framing** to handle variable-length data
3. **Handling message buffering** for data that exceeds single `recv()` calls
4. **Building both client and server** applications that communicate over TCP sockets
5. **Debugging network protocols** using tools like Wireshark and logging

## Why This Matters
This project will give you hands-on experience with the same fundamental concepts used in production network management systems at companies like Cisco, Juniper, and every major cloud provider.
* **Industry Relevance:** SNMP manages billions of devices worldwide
* **Fundamental Skills:** Binary protocols, buffering, and client-server architecture
* **Real Protocol:** You're building a subset of an actual IETF standard
* **Practical Application:** The same concepts apply to REST APIs, gRPC, and other network protocols

# 2. Prerequisites and Getting Started

## Required Knowledge
* Basic Python programming (loops, functions, dictionaries)
* Understanding of TCP sockets (`socket`, `bind`, `listen`, `accept`, `connect`, `send`, `recv`)
* Familiarity with binary data (`bytes` vs `str` in Python)

## Project File Structure

The project template contains several files and folders. You are responsible for implementing two main files: `snmp_agent.py` and `snmp_manager.py`. A brief explanation of each file is provided below:

### Files You Will Implement

- **snmp_agent.py** - The SNMP server that simulates a network device. This program listens for SNMP requests, maintains device state (MIB database), and responds with appropriate data from its Management Information Base (MIB).

- **snmp_manager.py** - The SNMP client used to query and configure network devices. This program sends SNMP requests to agents and displays the responses.

### Files We Provide

- **mib_database.py** - Contains the MIB structure that defines what data your SNMP agent can serve. This includes system information, interface statistics, and configuration parameters. The MIB is provided as a Python dictionary with OIDs as keys. Do not modify this file.

- **snmp_types.py** - Helper functions for encoding and decoding SNMP data types. Includes utilities for OID manipulation and value type conversion. You should use these functions but not modify them.

- **test_suite.py** - Automated tests that verify your implementation against the protocol specification. Run this to check your progress on each milestone.

- **packet_captures/** - Directory containing real SNMP packet captures that you can examine with Wireshark to understand the protocol better.

- **examples/** - Sample command outputs showing expected behavior for various SNMP operations.

# 3. SNMP Protocol

## What is SNMP? 
The Simple Network Management Protocol (SNMP) is one of the most widely deployed protocols on the Internet, yet it often operates invisibly in the background. First standardized in 1988, SNMP provides a universal language for monitoring and managing network devices. When network administrators need to check if a router is overheating, monitor bandwidth usage on a switch, or update configuration settings on hundreds of devices simultaneously, they rely on SNMP. The protocol works by organizing device information into a structured hierarchy called a Management Information Base (MIB), where each piece of data—from CPU temperature to packet counts—has a unique address called an Object Identifier (OID).

What makes SNMP particularly powerful is its simplicity and universality. Whether you're managing a small office printer or a massive data center switch, the protocol works the same way: a management station sends requests to agents running on network devices, and those agents respond with the requested information or confirm configuration changes. This standardization means that equipment from different vendors—Cisco routers, HP printers, Dell servers—can all be managed using the same protocol and often the same management software. Today, SNMP is built into virtually every enterprise network device and forms the backbone of network monitoring systems used by companies worldwide. Tools like Nagios, SolarWinds, and PRTG all rely on SNMP to collect the data that keeps modern networks running smoothly.

## Building Intuition: An Analogy

To help understand how the SNMP protocols works, let's imagine how the SNMP protocol could be applied in the context of a coffee shop. The barista is the SNMP agent who keeps track of everything in the store and the regional manager coordinating many different stores is the SNMP manager.

* **OID** = Menu item number 
  * OID #3.1.7 = "latte"
* **Get Request** = Regional manager asking a question
  * "How many lattes [OID #3.1.7] sold today?"
* **Set Request** = Regional manager instructs the barista to change something 
  * "Set the WiFi password [OID #2.4.13] to 'brew2025'"
* **Get Bulk** = Regional manager asking for information about many things at once 
  * "Tell me all stats for items #3.1 through #3.50"
* **Get Response** = Barista's response to the regional manager's individual requests, bulk requests, or instructions 
  * "42 lattes [OID #3.1.7] sold"
  * "3.1 stats are..., 3.2 stats are..., 3.3 stats are ..., ..."
  * "Password [OID #2.4.13] changed successfully")

## SNMP Protocol Specification

### Object Identifiers (OID)
Object Identifiers (OIDs) are a universal addressing system for data in network devices. Just like every location on earth can be identified by a specific latitude and longitude, every piece of manageable information in a network device has a unique OID. These address ensure that when you ask for "system uptime", every device, regardless of manufacturer, knows you mean the value at OID 1.3.6.1.2.1.1.3.0.

OIDs form a hierarchical tree structure, similar to a filesystem. Each number in the OID represents a branch in this tree, creating increasingly specific paths to individual data points. The tree starts from the root and branches out into various standards organizations, then into specific uses, and finally to individual data items. 

```
                            Root
                             |
        ┌────────────┬───────┴───────┬────────────┐
        0            1               2             3
    (ITU-T)      (ISO)           (Joint)      (Reserved)
                  |
            ┌─────┴─────┐
            3           4
         (Org)      (Others)
            |
        ┌───┴───┐
        6      ...
      (DOD)
        |
        1
    (Internet)
        |
    ┌───┴───┬───────┬───────┐
    1       2       3       4
(Directory) (Mgmt) (Exp)  (Private)
            |
            1
         (MIB-2)
            |
    ┌───────┼───────┬───────┐
    1       2      ...     11
(System) (Interfaces)    (SNMP)
```

Let's decode the OID 1.3.6.1.2.1.1.5.0 step-by-step
* 1 = ISO (International Organization for Standardization)
* 3 = org (organizations)
* 6 = dod (U.S. Department of Defense - they developed the Internet)
* 1 = internet
* 2 = mgmt (management)
* 1 = mib-2 (the second version of the Management Information Base)
* 1 = system (system information group)
* 5 = sysName (the system's name)
* 0 = instance (scalar objects always end in .0)

So 1.3.6.1.2.1.1.5.0 universally means "the system name" on any SNMP-enabled device.

#### Why Use a Hierarchical Addressing System?
The hierarchical structure serves several purposes
1. **Global Uniqueness:** The top levels are managed by international organizations, ensuring no conflicts
2. **Vendor Extensions:** Companies can register their own branches (like 1.3.6.1.4.1.9 for Cisco)
3. **Logical Organization:** Related data is grouped together (all interface data under 1.3.6.1.2.1.2)
4. **Discoverability:** You can "walk" the tree to find what data is available

This standardization is why SNMP remains crucial to network management after nearly four decades. It provides a common language for managing the incredible diversity of network devices in modern infrastructure and ensures that network administrators can write scripts that work across their entire infrastructure.

#### OID Encoding

While we write OIDs using a hierarchical dotted notation, internally they are represented as a bit-string. For our simplified SNMP protocol, we'll represent each number in the hierarchy as a single byte. Real SNMP protocols employ more advanced encoding formats that allow them to shrink the number of bits required to represent individual OIDs.

**Encoding Process**
```
OID String: "1.3.6.1.2.1.1.5.0"
            ↓ split by '.'
Numbers:    [1, 3, 6, 1, 2, 1, 1, 5, 0]
            ↓ convert to bytes
Bytes:      [0x01, 0x03, 0x06, 0x01, 0x02, 0x01, 0x01, 0x05, 0x00]
```

**Implementation Helper**
```
def encode_oid(oid_string):
    """Convert OID string to bytes"""
    # "1.3.6.1.2.1.1.5.0" → [1,3,6,1,2,1,1,5,0] → b'\x01\x03\x06\x01\x02\x01\x01\x05\x00'
    return bytes([int(x) for x in oid_string.split('.')])

def decode_oid(oid_bytes):
    """Convert OID bytes back to string"""
    # b'\x01\x03\x06\x01\x02\x01\x01\x05\x00' → "1.3.6.1.2.1.1.5.0"
    return '.'.join(str(b) for b in oid_bytes)
```

### SNMP Message Structure

Every SNMP message follows this pattern. Note how there is a fixed 9 byte header that starts the message. The 10th byte will either be the error code, or the start of the payload, depending on the pdu_type.
```
┌─────────────┬──────────────┬───────────┬─────────────┬──────────────┐
│ total_size  │ request_id   │ pdu_type  │ error_code  │ payload      │
│ (4 bytes)   │ (4 bytes)    │ (1 byte)  │ (1 byte)*   │ (variable)   │
└─────────────┴──────────────┴───────────┴─────────────┴──────────────┘
                                          * Only in responses
```

**Field Descriptions:**
- `total_size` (4 bytes, big-endian unsigned int): Total message size including this field and all other header fields
- `request_id` (4 bytes, big-endian unsigned int): Unique identifier for matching responses to requests (like a ticket number)
- `pdu_type` (1 byte): The kind of message (GET_REQUEST=0xA0, GET_RESPONSE=0xA1, SET_REQUEST=0xA3, GET_BULK_REQUEST=0xA5)
- `error_code` (1 byte, only in responses): 0=success, 1=no such Object Identifier (OID), 2=bad value, 3=read-only
- `payload`: PDU-specific data (see SNMP Payload Formats below)

### SNMP Payload Formats

The payload (data section) format depends on the PDU type:

#### 1. GetRequest Payload
The payload of the GetRequest message contains all of the OIDs information is being requested for. OIDs must be explicitly requested by listing them individually in the request message. Since GetRequests can ask for a different number of OIDs, the payload starts with the number of requested OIDs (up to 255)   
```
┌────────────┬────────────┬────────────┬     ┬────────────┐
│ oid_count  │ oid_1      │ oid_2      │ ... │ oid_n      │
│ (1 byte)   │ (variable) │ (variable) │ ... │ (variable) │
└────────────┴────────────┴────────────┴     ┴────────────┘

where each oid is

┌─────────────┬────────────┐
│ oid_length  │ oid_bytes  │
│ (1 byte)    │ (variable) │
└─────────────┴────────────┘

```

As we saw earlier, OIDs themselves are variable length (e.g. 3.2.17 or 4.1.65.3.2.6.1.3). As such, each OID listed in the payload includes a length value in the first byte so the receiver knows how many bytes to fetch for this OID.

**Example - Requesting two OIDs:**
```
GetRequest Payload
↓
02                            # oid_count = 2
09                            # first OID length = 9
01 03 06 01 02 01 01 01 00    # OID: 1.3.6.1.2.1.1.1.0
09                            # second OID length = 9  
01 03 06 01 02 01 01 03 00    # OID: 1.3.6.1.2.1.1.3.0
```

#### 2. SetRequest Payload
The payload of the SetRequest message contains multiple OIDs and the new values they should be set to. Just as with the GetRequest payload, we must specify each OID we want to set individually, and the payload starts with the number of OIDs to be set (up to 255).
```
┌────────────┬──────────────────┬──────────────────┬     ┬──────────────────┐
│ oid_count  │ oid_with_value_1 │ oid_with_value_2 │ ... │ oid_with_value_n │
│ (1 byte)   │ (variable)       │ (variable)       │ ... │ (variable)       │
└────────────┴──────────────────┴──────────────────┴     ┴──────────────────┘

Where each oid_with_value is:
┌─────────────┬────────────┬────────────┬──────────────┬────────────┐
│ oid_length  │ oid_bytes  │ value_type │ value_length │ value_data |
│ (1 byte)    │ (variable) │ (1 byte)   │ (2 bytes)    │ (variable) |
└─────────────┴────────────┴────────────┴──────────────┴────────────┘
```

Just as OIDs are variable length, the values associated with them can be variable length (as well as different types). As such, the OID_with_value used in the SetRequest payload includes additional fields defining what type of value is being returned (e.g. INT, string, etc) and it's length, in addition to the value itself. More information about the types of values supported and their meaning are discussed below in Value Types.

**Example - Setting system name:**
```
SetRequest Payload
↓
01                                 # oid_count = 1
09                                 # OID length = 9
01 03 06 01 02 01 01 05 00         # OID: 1.3.6.1.2.1.1.5.0
04                                 # value_type = STRING
00 0B                              # value_length = 11
72 6F 75 74 65 72 2D 6D 61 69 6E   # "router-main"
```

#### 3. GetResponse Payload
The payload of the GetResponse message contains responses to GetResponse, GetBulk, or SetResponse messages. Each OID included in the original message is "bound" to a response value in this message. Again, as we've seen before, these messages are variable length due to their ability to contain responses for each OID in the original request and must start with the number of OIDs and their responses included in this message (up to 255).

```
┌────────────────┬────────────┬────────────┬     ┬────────────┐
│ binding_count  │ binding_1  │ binding_2  │ ... │ binding_n  │
│ (1 byte)       │ (variable) │ (variable) │ ... │ (variable) │
└────────────────┴────────────┴────────────┴     ┴────────────┘

Where each binding is:
┌─────────────┬────────────┬────────────┬──────────────┬────────────┐
│ oid_length  │ oid_bytes  │ value_type │ value_length │ value_data |
│ (1 byte)    │ (variable) │ (1 byte)   │ (2 bytes)    │ (variable) |
└─────────────┴────────────┴────────────┴──────────────┴────────────┘
```

**Example - Response with one value**
```
GetResponse Payload
↓
01                    # binding_count = 1
09                    # OID length = 9
01 03 06 01 02 01 01 01 00  # OID: 1.3.6.1.2.1.1.1.0
04                    # value_type = STRING
00 10                 # value_length = 16
52 6F 75 74 65 72 20 4D 6F 64 65 6C 20 58 32 30 30 30  # "Router Model X2000"
```

#### 4. GetBulkRequest Payload
The payload of the GetBulkRequest message contains a single starting OID and the maximum number of sequential OIDs to return. Unlike GetRequest which requires explicitly listing each desired OID, GetBulkRequest enables efficient retrieval of multiple sequential OIDs by performing a walk through the MIB tree in lexicographic order (up to 65,635).

```
┌─────────────┬────────────┬───────────────────┐
│ oid_length  │ oid_bytes  │ max_repetitions   │
│ (1 byte)    │ (variable) │ (2 bytes)         │
└─────────────┴────────────┴───────────────────┘
```

The GetBulkRequest is particularly useful when you need to retrieve all entries in a table (like interface statistics) without knowing how many entries exist. The agent will return up to max_repetitions OIDs starting from the specified OID, following the lexicographic ordering of the MIB tree and potentially crossing into different branches and tables. This also means that GetBulkRequests can return a very large amount of data, which makes buffering the data at the receiver is crucial (see *Handling Large Messages with Buffering* below)

**Lexicographic Ordering Example:**
Starting from 1.3.6.1.2.1.2.2.1.10, the sequence would be:

```
1.3.6.1.2.1.2.2.1.10.1 (interface 1 bytes in)
1.3.6.1.2.1.2.2.1.10.2 (interface 2 bytes in)
1.3.6.1.2.1.2.2.1.10.3 (interface 3 bytes in)
1.3.6.1.2.1.2.2.1.11.1 (moves to next table - interface 1 unicast packets)
1.3.6.1.2.1.2.2.1.11.2 (interface 2 unicast packets)
... and so on through the MIB tree
```

**Example - Get 50 OIDs starting from interfaces**
```
GetBulkRequest Payload
↓
0A                             # OID length = 10
01 03 06 01 02 01 02 02 01 10  # OID: 1.3.6.1.2.1.2.2.1.10 (interface in octets)
00 32                          # max_repetitions = 50
```
This request would return up to 50 OIDs starting from the first OID after 1.3.6.1.2.1.2.2.1.10. If there are only 3 interfaces, it would return:

* All interface input byte counters (1.3.6.1.2.1.2.2.1.10.1 through .10.3)
* Continue to interface unicast packets (1.3.6.1.2.1.2.2.1.11.1 through .11.3)
* Continue to interface output bytes (1.3.6.1.2.1.2.2.1.16.1 through .16.3)
  * 1.3.6.1.2.1.2.2.1.12 through 1.3.6.1.2.1.2.2.1.15 don't exist on this device, so they are skipped
* And keep walking through subsequent OIDs until 50 are returned



### Value Types
Different OIDs are associated with different types of values (strings, integers, floating point values, etc). This means that we need to encode the type of value in the message itself, as well as how long the value is. Each value in SNMP has a type that determines how it's encoded:

#### INTEGER (Type = 0x02)
* Size: Always 4 bytes
* Encoding: Big-endian signed integer
* Example: Temperature = -5°C

```
Type: 02
Length: 00 04
Value: FF FF FF FB  # -5 in two's complement
```

#### STRING (Type = 0x04)
* Size: Variable
* Encoding: UTF-8 text
* Example: System name = "gateway"

```
Type: 04
Length: 00 07
Value: 67 61 74 65 77 61 79  # "gateway"
```

#### COUNTER (Type = 0x41)
* Size: Always 4 bytes
* Encoding: Big-endian unsigned integer
* Example: Bytes received = 1,234,567

```
Type: 41
Length: 00 04
Value: 00 12 D6 87  # 1234567
```

#### TIMETICKS (Type = 0x43)
* Size: Always 4 bytes
* Encoding: Big-endian unsigned integer (hundredths of seconds)
* Example: Uptime = 1 hour (360,000 hundredths)

```
Type: 43
Length: 00 04
Value: 00 05 7E 40  # 360000
```

## Examples
### Example 1: Getting System Name
**Step 1: Manager sends GetRequest**
```
# Human readable:
# "What is the value at OID 1.3.6.1.2.1.1.5.0?"

# As bytes (hex):
00 00 00 16  # Total size: 22 bytes
00 00 04 D2  # Request ID: 1234
A0           # Type: GetRequest
01           # OID count: 1
09           # OID length: 9 bytes
01 03 06 01 02 01 01 05 00  # OID bytes
```

**Step 2: Agent sends GetResponse**
```
# Human readable:
# "The value is 'router-main'"

# As bytes (hex):
00 00 00 20  # Total size: 32 bytes
00 00 04 D2  # Request ID: 1234 (matches request!)
A1           # Type: GetResponse
00           # Error: Success
01           # Binding count: 1
09           # OID length: 9
01 03 06 01 02 01 01 05 00  # OID bytes
04           # Value type: String
00 0B        # Value length: 11
72 6F 75 74 65 72 2D 6D 61 69 6E  # "router-main"
```

### Example 2: Set Interface 1 Description
**Step1: Manager sets SetRequest**
```
# SetRequest message breakdown:
00 00 00 26              # Total size: 38 bytes
00 00 10 01              # Request ID: 4097
A3                       # Type: SetRequest (0xA3)
01                       # OID count: 1
# OID with value:
0C                       # OID length: 12
01 03 06 01 02 01 02 02 01 12 01  # OID: 1.3.6.1.2.1.2.2.1.18.1
04                       # Value type: STRING (0x04)
00 09                    # Value length: 9
57 41 4E 20 4C 69 6E 6B 31  # Value: "WAN Link1"

# Total: 4+4+1+1+1+12+1+2+9 = 38 bytes ✓
```

**Step 2: Agent Responds**
```
# GetResponse for the SetRequest:
00 00 00 26              # Total size: 38 bytes  
00 00 10 01              # Request ID: 4097 (matches!)
A1                       # Type: GetResponse (0xA1)
00                       # Error: Success (0x00)
01                       # Binding count: 1
# The binding (OID + value):
0C                       # OID length: 12
01 03 06 01 02 01 02 02 01 12 01  # Same OID
04                       # Value type: STRING
00 09                    # Value length: 9
57 41 4E 20 4C 69 6E 6B 31  # Confirmed: "WAN Link1"
```


# 4. Handling Large Messages with Buffering

One of the key challenges in network programming is handling messages that are too large to be received in a single `recv()` call. The socket's receive buffer has a limited size, and the operating system may deliver data in chunks smaller than the complete message.

## The Buffering Problem

Consider a GetBulk response containing information for 50 network interfaces. This response might be 5KB or larger. When you call `sock.recv(4096)`, you might only receive the first 1KB of data. Your recv() calls might return data like this:

```
recv(4096) → 1460 bytes (partial message!)
recv(4096) → 2920 bytes (more data...)
recv(4096) → 620 bytes  (finally complete!)
```

Your code must:
1. Recognize that the message is incomplete
2. Continue receiving data until the full message arrives
3. Parse the complete message only after all data is received

We will need to rely on the length field(s) to determine the total size of the message and determine when we have received the entire message. Be prepared to make multiple calls to receive until this is true. However, be careful not to request too MUCH data as the operating system will happily give you part of the next message if you accidentally ask for it.

### Pseudocode Example
```
received_bytes = b''

# Get message length
while received_bytes < 4
    received_bytes += recv(4-len(received_bytes))

message_size = decode first 4 bytes as an integer

while len(received_bytes) < message_size
    # Find out how many more bytes we need
    bytes_needed = message_size - len(received_bytes)
    
    # Either ask for 4096 bytes or the number of bytes remaining, whichever is smaller
    # We should avoid ever asking for more than 4096 bytes at a time
    received_bytes += recv(min(len(received_size), 4096)     

if len(received_bytes) == message_size
    return received_bytes
else
    raise Exception
```

## Testing Your Buffering Implementation

The test suite includes specific tests for buffering:
- Sending GetBulk requests that generate >4KB responses
- Verifying correct reassembly of fragmented messages
- Stress testing with repeated large requests

# 5. Implementation Requirements

### Part 1: SNMP Agent (snmp_agent.py)

Your SNMP agent must:

1. **Listen on TCP port 1161** (we use 1161 instead of the standard 161 to avoid requiring root privileges)

2. **Handle sequential client connections** - The server should continue running and accept new connections after clients disconnect. You do NOT need to serve multiple clients simultaneously (we'll tackle this in a later project)

3. **Process four request types:**
   - GetRequest: Return the current value for requested OID(s)
   - SetRequest: Update values for writable OIDs, return error for read-only OIDs
   - GetBulkRequest: Return multiple sequential OIDs starting from a given OID
   - Maintain proper error codes in responses

4. **Implement proper message framing** - Use the msg_length field to determine message boundaries

### Part 2: SNMP Manager (snmp_manager.py)

Your SNMP manager must: 
The manager must:
1. **Create proper request messages** according to the protocol
   - Pack messages with correct byte order (big-endian)
   - Include appropriate PDU type for each operation
   - Generate unique request IDs to match responses
2. **Send requests and handle responses** with proper buffering
   - Implement the complete message receiving algorithm
   - Handle responses that exceed socket buffer size
   - Match responses to requests using request ID
3. **Display results in a readable format**
   - Show OID and value for get operations
   - Confirm successful sets or display error messages
   - List all OID/value pairs for bulk operations
   - Convert value types to human-readable format (e.g., timeticks to hours:minutes:seconds)
4. **Handle errors gracefully**
   - Connection failures (server not running, network issues)
   - Protocol errors (malformed responses, wrong PDU types)
   - Application errors (non-zero error codes in responses)

# 6. Project Milestones

### Milestone 1: Basic Get Operations (Week 1)

Implement GetRequest and GetResponse for single OIDs:
- Agent can respond to basic queries
- Manager can request and display single values
- Proper binary encoding/decoding
- Basic error handling

**Test with:**
```bash
python snmp_manager.py get localhost:1161 1.3.6.1.2.1.1.1.0
# Should return: "Router Model X2000"
```

### Milestone 2: Buffering & GetBulk (Week 2)

Add GetBulkRequest support with proper buffering:
- Handle responses exceeding socket buffer size
- Implement the buffering algorithm correctly
- Support requesting 50+ OIDs in a single request

**Test with:**
```bash
python snmp_manager.py bulk localhost:1161 1.3.6.1.2.1.2.2.1 50
# Should return multiple interface statistics requiring buffered receive
```

### Milestone 3: Set Operations & State Management (Week 3)

Implement SetRequest with validation:
- Check if OIDs are writable
- Validate value types match OID specifications
- Persist changes across requests
- Return appropriate error codes

**Test with:**
```bash
python snmp_manager.py set localhost:1161 1.3.6.1.2.1.1.5.0 string "new-name"
# Should succeed and persist

python snmp_manager.py set localhost:1161 1.3.6.1.2.1.1.3.0 integer 0
# Should fail - system uptime is read-only
```

# 7. Testing Your Implementation

### Running the Test Suite

```bash
python test_suite.py
```

The test suite will automatically:
1. Start your agent on a test port
2. Run various manager commands
3. Verify responses match expected values
4. Test error conditions
5. Measure performance for bulk operations

### Manual Testing

You can also test manually by running the agent and manager in separate terminals:

**Terminal 1:**
```bash
python snmp_agent.py
SNMP Agent listening on port 1161...
```

**Terminal 2:**
```bash
python snmp_manager.py get localhost:1161 1.3.6.1.2.1.1.3.0
System uptime: 4523 (45.23 seconds)
```

### Debugging Tips

1. **Use Wireshark** - Compare your packets with the provided captures
2. **Add logging** - Print message bytes before sending/after receiving
3. **Test incrementally** - Get single OID working before bulk requests
4. **Check byte order** - Remember to use big-endian (`>I`, `>H`)
5. **Verify lengths** - Ensure msg_length includes all bytes

## Common Pitfalls and Solutions

### Pitfall 1: Incomplete Message Reception
**Problem:** Assuming `recv()` returns complete messages  
**Solution:** Always use msg_length field and buffer until complete

### Pitfall 2: Byte Order Issues
**Problem:** Using little-endian instead of network byte order  
**Solution:** Always use `!` prefix in struct format strings

### Pitfall 3: String Encoding
**Problem:** Forgetting to encode/decode strings  
**Solution:** Use `.encode('utf-8')` and `.decode('utf-8')` consistently

### Pitfall 4: Socket Reuse
**Problem:** "Address already in use" errors  
**Solution:** Set `SO_REUSEADDR` option on server socket

### Pitfall 5: Message Framing
**Problem:** Messages bleeding into each other  
**Solution:** Always include and check msg_length field

## Grading Rubric

| Component | Points | Criteria |
|-----------|--------|----------|
| **Protocol Compliance** | 25% | Correct binary format, proper encoding/decoding, follows specification exactly |
| **Buffering Implementation** | 20% | Correctly handles messages larger than recv buffer, no data loss or corruption |
| **Get/GetBulk Operations** | 20% | Both operations work correctly, efficient handling of bulk requests |
| **Set Operations** | 15% | Validates permissions, correct value types, persistent state |
| **Error Handling** | 10% | Graceful handling of all error conditions, proper error codes |
| **Code Quality** | 10% | Clean, well-documented code following Python conventions |

## Submission Requirements

Submit the following files to Gradescope:

1. **snmp_agent.py** - Your complete agent implementation
2. **snmp_manager.py** - Your complete manager implementation
3. **protocol_notes.txt** - Brief documentation of any design decisions or deviations from the specification

Do not modify or submit the provided files (mib_database.py, snmp_types.py, etc.).

## Additional Resources

- **RFC 1157** - Original SNMP specification (for reference only)
- **Python struct documentation** - Essential for binary protocol implementation
- **Wireshark SNMP dissector** - Useful for comparing with real SNMP
- **Office hours** - Available for protocol questions and debugging help

Remember: You're building the same fundamental protocol that manages network infrastructure worldwide. Take pride in creating a working implementation of this critical technology!

## License

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)