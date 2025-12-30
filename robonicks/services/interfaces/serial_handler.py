"""
Serial Interface Handler
Handles direct serial port communication (RS232/RS485)
"""

import serial
import serial.tools.list_ports
from typing import Optional, List, Dict
from .base_interface import BaseInterface


class SerialHandler(BaseInterface):
    """Handles direct serial communication (RS232/RS485)"""
    
    def __init__(self):
        super().__init__()
        self.serial_port: Optional[serial.Serial] = None
        self.port_name: str = ""
        self.baudrate: int = 9600
        self.timeout: float = 1.0
        self.bytesize: int = 8
        self.parity: str = 'N'
        self.stopbits: int = 1
    
    @staticmethod
    def list_available_ports() -> List[Dict[str, str]]:
        """
        List all available serial ports
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
                'manufacturer': port.manufacturer,
                'location': getattr(port, 'location', 'N/A')
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
        xonxoff: bool = False,
        rtscts: bool = False,
        dsrdtr: bool = False,
        **kwargs
    ) -> bool:
        """
        Connect to serial device
        Args:
            port: Serial port name (e.g., 'COM1', '/dev/ttyS0')
            baudrate: Baud rate (default 9600)
            bytesize: Data bits (5, 6, 7, or 8)
            parity: Parity ('N', 'E', 'O', 'M', 'S')
            stopbits: Stop bits (1, 1.5, or 2)
            timeout: Read timeout in seconds
            xonxoff: Enable software flow control
            rtscts: Enable hardware (RTS/CTS) flow control
            dsrdtr: Enable hardware (DSR/DTR) flow control
        Returns: True if connected successfully
        """
        try:
            if self.connected:
                self.disconnect()
            
            # Auto-detect port if not specified
            if not port:
                available_ports = self.list_available_ports()
                if not available_ports:
                    raise Exception("No serial ports found")
                port = available_ports[0]['device']
            
            self.port_name = port
            self.baudrate = baudrate
            self.bytesize = bytesize
            self.parity = parity
            self.stopbits = stopbits
            self.timeout = timeout
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout,
                xonxoff=xonxoff,
                rtscts=rtscts,
                dsrdtr=dsrdtr,
                write_timeout=timeout
            )
            
            # Flush buffers
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            self.connected = True
            print(f"Serial connected on {port} at {baudrate} baud")
            print(f"Settings: {bytesize}-{parity}-{stopbits}")
            return True
            
        except serial.SerialException as e:
            print(f"Serial connection failed: {e}")
            if self.on_error:
                self.on_error(e)
            return False
        except Exception as e:
            print(f"Serial connection error: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    def disconnect(self) -> bool:
        """Close serial connection"""
        try:
            self.stop_receiving()
            
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                print(f"Serial disconnected from {self.port_name}")
            
            self.connected = False
            self.serial_port = None
            
            if self.on_connection_lost:
                self.on_connection_lost()
            
            return True
            
        except Exception as e:
            print(f"Serial disconnect error: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    def send(self, data: bytes) -> bool:
        """
        Send data over serial
        Args:
            data: Bytes to send
        Returns: True if successful
        """
        if not self.connected or not self.serial_port:
            print("Serial not connected")
            return False
        
        try:
            bytes_written = self.serial_port.write(data)
            self.serial_port.flush()
            print(f"Serial sent {bytes_written} bytes")
            return True
            
        except serial.SerialTimeoutException:
            print("Serial send timeout")
            return False
        except Exception as e:
            print(f"Serial send error: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    def receive(self, timeout: float = 5.0, buffer_size: int = 4096) -> Optional[bytes]:
        """
        Receive data from serial port
        Args:
            timeout: Timeout in seconds
            buffer_size: Maximum bytes to read
        Returns: Received bytes or None
        """
        if not self.connected or not self.serial_port:
            return None
        
        try:
            # Temporarily set timeout
            original_timeout = self.serial_port.timeout
            self.serial_port.timeout = timeout
            
            # Read available data
            bytes_available = self.serial_port.in_waiting
            if bytes_available > 0:
                data = self.serial_port.read(min(bytes_available, buffer_size))
                if data:
                    print(f"Serial received {len(data)} bytes")
                    self.serial_port.timeout = original_timeout
                    return data
            
            # Restore original timeout
            self.serial_port.timeout = original_timeout
            return None
            
        except serial.SerialException as e:
            print(f"Serial receive error: {e}")
            if self.on_error:
                self.on_error(e)
            return None
    
    def read_line(self, timeout: float = 5.0, eol: bytes = b'\n') -> Optional[str]:
        """
        Read a line of text from serial
        Args:
            timeout: Timeout in seconds
            eol: End of line character(s)
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
            print(f"Serial readline error: {e}")
            if self.on_error:
                self.on_error(e)
            return None
    
    def read_until(self, terminator: bytes = b'\r\n', timeout: float = 5.0) -> Optional[bytes]:
        """
        Read until a specific terminator is found
        Args:
            terminator: Byte sequence to read until
            timeout: Timeout in seconds
        Returns: Received bytes including terminator, or None
        """
        if not self.connected or not self.serial_port:
            return None
        
        try:
            original_timeout = self.serial_port.timeout
            self.serial_port.timeout = timeout
            
            data = self.serial_port.read_until(terminator)
            
            self.serial_port.timeout = original_timeout
            
            if data:
                print(f"Serial read {len(data)} bytes until terminator")
                return data
            return None
            
        except Exception as e:
            print(f"Serial read_until error: {e}")
            if self.on_error:
                self.on_error(e)
            return None
    
    def flush(self):
        """Flush input and output buffers"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
    
    def set_dtr(self, state: bool):
        """Set DTR (Data Terminal Ready) signal"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.dtr = state
    
    def set_rts(self, state: bool):
        """Set RTS (Request To Send) signal"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.rts = state
    
    def get_cd(self) -> bool:
        """Get CD (Carrier Detect) signal state"""
        if self.serial_port and self.serial_port.is_open:
            return self.serial_port.cd
        return False
    
    def get_cts(self) -> bool:
        """Get CTS (Clear To Send) signal state"""
        if self.serial_port and self.serial_port.is_open:
            return self.serial_port.cts
        return False
    
    def get_dsr(self) -> bool:
        """Get DSR (Data Set Ready) signal state"""
        if self.serial_port and self.serial_port.is_open:
            return self.serial_port.dsr
        return False
    
    def send_break(self, duration: float = 0.25):
        """Send break condition"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.send_break(duration)
    
    def get_status(self) -> Dict:
        """Get current connection status"""
        status = {
            'connected': self.connected,
            'port': self.port_name,
            'baudrate': self.baudrate,
            'bytesize': self.bytesize,
            'parity': self.parity,
            'stopbits': self.stopbits,
            'timeout': self.timeout
        }
        
        if self.serial_port and self.serial_port.is_open:
            status.update({
                'is_open': True,
                'in_waiting': self.serial_port.in_waiting,
                'out_waiting': self.serial_port.out_waiting,
                'dtr': self.serial_port.dtr,
                'rts': self.serial_port.rts,
                'cts': self.serial_port.cts,
                'dsr': self.serial_port.dsr,
                'cd': self.serial_port.cd
            })
        else:
            status['is_open'] = False
        
        return status
