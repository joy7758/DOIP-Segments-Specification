# DOIP 2.0 Active Segment Extension Proposal

## 1. Specification Table: Active-Segment-Header

Based on the Proof of Concept (`fdo_segment_test.py`), the following table defines the structure of the **Active-Segment-Header**. This header is prepended to every data segment in a DOIP 2.0 transmission to enable granular, governance-aware handling.

| Offset (Bytes) | Field Name        | Size (Bytes) | Description                                                                 | Example Values               |
| :------------- | :---------------- | :----------- | :-------------------------------------------------------------------------- | :--------------------------- |
| 0-1            | Magic Byte        | 2            | Protocol identifier constant to verify the start of a valid header.          | `0x44 0x32` (`'D2'`)         |
| 2-5            | Segment ID        | 4            | Unique identifier for the specific message or file being transmitted.       | `0x000F4240` (1000000)       |
| 6-9            | Sequence Number   | 4            | The order of this specific segment within the total stream (0-indexed).     | `0x00000001`                 |
| 10-13          | Total Segments    | 4            | The total number of segments required to reconstruct the full object.       | `0x00000010` (16)            |
| 14             | Sensitivity_Level | 1            | Classification tag dictating the confidentiality level of this specific segment. | `0x00` (Public), `0x02` (Legal) |
| 15             | Operation_Hint    | 1            | Instruction for the receiving node on how to process the segment.           | `0x00` (Store), `0x02` (Inspect) |
| 16-19          | Policy_ID         | 4            | Reference to the specific governance rule or contract enforcing this data.  | `0xCAFEBABE`                 |
| 20-23          | Payload Length    | 4            | Exact length of the data payload following this header.                     | `0x00010000` (65536)         |
| 24-55          | Checksum          | 32           | SHA-256 hash of the payload for integrity verification.                     | (32-byte SHA-256 Hash)       |

**Total Header Size:** 56 Bytes

---

## 2. State Machine: Compliance Filter Logic

The **Compliance Filter** acts as a gateway guard on every node participating in the DOIP network. It evaluates every incoming segment's `Sensitivity_Level` against the node's declared `node_location` (or security clearance).

**Logic Flow:**

1.  **Packet Arrival:** Node receives an Active DOIP Segment.
2.  **Header Parsing:** Node unpacks the 56-byte header to extract metadata.
3.  **Policy Evaluation:**
    *   **IF** `node_location` is **"internal"**:
        *   **ACTION:** Forward/Process All Segments. (Trusts internal network).
    *   **IF** `node_location` is **"external"**:
        *   **CHECK:** Is `Sensitivity_Level` >= `0x02` (Legal Prohibited / High Sensitivity)?
            *   **YES:** **BLOCK/DROP** the segment. Log the event.
            *   **NO:** **FORWARD** the segment.
4.  **Result:** High-sensitivity fragments never leave the secure boundary, even if the file is being streamed.

---

## 3. Policy Mapping Guide

This guide illustrates how abstract governance laws map to the concrete byte values used in the Active Segment Header.

| Policy / Regulation                            | Sensitivity_Level (Hex) | Description                                      | Action (External Node) |
| :--------------------------------------------- | :---------------------- | :----------------------------------------------- | :--------------------- |
| **Public Information**                         | `0x00`                  | Data intended for public consumption.            | **ALLOW**              |
| **Internal Business Use**                      | `0x01`                  | Restricted to company employees; not confidential.| **ALLOW** (with Log)   |
| **China Data Security Law - Important Data**   | `0x02`                  | Data strictly prohibited from cross-border transfer.| **BLOCK**              |
| **GDPR - Special Category (Health/Biometric)** | `0x03`                  | Highly sensitive personal data.                  | **BLOCK**              |
| **Top Secret / Classified**                    | `0xFF`                  | Highest level of security clearance required.    | **BLOCK**              |

---

## 4. Architecture Memo

**Subject:** Proposal for Enhancing DOIP 2.0 Segment Specification with Governance-Aware Metadata
**Date:** 2024-05-22 (Ref: FDO-DOIP-SEC-2024)
**Lead Researcher:** Bin Zhang (GitHub: joy7758)
**Status:** Draft / Proof of Concept Validated

**1. The "Governance-Blind" Gap in Current Draft**
Based on my recent implementation and pressure testing of the DOIP 2.0 segmentation draft (Ref: joy7758/DOIP-Segments-Specification), I have identified a critical "Semantic Vacuum."
> Current byte-level transport efficiency is commendable, but the segments remain governance-blind. In decentralized networks, passive segments cannot self-identify their legal status or sensitivity. This makes protocol-level compliance—specifically regarding Data Sovereignty (e.g., China's Data Security Law)—impossible to enforce at the edge during transit.

**2. The Solution: Active Metadata Injection**
I propose the "Active Segment Header" extension to bridge this gap. By injecting specific governance fields into the segment header, we transform a "dumb chunk" into a Machine-Actionable Digital Object Fragment.

**Proposed Extensions:**
*   **Sensitivity_Level (1 byte):** Enables autonomous node decision-making.
*   **Policy_ID (4 bytes):** Provides an immutable link to the governance framework (e.g., MCP-Legal-China).

**3. Empirical Validation (POC Results)**
I have successfully validated this architecture using a Python-based FDO Proxy.
*   **Condition:** Transmission of "Critical IP" segments across non-trusted external nodes.
*   **Mechanism:** The node executed an $Allow(s)$ function at the protocol layer.
*   **Result:** Unauthorized segments were successfully intercepted at the atomic level, preventing illegal data reassembly while maintaining line-rate performance for public segments.

**4. Recommendation**
I recommend integrating these fields into the next iteration of the DOIP 2.0 specification to ensure that the standard is not just efficient, but legally robust and globally interoperable.
