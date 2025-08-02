# Simplified SNMP Protocol Implementation
**CPSC 3600 - Networks and Network Programming**  
**Fall 2025**

---

## 📑 Table of Contents

### Quick References
- [📊 Grading Information](GRADING.md) - Specification grading and bundles
- [🧪 Testing Guide](TESTING.md) - How to run and understand tests

### Main Documentation
1. [**Introduction**](#1-introduction)
   - [Learning Objectives](#learning-objectives)
   - [Why This Matters](#why-this-matters)

2. [**Getting Started**](#2-getting-started)
   - [Environment Setup](#environment-setup)
   - [Project Overview](#project-overview)
   - [Your First Implementation: OID Encoding](#your-first-implementation-oid-encoding)
   - [Testing Your First Feature](#testing-your-first-feature)

3. [**Prerequisites and Project Structure**](#3-prerequisites-and-project-structure)
   - [Required Knowledge](#required-knowledge)
   - [Project File Structure](#project-file-structure)

4. [**SNMP Protocol**](#4-snmp-protocol)
   - [What is SNMP?](#what-is-snmp)
   - [Building Intuition: An Analogy](#building-intuition-an-analogy)
   - [SNMP Protocol Specification](#snmp-protocol-specification)
     - [Object Identifiers (OID)](#object-identifiers-oid)
     - [SNMP Message Structure](#snmp-message-structure)
     - [SNMP Payload Formats](#snmp-payload-formats)
     - [Value Types](#value-types)
   - [Examples](#examples)

5. [**Handling Large Messages with Buffering**](#5-handling-large-messages-with-buffering)
   - [The Buffering Problem](#the-buffering-problem)
   - [Testing Your Buffering Implementation](#testing-your-buffering-implementation)

6. [**Implementation Requirements**](#6-implementation-requirements)
   - [Part 1: SNMP Agent](#part-1-snmp-agent-snmp_agentpy)
   - [Part 2: SNMP Manager](#part-2-snmp-manager-snmp_managerpy)

7. [**Project Milestones**](#7-project-milestones)
   - [Milestone 1: Basic Get Operations](#milestone-1-basic-get-operations-week-1)
   - [Milestone 2: Multiple OIDs & Error Handling](#milestone-2-multiple-oids--error-handling-week-2)
   - [Milestone 3: Set Operations & State Management](#milestone-3-set-operations--state-management-week-3)

8. [**Testing Your Implementation**](#8-testing-your-implementation)
   - [Running the Test Suite](#running-the-test-suite)
   - [Manual Testing](#manual-testing)

9. [**Debugging Guide**](#9-debugging-guide)
   - [Essential Debugging Tools](#essential-debugging-tools)
   - [Common Errors and Solutions](#common-errors-and-solutions)
   - [Understanding Error Messages](#understanding-error-messages)
   - [Protocol Debugging Techniques](#protocol-debugging-techniques)
   - [Socket Programming Issues](#socket-programming-issues)

10. [**Grading and Submission**](#10-grading-and-submission)
    - [Grading Rubric](#grading-rubric)
    - [Submission Requirements](#submission-requirements)

11. [**Additional Resources**](#11-additional-resources)

---

# 1. Introduction

In this project, you will implement a simplified version of the Simple Network Management Protocol (SNMP), the industry-standard protocol used to monitor and manage network devices worldwide. Every router, switch, server, and network-enabled printer uses SNMP for monitoring and configuration. Your implementation will allow network administrators to 1) query device information (uptime, system name, traffic statistics, etc), 2) modify device configurations, 3) and handle multiple OID requests efficiently.

There is a lot of information in this document that you need to understand how this protocol works, however it maps to a fairly small amount of code that you will need to write. The bulk of the detail discussed in this document is in the *data* (which we provide you with), not the *code* required to access it.

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

---

# 2. Getting Started

## Environment Setup

### Prerequisites
Ensure you have Python 3.8 or higher installed:
```bash
python --version
# Should show Python 3.8.x or higher

# Note: If the above doesn't work, try:
python3 --version
```

### Install Required Packages
Install all required packages using the provided requirements.txt file:
```bash
# Install all requirements at once
pip install -r requirements.txt

# Note: If pip doesn't work, try:
pip3 install -r requirements.txt

# Alternative: If you encounter issues, use the minimal requirements:
pip install -r requirements-minimal.txt
```

This will install:
- `pytest` - Testing framework (required)
- `pytest-timeout` - Timeout handling for tests (required)
- `colorama` - Colored output for better readability (recommended)
- `pytest-json-report` - Test reporting for autograder (required)

**Troubleshooting Installation:**
- If you get permission errors, add `--user`: `pip install --user -r requirements.txt`
- On Mac/Linux, you might need `sudo`: `sudo pip install -r requirements.txt`
- In a virtual environment (recommended): 
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

### Verify Your Setup
```bash
# Check that all required files are present
ls *.py
# Should show: snmp_protocol.py, snmp_agent.py, snmp_manager.py, mib_database.py

# Verify pytest is installed correctly
python -m pytest --version

# Try running a simple test (it will fail initially - that's expected!)
python -m pytest tests/ -v -k "test_oid_encoding" 
```

## Project Overview

You'll be implementing three main files:

```
snmp_protocol.py   ← Start here! (Protocol encoding/decoding)
    ↓
snmp_agent.py      ← Then this (Server implementation)
    ↓
snmp_manager.py    ← Finally this (Client implementation)
```

**DO NOT MODIFY**: `mib_database.py` (this contains the data your agent will serve)

## Your First Implementation: OID Encoding

Let's start with the simplest feature: converting OID strings to bytes. This will give you a quick win and help you understand the project structure.

### Step 1: Open `snmp_protocol.py`

Find the `encode_oid` function around line 56:

```python
def encode_oid(oid_string: str) -> bytes:
    """
    TODO: Convert OID string to bytes
    
    Example: "1.3.6.1.2.1.1.5.0" → b'\x01\x03\x06\x01\x02\x01\x01\x05\x00'
    ...
    """
    # TODO: Implement OID encoding
    raise NotImplementedError("Implement encode_oid")
```

### Step 2: Understand What OIDs Are

An OID (Object Identifier) is like a path in a tree:
- "1.3.6.1.2.1.1.5.0" means: Start at root, go to child 1, then child 3, then 6, etc.
- Each number becomes one byte in our simplified protocol
- Real SNMP uses more complex encoding, but we're keeping it simple!

### Step 3: Implement the Function

Replace the `raise NotImplementedError` with this implementation:

```python
def encode_oid(oid_string: str) -> bytes:
    """
    Convert OID string to bytes
    
    Example: "1.3.6.1.2.1.1.5.0" → b'\x01\x03\x06\x01\x02\x01\x01\x05\x00'
    """
    # Split the string by '.' to get individual numbers
    # "1.3.6.1.2.1.1.5.0" → ["1", "3", "6", "1", "2", "1", "1", "5", "0"]
    parts = oid_string.split('.')
    
    # Convert each string number to an integer
    # ["1", "3", "6", ...] → [1, 3, 6, ...]
    numbers = [int(part) for part in parts]
    
    # Convert the list of integers to bytes
    # [1, 3, 6, ...] → b'\x01\x03\x06...'
    return bytes(numbers)
```

### Step 4: Implement the Decode Function

Now implement `decode_oid` (around line 75):

```python
def decode_oid(oid_bytes: bytes) -> str:
    """
    Convert OID bytes back to string
    
    Example: b'\x01\x03\x06\x01\x02\x01\x01\x05\x00' → "1.3.6.1.2.1.1.5.0"
    """
    # Convert each byte to its integer value and join with '.'
    return '.'.join(str(byte) for byte in oid_bytes)
```

## Testing Your First Feature

### Run the OID Tests
```bash
# Run just the OID encoding tests
python -m pytest tests/ -v -k "test_oid"

# You should see something like:
# tests/test_protocol_structure.py::test_oid_encoding PASSED
# tests/test_protocol_structure.py::test_oid_decoding PASSED
```

### Understanding Test Output

✅ **PASSED** - Your implementation is correct!  
❌ **FAILED** - Check the error message for details  
⚠️ **SKIPPED** - Test was skipped (usually due to dependencies)

### Verify with Interactive Python

```python
# Start Python interactive mode
python

# Note: If 'python' doesn't work, use 'python3'

>>> from snmp_protocol import encode_oid, decode_oid
>>> 
>>> # Test encoding
>>> oid_bytes = encode_oid("1.3.6.1.2.1.1.5.0")
>>> print(oid_bytes.hex())  # Should show: 010306010201010500
>>> 
>>> # Test decoding
>>> result = decode_oid(oid_bytes)
>>> print(result)  # Should show: 1.3.6.1.2.1.1.5.0
>>> 
>>> # Test round-trip
>>> original = "1.3.6.1.2.1.1.1.0"
>>> assert decode_oid(encode_oid(original)) == original
>>> print("Round-trip test passed!")
```

---

# 3. Prerequisites and Project Structure

## Required Knowledge
* Basic Python programming (loops, functions, dictionaries)
* Understanding of TCP sockets (`socket`, `bind`, `listen`, `accept`, `connect`, `send`, `recv`)
* Familiarity with binary data (`bytes` vs `str` in Python)

## Project File Structure

The project template contains several files and folders. You are responsible for implementing three main files: `snmp_protocol.py`, `snmp_agent.py` and `snmp_manager.py`. A brief explanation of each file is provided below:

### Files You Will Implement

- **snmp_protocol.py** - Contains message classes and encoding/decoding logic for simplified SNMP. Start here!

- **snmp_agent.py** - The SNMP server that simulates a network device. This program listens for SNMP requests, maintains device state (MIB database), and responds with appropriate data from its Management Information Base (MIB).

- **snmp_manager.py** - The SNMP client used to query and configure network devices. This program sends SNMP requests to agents and displays the responses.

### Files We Provide

- **mib_database.py** - Contains the MIB structure that defines what data your SNMP agent can serve. This includes system information, interface statistics, and configuration parameters. The MIB is provided as a Python dictionary with OIDs as keys. Do not modify this file.

- **packet_captures/** - Directory containing real SNMP packet captures that you can examine to understand the protocol better.

- **examples/** - Sample command outputs showing expected behavior for various SNMP operations.

---

# 4. SNMP Protocol

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
* **Get Response** = Barista's response to the regional manager's individual requests or instructions 
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
- `pdu_type` (1 byte): The kind of message (GET_REQUEST=0xA0, GET_RESPONSE=0xA1, SET_REQUEST=0xA3)
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
The payload of the GetResponse message contains responses to GetRequest or SetRequest messages. Each OID included in the original message is "bound" to a response value in this message. Again, as we've seen before, these messages are variable length due to their ability to contain responses for each OID in the original request and must start with the number of OIDs and their responses included in this message (up to 255).

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

---

# 5. Handling Large Messages with Buffering

## The Buffering Problem

One of the key challenges in network programming is handling messages that are too large to be received in a single `recv()` call. The socket's receive buffer has a limited size, and the operating system may deliver data in chunks smaller than the complete message.

Consider a GetResponse containing information for multiple OIDs with large string values. This response might exceed the socket buffer size. When you call `sock.recv(4096)`, you might only receive part of the data. Your recv() calls might return data like this:

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
- Sending requests with multiple OIDs that generate large responses
- Verifying correct reassembly of fragmented messages
- Stress testing with repeated large requests

---

# 6. Implementation Requirements

### Part 1: SNMP Agent (snmp_agent.py)

Your SNMP agent must:

1. **Listen on TCP port 1161** (we use 1161 instead of the standard 161 to avoid requiring root privileges)

2. **Handle sequential client connections** - The server should continue running and accept new connections after clients disconnect. You do NOT need to serve multiple clients simultaneously (we'll tackle this in a later project)

3. **Process three request types:**
   - GetRequest: Return the current value for requested OID(s)
   - SetRequest: Update values for writable OIDs, return error for read-only OIDs
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
   - List all OID/value pairs for multiple OID requests
   - Convert value types to human-readable format (e.g., timeticks to hours:minutes:seconds)
4. **Handle errors gracefully**
   - Connection failures (server not running, network issues)
   - Protocol errors (malformed responses, wrong PDU types)
   - Application errors (non-zero error codes in responses)

---

# 7. Project Milestones

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

### Milestone 2: Multiple OIDs & Error Handling (Week 2)

Add support for multiple OID requests and proper error handling:
- Handle GetRequest with multiple OIDs in a single request
- Implement proper buffering for larger responses
- Return appropriate error codes for non-existent OIDs
- Handle partial failures (some OIDs exist, others don't)

**Test with:**
```bash
python snmp_manager.py get localhost:1161 1.3.6.1.2.1.1.1.0 1.3.6.1.2.1.1.3.0 1.3.6.1.2.1.1.5.0
# Should return multiple values in one response

python snmp_manager.py get localhost:1161 1.3.6.1.2.1.1.99.0
# Should return error: No such OID exists
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

---

# 8. Testing Your Implementation

### Running the Test Suite

```bash
# Run the complete test suite
python -m pytest tests/ -v

# Or run with a summary report
python run_tests.py

# Note: If 'python' doesn't work, use 'python3'
```

The test suite will automatically:
1. Start your agent on a test port
2. Run various manager commands
3. Verify responses match expected values
4. Test error conditions
5. Measure performance for multiple OID operations

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

---

# 9. Debugging Guide

## Essential Debugging Tools

### 1. Hex Viewer for Bytes
When working with binary protocols, you MUST see your bytes in hex format:

```python
def debug_bytes(label, data):
    """Helper function to print bytes in readable format"""
    print(f"{label}:")
    print(f"  Raw bytes ({len(data)} bytes): {data}")
    print(f"  Hex: {data.hex()}")
    print(f"  Hex spaced: {' '.join(f'{b:02x}' for b in data)}")
    
# Usage example:
message = struct.pack('!IIB', 22, 1234, 0xA0)
debug_bytes("GetRequest header", message)
# Output:
# GetRequest header:
#   Raw bytes (9 bytes): b'\x00\x00\x00\x16\x00\x00\x04\xd2\xa0'
#   Hex: 00000016000004d2a0
#   Hex spaced: 00 00 00 16 00 00 04 d2 a0
```

### 2. Message Structure Analyzer
Add this to your `snmp_protocol.py` for debugging:

```python
def analyze_message(data: bytes):
    """Analyze and print SNMP message structure"""
    if len(data) < 9:
        print(f"ERROR: Message too short ({len(data)} bytes, need at least 9)")
        return
    
    # Parse header
    total_size = struct.unpack('!I', data[0:4])[0]
    request_id = struct.unpack('!I', data[4:8])[0]
    pdu_type = struct.unpack('!B', data[8:9])[0]
    
    print("="*60)
    print("SNMP Message Analysis")
    print("="*60)
    print(f"Total Size: {total_size} bytes (0x{total_size:08x})")
    print(f"Request ID: {request_id} (0x{request_id:08x})")
    print(f"PDU Type: 0x{pdu_type:02x} ", end="")
    
    # Decode PDU type
    pdu_names = {0xA0: "GET_REQUEST", 0xA1: "GET_RESPONSE", 
                 0xA3: "SET_REQUEST"}
    print(f"({pdu_names.get(pdu_type, 'UNKNOWN')})")
```

## Common Errors and Solutions

### 1. Byte Order Issues

**Symptom**: Values are wrong by huge amounts (e.g., expecting 22, getting 369098752)

```python
# DEBUGGING: Check your byte order
value = 22
little_endian = struct.pack('<I', value)  # b'\x16\x00\x00\x00'
big_endian = struct.pack('!I', value)     # b'\x00\x00\x00\x16'

print(f"Value: {value}")
print(f"Little-endian: {little_endian.hex()} -> {struct.unpack('<I', little_endian)[0]}")
print(f"Big-endian: {big_endian.hex()} -> {struct.unpack('!I', big_endian)[0]}")
print(f"Wrong order: {big_endian.hex()} -> {struct.unpack('<I', big_endian)[0]}")  # 369098752!
```

**Solution**: ALWAYS use `!` prefix for network protocols:
```python
# ALWAYS use these for SNMP:
struct.pack('!I', value)    # 4-byte unsigned int
struct.pack('!H', value)    # 2-byte unsigned short
struct.pack('!B', value)    # 1-byte unsigned
```

### 2. Message Size Calculation Errors

**Symptom**: "Message size mismatch" or incomplete messages

```python
# WRONG - Common mistakes:
def pack(self):
    payload = self._build_payload()
    # Forgot to include header in size!
    total_size = len(payload)  # WRONG!
    
# CORRECT - Include ALL bytes:
def pack(self):
    payload = self._build_payload()
    # 4 (size) + 4 (request_id) + 1 (pdu_type) + payload
    total_size = 9 + len(payload)
    
    # Build message
    message = struct.pack('!I', total_size)
    message += struct.pack('!I', self.request_id)
    message += struct.pack('!B', self.pdu_type)
    message += payload
    
    # VERIFY the size is correct!
    assert len(message) == total_size, f"Size mismatch: declared {total_size}, actual {len(message)}"
    
    return message
```

### 3. String Encoding Issues

**Symptom**: `TypeError: a bytes-like object is required, not 'str'`

```python
# WRONG - Mixing strings and bytes
oid_string = "1.3.6.1.2.1.1.5.0"
message = oid_string  # This is a string, not bytes!

# CORRECT - Encode strings to bytes
oid_string = "1.3.6.1.2.1.1.5.0"
oid_bytes = encode_oid(oid_string)  # Convert to bytes

# For regular strings:
text = "router-main"
text_bytes = text.encode('utf-8')  # Convert to bytes
```

### 4. Buffering Problems

**Symptom**: Large messages arrive incomplete or corrupted

```python
# WRONG - Assumes recv() returns complete message
def receive_message(sock):
    data = sock.recv(4096)  # Might be incomplete!
    return data

# CORRECT - Buffer until complete
def receive_complete_message(sock):
    # First, get the message size (4 bytes)
    received = b''
    while len(received) < 4:
        chunk = sock.recv(4 - len(received))
        if not chunk:
            raise ConnectionError("Connection closed")
        received += chunk
    
    # Decode the size
    message_size = struct.unpack('!I', received[:4])[0]
    
    # Get the rest of the message
    while len(received) < message_size:
        remaining = message_size - len(received)
        chunk = sock.recv(min(remaining, 4096))
        if not chunk:
            raise ConnectionError("Connection closed")
        received += chunk
    
    return received
```

## Understanding Error Messages

### Struct Pack/Unpack Errors

#### Error: `struct.error: unpack requires a buffer of 4 bytes`
**Cause**: Trying to unpack more bytes than available
```python
# WRONG - Not checking if enough data exists
request_id = struct.unpack('!I', data[4:8])[0]  # Fails if len(data) < 8

# CORRECT - Check length first
if len(data) >= 8:
    request_id = struct.unpack('!I', data[4:8])[0]
else:
    raise ValueError(f"Message too short: {len(data)} bytes")
```

#### Error: `struct.error: bad char in struct format`
**Cause**: Invalid format character
```python
# Format character reference:
# B = unsigned byte (0-255)
# H = unsigned short (2 bytes, 0-65535)
# I = unsigned int (4 bytes, 0-4294967295)
# i = signed int (4 bytes, -2147483648 to 2147483647)
```

### Socket Errors

#### Error: `[Errno 98] Address already in use`
**Cause**: Previous server still holding the port
```python
# SOLUTION: Add SO_REUSEADDR before binding
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Add this!
server_socket.bind(('', 1161))
```

#### Error: `[Errno 111] Connection refused`
**Cause**: Server not running or wrong port
```python
# Debugging steps:
# 1. Check server is running: ps aux | grep snmp_agent
# 2. Check port is correct: netstat -an | grep 1161
# 3. Try connecting manually: telnet localhost 1161
```

## Protocol Debugging Techniques

### Create Test Messages Manually

```python
# Create a test GetRequest manually to understand the format
def create_test_get_request():
    # Manual message construction
    request_id = 1234
    oid = "1.3.6.1.2.1.1.1.0"
    
    # Build payload
    oid_bytes = encode_oid(oid)
    payload = struct.pack('!B', 1)  # oid_count = 1
    payload += struct.pack('!B', len(oid_bytes))  # oid_length
    payload += oid_bytes
    
    # Build message
    total_size = 9 + len(payload)
    message = struct.pack('!IIB', total_size, request_id, 0xA0)
    message += payload
    
    # Analyze what we built
    print(f"Built GetRequest:")
    print(f"  Total size: {total_size}")
    print(f"  Request ID: {request_id}")
    print(f"  PDU Type: 0xA0 (GET_REQUEST)")
    print(f"  OID: {oid}")
    print(f"  Message hex: {message.hex()}")
    
    return message
```

## Socket Programming Issues

### Server Not Accepting Connections

```python
# Add debug output to your server
def start(self):
    self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Debug: Print what we're binding to
    bind_address = ('', self.port)
    print(f"DEBUG: Binding to {bind_address}")
    self.server_socket.bind(bind_address)
    
    # Debug: Confirm listening
    self.server_socket.listen(5)
    print(f"SNMP Agent listening on port {self.port}...")
    
    while True:
        print("DEBUG: Waiting for connection...")
        client_socket, client_address = self.server_socket.accept()
        print(f"DEBUG: Accepted connection from {client_address}")
        self._handle_client(client_socket, client_address)
```

### Quick Reference Card

```python
# Quick debug snippets to copy-paste

# 1. Print hex of any bytes
print(f"Hex: {data.hex()}")

# 2. Check message size
print(f"Message size: declared={struct.unpack('!I', data[:4])[0]}, actual={len(data)}")

# 3. Verify byte order
print(f"As big-endian: {struct.unpack('!I', data[:4])[0]}")
print(f"As little-endian: {struct.unpack('<I', data[:4])[0]}")

# 4. OID debugging
oid = "1.3.6.1.2.1.1.1.0"
encoded = encode_oid(oid)
decoded = decode_oid(encoded)
print(f"OID: {oid} -> {encoded.hex()} -> {decoded}")
assert oid == decoded, "Round-trip failed!"
```

---

# 10. Grading and Submission

## Grading Rubric

| Component | Points | Criteria |
|-----------|--------|----------|
| **Protocol Compliance** | 25% | Correct binary format, proper encoding/decoding, follows specification exactly |
| **Buffering Implementation** | 20% | Correctly handles messages larger than recv buffer, no data loss or corruption |
| **Get Operations** | 20% | Single and multiple OID queries work correctly, efficient handling |
| **Set Operations** | 15% | Validates permissions, correct value types, persistent state |
| **Error Handling** | 10% | Graceful handling of all error conditions, proper error codes |
| **Code Quality** | 10% | Clean, well-documented code following Python conventions |

## Submission Requirements

Submit the following files to Gradescope:

1. **snmp_agent.py** - Your complete agent implementation
2. **snmp_manager.py** - Your complete manager implementation
3. **snmp_protocol.py** - Your protocol encoding/decoding implementation
4. **protocol_notes.txt** - Brief documentation of any design decisions or deviations from the specification

Do not modify or submit the provided files (mib_database.py, etc.).

---

# 11. Additional Resources

- **RFC 1157** - Original SNMP specification (for reference only)
- **Python struct documentation** - Essential for binary protocol implementation
- **Wireshark SNMP dissector** - Useful for comparing with real SNMP
- **Office hours** - Available for protocol questions and debugging help

Remember: You're building the same fundamental protocol that manages network infrastructure worldwide. Take pride in creating a working implementation of this critical technology!

## License

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)