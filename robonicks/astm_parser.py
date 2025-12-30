"""
ASTM Message Parser Module
Parses ASTM E1394 messages and extracts test result data
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ASTMPatientInfo:
    """Patient information extracted from P record"""
    sequence: str = ''
    patient_id: str = ''
    lab_patient_id: str = ''
    first_name: str = ''
    last_name: str = ''
    middle_name: str = ''
    dob: str = ''
    gender: str = ''
    race: str = ''
    street: str = ''
    city: str = ''
    state: str = ''
    zip: str = ''
    phone: str = ''
    attending_physician: str = ''


@dataclass
class ASTMOrderInfo:
    """Order information extracted from O record"""
    sequence: str = ''
    specimen_id: str = ''
    instrument_specimen_id: str = ''
    test_code: str = ''
    test_name: str = ''
    priority: str = ''
    requested_datetime: str = ''
    collection_datetime: str = ''
    ordering_provider: str = ''
    report_type: str = ''


@dataclass
class ASTMResultInfo:
    """Result information extracted from R record"""
    sequence: str = ''
    test_code: str = ''
    test_name: str = ''
    value: str = ''
    units: str = ''
    reference_range: str = ''
    abnormal_flag: str = ''
    result_status: str = ''
    result_datetime: str = ''
    operator_id: str = ''


@dataclass
class ASTMCommentInfo:
    """Comment information extracted from C record"""
    sequence: str = ''
    source: str = ''
    comment_text: str = ''
    comment_type: str = ''


class ASTMParser:
    """Parses ASTM E1394-97 messages"""
    
    # ASTM delimiters
    FIELD_DELIMITER = '|'
    COMPONENT_DELIMITER = '^'
    REPEAT_DELIMITER = '\\'
    ESCAPE_DELIMITER = '&'
    
    # Record types
    HEADER = 'H'
    PATIENT = 'P'
    ORDER = 'O'
    RESULT = 'R'
    COMMENT = 'C'
    TERMINATOR = 'L'
    
    # Frame characters
    STX = '\x02'
    ETX = '\x03'
    CR = '\r'
    LF = '\n'
    
    def __init__(self):
        self.sender_id = ''
        self.receiver_id = ''
        self.message_timestamp = ''
        self.version = ''
        self.processing_id = ''
    
    def parse_message(self, message: str) -> Dict:
        """
        Parse a complete ASTM message
        
        Args:
            message: ASTM message string
            
        Returns:
            Dictionary containing parsed data
        """
        # Remove framing characters if present
        message = self._remove_framing(message)
        
        # Split into records
        records = self._split_records(message)
        
        parsed_data = {
            'header': {},
            'patient': None,
            'orders': [],
            'results': [],
            'comments': [],
            'terminator': {}
        }
        
        current_order_idx = -1
        
        for record in records:
            if not record:
                continue
            
            record_type = record[0] if record else ''
            
            if record_type == self.HEADER:
                parsed_data['header'] = self._parse_header(record)
            
            elif record_type == self.PATIENT:
                parsed_data['patient'] = self._parse_patient(record)
            
            elif record_type == self.ORDER:
                order_data = self._parse_order(record)
                parsed_data['orders'].append(order_data)
                current_order_idx += 1
            
            elif record_type == self.RESULT:
                result_data = self._parse_result(record)
                parsed_data['results'].append(result_data)
            
            elif record_type == self.COMMENT:
                comment_data = self._parse_comment(record)
                parsed_data['comments'].append(comment_data)
            
            elif record_type == self.TERMINATOR:
                parsed_data['terminator'] = self._parse_terminator(record)
        
        return parsed_data
    
    def _remove_framing(self, message: str) -> str:
        """Remove STX, ETX, and checksum framing"""
        # Remove STX at start
        if message.startswith(self.STX):
            message = message[1:]
        
        # Remove ETX, checksum, and trailing CR/LF
        if self.ETX in message:
            etx_pos = message.find(self.ETX)
            message = message[:etx_pos]
        
        return message
    
    def _split_records(self, message: str) -> List[str]:
        """Split message into individual records"""
        # Split by CR+LF or just CR or just LF
        records = message.replace(self.CR + self.LF, '\n').replace(self.CR, '\n').split('\n')
        return [r.strip() for r in records if r.strip()]
    
    def _split_fields(self, record: str) -> List[str]:
        """Split record into fields"""
        return record.split(self.FIELD_DELIMITER)
    
    def _split_components(self, field: str) -> List[str]:
        """Split field into components"""
        if not field:
            return []
        return field.split(self.COMPONENT_DELIMITER)
    
    def _get_field(self, fields: List[str], index: int, default: str = '') -> str:
        """Safely get field by index"""
        try:
            if index < len(fields):
                return fields[index] if fields[index] else default
            return default
        except (IndexError, AttributeError):
            return default
    
    def _parse_header(self, record: str) -> Dict:
        """Parse Header (H) record"""
        fields = self._split_fields(record)
        
        # Field 5 contains sender ID and version
        sender_field = self._get_field(fields, 4)
        sender_components = self._split_components(sender_field)
        
        self.sender_id = sender_components[0] if len(sender_components) > 0 else ''
        self.version = sender_components[1] if len(sender_components) > 1 else ''
        self.receiver_id = self._get_field(fields, 9)
        self.processing_id = self._get_field(fields, 11)
        self.message_timestamp = self._get_field(fields, 13)
        
        return {
            'record_type': 'H',
            'delimiter_definition': self._get_field(fields, 1),
            'message_control_id': self._get_field(fields, 2),
            'sender_id': self.sender_id,
            'version': self.version,
            'receiver_id': self.receiver_id,
            'processing_id': self.processing_id,
            'timestamp': self.message_timestamp
        }
    
    def _parse_patient(self, record: str) -> ASTMPatientInfo:
        """Parse Patient (P) record"""
        fields = self._split_fields(record)
        
        patient = ASTMPatientInfo()
        patient.sequence = self._get_field(fields, 1)
        patient.patient_id = self._get_field(fields, 2)
        patient.lab_patient_id = self._get_field(fields, 3)
        
        # Parse patient name (Last^First^Middle)
        name_field = self._get_field(fields, 5)
        name_components = self._split_components(name_field)
        patient.last_name = name_components[0] if len(name_components) > 0 else ''
        patient.first_name = name_components[1] if len(name_components) > 1 else ''
        patient.middle_name = name_components[2] if len(name_components) > 2 else ''
        
        patient.dob = self._get_field(fields, 7)
        patient.gender = self._get_field(fields, 8)
        patient.race = self._get_field(fields, 9)
        
        # Parse address
        address_field = self._get_field(fields, 10)
        address_components = self._split_components(address_field)
        patient.street = address_components[0] if len(address_components) > 0 else ''
        patient.city = address_components[2] if len(address_components) > 2 else ''
        patient.state = address_components[3] if len(address_components) > 3 else ''
        patient.zip = address_components[4] if len(address_components) > 4 else ''
        
        patient.phone = self._get_field(fields, 12)
        patient.attending_physician = self._get_field(fields, 13)
        
        return patient
    
    def _parse_order(self, record: str) -> ASTMOrderInfo:
        """Parse Order (O) record"""
        fields = self._split_fields(record)
        
        order = ASTMOrderInfo()
        order.sequence = self._get_field(fields, 1)
        order.specimen_id = self._get_field(fields, 2)
        order.instrument_specimen_id = self._get_field(fields, 3)
        
        # Parse universal test ID (^^^code^name)
        test_field = self._get_field(fields, 4)
        test_components = self._split_components(test_field)
        order.test_code = test_components[3] if len(test_components) > 3 else ''
        order.test_name = test_components[4] if len(test_components) > 4 else ''
        
        order.priority = self._get_field(fields, 5)
        order.requested_datetime = self._get_field(fields, 6)
        order.collection_datetime = self._get_field(fields, 7)
        order.ordering_provider = self._get_field(fields, 16)
        order.report_type = self._get_field(fields, 25)
        
        return order
    
    def _parse_result(self, record: str) -> ASTMResultInfo:
        """Parse Result (R) record"""
        fields = self._split_fields(record)
        
        result = ASTMResultInfo()
        result.sequence = self._get_field(fields, 1)
        
        # Parse universal test ID (^^^code^name)
        test_field = self._get_field(fields, 2)
        test_components = self._split_components(test_field)
        result.test_code = test_components[3] if len(test_components) > 3 else ''
        result.test_name = test_components[4] if len(test_components) > 4 else ''
        
        result.value = self._get_field(fields, 3)
        result.units = self._get_field(fields, 4)
        result.reference_range = self._get_field(fields, 5)
        result.abnormal_flag = self._get_field(fields, 6)
        result.result_status = self._get_field(fields, 8)
        result.operator_id = self._get_field(fields, 10)
        result.result_datetime = self._get_field(fields, 12)
        
        return result
    
    def _parse_comment(self, record: str) -> ASTMCommentInfo:
        """Parse Comment (C) record"""
        fields = self._split_fields(record)
        
        comment = ASTMCommentInfo()
        comment.sequence = self._get_field(fields, 1)
        comment.source = self._get_field(fields, 2)
        comment.comment_text = self._get_field(fields, 3)
        comment.comment_type = self._get_field(fields, 4)
        
        return comment
    
    def _parse_terminator(self, record: str) -> Dict:
        """Parse Terminator (L) record"""
        fields = self._split_fields(record)
        
        return {
            'record_type': 'L',
            'sequence': self._get_field(fields, 1),
            'termination_code': self._get_field(fields, 2)
        }
    
    def extract_patient_data(self, parsed_message: Dict) -> Optional[Dict]:
        """Extract patient data from parsed message"""
        patient = parsed_message.get('patient')
        if not patient:
            return None
        
        return {
            'patient_id': patient.patient_id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'middle_name': patient.middle_name,
            'dob': patient.dob,
            'gender': patient.gender,
            'phone': patient.phone,
            'street': patient.street,
            'city': patient.city,
            'state': patient.state,
            'zip': patient.zip
        }
    
    def extract_test_results(self, parsed_message: Dict) -> List[Dict]:
        """Extract test results from parsed message"""
        results = []
        
        for result in parsed_message.get('results', []):
            results.append({
                'test_code': result.test_code,
                'test_name': result.test_name,
                'value': result.value,
                'units': result.units,
                'reference_range': result.reference_range,
                'abnormal_flag': result.abnormal_flag,
                'result_status': result.result_status,
                'result_datetime': result.result_datetime,
                'operator_id': result.operator_id
            })
        
        return results
    
    def extract_comments(self, parsed_message: Dict) -> List[str]:
        """Extract comments from parsed message"""
        return [comment.comment_text for comment in parsed_message.get('comments', [])]


# Example usage
if __name__ == "__main__":
    # Example ASTM message
    sample_message = """H|\\^&|||IVD_DEVICE^E1394-97|||||LIS||P|1|20231215120000
P|1|PAT12345||DOE^JOHN^M||19850615|M|||123 Main St^^Boston^MA^02101||+1234567890|||||||||||||||||||||
O|1|SAMPLE001||^^^MALARIA^Malaria Parasite Detection|R|20231215120000|||||||||||Dr. Smith||||||F||||||
R|1|^^^MALARIA^Malaria Result|Positive||Negative|A||F||TECH01||20231215120500|
R|2|^^^SPECIES^Parasite Species|Plasmodium falciparum|||||F||TECH01||20231215120500|
C|1|I|Ring forms and gametocytes observed|G
L|1|N"""
    
    parser = ASTMParser()
    
    print("Parsing ASTM Message:")
    print("=" * 80)
    
    parsed = parser.parse_message(sample_message)
    
    print("\nHeader:")
    print(parsed['header'])
    
    print("\nPatient:")
    patient = parsed['patient']
    if patient:
        print(f"  ID: {patient.patient_id}")
        print(f"  Name: {patient.first_name} {patient.last_name}")
        print(f"  DOB: {patient.dob}")
        print(f"  Gender: {patient.gender}")
    
    print("\nOrders:")
    for order in parsed['orders']:
        print(f"  Specimen: {order.specimen_id}")
        print(f"  Test: {order.test_name} ({order.test_code})")
    
    print("\nResults:")
    for result in parsed['results']:
        print(f"  {result.test_name}: {result.value} {result.units}")
        print(f"    Abnormal: {result.abnormal_flag}, Status: {result.result_status}")
    
    print("\nComments:")
    for comment in parsed['comments']:
        print(f"  {comment.comment_text}")
    
    print("\n" + "=" * 80)
