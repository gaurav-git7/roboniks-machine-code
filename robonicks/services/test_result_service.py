"""
Test Result Service (Lightweight Client Version)
Handles test result storage locally using MinimalDB.
Decoupled from Server Backend.
"""

import sys
import os
from typing import Dict, Optional, List
from datetime import datetime
from types import SimpleNamespace

# Local imports
from utils.minimal_db import MinimalDB
from hl7_generator import HL7MessageGenerator
from astm_generator import ASTMMessageGenerator

class TestResultService:
    """
    Client-side service for managing test results.
    Writes to local SQLite 'client_data.db'.
    """
    
    def __init__(self):
        self.db = MinimalDB()
        self.hl7_generator = HL7MessageGenerator()
        self.astm_generator = ASTMMessageGenerator()
        
    def save_test_result(
        self,
        sample_id: str,
        test_name: str,
        result_data: Dict,
        patient_data: Dict = None,
        observations: List[Dict] = None,
        device_id: str = None
    ) -> Optional[int]:
        """
        Save test result to local DB and generate protocol messages
        """
        try:
            # 1. Prepare Data Object (Mimicking the old Pydantic model for compatibility)
            # We use SimpleNamespace so dot notation (obj.field) works in generators
            patient_info = patient_data or {}
            
            # Helper to create a dot-accessible object from dict
            class DataObj:
                def __init__(self, **entries):
                    self.__dict__.update(entries)
                    
            # Construct the data object expected by generators
            test_result = DataObj(
                sample_id=sample_id,
                patient_id=patient_info.get('patient_id'),
                patient_first_name=patient_info.get('first_name'),
                patient_last_name=patient_info.get('last_name'),
                patient_dob=patient_info.get('dob'),
                patient_gender=patient_info.get('gender'),
                patient_phone=patient_info.get('phone'),
                
                test_name=test_name,
                test_code=result_data.get('test_code'),
                loinc_code=result_data.get('loinc_code'),
                result_value=result_data.get('result_value'),
                result_unit=result_data.get('result_unit'),
                reference_range=result_data.get('reference_range'),
                abnormal_flag=result_data.get('abnormal_flag'),
                result_status=result_data.get('result_status', 'F'),
                
                parasite_detected=result_data.get('parasite_detected', False),
                parasite_species=result_data.get('parasite_species'),
                parasite_count=result_data.get('parasite_count'),
                microscopy_findings=result_data.get('microscopy_findings'),
                
                order_number=result_data.get('order_number'),
                ordering_provider=result_data.get('ordering_provider'),
                device_id=device_id,
                operator_id=result_data.get('operator_id'),
                
                test_performed_at=datetime.now(),
                sample_collected_at=result_data.get('sample_collected_at')
            )
            
            # 2. Generate Protocol Messages
            # The existing generators take an object with attributes, which we just created
            hl7_message = self._generate_hl7_message(test_result, observations or [])
            astm_message = self._generate_astm_message(test_result, observations or [])
            
            # 3. Save to Local SQLite
            # We flatten the important fields and dump the rest as JSON
            full_data_dump = {
                "result_data": result_data,
                "patient_data": patient_data,
                "observations": observations,
                "device_info": device_id
            }
            
            new_id = self.db.insert_result(
                sample_id=sample_id,
                patient_id=patient_info.get('patient_id'),
                test_name=test_name,
                result_value=result_data.get('result_value'),
                hl7_msg=hl7_message,
                astm_msg=astm_message,
                raw_data_dict=full_data_dump
            )
            
            return new_id
            
        except Exception as e:
            print(f"Service Error saving test result: {e}")
            import traceback
            traceback.print_exc()
            return None

    # -------------------------------------------------------------------------
    # Protocol Generators (Copied logic, adapted for our DataObj)
    # -------------------------------------------------------------------------
    
    def _generate_hl7_message(self, test_data, observations: List[Dict]) -> str:
        """Generate HL7 message from test data object"""
        try:
            # Prepare patient data for HL7
            patient_data = {
                'patient_id': getattr(test_data, 'patient_id', None) or test_data.sample_id,
                'first_name': getattr(test_data, 'patient_first_name', '') or '',
                'last_name': getattr(test_data, 'patient_last_name', 'Unknown') or 'Unknown',
                'middle_name': '',
                'dob': getattr(test_data, 'patient_dob', '') or '',
                'gender': getattr(test_data, 'patient_gender', 'U') or 'U',
                'phone': getattr(test_data, 'patient_phone', '') or ''
            }
            
            # Prepare order data
            timestamp = test_data.test_performed_at.strftime('%Y%m%d%H%M%S')
            order_data = {
                'placer_order_number': getattr(test_data, 'order_number', None) or test_data.sample_id,
                'filler_order_number': test_data.sample_id,
                'test_code': getattr(test_data, 'test_code', 'PARASITE'),
                'test_name': test_data.test_name,
                'ordering_provider': getattr(test_data, 'ordering_provider', '') or '',
                'observation_datetime': timestamp
            }
            
            # Prepare observations
            obs_list = []
            
            # Main result
            obs_list.append({
                'value_type': 'ST',
                'test_code': getattr(test_data, 'test_code', 'PARASITE'),
                'test_name': test_data.test_name,
                'value': str(test_data.result_value),
                'units': getattr(test_data, 'result_unit', '') or '',
                'reference_range': getattr(test_data, 'reference_range', '') or '',
                'abnormal_flag': getattr(test_data, 'abnormal_flag', '') or '',
                'result_status': getattr(test_data, 'result_status', 'F')
            })
            
            # Dictionary Observations
            if observations:
                for obs in observations:
                    obs_list.append({
                        'value_type': 'ST',
                        'test_code': obs.get('test_code', ''),
                        'test_name': obs.get('test_name', ''),
                        'value': obs.get('value', ''),
                        'units': obs.get('unit', ''),
                        'reference_range': obs.get('reference_range', ''),
                        'abnormal_flag': obs.get('abnormal_flag', ''),
                        'result_status': 'F'
                    })
            
            # Parasite-specific
            if getattr(test_data, 'parasite_detected', False):
                species = getattr(test_data, 'parasite_species', None)
                if species:
                    obs_list.append({
                        'value_type': 'ST',
                        'test_code': 'SPECIES',
                        'test_name': 'Parasite Species',
                        'value': species,
                        'units': '', 'reference_range': '', 'abnormal_flag': '', 'result_status': 'F'
                    })
                
                count = getattr(test_data, 'parasite_count', None)
                if count is not None:
                     obs_list.append({
                        'value_type': 'NM',
                        'test_code': 'COUNT',
                        'test_name': 'Parasite Count',
                        'value': str(count),
                        'units': 'per_hpf', 'reference_range': '', 'abnormal_flag': '', 'result_status': 'F'
                    })

            return self.hl7_generator.generate_hl7_message(
                patient_data=patient_data,
                order_data=order_data,
                observations=obs_list,
                sending_app=getattr(test_data, 'device_id', 'IVD_DEVICE') or 'IVD_DEVICE',
                sending_facility='IVD_LAB'
            )
        except Exception as e:
            print(f"Error generating HL7: {e}")
            return ""

    def _generate_astm_message(self, test_data, observations: List[Dict]) -> str:
        """Generate ASTM message from test data object"""
        try:
            # Prepare patient data
            patient_data = {
                'patient_id': getattr(test_data, 'patient_id', None) or test_data.sample_id,
                'first_name': getattr(test_data, 'patient_first_name', '') or '',
                'last_name': getattr(test_data, 'patient_last_name', 'Unknown') or 'Unknown',
                'middle_name': '',
                'dob': getattr(test_data, 'patient_dob', '') or '',
                'gender': getattr(test_data, 'patient_gender', 'U') or 'U',
                'phone': getattr(test_data, 'patient_phone', '') or ''
            }
            
            timestamp = test_data.test_performed_at.strftime('%Y%m%d%H%M%S')
            
            # Prepare order data
            order_data = {
                'specimen_id': test_data.sample_id,
                'test_code': getattr(test_data, 'test_code', 'PARASITE'),
                'test_name': test_data.test_name,
                'priority': 'R',
                'ordering_provider': getattr(test_data, 'ordering_provider', '') or '',
                'report_type': 'F',
                'requested_datetime': timestamp
            }
            
            # Prepare results
            results = []
            results.append({
                'test_code': getattr(test_data, 'test_code', 'PARASITE'),
                'test_name': test_data.test_name,
                'value': str(test_data.result_value),
                'units': getattr(test_data, 'result_unit', '') or '',
                'reference_range': getattr(test_data, 'reference_range', '') or '',
                'abnormal_flag': getattr(test_data, 'abnormal_flag', '') or '',
                'result_status': getattr(test_data, 'result_status', 'F')
            })
            
             # Dictionary Observations
            if observations:
                for obs in observations:
                    results.append({
                        'test_code': obs.get('test_code', ''),
                        'test_name': obs.get('test_name', ''),
                        'value': obs.get('value', ''),
                        'units': obs.get('unit', ''),
                        'reference_range': obs.get('reference_range', ''),
                        'abnormal_flag': obs.get('abnormal_flag', ''),
                        'result_status': 'F'
                    })

             # Parasite-specific
            if getattr(test_data, 'parasite_detected', False):
                species = getattr(test_data, 'parasite_species', None)
                if species:
                    results.append({
                        'test_code': 'SPECIES',
                        'test_name': 'Parasite Species',
                        'value': species,
                        'units': '', 'reference_range': '', 'abnormal_flag': '', 'result_status': 'F'
                    })
                
                count = getattr(test_data, 'parasite_count', None)
                if count is not None:
                     results.append({
                        'test_code': 'COUNT',
                        'test_name': 'Parasite Count',
                        'value': str(count),
                        'units': 'per_hpf', 'reference_range': '', 'abnormal_flag': '', 'result_status': 'F'
                    })
            
            comments = []
            findings = getattr(test_data, 'microscopy_findings', None)
            if findings:
                comments.append(findings)

            return self.astm_generator.generate_astm_message(
                patient_data=patient_data,
                order_data=order_data,
                results=results,
                sender_id=getattr(test_data, 'device_id', 'IVD_DEVICE') or 'IVD_DEVICE',
                comments=comments if comments else None
            )
            
        except Exception as e:
            print(f"Error generating ASTM: {e}")
            return ""

