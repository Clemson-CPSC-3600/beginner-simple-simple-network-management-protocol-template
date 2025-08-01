#!/usr/bin/env python3
"""
MIB Database for SNMP Agent
Contains the Management Information Base structure and permissions
"""

# MIB Database - (type, value) tuples
MIB_DATABASE = {
    # System Group (1.3.6.1.2.1.1)
    '1.3.6.1.2.1.1.1.0': ('STRING', 'Router Model X2000 - High Performance Edge Router'),
    '1.3.6.1.2.1.1.2.0': ('OID', '1.3.6.1.4.1.9.1.1234'),  # sysObjectID (Cisco example)
    '1.3.6.1.2.1.1.3.0': ('TIMETICKS', 0),  # sysUpTime (dynamically updated)
    '1.3.6.1.2.1.1.4.0': ('STRING', 'admin@example.com'),  # sysContact
    '1.3.6.1.2.1.1.5.0': ('STRING', 'router-main'),  # sysName
    '1.3.6.1.2.1.1.6.0': ('STRING', 'Server Room, Building A, Floor 2'),  # sysLocation
    '1.3.6.1.2.1.1.7.0': ('INTEGER', 72),  # sysServices
    
    # Interfaces Group (1.3.6.1.2.1.2)
    '1.3.6.1.2.1.2.1.0': ('INTEGER', 3),  # ifNumber - number of interfaces
    
    # Interface Table (1.3.6.1.2.1.2.2.1)
    # Interface 1 - WAN
    '1.3.6.1.2.1.2.2.1.1.1': ('INTEGER', 1),  # ifIndex
    '1.3.6.1.2.1.2.2.1.2.1': ('STRING', 'eth0'),  # ifDescr
    '1.3.6.1.2.1.2.2.1.3.1': ('INTEGER', 6),  # ifType (6 = ethernet)
    '1.3.6.1.2.1.2.2.1.4.1': ('INTEGER', 1500),  # ifMtu
    '1.3.6.1.2.1.2.2.1.5.1': ('COUNTER', 1000000000),  # ifSpeed (1 Gbps)
    '1.3.6.1.2.1.2.2.1.6.1': ('STRING', '00:1B:44:11:3A:B7'),  # ifPhysAddress
    '1.3.6.1.2.1.2.2.1.7.1': ('INTEGER', 1),  # ifAdminStatus (1 = up)
    '1.3.6.1.2.1.2.2.1.8.1': ('INTEGER', 1),  # ifOperStatus (1 = up)
    '1.3.6.1.2.1.2.2.1.9.1': ('TIMETICKS', 0),  # ifLastChange
    '1.3.6.1.2.1.2.2.1.10.1': ('COUNTER', 3456789012),  # ifInOctets
    '1.3.6.1.2.1.2.2.1.11.1': ('COUNTER', 23456789),  # ifInUcastPkts
    '1.3.6.1.2.1.2.2.1.12.1': ('COUNTER', 123456),  # ifInNUcastPkts
    '1.3.6.1.2.1.2.2.1.13.1': ('COUNTER', 234),  # ifInDiscards
    '1.3.6.1.2.1.2.2.1.14.1': ('COUNTER', 12),  # ifInErrors
    '1.3.6.1.2.1.2.2.1.15.1': ('COUNTER', 0),  # ifInUnknownProtos
    '1.3.6.1.2.1.2.2.1.16.1': ('COUNTER', 2345678901),  # ifOutOctets
    '1.3.6.1.2.1.2.2.1.17.1': ('COUNTER', 12345678),  # ifOutUcastPkts
    '1.3.6.1.2.1.2.2.1.18.1': ('STRING', 'WAN Interface - ISP Connection'),  # ifAlias
    
    # Interface 2 - LAN
    '1.3.6.1.2.1.2.2.1.1.2': ('INTEGER', 2),
    '1.3.6.1.2.1.2.2.1.2.2': ('STRING', 'eth1'),
    '1.3.6.1.2.1.2.2.1.3.2': ('INTEGER', 6),
    '1.3.6.1.2.1.2.2.1.4.2': ('INTEGER', 1500),
    '1.3.6.1.2.1.2.2.1.5.2': ('COUNTER', 1000000000),
    '1.3.6.1.2.1.2.2.1.6.2': ('STRING', '00:1B:44:11:3A:B8'),
    '1.3.6.1.2.1.2.2.1.7.2': ('INTEGER', 1),
    '1.3.6.1.2.1.2.2.1.8.2': ('INTEGER', 1),
    '1.3.6.1.2.1.2.2.1.9.2': ('TIMETICKS', 0),
    '1.3.6.1.2.1.2.2.1.10.2': ('COUNTER', 1876543210),
    '1.3.6.1.2.1.2.2.1.11.2': ('COUNTER', 8765432),
    '1.3.6.1.2.1.2.2.1.12.2': ('COUNTER', 54321),
    '1.3.6.1.2.1.2.2.1.13.2': ('COUNTER', 123),
    '1.3.6.1.2.1.2.2.1.14.2': ('COUNTER', 5),
    '1.3.6.1.2.1.2.2.1.15.2': ('COUNTER', 0),
    '1.3.6.1.2.1.2.2.1.16.2': ('COUNTER', 987654321),
    '1.3.6.1.2.1.2.2.1.17.2': ('COUNTER', 4567890),
    '1.3.6.1.2.1.2.2.1.18.2': ('STRING', 'LAN Interface - Internal Network'),
    
    # Interface 3 - Loopback
    '1.3.6.1.2.1.2.2.1.1.3': ('INTEGER', 3),
    '1.3.6.1.2.1.2.2.1.2.3': ('STRING', 'lo'),
    '1.3.6.1.2.1.2.2.1.3.3': ('INTEGER', 24),  # 24 = software loopback
    '1.3.6.1.2.1.2.2.1.4.3': ('INTEGER', 65536),
    '1.3.6.1.2.1.2.2.1.5.3': ('COUNTER', 0),
    '1.3.6.1.2.1.2.2.1.6.3': ('STRING', ''),
    '1.3.6.1.2.1.2.2.1.7.3': ('INTEGER', 1),
    '1.3.6.1.2.1.2.2.1.8.3': ('INTEGER', 1),
    '1.3.6.1.2.1.2.2.1.9.3': ('TIMETICKS', 0),
    '1.3.6.1.2.1.2.2.1.10.3': ('COUNTER', 567890),
    '1.3.6.1.2.1.2.2.1.11.3': ('COUNTER', 4567),
    '1.3.6.1.2.1.2.2.1.12.3': ('COUNTER', 0),
    '1.3.6.1.2.1.2.2.1.13.3': ('COUNTER', 0),
    '1.3.6.1.2.1.2.2.1.14.3': ('COUNTER', 0),
    '1.3.6.1.2.1.2.2.1.15.3': ('COUNTER', 0),
    '1.3.6.1.2.1.2.2.1.16.3': ('COUNTER', 567890),
    '1.3.6.1.2.1.2.2.1.17.3': ('COUNTER', 4567),
    '1.3.6.1.2.1.2.2.1.18.3': ('STRING', 'Loopback Interface'),
    
    # IP Group (1.3.6.1.2.1.4) - Basic IP statistics
    '1.3.6.1.2.1.4.1.0': ('INTEGER', 1),  # ipForwarding (1 = forwarding)
    '1.3.6.1.2.1.4.2.0': ('INTEGER', 64),  # ipDefaultTTL
    '1.3.6.1.2.1.4.3.0': ('COUNTER', 98765432),  # ipInReceives
    '1.3.6.1.2.1.4.4.0': ('COUNTER', 1234),  # ipInHdrErrors
    '1.3.6.1.2.1.4.5.0': ('COUNTER', 456),  # ipInAddrErrors
    '1.3.6.1.2.1.4.6.0': ('COUNTER', 87654321),  # ipForwDatagrams
    '1.3.6.1.2.1.4.9.0': ('COUNTER', 76543210),  # ipInDelivers
    '1.3.6.1.2.1.4.10.0': ('COUNTER', 65432109),  # ipOutRequests
    
    # TCP Group (1.3.6.1.2.1.6)
    '1.3.6.1.2.1.6.1.0': ('INTEGER', 2),  # tcpRtoAlgorithm
    '1.3.6.1.2.1.6.2.0': ('INTEGER', 200),  # tcpRtoMin (ms)
    '1.3.6.1.2.1.6.3.0': ('INTEGER', 120000),  # tcpRtoMax (ms)
    '1.3.6.1.2.1.6.4.0': ('INTEGER', -1),  # tcpMaxConn
    '1.3.6.1.2.1.6.5.0': ('COUNTER', 234567),  # tcpActiveOpens
    '1.3.6.1.2.1.6.6.0': ('COUNTER', 345678),  # tcpPassiveOpens
    '1.3.6.1.2.1.6.7.0': ('COUNTER', 123),  # tcpAttemptFails
    '1.3.6.1.2.1.6.8.0': ('COUNTER', 234),  # tcpEstabResets
    '1.3.6.1.2.1.6.9.0': ('INTEGER', 42),  # tcpCurrEstab
    '1.3.6.1.2.1.6.10.0': ('COUNTER', 12345678),  # tcpInSegs
    '1.3.6.1.2.1.6.11.0': ('COUNTER', 11234567),  # tcpOutSegs
    '1.3.6.1.2.1.6.12.0': ('COUNTER', 456),  # tcpRetransSegs
    
    # UDP Group (1.3.6.1.2.1.7)
    '1.3.6.1.2.1.7.1.0': ('COUNTER', 3456789),  # udpInDatagrams
    '1.3.6.1.2.1.7.2.0': ('COUNTER', 789),  # udpNoPorts
    '1.3.6.1.2.1.7.3.0': ('COUNTER', 123),  # udpInErrors
    '1.3.6.1.2.1.7.4.0': ('COUNTER', 2345678),  # udpOutDatagrams
    
    # SNMP Group (1.3.6.1.2.1.11)
    '1.3.6.1.2.1.11.1.0': ('COUNTER', 54321),  # snmpInPkts
    '1.3.6.1.2.1.11.2.0': ('COUNTER', 43210),  # snmpOutPkts
    '1.3.6.1.2.1.11.3.0': ('COUNTER', 5),  # snmpInBadVersions
    '1.3.6.1.2.1.11.4.0': ('COUNTER', 2),  # snmpInBadCommunityNames
    '1.3.6.1.2.1.11.5.0': ('COUNTER', 1),  # snmpInBadCommunityUses
    '1.3.6.1.2.1.11.6.0': ('COUNTER', 0),  # snmpInASNParseErrs
}

# Add some extra OIDs to ensure we have enough for bulk testing
for i in range(1, 51):
    MIB_DATABASE[f'1.3.6.1.4.1.99.1.{i}.0'] = ('STRING', f'Test OID {i} - This is a longer string to help test buffering of large SNMP messages')

# Permissions for each OID
MIB_PERMISSIONS = {
    # System group - mostly read-only except contact, name, location
    '1.3.6.1.2.1.1.1.0': 'read-only',
    '1.3.6.1.2.1.1.2.0': 'read-only',
    '1.3.6.1.2.1.1.3.0': 'read-only',
    '1.3.6.1.2.1.1.4.0': 'read-write',  # sysContact
    '1.3.6.1.2.1.1.5.0': 'read-write',  # sysName
    '1.3.6.1.2.1.1.6.0': 'read-write',  # sysLocation
    '1.3.6.1.2.1.1.7.0': 'read-only',
    
    # Interface descriptions are writable
    '1.3.6.1.2.1.2.2.1.18.1': 'read-write',
    '1.3.6.1.2.1.2.2.1.18.2': 'read-write',
    '1.3.6.1.2.1.2.2.1.18.3': 'read-write',
}

# All other OIDs default to read-only
for oid in MIB_DATABASE:
    if oid not in MIB_PERMISSIONS:
        MIB_PERMISSIONS[oid] = 'read-only'