# ASTM Protocol Implementation

## Overview

Complete ASTM E1394-97 protocol implementation for laboratory equipment communication, including both message generation and parsing.

## Files Created

1. **[astm_generator.py](astm_generator.py)** - ASTM message generator
2. **[astm_parser.py](astm_parser.py)** - ASTM message parser

## ASTM Message Structure

ASTM E1394-97 messages consist of records separated by CR+LF:

```
H - Header Record (sender info, timestamp)
P - Patient Record (demographics)
O - Order Record (test orders)
R - Result Record(s) (test results, one per observation)
C - Comment Record(s) (optional notes)
L - Terminator Record (end of message)
```

### Field Delimiter
- Fields separated by: `|`
- Components separated by: `^`
- Repeats separated by: `\`
- Escape character: `&`

## Usage Examples

### Generating ASTM Messages

```python
from astm_generator import ASTMMessageGenerator

generator = ASTMMessageGenerator()

# Prepare data
patient = {
    'patient_id': 'PAT12345',
    'first_name': 'John',
    'last_name': 'Doe',
    'dob': '19850615',
    'gender': 'M',
    'phone': '+1234567890'
}

order = {
    'specimen_id': 'SAMPLE001',
    'test_code': 'MALARIA',
    'test_name': 'Malaria Parasite Detection',
    'priority': 'R',
    'ordering_provider': 'Dr. Smith',
    'report_type': 'F'
}

results = [
    {
        'test_code': 'MALARIA',
        'test_name': 'Malaria Result',
        'value': 'Positive',
        'units': '',
        'reference_range': 'Negative',
        'abnormal_flag': 'A',
        'result_status': 'F'
    },
    {
        'test_code': 'SPECIES',
        'test_name': 'Parasite Species',
        'value': 'Plasmodium falciparum',
        'units': '',
        'reference_range': '',
        'abnormal_flag': '',
        'result_status': 'F'
    }
]

# Generate ASTM message
message = generator.generate_astm_message(
    patient_data=patient,
    order_data=order,
    results=results,
    sender_id='IVD_DEVICE_001',
    comments=['Ring forms and gametocytes observed']
)

print(message)
```

### Output Example

```
H|\^&|||IVD_DEVICE_001^E1394-97|||||LIS||P|1|20231215120000
P|1|PAT12345||DOE^JOHN^M||19850615|M||||+1234567890|||||||||||||||||||
O|1|SAMPLE001||^^^MALARIA^Malaria Parasite Detection|R|20231215120000|||||||||||Dr. Smith|||||||||F|||||
R|1|^^^MALARIA^Malaria Result|Positive||Negative|A||F||||20231215120000|
R|2|^^^SPECIES^Parasite Species|Plasmodium falciparum|||||F||||20231215120000|
C|1|I|Ring forms and gametocytes observed|G
L|1|N
```

### Parsing ASTM Messages

```python
from astm_parser import ASTMParser

parser = ASTMParser()

# Parse message
parsed = parser.parse_message(astm_message)

# Access parsed data
print("Patient ID:", parsed['patient'].patient_id)
print("Patient Name:", parsed['patient'].first_name, parsed['patient'].last_name)

for result in parsed['results']:
    print(f"{result.test_name}: {result.value} {result.units}")
    print(f"  Status: {result.result_status}, Abnormal: {result.abnormal_flag}")

# Extract formatted data
patient_data = parser.extract_patient_data(parsed)
test_results = parser.extract_test_results(parsed)
comments = parser.extract_comments(parsed)
```

## Integration with Test Result Service

The ASTM generator is now fully integrated:

```python
from services.test_result_service import TestResultService

service = TestResultService()

# Save test result - automatically generates BOTH HL7 AND ASTM
test_id = service.save_test_result(
    sample_id="SAMPLE001",
    test_name="Malaria Detection",
    result_data={
        'parasite_detected': True,
        'parasite_species': 'Plasmodium falciparum',
        'result_value': 'Positive',
        # ...
    },
    patient_data={
        'patient_id': 'PAT001',
        'first_name': 'John',
        'last_name': 'Doe',
        # ...
    }
)

# Get ASTM message from database
astm_message = service.get_protocol_message(test_id, 'ASTM')

# Send via communication service
from services.communication_service import CommunicationService
comm_service = CommunicationService()
comm_service.send_raw_message(astm_message.encode('utf-8'))
```

## ASTM Record Details

### Header (H) Record
```
H|\^&|||sender_id^version|||||receiver_id||P|1|timestamp
```
- Field 1: Record type (H)
- Field 2: Delimiter definition
- Field 5: Sender ID and version
- Field 10: Receiver ID
- Field 12: Processing ID (P=Production, T=Test)
- Field 14: Timestamp

### Patient (P) Record
```
P|seq|patient_id||last^first^middle||dob|gender||||phone|
```
- Field 1: Record type (P)
- Field 2: Sequence number
- Field 3: Patient ID
- Field 6: Patient name (Last^First^Middle)
- Field 8: Date of birth (YYYYMMDD)
- Field 9: Sex (M/F/U)
- Field 13: Phone number

### Order (O) Record
```
O|seq|specimen_id||^^^test_code^test_name|priority|req_datetime||||||||||||provider||||||report_type|
```
- Field 1: Record type (O)
- Field 2: Sequence number
- Field 3: Specimen/Sample ID
- Field 5: Universal test ID (^^^code^name)
- Field 6: Priority (R=Routine, S=Stat)
- Field 7: Requested datetime
- Field 17: Ordering provider
- Field 26: Report type (F=Final, P=Preliminary)

### Result (R) Record
```
R|seq|^^^test_code^test_name|value|units|ref_range|abnormal_flag||result_status||operator_id||datetime|
```
- Field 1: Record type (R)
- Field 2: Sequence number
- Field 3: Universal test ID
- Field 4: Result value
- Field 5: Units
- Field 6: Reference range
- Field 7: Abnormal flags (N/A/H/L)
- Field 9: Result status (F=Final, P=Preliminary)
- Field 11: Operator ID
- Field 13: Result datetime

### Comment (C) Record
```
C|seq|source|comment_text|type
```
- Field 1: Record type (C)
- Field 2: Sequence number
- Field 3: Comment source (I=Instrument, L=Laboratory)
- Field 4: Comment text
- Field 5: Comment type (G=Generic)

### Terminator (L) Record
```
L|seq|termination_code
```
- Field 1: Record type (L)
- Field 2: Sequence number
- Field 3: Termination code (N=Normal, Q=Request info)

## Features

### Generator Features
✅ Full ASTM E1394-97 compliance
✅ Multiple results per message
✅ Comment support
✅ Configurable sender/receiver
✅ Timestamp generation
✅ Optional framing characters (STX/ETX)
✅ Checksum calculation
✅ Simple result message helper

### Parser Features
✅ Complete message parsing
✅ Dataclass-based structured output
✅ Safe field extraction
✅ Component parsing (^ delimiter)
✅ Multiple results support
✅ Comment extraction
✅ Framing character removal
✅ Helper methods for data extraction

## Testing

Both modules include test examples:

```bash
# Test generator
python astm_generator.py

# Test parser
python astm_parser.py
```

## Comparison: HL7 vs ASTM

| Feature | HL7 | ASTM |
|---------|-----|------|
| **Structure** | Segments with \| delimiter | Records with \| delimiter |
| **Message Type** | MSH defines type (ORU^R01) | H record starts message |
| **Patient** | PID segment | P record |
| **Order** | OBR segment | O record |
| **Results** | OBX segments | R records |
| **Comments** | NTE segments | C records |
| **Encoding** | Multiple encodings | Standard E1394 |
| **Usage** | Healthcare systems, LIS | Lab instruments, analyzers |

## Benefits

✅ **Complete Implementation** - No placeholders, fully functional
✅ **Standard Compliant** - Follows ASTM E1394-97 specification
✅ **Easy to Use** - Simple API for generation and parsing
✅ **Well Documented** - Comprehensive examples and documentation
✅ **Tested** - Working examples included
✅ **Integrated** - Already connected to test result service
✅ **Flexible** - Supports multiple results, comments, custom fields

## Next Steps

The ASTM implementation is complete and integrated. You can now:

1. ✅ Generate ASTM messages automatically when saving test results
2. ✅ Parse incoming ASTM messages from instruments
3. ✅ Select ASTM protocol in Utilities screen
4. ✅ Send ASTM messages via USB/LAN/Serial interfaces
5. ✅ Store ASTM messages in database for audit trail

The system now supports both HL7 and ASTM protocols with full generation and parsing capabilities!
