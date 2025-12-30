"""
ASTM Message Generator Module
Generates ASTM E1394 messages for IVD (In Vitro Diagnostic) device test results
"""

from datetime import datetime
from typing import Dict, List, Optional


class ASTMMessageGenerator:
    """Generates ASTM E1394-97 messages from IVD device test data"""
    
    # ASTM delimiters
    FIELD_DELIMITER = '|'
    REPEAT_DELIMITER = '\\'
    COMPONENT_DELIMITER = '^'
    ESCAPE_DELIMITER = '&'
    
    # Record type indicators
    HEADER = 'H'
    PATIENT = 'P'
    ORDER = 'O'
    RESULT = 'R'
    COMMENT = 'C'
    TERMINATOR = 'L'
    
    # Frame characters
    STX = '\x02'  # Start of text
    ETX = '\x03'  # End of text
    CR = '\r'     # Carriage return
    LF = '\n'     # Line feed
    
    def __init__(self):
        self.message_sequence = 1
    
    def _get_timestamp(self, format_type: str = 'full') -> str:
        """
        Generate ASTM timestamp
        Full format: YYYYMMDDHHMMSS
        Date only: YYYYMMDD
        """
        now = datetime.now()
        if format_type == 'full':
            return now.strftime('%Y%m%d%H%M%S')
        elif format_type == 'date':
            return now.strftime('%Y%m%d')
        else:
            return now.strftime('%Y%m%d%H%M%S')
    
    def _build_header(
        self,
        sender_id: str = 'IVD_DEVICE',
        receiver_id: str = '',
        version: str = 'E1394-97'
    ) -> str:
        """
        Build ASTM Header (H) record
        Format: H|\^&|||sender^version|||||receiver||P|1|timestamp
        """
        delimiter_definition = f'{self.REPEAT_DELIMITER}{self.COMPONENT_DELIMITER}{self.ESCAPE_DELIMITER}'
        timestamp = self._get_timestamp('full')
        
        fields = [
            self.HEADER,                    # 1: Record Type ID
            delimiter_definition,            # 2: Delimiter Definition
            '',                             # 3: Message Control ID (optional)
            '',                             # 4: Access Password (optional)
            f'{sender_id}{self.COMPONENT_DELIMITER}{version}',  # 5: Sender ID
            '',                             # 6: Sender Address
            '',                             # 7: Reserved
            '',                             # 8: Reserved
            '',                             # 9: Reserved
            receiver_id,                    # 10: Receiver ID
            '',                             # 11: Comment
            'P',                            # 12: Processing ID (P=Production, T=Test)
            '1',                            # 13: Version Number
            timestamp                       # 14: Timestamp
        ]
        
        return self.FIELD_DELIMITER.join(fields)
    
    def _build_patient(
        self,
        patient_data: Dict,
        sequence: int = 1
    ) -> str:
        """
        Build ASTM Patient (P) record
        Format: P|seq|patient_id||name||birthdate|sex|||||||||||||
        """
        patient_id = patient_data.get('patient_id', '')
        
        # Build patient name: Last^First^Middle
        last_name = patient_data.get('last_name', '')
        first_name = patient_data.get('first_name', '')
        middle_name = patient_data.get('middle_name', '')
        patient_name = f"{last_name}{self.COMPONENT_DELIMITER}{first_name}{self.COMPONENT_DELIMITER}{middle_name}"
        
        dob = patient_data.get('dob', '')
        gender = patient_data.get('gender', 'U')
        
        # Build address if available
        street = patient_data.get('street', '')
        city = patient_data.get('city', '')
        state = patient_data.get('state', '')
        zip_code = patient_data.get('zip', '')
        address = ''
        if street or city:
            address = f"{street}{self.COMPONENT_DELIMITER}{self.COMPONENT_DELIMITER}{city}{self.COMPONENT_DELIMITER}{state}{self.COMPONENT_DELIMITER}{zip_code}"
        
        phone = patient_data.get('phone', '')
        
        fields = [
            self.PATIENT,      # 1: Record Type ID
            str(sequence),     # 2: Sequence Number
            patient_id,        # 3: Practice Assigned Patient ID
            '',                # 4: Laboratory Assigned Patient ID
            '',                # 5: Patient ID No. 3
            patient_name,      # 6: Patient Name
            '',                # 7: Mother's Maiden Name
            dob,               # 8: Birthdate
            gender,            # 9: Patient Sex (M/F/U)
            '',                # 10: Patient Race
            address,           # 11: Patient Address
            '',                # 12: Reserved
            phone,             # 13: Patient Telephone Number
            '',                # 14: Attending Physician ID
            '',                # 15: Special Field 1
            '',                # 16: Special Field 2
            '',                # 17: Patient Height
            '',                # 18: Patient Weight
            '',                # 19: Diagnosis
            '',                # 20: Patient Medications
            '',                # 21: Patient Diet
            '',                # 22: Practice Field 1
            '',                # 23: Practice Field 2
            '',                # 24: Admission Date
            '',                # 25: Admission Status
            '',                # 26: Location
            '',                # 27: Nature of Alt. Diagnostic Code
            '',                # 28: Alt. Diagnostic Code
            '',                # 29: Patient Religion
            '',                # 30: Marital Status
            '',                # 31: Isolation Status
            '',                # 32: Language
            '',                # 33: Hospital Service
            '',                # 34: Hospital Institution
            ''                 # 35: Dosage Category
        ]
        
        return self.FIELD_DELIMITER.join(fields)
    
    def _build_order(
        self,
        order_data: Dict,
        sequence: int = 1
    ) -> str:
        """
        Build ASTM Order (O) record
        Format: O|seq|specimen_id||test_id|priority|req_datetime||||||||||||||||||action_code
        """
        specimen_id = order_data.get('specimen_id', '')
        
        # Build test identifier: ^^^test_code^test_name
        test_code = order_data.get('test_code', '')
        test_name = order_data.get('test_name', '')
        test_id = f"{self.COMPONENT_DELIMITER}{self.COMPONENT_DELIMITER}{self.COMPONENT_DELIMITER}{test_code}{self.COMPONENT_DELIMITER}{test_name}"
        
        priority = order_data.get('priority', 'R')  # R=Routine, S=Stat, A=ASAP
        
        req_datetime = order_data.get('requested_datetime', self._get_timestamp('full'))
        collection_datetime = order_data.get('collection_datetime', '')
        
        action_code = order_data.get('action_code', 'N')  # N=New, Q=QC
        
        # Ordering provider
        provider = order_data.get('ordering_provider', '')
        
        report_type = order_data.get('report_type', 'F')  # F=Final, P=Preliminary
        
        fields = [
            self.ORDER,           # 1: Record Type ID
            str(sequence),        # 2: Sequence Number
            specimen_id,          # 3: Specimen ID
            '',                   # 4: Instrument Specimen ID
            test_id,              # 5: Universal Test ID
            priority,             # 6: Priority
            req_datetime,         # 7: Requested/Ordered Date/Time
            collection_datetime,  # 8: Specimen Collection Date/Time
            '',                   # 9: Collection End Time
            '',                   # 10: Collection Volume
            '',                   # 11: Collector ID
            '',                   # 12: Action Code
            '',                   # 13: Danger Code
            '',                   # 14: Relevant Clinical Info
            '',                   # 15: Date/Time Specimen Received
            '',                   # 16: Specimen Descriptor
            provider,             # 17: Ordering Physician
            '',                   # 18: Physician's Phone Number
            '',                   # 19: User Field No. 1
            '',                   # 20: User Field No. 2
            '',                   # 21: Laboratory Field No. 1
            '',                   # 22: Laboratory Field No. 2
            '',                   # 23: Date/Time Results Reported
            '',                   # 24: Instrument Charge
            '',                   # 25: Instrument Section ID
            report_type,          # 26: Report Type
            '',                   # 27: Reserved
            '',                   # 28: Location of Specimen Collection
            '',                   # 29: Nosocomial Infection Flag
            '',                   # 30: Specimen Service
            ''                    # 31: Specimen Institution
        ]
        
        return self.FIELD_DELIMITER.join(fields)
    
    def _build_result(
        self,
        result_data: Dict,
        sequence: int = 1
    ) -> str:
        """
        Build ASTM Result (R) record
        Format: R|seq|test_id|result|units|ref_range|abnormal_flag|status|datetime||operator_id
        """
        # Build test identifier: ^^^test_code^test_name
        test_code = result_data.get('test_code', '')
        test_name = result_data.get('test_name', '')
        test_id = f"{self.COMPONENT_DELIMITER}{self.COMPONENT_DELIMITER}{self.COMPONENT_DELIMITER}{test_code}{self.COMPONENT_DELIMITER}{test_name}"
        
        value = str(result_data.get('value', ''))
        units = result_data.get('units', '')
        reference_range = result_data.get('reference_range', '')
        abnormal_flag = result_data.get('abnormal_flag', '')
        result_status = result_data.get('result_status', 'F')  # F=Final, P=Preliminary
        
        result_datetime = result_data.get('result_datetime', self._get_timestamp('full'))
        operator_id = result_data.get('operator_id', '')
        
        fields = [
            self.RESULT,          # 1: Record Type ID
            str(sequence),        # 2: Sequence Number
            test_id,              # 3: Universal Test ID
            value,                # 4: Data/Measurement Value
            units,                # 5: Units
            reference_range,      # 6: Reference Ranges
            abnormal_flag,        # 7: Result Abnormal Flags
            '',                   # 8: Nature of Abnormality
            result_status,        # 9: Result Status
            '',                   # 10: Date of Change
            operator_id,          # 11: Operator Identification
            '',                   # 12: Date/Time Test Started
            result_datetime,      # 13: Date/Time Test Completed
            ''                    # 14: Instrument Identification
        ]
        
        return self.FIELD_DELIMITER.join(fields)
    
    def _build_comment(
        self,
        comment_text: str,
        sequence: int = 1,
        comment_source: str = 'I'  # I=Instrument, L=Laboratory
    ) -> str:
        """
        Build ASTM Comment (C) record
        Format: C|seq|source|comment_text|type
        """
        fields = [
            self.COMMENT,         # 1: Record Type ID
            str(sequence),        # 2: Sequence Number
            comment_source,       # 3: Comment Source
            comment_text,         # 4: Comment Text
            'G'                   # 5: Comment Type (G=Generic)
        ]
        
        return self.FIELD_DELIMITER.join(fields)
    
    def _build_terminator(
        self,
        sequence: int = 1,
        termination_code: str = 'N'  # N=Normal, Q=Request info, I=Instrument error
    ) -> str:
        """
        Build ASTM Terminator (L) record
        Format: L|seq|termination_code
        """
        fields = [
            self.TERMINATOR,      # 1: Record Type ID
            str(sequence),        # 2: Sequence Number
            termination_code      # 3: Termination Code
        ]
        
        return self.FIELD_DELIMITER.join(fields)
    
    def generate_astm_message(
        self,
        patient_data: Dict,
        order_data: Dict,
        results: List[Dict],
        sender_id: str = 'IVD_DEVICE',
        receiver_id: str = '',
        comments: Optional[List[str]] = None,
        include_framing: bool = False
    ) -> str:
        """
        Generate a complete ASTM message
        
        Args:
            patient_data: Dictionary containing patient information
            order_data: Dictionary containing order/test information
            results: List of result dictionaries
            sender_id: Sending device/system ID
            receiver_id: Receiving system ID
            comments: Optional list of comment strings
            include_framing: Include STX/ETX framing characters
            
        Returns:
            Complete ASTM message string
        """
        records = []
        
        # Build Header record
        header = self._build_header(sender_id, receiver_id)
        records.append(header)
        
        # Build Patient record
        patient = self._build_patient(patient_data, sequence=1)
        records.append(patient)
        
        # Build Order record
        order = self._build_order(order_data, sequence=1)
        records.append(order)
        
        # Build Result records
        for idx, result in enumerate(results, start=1):
            result_record = self._build_result(result, sequence=idx)
            records.append(result_record)
        
        # Build Comment records (if any)
        if comments:
            for idx, comment in enumerate(comments, start=1):
                comment_record = self._build_comment(comment, sequence=idx)
                records.append(comment_record)
        
        # Build Terminator record
        terminator = self._build_terminator(sequence=1)
        records.append(terminator)
        
        # Join all records with CR+LF
        message = f"{self.CR}{self.LF}".join(records)
        
        # Add framing if requested
        if include_framing:
            # Calculate checksum
            checksum = self._calculate_checksum(message)
            message = f"{self.STX}{message}{self.CR}{self.ETX}{checksum}{self.CR}{self.LF}"
        
        return message
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate ASTM checksum (sum of ASCII values % 256)"""
        checksum = sum(ord(c) for c in data) % 256
        return f"{checksum:02X}"
    
    def generate_simple_result_message(
        self,
        patient_id: str,
        patient_name: str,
        sample_id: str,
        test_code: str,
        test_name: str,
        result_value: str,
        units: str = '',
        reference_range: str = '',
        abnormal_flag: str = '',
        sender_id: str = 'IVD_DEVICE'
    ) -> str:
        """
        Generate a simple ASTM message for a single test result
        
        Args:
            patient_id: Patient identifier
            patient_name: Patient full name (Last^First format)
            sample_id: Sample/Specimen ID
            test_code: Test code
            test_name: Test name
            result_value: Result value
            units: Unit of measurement
            reference_range: Reference range
            abnormal_flag: Abnormal flag (N/A/H/L)
            sender_id: Sender device ID
            
        Returns:
            ASTM message string
        """
        # Parse patient name
        name_parts = patient_name.split(' ')
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        
        patient_data = {
            'patient_id': patient_id,
            'first_name': first_name,
            'last_name': last_name,
            'dob': '',
            'gender': 'U'
        }
        
        order_data = {
            'specimen_id': sample_id,
            'test_code': test_code,
            'test_name': test_name,
            'priority': 'R',
            'report_type': 'F'
        }
        
        result = {
            'test_code': test_code,
            'test_name': test_name,
            'value': result_value,
            'units': units,
            'reference_range': reference_range,
            'abnormal_flag': abnormal_flag,
            'result_status': 'F'
        }
        
        return self.generate_astm_message(
            patient_data=patient_data,
            order_data=order_data,
            results=[result],
            sender_id=sender_id
        )


# Example usage
if __name__ == "__main__":
    generator = ASTMMessageGenerator()
    
    # Example patient data
    patient = {
        'patient_id': 'PAT12345',
        'first_name': 'John',
        'last_name': 'Doe',
        'middle_name': 'M',
        'dob': '19850615',
        'gender': 'M',
        'phone': '+1234567890'
    }
    
    # Example order data
    order = {
        'specimen_id': 'SAMPLE001',
        'test_code': 'MALARIA',
        'test_name': 'Malaria Parasite Detection',
        'priority': 'R',
        'ordering_provider': 'Dr. Smith',
        'report_type': 'F'
    }
    
    # Example results
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
    
    # Generate message
    message = generator.generate_astm_message(
        patient_data=patient,
        order_data=order,
        results=results,
        sender_id='IVD_DEVICE_001',
        comments=['Ring forms and gametocytes observed']
    )
    
    print("Generated ASTM Message:")
    print("=" * 80)
    print(message)
    print("=" * 80)
