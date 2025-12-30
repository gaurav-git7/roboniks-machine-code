"""
Example: Integration of Test Result Service with Communication Service

This example shows how to:
1. Save test results to database (with HL7/ASTM messages)
2. Load the configured protocol from utilities
3. Send the appropriate message via the configured interface
"""

from services.test_result_service import TestResultService
from services.communication_service import CommunicationService
import json
import os


def save_and_send_test_result():
    """
    Example workflow: Save test result and send via configured protocol
    """
    
    # Initialize services
    test_service = TestResultService()
    comm_service = CommunicationService()
    
    # Example: Test result data from Read Sample screen
    sample_id = "SAMPLE001"
    test_name = "Malaria Parasite Detection"
    
    result_data = {
        'test_code': 'MALARIA',
        'loinc_code': '32700-7',  # LOINC code for malaria
        'result_value': 'Positive',
        'result_unit': '',
        'reference_range': 'Negative',
        'abnormal_flag': 'A',
        'result_status': 'F',  # Final
        'parasite_detected': True,
        'parasite_species': 'Plasmodium falciparum',
        'parasite_count': 150,
        'microscopy_findings': 'Ring forms and gametocytes observed',
        'order_number': 'ORD123',
        'ordering_provider': 'Dr. Smith'
    }
    
    patient_data = {
        'patient_id': 'PAT001',
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '19850615',
        'gender': 'M',
        'phone': '+1234567890'
    }
    
    observations = [
        {
            'test_code': 'WBC',
            'test_name': 'White Blood Cell Count',
            'value': '11.5',
            'unit': 'x10^9/L',
            'reference_range': '4.0-10.0',
            'abnormal_flag': 'H'
        },
        {
            'test_code': 'HGB',
            'test_name': 'Hemoglobin',
            'value': '10.2',
            'unit': 'g/dL',
            'reference_range': '12.0-16.0',
            'abnormal_flag': 'L'
        }
    ]
    
    # Step 1: Save test result to database (generates HL7 and ASTM messages)
    print("Saving test result to database...")
    test_id = test_service.save_test_result(
        sample_id=sample_id,
        test_name=test_name,
        result_data=result_data,
        patient_data=patient_data,
        observations=observations,
        device_id='IVD_DEVICE_001'
    )
    
    if not test_id:
        print("Failed to save test result")
        return
    
    print(f"Test result saved with ID: {test_id}")
    
    # Step 2: Load configured protocol from utilities config
    config_path = os.path.join('config', 'utilities_config.json')
    protocol = 'HL7'  # Default
    interface = 'USB'  # Default
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            protocol = config.get('protocol', 'HL7')
            interface = config.get('interface', 'USB')
    
    print(f"Using protocol: {protocol}, interface: {interface}")
    
    # Step 3: Get the appropriate protocol message from database
    message = test_service.get_protocol_message(test_id, protocol)
    
    if not message:
        print(f"No {protocol} message found for test {test_id}")
        return
    
    print(f"\n{protocol} Message Preview:")
    print("=" * 80)
    print(message[:500] + "..." if len(message) > 500 else message)
    print("=" * 80)
    
    # Step 4: Connect to device (example connection parameters)
    print(f"\nConnecting via {interface}...")
    
    connection_params = {}
    if interface == 'USB' or interface == 'Serial':
        connection_params = {
            'port': 'COM3',  # Adjust as needed
            'baudrate': 9600,
            'timeout': 5.0
        }
    elif interface == 'LAN':
        connection_params = {
            'host': '192.168.1.100',  # Adjust as needed
            'port': 5000,
            'mode': 'client'
        }
    
    if comm_service.connect(**connection_params):
        print("Connected successfully!")
        
        # Step 5: Send the message
        print(f"\nSending {protocol} message...")
        
        # Convert message to bytes
        message_bytes = message.encode('utf-8')
        
        if comm_service.send_raw_message(message_bytes):
            print("Message sent successfully!")
            
            # Mark as transmitted in database
            test_service.mark_transmitted(test_id, protocol, "success")
            print("Test result marked as transmitted")
        else:
            print("Failed to send message")
            test_service.mark_transmitted(test_id, protocol, "failed")
        
        # Disconnect
        comm_service.disconnect()
    else:
        print("Connection failed")


def get_untransmitted_and_send():
    """
    Example: Get all untransmitted results and send them
    """
    test_service = TestResultService()
    comm_service = CommunicationService()
    
    # Get untransmitted results
    untransmitted = test_service.get_untransmitted_results()
    
    print(f"Found {len(untransmitted)} untransmitted test results")
    
    if not untransmitted:
        return
    
    # Load protocol from config
    config_path = os.path.join('config', 'utilities_config.json')
    protocol = 'HL7'
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            protocol = config.get('protocol', 'HL7')
    
    # Connect (example)
    if comm_service.connect(port='COM3', baudrate=9600):
        for result in untransmitted:
            test_id = result['id']
            sample_id = result['sample_id']
            
            print(f"\nSending result for sample {sample_id}...")
            
            # Get protocol message
            message = test_service.get_protocol_message(test_id, protocol)
            if message:
                if comm_service.send_raw_message(message.encode('utf-8')):
                    test_service.mark_transmitted(test_id, protocol, "success")
                    print(f"  ✓ Sent successfully")
                else:
                    print(f"  ✗ Failed to send")
        
        comm_service.disconnect()


if __name__ == "__main__":
    print("Example 1: Save and send a test result")
    print("=" * 80)
    save_and_send_test_result()
    
    print("\n\n")
    print("Example 2: Send all untransmitted results")
    print("=" * 80)
    # get_untransmitted_and_send()
