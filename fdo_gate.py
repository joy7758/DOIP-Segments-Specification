import struct
import hashlib
import time

class FDOGate:
    def __init__(self, policy_file="DOIP-Segments-Specification/Policy_Dictionary.json"):
        # Simulated O(1) MsBV (Multistate Bit Vector) using a dictionary for constant time lookup
        # In a real hardware implementation, this would be a bit vector.
        self.msbv_table = {
            # Policy ID (int) -> Allowed Security Level (int)
            0x01: 0, # Public
            0x02: 1, # Restricted
            0x03: 2, # Confidential
            0x04: 3  # Top Secret
        }
        self.default_security_level = 0

    def parse_header(self, header_bytes):
        """
        Parses the 16-byte fixed header based on RFC 8200 alignment.
        Format:
        - Version (4 bits): 6 (IPv6/FDO)
        - Traffic Class (8 bits)
        - Flow Label (20 bits)
        - Payload Length (16 bits)
        - Next Header (8 bits)
        - Hop Limit (8 bits)
        - Source Address (128 bits) - Mocked as 64 bits here for simplified 16-byte structure in this specific FDO profile
        
        *Correction for FDO specific 16-byte header requirement from prompt*:
        The prompt asks for "16字节报头" (16-byte header).
        Standard IPv6 header is 40 bytes.
        FDO specific compact header might be defined differently.
        Let's assume a custom 16-byte structure for this "FDO Gateway":
        [ Version(4b) | Type(4b) | Flags(8b) ] = 2 bytes
        [ Sequence ID (32b) ] = 4 bytes
        [ Timestamp (32b) ] = 4 bytes
        [ Policy ID (32b) ] = 4 bytes
        Total: 14 bytes... need 2 more.
        
        Let's try:
        [ Magic/Ver (16b) ]
        [ Sequence (32b) ]
        [ Timestamp (32b) ]
        [ Policy ID (32b) ]
        [ Checksum (16b) ]
        Total: 16 bytes.
        """
        if len(header_bytes) != 16:
            raise ValueError("Header must be exactly 16 bytes")
        
        # Unpack: H (2 bytes), I (4 bytes), I (4 bytes), I (4 bytes), H (2 bytes)
        # Big-endian network byte order
        magic_ver, seq, ts, policy_id, checksum = struct.unpack('!HIIIH', header_bytes)
        
        return {
            "version": (magic_ver >> 12) & 0xF,
            "type": (magic_ver >> 8) & 0xF,
            "sequence": seq,
            "timestamp": ts,
            "policy_id": policy_id,
            "checksum": checksum
        }

    def validate_segment_header(self, header_bytes):
        """
        O(1) Validation using MsBV logic.
        """
        try:
            header = self.parse_header(header_bytes)
        except ValueError as e:
            return False, str(e)

        # 1. Version Check (RFC 8200 style versioning, FDO uses 6 or custom)
        # Assuming FDO spec mandates version 1 for this prototype
        if header["version"] != 1:
            return False, f"Invalid Protocol Version: {header['version']}"

        # 2. MsBV O(1) Policy Lookup
        policy_id = header["policy_id"]
        
        # In a real MsBV, this is a bitwise check: (vector >> policy_id) & 1
        # Here we use the hash map which is O(1) on average.
        if policy_id not in self.msbv_table:
            return False, f"Policy ID {policy_id} rejected by MsBV"

        return True, "Header Valid"

    def process_packet(self, packet_bytes):
        if len(packet_bytes) < 16:
            return {"status": "dropped", "reason": "Packet too short"}
        
        header_bytes = packet_bytes[:16]
        payload = packet_bytes[16:]
        
        is_valid, msg = self.validate_segment_header(header_bytes)
        
        if is_valid:
            return {
                "status": "forwarded", 
                "policy_id": struct.unpack('!I', header_bytes[10:14])[0],
                "timestamp": time.time()
            }
        else:
            return {"status": "dropped", "reason": msg}
