
"""
HL7 Message Generator Module
Generates HL7 v2.x messages for IVD (In Vitro Diagnostic) device test results
Using the hl7 library for standard message generation
"""

import hl7
from datetime import datetime
from typing import Dict, List


class HL7MessageGenerator:
    """Generates HL7 messages from IVD device test data using hl7 library"""
    
    def __init__(self):
        self.message_control_id = 1
    
    def _get_timestamp(self) -> str:
        """Generate HL7 timestamp (YYYYMMDDHHMMSS)"""
        return datetime.now().strftime('%Y%m%d%H%M%S')
    
    def generate_hl7_message(
        self,
        patient_data: Dict,
        order_data: Dict,
        observations: list,
        sending_app: str = 'LIMS',
        sending_facility: str = 'ABC_Hospital',
        receiving_app: str = 'EMR',
        receiving_facility: str = 'XYZ_Clinic',
        message_control_id: str = None
    ) -> str:
        """
        Generate a complete HL7 ORU^R01 message using hl7 library
        
        Args:
            patient_data: Dictionary containing patient information
            order_data: Dictionary containing order/test information
            observations: List of observation dictionaries
            sending_app: Sending application name
            sending_facility: Name of sending facility
            receiving_app: Receiving application name
            receiving_facility: Name of receiving facility
            message_control_id: Custom message control ID
            
        Returns:
            Complete HL7 message string
        """
        timestamp = self._get_timestamp()
        if not message_control_id:
            message_control_id = f'MSG{self.message_control_id}'
            self.message_control_id += 1
        
        # Build MSH segment
        msh = [
            'MSH',
            '^~\\&',
            sending_app or 'LIMS',
            sending_facility or 'ABC_Hospital',
            receiving_app or 'EMR',
            receiving_facility or 'XYZ_Clinic',
            timestamp,
            '',
            'ORU^R01',
            message_control_id,
            'P',
            '2.5'
        ]
        
        # Build PID segment
        patient_id_full = f"{patient_data.get('patient_id', '')}^^^{patient_data.get('assigning_authority', 'ABC_Hospital')}^{patient_data.get('id_type', 'MR')}"
        
        patient_name_parts = [
            patient_data.get('last_name', ''),
            patient_data.get('first_name', ''),
            patient_data.get('middle_name', ''),
            patient_data.get('suffix', '')
        ]
        patient_name = '^'.join(patient_name_parts)
        
        address_parts = [
            patient_data.get('street', ''),
            '',
            patient_data.get('city', ''),
            patient_data.get('state', ''),
            patient_data.get('zip', ''),
            patient_data.get('country', '')
        ]
        patient_address = '^'.join(address_parts)
        
        pid = [
            'PID',
            '1',
            '',
            patient_id_full,
            '',
            patient_name,
            '',
            patient_data.get('dob', ''),
            patient_data.get('gender', 'U'),
            '',
            '',
            patient_address,
            '',
            patient_data.get('phone', '')
        ]
        
        # Build ORC segment
        orc = [
            'ORC',
            order_data.get('order_control', 'RE'),
            order_data.get('placer_order_number', ''),
            order_data.get('filler_order_number', ''),
            '',
            order_data.get('order_status', 'NW')
        ]
        
        # Build OBR segment
        service_id_parts = [
            order_data.get('loinc_code', order_data.get('test_code', '')),
            order_data.get('test_name', ''),
            'LN' if order_data.get('loinc_code') else '',
            order_data.get('local_code', ''),
            order_data.get('local_name', '')
        ]
        # Remove trailing empty components
        while service_id_parts and not service_id_parts[-1]:
            service_id_parts.pop()
        universal_service_id = '^'.join(service_id_parts)
        
        obr = [
            'OBR',
            '1',
            order_data.get('placer_order_number', order_data.get('order_id', '')),
            order_data.get('filler_order_number', ''),
            universal_service_id,
            '',
            order_data.get('observation_datetime', timestamp)
        ]
        
        # Build OBX segments for each observation
        obx_segments = []
        for idx, obs in enumerate(observations, start=1):
            obs_id_parts = [
                obs.get('loinc_code', obs.get('test_code', '')),
                obs.get('test_name', ''),
                'LN' if obs.get('loinc_code') else ''
            ]
            # Remove trailing empty components
            while obs_id_parts and not obs_id_parts[-1]:
                obs_id_parts.pop()
            observation_identifier = '^'.join(obs_id_parts)
            
            obx = [
                'OBX',
                str(idx),
                obs.get('value_type', 'NM'),
                observation_identifier,
                '',
                str(obs.get('value', '')),
                obs.get('units', ''),
                obs.get('reference_range', ''),
                obs.get('abnormal_flag', ''),
                '',
                '',
                '',
                '',
                '',
                '',
                obs.get('producer_id', ''),
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                'F'
            ]
            obx_segments.append(obx)
        
        # Create HL7 message using hl7 library
        segments = [msh, pid, orc, obr] + obx_segments
        
        # Join segments with \r separator
        message = '\r'.join(['|'.join(seg) for seg in segments])
        
        return message
    
    def format_message_for_display(self, message: str) -> str:
        """Format HL7 message for readable display"""
        return message.replace('\r', '\n')


if __name__ == '__main__':
    # Example usage
    generator = HL7MessageGenerator()
    
    patient = {
        'patient_id': 'P1234567',
        'assigning_authority': 'ABC_Hospital',
        'id_type': 'MR',
        'first_name': 'ADAM',
        'last_name': 'EVERYMAN',
        'middle_name': '',
        'suffix': 'JR',
        'dob': '19800101',
        'gender': 'M',
        'street': '123 Main St',
        'city': 'Anytown',
        'state': 'CA',
        'zip': '90210',
        'country': 'USA',
        'phone': ''
    }
    
    order = {
        'order_control': 'RE',
        'placer_order_number': 'L7890',
        'filler_order_number': '',
        'order_status': 'NW',
        'loinc_code': '1498-5',
        'test_name': 'RBC',
        'local_code': 'RBC',
        'local_name': 'L',
        'observation_datetime': '20251215103000'
    }
    
    observations = [
        {
            'loinc_code': '1498-5',
            'test_name': 'RBC',
            'value': '4.56',
            'value_type': 'NM',
            'units': 'x10(6)/uL',
            'reference_range': '4.20-5.90',
            'abnormal_flag': 'F',
            'producer_id': ''
        }
    ]
    
    message = generator.generate_hl7_message(
        patient, order, observations,
        sending_app='LIMS',
        sending_facility='ABC_Hospital',
        receiving_app='EMR',
        receiving_facility='XYZ_Clinic',
        message_control_id='MSG12345'
    )
    print("Generated HL7 Message:")
    print(generator.format_message_for_display(message))

    """Generates HL7 messages from IVD device test data"""
    
    SEGMENT_SEPARATOR = '\r'
    FIELD_SEPARATOR = '|'
    COMPONENT_SEPARATOR = '^'
    REPETITION_SEPARATOR = '~'
    ESCAPE_CHARACTER = '\\'
    SUBCOMPONENT_SEPARATOR = '&'
    
    def __init__(self):
        self.message_control_id = 1
    
    def _get_timestamp(self) -> str:
        """Generate HL7 timestamp (YYYYMMDDHHMMSS)"""
        return datetime.now().strftime('%Y%m%d%H%M%S')
    
    def _escape_text(self, text: str) -> str:
        """Escape special characters in HL7 text"""
        if not text:
            return ''
        text = str(text)
        text = text.replace('\\', '\\E\\')
        text = text.replace('|', '\\F\\')
        text = text.replace('^', '\\S\\')
        text = text.replace('&', '\\T\\')
        text = text.replace('~', '\\R\\')
        return text
    
    def generate_msh_segment(self, sending_app: str, sending_facility: str, 
                            receiving_app: str, receiving_facility: str, 
                            message_control_id: str = None) -> str:
        """
        Generate MSH (Message Header) segment
        MSH - Contains information about the message itself
        """
        timestamp = self._get_timestamp()
        if not message_control_id:
            message_control_id = f'MSG{self.message_control_id}'
            self.message_control_id += 1
        
        msh = [
            'MSH',
            self.FIELD_SEPARATOR,  # Encoding characters
            sending_app or 'LIMS',  # Sending Application
            sending_facility or 'ABC_Hospital',  # Sending Facility
            receiving_app or 'EMR',  # Receiving Application
            receiving_facility or 'XYZ_Clinic',  # Receiving Facility
            timestamp,  # Message timestamp
            '',  # Security
            'ORU^R01',  # Message Type (Observation Result)
            message_control_id,  # Message Control ID
            'P',  # Processing ID (P=Production, T=Test)
            '2.5',  # HL7 Version
        ]
        return self.FIELD_SEPARATOR.join(msh)
    
    def generate_pid_segment(self, patient_data: Dict) -> str:
        """
        Generate PID (Patient Identification) segment
        Contains patient demographic information
        """
        # Build patient ID with identifier type
        patient_id_full = f"{patient_data.get('patient_id', '')}^^^{patient_data.get('assigning_authority', 'ABC_Hospital')}^{patient_data.get('id_type', 'MR')}"
        
        # Build patient name: Last^First^Middle^Suffix
        name_parts = [
            self._escape_text(patient_data.get('last_name', '')),
            self._escape_text(patient_data.get('first_name', '')),
            self._escape_text(patient_data.get('middle_name', '')),
            patient_data.get('suffix', '')
        ]
        patient_name = self.COMPONENT_SEPARATOR.join(name_parts)
        
        # Build address: Street^City^State^Zip^Country
        address_parts = [
            self._escape_text(patient_data.get('street', '')),
            '',  # Additional street info
            self._escape_text(patient_data.get('city', '')),
            patient_data.get('state', ''),
            patient_data.get('zip', ''),
            patient_data.get('country', '')
        ]
        patient_address = self.COMPONENT_SEPARATOR.join(address_parts)
        
        pid = [
            'PID',
            '1',  # Set ID
            '',  # Patient ID (external)
            patient_id_full,  # Patient ID (internal) with identifiers
            '',  # Alternate Patient ID
            patient_name,  # Patient Name
            '',  # Mother's Maiden Name
            patient_data.get('dob', ''),  # Date of Birth (YYYYMMDD)
            patient_data.get('gender', 'U'),  # Gender (M/F/U)
            '',  # Patient Alias
            '',  # Race
            patient_address,  # Patient Address
            '',  # County Code
            patient_data.get('phone', ''),  # Phone Number
        ]
        return self.FIELD_SEPARATOR.join(pid)
    
    def generate_orc_segment(self, order_data: Dict) -> str:
        """
        Generate ORC (Common Order) segment
        Contains order control information
        """
        orc = [
            'ORC',
            order_data.get('order_control', 'RE'),  # Order Control (RE=Observations to follow, NW=New order)
            order_data.get('placer_order_number', ''),  # Placer Order Number
            order_data.get('filler_order_number', ''),  # Filler Order Number
            '',  # Placer Group Number
            order_data.get('order_status', 'NW'),  # Order Status (NW=New, IP=In Process, CM=Complete)
        ]
        return self.FIELD_SEPARATOR.join(orc)
    
    def generate_obr_segment(self, order_data: Dict) -> str:
        """
        Generate OBR (Observation Request) segment
        Contains information about the test order
        """
        timestamp = self._get_timestamp()
        
        # Build Universal Service ID with LOINC: LOINC_code^Test_Name^LN^Local_Code^Local_Name
        service_id_parts = [
            order_data.get('loinc_code', order_data.get('test_code', '')),
            self._escape_text(order_data.get('test_name', '')),
            'LN' if order_data.get('loinc_code') else '',
            order_data.get('local_code', ''),
            order_data.get('local_name', '')
        ]
        # Remove trailing empty components
        while service_id_parts and not service_id_parts[-1]:
            service_id_parts.pop()
        universal_service_id = self.COMPONENT_SEPARATOR.join(service_id_parts)
        
        obr = [
            'OBR',
            '1',  # Set ID
            order_data.get('placer_order_number', order_data.get('order_id', '')),  # Placer Order Number
            order_data.get('filler_order_number', ''),  # Filler Order Number
            universal_service_id,  # Universal Service ID
            '',  # Priority
            order_data.get('observation_datetime', timestamp),  # Observation Date/Time
        ]
        return self.FIELD_SEPARATOR.join(obr)
    
    def generate_obx_segment(self, observation_data: Dict, set_id: int = 1) -> str:
        """
        Generate OBX (Observation Result) segment
        Contains the actual test result data
        """
        timestamp = self._get_timestamp()
        
        # Build Observation Identifier with LOINC: LOINC_code^Test_Name^LN
        obs_id_parts = [
            observation_data.get('loinc_code', observation_data.get('test_code', '')),
            self._escape_text(observation_data.get('test_name', '')),
            'LN' if observation_data.get('loinc_code') else ''
        ]
        # Remove trailing empty components
        while obs_id_parts and not obs_id_parts[-1]:
            obs_id_parts.pop()
        observation_identifier = self.COMPONENT_SEPARATOR.join(obs_id_parts)
        
        obx = [
            'OBX',
            str(set_id),  # Set ID
            observation_data.get('value_type', 'NM'),  # Value Type (NM=Numeric, ST=String, CE=Coded Entry)
            observation_identifier,  # Observation Identifier with LOINC
            '',  # Observation Sub-ID
            self._escape_text(str(observation_data.get('value', ''))),  # Observation Value
            observation_data.get('units', ''),  # Units
            observation_data.get('reference_range', ''),  # Reference Range
            observation_data.get('abnormal_flag', ''),  # Abnormal Flags (N=Normal, H=High, L=Low, F=Final below range)
            '',  # Probability
            '',  # Nature of Abnormal Test
            '',  # Observation Result Status
            '',  # Effective Date
            '',  # User Defined Access Checks
            '',  # Date/Time of Observation
            observation_data.get('producer_id', ''),  # Producer's ID
            observation_data.get('responsible_observer', ''),  # Responsible Observer
            '',  # Observation Method
            '',  # Equipment Instance Identifier
            '',  # Date/Time of Analysis
            '',  # Reserved
            '',  # Reserved
            '',  # Reserved
            '',  # Reserved  
            'F',  # Observation Result Status (F=Final) - Field 11
        ]
        return self.FIELD_SEPARATOR.join(obx)
    
    def generate_hl7_message(
        self,
        patient_data: Dict,
        order_data: Dict,
        observations: list,
        sending_app: str = 'LIMS',
        sending_facility: str = 'ABC_Hospital',
        receiving_app: str = 'EMR',
        receiving_facility: str = 'XYZ_Clinic',
        message_control_id: str = None
    ) -> str:
        """
        Generate a complete HL7 ORU^R01 message
        
        Args:
            patient_data: Dictionary containing patient information
            order_data: Dictionary containing order/test information
            observations: List of observation dictionaries
            sending_app: Sending application name
            sending_facility: Name of sending facility
            receiving_app: Receiving application name
            receiving_facility: Name of receiving facility
            message_control_id: Custom message control ID
            
        Returns:
            Complete HL7 message string
        """
        segments = []
        
        # MSH - Message Header
        segments.append(self.generate_msh_segment(
            sending_app, sending_facility, 
            receiving_app, receiving_facility,
            message_control_id
        ))
        
        # PID - Patient Identification
        segments.append(self.generate_pid_segment(patient_data))
        
        # ORC - Common Order
        segments.append(self.generate_orc_segment(order_data))
        
        # OBR - Observation Request
        segments.append(self.generate_obr_segment(order_data))
        
        # OBX - Observation Results (can be multiple)
        for idx, observation in enumerate(observations, start=1):
            segments.append(self.generate_obx_segment(observation, set_id=idx))
        
        # Join all segments with segment separator
        message = self.SEGMENT_SEPARATOR.join(segments)
        
        return message
    
    def format_message_for_display(self, message: str) -> str:
        """Format HL7 message for readable display"""
        return message.replace(self.SEGMENT_SEPARATOR, '\n')


if __name__ == '__main__':
    # Example usage
    generator = HL7MessageGenerator()
    
    patient = {
        'patient_id': 'P1234567',
        'assigning_authority': 'ABC_Hospital',
        'id_type': 'MR',
        'first_name': 'ADAM',
        'last_name': 'EVERYMAN',
        'middle_name': '',
        'suffix': 'JR',
        'dob': '19800101',
        'gender': 'M',
        'street': '123 Main St',
        'city': 'Anytown',
        'state': 'CA',
        'zip': '90210',
        'country': 'USA',
        'phone': ''
    }
    
    order = {
        'order_control': 'RE',
        'placer_order_number': 'L7890',
        'filler_order_number': '',
        'order_status': 'NW',
        'loinc_code': '1498-5',
        'test_name': 'RBC',
        'local_code': 'RBC',
        'local_name': 'L',
        'observation_datetime': '20251215103000'
    }
    
    observations = [
        {
            'loinc_code': '1498-5',
            'test_name': 'RBC',
            'value': '4.56',
            'value_type': 'NM',
            'units': 'x10(6)/uL',
            'reference_range': '4.20-5.90',
            'abnormal_flag': 'F',
            'producer_id': ''
        }
    ]
    
    message = generator.generate_hl7_message(
        patient, order, observations,
        sending_app='LIMS',
        sending_facility='ABC_Hospital',
        receiving_app='EMR',
        receiving_facility='XYZ_Clinic',
        message_control_id='MSG12345'
    )
    print("Generated HL7 Message:")
    print(generator.format_message_for_display(message))
