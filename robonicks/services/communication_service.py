"""
Communication Service
Orchestrates device communication using configured protocol and interface
"""

import json
import os
from typing import Optional, Dict, Callable
from datetime import datetime

from services.interfaces import USBHandler, LANHandler, SerialHandler
from hl7_generator import HL7MessageGenerator
from hl7_parser import HL7Parser
from astm_generator import ASTMMessageGenerator
from astm_parser import ASTMParser


class CommunicationService:
    """
    Main communication service that handles:
    - Configuration loading
    - Interface initialization
    - Protocol routing
    - Message transmission/reception
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize communication service
        Args:
            config_path: Path to utilities config file
        """
        self.config_path = config_path or os.path.join('config', 'utilities_config.json')
        self.config = self.load_config()
        
        # Interface handler
        self.interface = None
        self.interface_type = self.config.get('interface', 'USB')
        
        # Protocol handlers
        self.hl7_generator = HL7MessageGenerator()
        self.hl7_parser = HL7Parser()
        self.astm_generator = ASTMMessageGenerator()
        self.astm_parser = ASTMParser()
        
        # Message callbacks
        self.on_message_received: Optional[Callable[[bytes, Dict], None]] = None
        self.on_connection_status: Optional[Callable[[bool, str], None]] = None
        self.on_error: Optional[Callable[[Exception, str], None]] = None
        
        # Message log
        self.message_log = []
        self.max_log_size = 1000
    
    def load_config(self) -> Dict:
        """Load utilities configuration from file"""
        default_config = {
            'interface': 'USB',
            'protocol': 'HL7',
            'communication': 'Internal',
            'id': 'Auto Seq'
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    print(f"Configuration loaded: {config}")
                    return config
            else:
                print("No configuration found, using defaults")
                return default_config
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return default_config
    
    def reload_config(self) -> bool:
        """Reload configuration from file"""
        try:
            old_config = self.config.copy()
            self.config = self.load_config()
            
            # Check if interface changed
            if old_config.get('interface') != self.config.get('interface'):
                print("Interface changed, reconnection required")
                if self.is_connected():
                    self.disconnect()
                self.interface_type = self.config.get('interface', 'USB')
            
            return True
        except Exception as e:
            print(f"Error reloading configuration: {e}")
            return False
    
    def initialize_interface(self, **connection_params) -> bool:
        """
        Initialize the configured interface
        Args:
            **connection_params: Interface-specific connection parameters
        Returns: True if initialized successfully
        """
        try:
            # Disconnect existing interface
            if self.interface:
                self.disconnect()
            
            interface_type = self.config.get('interface', 'USB')
            
            # Create appropriate interface handler
            if interface_type == 'USB':
                self.interface = USBHandler()
            elif interface_type == 'LAN':
                self.interface = LANHandler()
            elif interface_type == 'Serial':
                self.interface = SerialHandler()
            else:
                raise ValueError(f"Unknown interface type: {interface_type}")
            
            # Set callbacks
            self.interface.set_callbacks(
                on_message=self._handle_received_message,
                on_disconnect=self._handle_disconnection,
                on_error=self._handle_interface_error
            )
            
            print(f"Interface initialized: {interface_type}")
            return True
            
        except Exception as e:
            print(f"Error initializing interface: {e}")
            if self.on_error:
                self.on_error(e, "initialize_interface")
            return False
    
    def connect(self, **connection_params) -> bool:
        """
        Connect to device using configured interface
        Args:
            **connection_params: Interface-specific parameters
                USB/Serial: port, baudrate, bytesize, parity, stopbits, timeout
                LAN: host, port, timeout, mode
        Returns: True if connected successfully
        """
        try:
            # Initialize interface if not done
            if not self.interface:
                if not self.initialize_interface():
                    return False
            
            # Connect
            success = self.interface.connect(**connection_params)
            
            if success:
                print(f"Connected via {self.config.get('interface')}")
                if self.on_connection_status:
                    self.on_connection_status(True, f"Connected via {self.config.get('interface')}")
                
                # Start receiving in background
                self.interface.start_receiving(self._handle_received_message)
            else:
                print("Connection failed")
                if self.on_connection_status:
                    self.on_connection_status(False, "Connection failed")
            
            return success
            
        except Exception as e:
            print(f"Connection error: {e}")
            if self.on_error:
                self.on_error(e, "connect")
            if self.on_connection_status:
                self.on_connection_status(False, str(e))
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from device"""
        try:
            if self.interface:
                success = self.interface.disconnect()
                if success:
                    print("Disconnected")
                    if self.on_connection_status:
                        self.on_connection_status(False, "Disconnected")
                return success
            return True
        except Exception as e:
            print(f"Disconnect error: {e}")
            if self.on_error:
                self.on_error(e, "disconnect")
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to device"""
        return self.interface and self.interface.is_connected()
    
    def send_hl7_message(
        self,
        patient_data: Dict,
        order_data: Dict,
        observations: list,
        **hl7_params
    ) -> bool:
        """
        Generate and send HL7 message
        Args:
            patient_data: Patient information dictionary
            order_data: Order information dictionary
            observations: List of observation dictionaries
            **hl7_params: Additional HL7 parameters
        Returns: True if sent successfully
        """
        try:
            if not self.is_connected():
                print("Not connected - cannot send message")
                return False
            
            protocol = self.config.get('protocol', 'HL7')
            if protocol != 'HL7':
                print(f"Protocol mismatch: configured for {protocol}, but sending HL7")
                return False
            
            # Generate HL7 message
            hl7_message = self.hl7_generator.generate_hl7_message(
                patient_data=patient_data,
                order_data=order_data,
                observations=observations,
                **hl7_params
            )
            
            # Convert to bytes
            message_bytes = hl7_message.encode('utf-8')
            
            # Log outgoing message
            self._log_message('sent', message_bytes, 'HL7')
            
            # Send
            success = self.interface.send(message_bytes)
            
            if success:
                print(f"HL7 message sent ({len(message_bytes)} bytes)")
            else:
                print("Failed to send HL7 message")
            
            return success
            
        except Exception as e:
            print(f"Error sending HL7 message: {e}")
            if self.on_error:
                self.on_error(e, "send_hl7_message")
            return False
    
    def send_raw_message(self, data: bytes) -> bool:
        """
        Send raw bytes
        Args:
            data: Bytes to send
        Returns: True if sent successfully
        """
        try:
            if not self.is_connected():
                print("Not connected - cannot send message")
                return False
            
            # Log outgoing message
            self._log_message('sent', data, 'RAW')
            
            success = self.interface.send(data)
            
            if success:
                print(f"Raw message sent ({len(data)} bytes)")
            else:
                print("Failed to send raw message")
            
            return success
            
        except Exception as e:
            print(f"Error sending raw message: {e}")
            if self.on_error:
                self.on_error(e, "send_raw_message")
            return False
    
    def _handle_received_message(self, data: bytes):
        """Handle incoming message from interface"""
        try:
            protocol = self.config.get('protocol', 'HL7')
            
            # Log incoming message
            self._log_message('received', data, protocol)
            
            # Parse based on protocol
            parsed_data = None
            if protocol == 'HL7':
                parsed_data = self._parse_hl7_message(data)
            elif protocol == 'ASTM':
                parsed_data = self._parse_astm_message(data)
            
            # Notify callback
            if self.on_message_received:
                self.on_message_received(data, parsed_data or {})
            
            print(f"Message received and parsed ({len(data)} bytes)")
            
        except Exception as e:
            print(f"Error handling received message: {e}")
            if self.on_error:
                self.on_error(e, "_handle_received_message")
    
    def _parse_hl7_message(self, data: bytes) -> Optional[Dict]:
        """Parse HL7 message"""
        try:
            message_str = data.decode('utf-8', errors='ignore')
            
            # Parse using HL7Parser
            parsed = self.hl7_parser.parse_message(message_str)
            
            return parsed
            
        except Exception as e:
            print(f"Error parsing HL7 message: {e}")
            return None
    
    def _parse_astm_message(self, data: bytes) -> Optional[Dict]:
        """Parse ASTM message"""
        try:
            message_str = data.decode('utf-8', errors='ignore')
            
            # Parse using ASTMParser
            parsed = self.astm_parser.parse_message(message_str)
            
            return parsed
            
        except Exception as e:
            print(f"Error parsing ASTM message: {e}")
            return None
    
    def _handle_disconnection(self):
        """Handle interface disconnection"""
        print("Connection lost")
        if self.on_connection_status:
            self.on_connection_status(False, "Connection lost")
    
    def _handle_interface_error(self, error: Exception):
        """Handle interface error"""
        print(f"Interface error: {error}")
        if self.on_error:
            self.on_error(error, "interface")
    
    def _log_message(self, direction: str, data: bytes, protocol: str):
        """Log message to internal log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'direction': direction,
            'protocol': protocol,
            'size': len(data),
            'data': data.decode('utf-8', errors='ignore')
        }
        
        self.message_log.append(log_entry)
        
        # Trim log if too large
        if len(self.message_log) > self.max_log_size:
            self.message_log = self.message_log[-self.max_log_size:]
    
    def get_message_log(self, limit: int = None) -> list:
        """Get message log"""
        if limit:
            return self.message_log[-limit:]
        return self.message_log.copy()
    
    def clear_message_log(self):
        """Clear message log"""
        self.message_log.clear()
    
    def get_status(self) -> Dict:
        """Get current service status"""
        status = {
            'connected': self.is_connected(),
            'interface': self.config.get('interface'),
            'protocol': self.config.get('protocol'),
            'communication': self.config.get('communication'),
            'id_mode': self.config.get('id'),
            'messages_logged': len(self.message_log)
        }
        
        if self.interface:
            status['interface_status'] = self.interface.get_status()
        
        return status
    
    def set_callbacks(
        self,
        on_message: Optional[Callable[[bytes, Dict], None]] = None,
        on_status: Optional[Callable[[bool, str], None]] = None,
        on_error: Optional[Callable[[Exception, str], None]] = None
    ):
        """Set callback functions"""
        if on_message:
            self.on_message_received = on_message
        if on_status:
            self.on_connection_status = on_status
        if on_error:
            self.on_error = on_error
