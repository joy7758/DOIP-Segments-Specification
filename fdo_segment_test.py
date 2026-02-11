import os
import hashlib
import struct
import random

class DOIPSegmentHeader:
    """
    Represents a DOIP 2.0 Segment Header (Active FDO).
    
    Structure (Updated):
    - Magic Byte (2 bytes): 'D2'
    - Segment ID (4 bytes): Unique ID for the message/file
    - Sequence Number (4 bytes): Order of this segment
    - Total Segments (4 bytes): Total number of segments
    - Sensitivity_Level (1 byte): 0x00=Public, 0x01=Restricted, 0x02=Legal Prohibited
    - Operation_Hint (1 byte): 0x00=Store, 0x01=Compute, 0x02=Inspect
    - Policy_ID (4 bytes): Reference to governance rule
    - Payload Length (4 bytes): Length of data in this segment
    - Checksum (32 bytes): SHA-256 checksum of the payload
    """
    # Updated Format: !2sIIIBBI I 32s
    # Note: 4 + 4 + 4 + 1 + 1 + 4 + 4 + 32 = 54 bytes + 2 (magic) = 56 bytes
    HEADER_FORMAT = "!2sIIIBBI I 32s"  
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, segment_id, seq_num, total_segments, sensitivity, op_hint, policy_id, payload):
        self.magic = b'D2'
        self.segment_id = segment_id
        self.seq_num = seq_num
        self.total_segments = total_segments
        self.sensitivity = sensitivity
        self.op_hint = op_hint
        self.policy_id = policy_id
        self.payload_length = len(payload)
        self.checksum = hashlib.sha256(payload).digest()

    def pack(self):
        return struct.pack(
            self.HEADER_FORMAT,
            self.magic,
            self.segment_id,
            self.seq_num,
            self.total_segments,
            self.sensitivity,
            self.op_hint,
            self.policy_id,
            self.payload_length,
            self.checksum
        )

    @classmethod
    def unpack(cls, data):
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Data too short for header")
        
        header_data = data[:cls.HEADER_SIZE]
        magic, seg_id, seq_num, total_segs, sens, op, pol_id, p_len, checksum = struct.unpack(cls.HEADER_FORMAT, header_data)
        
        if magic != b'D2':
            raise ValueError("Invalid Magic Bytes")
            
        return {
            "magic": magic,
            "segment_id": seg_id,
            "seq_num": seq_num,
            "total_segments": total_segs,
            "sensitivity": sens,
            "op_hint": op,
            "policy_id": pol_id,
            "payload_length": p_len,
            "checksum": checksum
        }, data[cls.HEADER_SIZE:]

def create_dummy_file(filename, size_mb=1):
    """Creates a dummy binary file of specified size in MB."""
    print(f"Generating {size_mb}MB dummy file: {filename}...")
    with open(filename, 'wb') as f:
        f.write(os.urandom(size_mb * 1024 * 1024))
    print("File generated.")

def split_file(filename, segment_size=1024*64, policy_id=0xCAFEBABE): # 64KB segments
    """Splits a file into Active DOIP segments with sensitivity tagging."""
    print(f"Splitting {filename} into segments...")
    segments = []
    file_size = os.path.getsize(filename)
    segment_id = random.randint(1, 1000000)
    
    # Calculate total segments
    total_segments = (file_size + segment_size - 1) // segment_size
    
    with open(filename, 'rb') as f:
        seq_num = 0
        current_offset = 0
        
        while True:
            chunk = f.read(segment_size)
            if not chunk:
                break
            
            # --- Governance Logic Injection ---
            # Rule: First 128KB (2 segments of 64KB) is Sensitive (0x02 - Legal Prohibited)
            # Rest is Public (0x00)
            if current_offset < (128 * 1024):
                sensitivity = 0x02 # Legal Prohibited
                op_hint = 0x02 # Inspect-Before-Merge
            else:
                sensitivity = 0x00 # Public
                op_hint = 0x00 # Store
            
            header = DOIPSegmentHeader(segment_id, seq_num, total_segments, sensitivity, op_hint, policy_id, chunk)
            segment_data = header.pack() + chunk
            segments.append(segment_data)
            
            seq_num += 1
            current_offset += len(chunk)
            
    print(f"Created {len(segments)} segments.")
    return segments

def simulate_distributed_node(segments, node_location="internal"):
    """
    Simulates a network node enforcing compliance rules.
    
    Rules:
    - If node_location == "external", DROP any segment with Sensitivity >= 0x02.
    """
    print(f"--- Simulating Node Processing (Location: {node_location}) ---")
    processed_segments = []
    dropped_count = 0
    
    for seg_data in segments:
        header_info, _ = DOIPSegmentHeader.unpack(seg_data)
        sens = header_info['sensitivity']
        
        if node_location == "external" and sens >= 0x02:
            print(f"  [BLOCK] Segment {header_info['seq_num']} dropped! (Sensitivity: {sens} >= 0x02)")
            dropped_count += 1
            continue # Drop segment
            
        processed_segments.append(seg_data)
        
    print(f"--- Node Processing Complete. Dropped: {dropped_count}, Forwarded: {len(processed_segments)} ---")
    return processed_segments

def reassemble_segments(segments, output_filename):
    """Reassembles segments into a file and verifies integrity."""
    print(f"Reassembling segments into {output_filename}...")
    
    if not segments:
        print("Error: No segments to reassemble!")
        return

    parsed_segments = []
    
    # Get total segments from the first available segment to check for missing parts
    first_header, _ = DOIPSegmentHeader.unpack(segments[0])
    expected_total = first_header['total_segments']
    
    for seg_data in segments:
        header_info, payload = DOIPSegmentHeader.unpack(seg_data)
        
        # Integrity Check
        calculated_checksum = hashlib.sha256(payload).digest()
        if calculated_checksum != header_info['checksum']:
            raise ValueError(f"Checksum mismatch in segment {header_info['seq_num']}")
            
        parsed_segments.append((header_info['seq_num'], payload))
    
    # Sort and check for gaps
    parsed_segments.sort(key=lambda x: x[0])
    
    unique_seq_nums = set(x[0] for x in parsed_segments)
    if len(unique_seq_nums) != expected_total:
        print(f"WARNING: Missing segments! Expected {expected_total}, got {len(unique_seq_nums)}.")
    
    with open(output_filename, 'wb') as f:
        for _, payload in parsed_segments:
            f.write(payload)
            
    print("Reassembly complete.")

def verify_files_match(file1, file2):
    """Compares two files to ensure they are identical."""
    if not os.path.exists(file2):
        print("FAILURE: Reassembled file does not exist.")
        return False
        
    h1 = hashlib.sha256()
    h2 = hashlib.sha256()
    
    with open(file1, 'rb') as f:
        h1.update(f.read())
    with open(file2, 'rb') as f:
        h2.update(f.read())
        
    if h1.digest() == h2.digest():
        print("SUCCESS: Original and reassembled files match exactly!")
        return True
    else:
        print("FAILURE: Files do not match.")
        return False

def main():
    original_file = "dummy_1mb.bin"
    reassembled_file = "reassembled_1mb.bin"
    
    # 1. Create Dummy File
    create_dummy_file(original_file, size_mb=1)
    
    # 2. Split into Active FDO Segments
    print("\nSTEP 1: Splitting file into Active FDO Segments...")
    segments = split_file(original_file)
    
    # 3. Simulate External Node Transmission (Compliance Check)
    print("\nSTEP 2: Transmitting through External Node (Compliance Check)...")
    filtered_segments = simulate_distributed_node(segments, node_location="external")
    
    # 4. Attempt Reassembly
    print("\nSTEP 3: Attempting Reassembly...")
    try:
        reassemble_segments(filtered_segments, reassembled_file)
        result = verify_files_match(original_file, reassembled_file)
        if not result:
            print("\nRESULT: FAILED as expected (Data Loss detected due to Governance Policy).")
        else:
             print("\nRESULT: PASSED (Unexpectedly).")
             
    except Exception as e:
        print(f"Error during processing: {e}")
    finally:
        # Cleanup
        if os.path.exists(original_file):
            os.remove(original_file)
        if os.path.exists(reassembled_file):
            os.remove(reassembled_file)

if __name__ == "__main__":
    main()
