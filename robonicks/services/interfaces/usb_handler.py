"""
USB Interface Handler
Handles communication over USB using serial protocol
"""

import serial
import serial.tools.list_ports
from typing import Optional, List, Dict
from .base_interface import BaseInterface


class USBHandler(BaseInterface):
    """Handles USB communication using PySerial"""
    
    def __init__(self):
        super().__init__()
        self.serial_port: Optional[serial.Serial] = None
        self.port_name: str = ""
        self.baudrate: int = 9600
        self.timeout: float = 1.0
    
    @staticmethod
    def list_available_ports() -> List[Dict[str, str]]:
        """
        List all available USB/Serial ports
        Returns: List of dictionaries with port information
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'name': port.name,
                'description': port.description,
                'hwid': port.hwid,
                'vid': port.vid,
                'pid': port.pid,
                'serial_number': port.serial_number,
                'manufacturer': port.manufacturer
            })
        return ports
    
    def connect(
        self,
        port: str = None,
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = 'N',
        stopbits: int = 1,
        timeout: float = 1.0,
        **kwargs
    ) -> bool:
        """
        Connect to USB device via serial port
        Args:
            port: COM port name (e.g., 'COM3', '/dev/ttyUSB0')
            baudrate: Baud rate (default 9600)
            bytesize: Number of data bits (default 8)
            parity: Parity ('N', 'E', 'O', 'M', 'S')
            stopbits: Number of stop bits (default 1)
            timeout: Read timeout in seconds
        Returns: True if connected successfully
        """
        try:
            if self.connected:
                self.disconnect()
            
            # Auto-detect port if not specified
            if not port:
                available_ports = self.list_available_ports()
                if not available_ports:
                    raise Exception("No USB/Serial ports found")
                port = available_ports[0]['device']
            
            self.port_name = port
            self.baudrate = baudrate
            self.timeout = timeout
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout,
                write_timeout=timeout
            )
            
            self.connected = True
            print(f"USB connected on {port} at {baudrate} baud")
            return True
            
        except serial.SerialException as e:
            print(f"USB connection failed: {e}")
            if self.on_error:
                self.on_error(e)
            return False
        except Exception as e:
            print(f"USB connection error: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    def disconnect(self) -> bool:
        """Close USB serial connection"""
        try:
            self.stop_receiving()
            
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                print(f"USB disconnected from {self.port_name}")
            
            self.connected = False
            self.serial_port = None
            
            if self.on_connection_lost:
                self.on_connection_lost()
            
            return True
            
        except Exception as e:
            print(f"USB disconnect error: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    def send(self, data: bytes) -> bool:
        """
        Send data over USB
        Args:
            data: Bytes to send
        Returns: True if successful
        """
        if not self.connected or not self.serial_port:
            print("USB not connected")
            return False
        
        try:
            bytes_written = self.serial_port.write(data)
            self.serial_port.flush()
            print(f"USB sent {bytes_written} bytes")
            return True
            
        except serial.SerialTimeoutException:
            print("USB send timeout")
            return False
        except Exception as e:
            print(f"USB send error: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    def receive(self, timeout: float = 5.0) -> Optional[bytes]:
        """
        Receive data from USB
        Args:
            timeout: Timeout in seconds
        Returns: Received bytes or None
        """
        if not self.connected or not self.serial_port:
            return None
        
        try:
            # Temporarily set timeout
            original_timeout = self.serial_port.timeout
            self.serial_port.timeout = timeout
            
            # Read available data
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read(self.serial_port.in_waiting)
                if data:
                    print(f"USB received {len(data)} bytes")
                    return data
            
            # Restore original timeout
            self.serial_port.timeout = original_timeout
            return None
            
        except serial.SerialException as e:
            print(f"USB receive error: {e}")
            if self.on_error:
                self.on_error(e)
            return None
    
    def read_line(self, timeout: float = 5.0) -> Optional[str]:
        """
        Read a line of text from USB
        Args:
            timeout: Timeout in seconds
        Returns: Decoded string or None
        """
        if not self.connected or not self.serial_port:
            return None
        
        try:
            original_timeout = self.serial_port.timeout
            self.serial_port.timeout = timeout
            
            line = self.serial_port.readline()
            
            self.serial_port.timeout = original_timeout
            
            if line:
                return line.decode('utf-8', errors='ignore').strip()
            return None
            
        except Exception as e:
            print(f"USB readline error: {e}")
            if self.on_error:
                self.on_error(e)
            return None
    
    def flush(self):
        """Flush input and output buffers"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
    
    def get_status(self) -> Dict:
        """Get current connection status"""
        return {
            'connected': self.connected,
            'port': self.port_name,
            'baudrate': self.baudrate,
            'timeout': self.timeout,
            'is_open': self.serial_port.is_open if self.serial_port else False,
            'in_waiting': self.serial_port.in_waiting if self.serial_port and self.serial_port.is_open else 0
        }
