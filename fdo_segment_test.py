import unittest
import struct
import time
from fdo_gate import FDOGate

class TestFDOGate(unittest.TestCase):
    def setUp(self):
        self.gate = FDOGate()

    def create_header(self, version=1, seq=1, ts=int(time.time()), policy_id=0x01):
        # Construct 16-byte header
        # Version 1 (0001), Type 0 (0000) -> 0x10 (high byte of magic_ver)
        magic_ver = (version << 12) | 0x0000 
        checksum = 0xFFFF # Mock checksum
        
        return struct.pack('!HIIIH', magic_ver, seq, ts, policy_id, checksum)

    def test_valid_header(self):
        header = self.create_header(policy_id=0x01) # 0x01 is allowed
        packet = header + b"payload_data"
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "forwarded")

    def test_invalid_policy_msbv(self):
        header = self.create_header(policy_id=0x99) # 0x99 not in MsBV
        packet = header + b"payload_data"
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "dropped")
        self.assertIn("rejected by MsBV", result["reason"])

    def test_invalid_version(self):
        header = self.create_header(version=2) # Expects 1
        packet = header + b"payload_data"
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "dropped")
        self.assertIn("Invalid Protocol Version", result["reason"])

    def test_short_packet(self):
        packet = b"short"
        result = self.gate.process_packet(packet)
        self.assertEqual(result["status"], "dropped")

if __name__ == '__main__':
    unittest.main()
