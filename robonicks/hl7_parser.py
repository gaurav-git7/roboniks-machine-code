"""
HL7 Message Parser Module
Parses HL7 v2.x messages and extracts test result data
Using the hl7 library for standard message parsing
"""

import hl7
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PatientInfo:
    """Patient information extracted from PID segment"""
    patient_id: str = ''
    assigning_authority: str = ''
    id_type: str = ''
    first_name: str = ''
    last_name: str = ''
    middle_name: str = ''
    suffix: str = ''
    dob: str = ''
    gender: str = ''
    street: str = ''
    city: str = ''
    state: str = ''
    zip: str = ''
    country: str = ''
    phone: str = ''


@dataclass
class OrderCommonInfo:
    """Order common information extracted from ORC segment"""
    order_control: str = ''
    placer_order_number: str = ''
    filler_order_number: str = ''
    order_status: str = ''


@dataclass
class OrderInfo:
    """Order information extracted from OBR segment"""
    placer_order_number: str = ''
    filler_order_number: str = ''
    loinc_code: str = ''
    test_name: str = ''
    local_code: str = ''
    local_name: str = ''
    ordering_provider: str = ''
    observation_datetime: str = ''
    result_status: str = ''


@dataclass
class ObservationResult:
    """Observation result extracted from OBX segment"""
    set_id: str = ''
    value_type: str = ''
    loinc_code: str = ''
    test_name: str = ''
    value: str = ''
    units: str = ''
    reference_range: str = ''
    abnormal_flag: str = ''
    result_status: str = ''
    observation_datetime: str = ''
    producer_id: str = ''


class HL7Parser:
    """Parses HL7 messages using hl7 library"""
    
    def __init__(self):
        self.message_type = ''
        self.message_control_id = ''
        self.sending_facility = ''
        self.receiving_facility = ''
        self.timestamp = ''
    
    def _get_field(self, segment, index: int, default: str = '') -> str:
        """Safely get field by index from segment"""
        try:
            if index < len(segment):
                value = str(segment[index])
                return value if value else default
            return default
        except (IndexError, AttributeError):
            return default
    
    def _parse_component(self, field_value: str) -> List[str]:
        """Split field by component separator ^"""
        if not field_value:
            return []
        return str(field_value).split('^')
    
    def parse_msh_segment(self, msh_segment) -> Dict:
        """Parse MSH (Message Header) segment"""
        msh_data = {
            'segment_type': self._get_field(msh_segment, 0),
            'encoding_characters': self._get_field(msh_segment, 2),
            'sending_application': self._get_field(msh_segment, 3),
            'sending_facility': self._get_field(msh_segment, 4),
            'receiving_application': self._get_field(msh_segment, 5),
            'receiving_facility': self._get_field(msh_segment, 6),
            'timestamp': self._get_field(msh_segment, 7),
            'message_type': self._get_field(msh_segment, 9),
            'message_control_id': self._get_field(msh_segment, 10),
            'processing_id': self._get_field(msh_segment, 11),
            'version': self._get_field(msh_segment, 12),
        }
        
        # Store for later use
        self.sending_facility = msh_data['sending_facility']
        self.receiving_facility = msh_data['receiving_facility']
        self.message_type = msh_data['message_type']
        self.message_control_id = msh_data['message_control_id']
        self.timestamp = msh_data['timestamp']
        
        return msh_data
    
    def parse_pid_segment(self, pid_segment) -> PatientInfo:
        """Parse PID (Patient Identification) segment"""
        # Parse patient ID (Field 3): PatientID^^^AssigningAuthority^IDType
        patient_id_field = self._parse_component(self._get_field(pid_segment, 3))
        patient_id = patient_id_field[0] if len(patient_id_field) > 0 else ''
        assigning_authority = patient_id_field[3] if len(patient_id_field) > 3 else ''
        id_type = patient_id_field[4] if len(patient_id_field) > 4 else ''
        
        # Parse patient name (Field 5): Last^First^Middle^Suffix
        patient_name = self._parse_component(self._get_field(pid_segment, 5))
        last_name = patient_name[0] if len(patient_name) > 0 else ''
        first_name = patient_name[1] if len(patient_name) > 1 else ''
        middle_name = patient_name[2] if len(patient_name) > 2 else ''
        suffix = patient_name[3] if len(patient_name) > 3 else ''
        
        # Parse address (Field 11): Street^^City^State^Zip^Country
        address = self._parse_component(self._get_field(pid_segment, 11))
        street = address[0] if len(address) > 0 else ''
        city = address[2] if len(address) > 2 else ''
        state = address[3] if len(address) > 3 else ''
        zip_code = address[4] if len(address) > 4 else ''
        country = address[5] if len(address) > 5 else ''
        
        patient_info = PatientInfo(
            patient_id=patient_id,
            assigning_authority=assigning_authority,
            id_type=id_type,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            suffix=suffix,
            dob=self._get_field(pid_segment, 7),
            gender=self._get_field(pid_segment, 8),
            street=street,
            city=city,
            state=state,
            zip=zip_code,
            country=country,
            phone=self._get_field(pid_segment, 13)
        )
        
        return patient_info
    
    def parse_orc_segment(self, orc_segment) -> OrderCommonInfo:
        """Parse ORC (Common Order) segment"""
        orc_info = OrderCommonInfo(
            order_control=self._get_field(orc_segment, 1),
            placer_order_number=self._get_field(orc_segment, 2),
            filler_order_number=self._get_field(orc_segment, 3),
            order_status=self._get_field(orc_segment, 5)
        )
        
        return orc_info
    
    def parse_obr_segment(self, obr_segment) -> OrderInfo:
        """Parse OBR (Observation Request) segment"""
        # Parse Universal Service ID (Field 4): LOINC_Code^Name^LN^Local_Code^Local_Name
        service_id = self._parse_component(self._get_field(obr_segment, 4))
        loinc_code = service_id[0] if len(service_id) > 0 else ''
        test_name = service_id[1] if len(service_id) > 1 else ''
        local_code = service_id[3] if len(service_id) > 3 else ''
        local_name = service_id[4] if len(service_id) > 4 else ''
        
        order_info = OrderInfo(
            placer_order_number=self._get_field(obr_segment, 2),
            filler_order_number=self._get_field(obr_segment, 3),
            loinc_code=loinc_code,
            test_name=test_name,
            local_code=local_code,
            local_name=local_name,
            ordering_provider=self._get_field(obr_segment, 16),
            observation_datetime=self._get_field(obr_segment, 7),
            result_status=self._get_field(obr_segment, 25) if len(obr_segment) > 25 else ''
        )
        
        return order_info
    
    def parse_obx_segment(self, obx_segment) -> ObservationResult:
        """Parse OBX (Observation Result) segment"""
        # Parse Observation Identifier (Field 3): LOINC_Code^Name^LN
        obs_id = self._parse_component(self._get_field(obx_segment, 3))
        loinc_code = obs_id[0] if len(obs_id) > 0 else ''
        test_name = obs_id[1] if len(obs_id) > 1 else ''
        
        observation = ObservationResult(
            set_id=self._get_field(obx_segment, 1),
            value_type=self._get_field(obx_segment, 2),
            loinc_code=loinc_code,
            test_name=test_name,
            value=self._get_field(obx_segment, 5),
            units=self._get_field(obx_segment, 6),
            reference_range=self._get_field(obx_segment, 7),
            abnormal_flag=self._get_field(obx_segment, 8),
            result_status=self._get_field(obx_segment, 11) if len(obx_segment) > 11 else '',
            observation_datetime=self._get_field(obx_segment, 14) if len(obx_segment) > 14 else '',
            producer_id=self._get_field(obx_segment, 15) if len(obx_segment) > 15 else ''
        )
        
        return observation
    
    def parse_hl7_message(self, message: str) -> Dict:
        """
        Parse a complete HL7 message using hl7 library
        
        Args:
            message: HL7 message string
            
        Returns:
            Dictionary containing parsed data
        """
        # Parse message using hl7 library
        try:
            parsed_msg = hl7.parse(message)
        except Exception as e:
            # If parsing fails, try to handle it manually
            parsed_msg = hl7.parse(message.replace('\n', '\r'))
        
        parsed_data = {
            'msh': None,
            'patient': None,
            'order_common': None,
            'order': None,
            'observations': []
        }
        
        # Iterate through segments
        for segment in parsed_msg:
            segment_type = str(segment[0]) if len(segment) > 0 else ''
            
            if segment_type == 'MSH':
                parsed_data['msh'] = self.parse_msh_segment(segment)
            elif segment_type == 'PID':
                parsed_data['patient'] = self.parse_pid_segment(segment)
            elif segment_type == 'ORC':
                parsed_data['order_common'] = self.parse_orc_segment(segment)
            elif segment_type == 'OBR':
                parsed_data['order'] = self.parse_obr_segment(segment)
            elif segment_type == 'OBX':
                parsed_data['observations'].append(self.parse_obx_segment(segment))
        
        return parsed_data
    
    def format_parsed_data(self, parsed_data: Dict) -> str:
        """Format parsed data for readable display"""
        output = []
        
        # Message Header Information
        if parsed_data.get('msh'):
            msh = parsed_data['msh']
            output.append("=" * 60)
            output.append("MESSAGE HEADER INFORMATION")
            output.append("=" * 60)
            output.append(f"Message Type: {msh.get('message_type', 'N/A')}")
            output.append(f"Message Control ID: {msh.get('message_control_id', 'N/A')}")
            output.append(f"Sending Application: {msh.get('sending_application', 'N/A')}")
            output.append(f"Sending Facility: {msh.get('sending_facility', 'N/A')}")
            output.append(f"Receiving Application: {msh.get('receiving_application', 'N/A')}")
            output.append(f"Receiving Facility: {msh.get('receiving_facility', 'N/A')}")
            output.append(f"Timestamp: {self._format_timestamp(msh.get('timestamp', ''))}")
            output.append(f"HL7 Version: {msh.get('version', 'N/A')}")
            output.append("")
        
        # Patient Information
        if parsed_data.get('patient'):
            patient = parsed_data['patient']
            output.append("=" * 60)
            output.append("PATIENT INFORMATION")
            output.append("=" * 60)
            output.append(f"Patient ID: {patient.patient_id}")
            if patient.id_type:
                output.append(f"ID Type: {patient.id_type} (Authority: {patient.assigning_authority})")
            
            # Full name with suffix
            full_name = f"{patient.first_name} {patient.middle_name} {patient.last_name}".strip()
            if patient.suffix:
                full_name += f", {patient.suffix}"
            output.append(f"Name: {full_name}")
            output.append(f"Date of Birth: {self._format_date(patient.dob)}")
            output.append(f"Gender: {self._format_gender(patient.gender)}")
            
            # Address
            if patient.street or patient.city:
                address_parts = []
                if patient.street:
                    address_parts.append(patient.street)
                city_state_zip = []
                if patient.city:
                    city_state_zip.append(patient.city)
                if patient.state:
                    city_state_zip.append(patient.state)
                if patient.zip:
                    city_state_zip.append(patient.zip)
                if city_state_zip:
                    address_parts.append(', '.join(city_state_zip))
                if patient.country:
                    address_parts.append(patient.country)
                output.append(f"Address: {', '.join(address_parts)}")
            
            output.append(f"Phone: {patient.phone or 'N/A'}")
            output.append("")
        
        # Order Common Information
        if parsed_data.get('order_common'):
            orc = parsed_data['order_common']
            output.append("=" * 60)
            output.append("ORDER COMMON INFORMATION")
            output.append("=" * 60)
            output.append(f"Order Control: {self._format_order_control(orc.order_control)}")
            output.append(f"Placer Order Number: {orc.placer_order_number}")
            if orc.filler_order_number:
                output.append(f"Filler Order Number: {orc.filler_order_number}")
            output.append(f"Order Status: {self._format_order_status(orc.order_status)}")
            output.append("")
        
        # Order Information
        if parsed_data.get('order'):
            order = parsed_data['order']
            output.append("=" * 60)
            output.append("ORDER/TEST INFORMATION")
            output.append("=" * 60)
            output.append(f"Placer Order Number: {order.placer_order_number}")
            if order.filler_order_number:
                output.append(f"Filler Order Number: {order.filler_order_number}")
            
            # Test information with LOINC
            if order.loinc_code:
                output.append(f"Test: {order.test_name} (LOINC: {order.loinc_code})")
            else:
                output.append(f"Test: {order.test_name}")
            
            if order.local_code:
                output.append(f"Local Code: {order.local_code}")
            if order.ordering_provider:
                output.append(f"Ordering Provider: {order.ordering_provider}")
            if order.observation_datetime:
                output.append(f"Observation Date/Time: {self._format_timestamp(order.observation_datetime)}")
            if order.result_status:
                output.append(f"Result Status: {self._format_result_status(order.result_status)}")
            output.append("")
        
        # Observation Results
        if parsed_data.get('observations'):
            output.append("=" * 60)
            output.append("TEST RESULTS")
            output.append("=" * 60)
            for obs in parsed_data['observations']:
                # Display test with LOINC
                test_display = f"Test #{obs.set_id}: {obs.test_name}"
                if obs.loinc_code:
                    test_display += f" (LOINC: {obs.loinc_code})"
                output.append(f"\n{test_display}")
                
                output.append(f"  Value: {obs.value} {obs.units}")
                output.append(f"  Reference Range: {obs.reference_range or 'N/A'}")
                output.append(f"  Status: {self._format_abnormal_flag(obs.abnormal_flag)}")
                if obs.result_status:
                    output.append(f"  Result Status: {self._format_result_status(obs.result_status)}")
                if obs.producer_id:
                    output.append(f"  Producer ID: {obs.producer_id}")
            output.append("")
        
        output.append("=" * 60)
        
        return '\n'.join(output)
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format HL7 timestamp for display"""
        if not timestamp or len(timestamp) < 8:
            return timestamp
        try:
            # YYYYMMDDHHMMSS format
            if len(timestamp) >= 14:
                dt = datetime.strptime(timestamp[:14], '%Y%m%d%H%M%S')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            elif len(timestamp) >= 8:
                dt = datetime.strptime(timestamp[:8], '%Y%m%d')
                return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
        return timestamp
    
    def _format_date(self, date_str: str) -> str:
        """Format HL7 date for display"""
        if not date_str or len(date_str) < 8:
            return date_str
        try:
            dt = datetime.strptime(date_str[:8], '%Y%m%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return date_str
    
    def _format_gender(self, gender: str) -> str:
        """Format gender code"""
        gender_map = {
            'M': 'Male',
            'F': 'Female',
            'U': 'Unknown',
            'O': 'Other'
        }
        return gender_map.get(gender.upper(), gender)
    
    def _format_abnormal_flag(self, flag: str) -> str:
        """Format abnormal flag"""
        flag_map = {
            'N': 'Normal',
            'H': 'High',
            'L': 'Low',
            'HH': 'Critical High',
            'LL': 'Critical Low',
            'A': 'Abnormal',
            'F': 'Final',
            '': 'Not specified'
        }
        return flag_map.get(flag.upper(), flag)
    
    def _format_result_status(self, status: str) -> str:
        """Format result status"""
        status_map = {
            'F': 'Final',
            'P': 'Preliminary',
            'C': 'Corrected',
            'X': 'Cannot be obtained',
            '': 'Not specified'
        }
        return status_map.get(status.upper(), status)
    
    def _format_order_control(self, order_control: str) -> str:
        """Format order control code"""
        control_map = {
            'NW': 'New order',
            'RE': 'Observations to follow',
            'CA': 'Cancel order request',
            'OC': 'Order canceled',
            'OK': 'Order accepted & OK',
        }
        return control_map.get(order_control.upper(), order_control)
    
    def _format_order_status(self, status: str) -> str:
        """Format order status code"""
        status_map = {
            'NW': 'New order',
            'IP': 'In process',
            'CM': 'Completed',
            'CA': 'Canceled',
            'HD': 'On hold',
        }
        return status_map.get(status.upper(), status)


if __name__ == '__main__':
    # Example usage
    parser = HL7Parser()
    
    # Sample HL7 message matching the reference format
    sample_message = "MSH|^~\\&|LIMS|ABC_Hospital|EMR|XYZ_Clinic|20251215113500||ORU^R01|MSG12345|P|2.5\rPID|1||P1234567^^^ABC_Hospital^MR||EVERYMAN^ADAM^^JR||19800101|M|||123 Main St^^Anytown^CA^90210^USA\rORC|RE|L7890|||NW\rOBR|1|L7890||1498-5^RBC^LN^RBC^L|||20251215103000\rOBX|1|NM|1498-5^RBC^LN||4.56|x10(6)/uL|4.20-5.90|F||||F"
    
    # Parse message
    parsed = parser.parse_hl7_message(sample_message)
    
    # Display parsed data
    print(parser.format_parsed_data(parsed))
