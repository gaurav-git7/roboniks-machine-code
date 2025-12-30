"""
LAN Interface Handler
Handles TCP/IP socket communication over network
"""

import socket
import threading
from typing import Optional, Dict
from .base_interface import BaseInterface


class LANHandler(BaseInterface):
    """Handles LAN communication using TCP/IP sockets"""
    
    def __init__(self):
        super().__init__()
        self.socket: Optional[socket.socket] = None
        self.host: str = ""
        self.port: int = 0
        self.timeout: float = 5.0
        self.mode: str = "client"  # 'client' or 'server'
        self.server_socket: Optional[socket.socket] = None
        self.client_connection: Optional[socket.socket] = None
    
    def connect(
        self,
        host: str = "localhost",
        port: int = 5000,
        timeout: float = 5.0,
        mode: str = "client",
        **kwargs
    ) -> bool:
        """
        Connect to device via TCP/IP
        Args:
            host: IP address or hostname
            port: Port number
            timeout: Connection timeout in seconds
            mode: 'client' to connect to server, 'server' to listen for connections
        Returns: True if connected successfully
        """
        try:
            if self.connected:
                self.disconnect()
            
            self.host = host
            self.port = port
            self.timeout = timeout
            self.mode = mode
            
            if mode == "client":
                return self._connect_as_client()
            else:
                return self._connect_as_server()
            
        except Exception as e:
            print(f"LAN connection error: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    def _connect_as_client(self) -> bool:
        """Connect as TCP client"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            
            print(f"Connecting to {self.host}:{self.port}...")
            self.socket.connect((self.host, self.port))
            
            self.connected = True
            print(f"LAN connected to {self.host}:{self.port}")
            return True
            
        except socket.timeout:
            print(f"LAN connection timeout to {self.host}:{self.port}")
            return False
        except socket.error as e:
            print(f"LAN socket error: {e}")
            return False
    
    def _connect_as_server(self) -> bool:
        """Start TCP server and wait for client connection"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(self.timeout)
            
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            
            print(f"LAN server listening on {self.host}:{self.port}")
            
            # Wait for client connection in background
            threading.Thread(target=self._accept_client, daemon=True).start()
            
            return True
            
        except socket.error as e:
            print(f"LAN server error: {e}")
            return False
    
    def _accept_client(self):
        """Accept incoming client connection (for server mode)"""
        try:
            print("Waiting for client connection...")
            self.client_connection, client_address = self.server_socket.accept()
            self.client_connection.settimeout(self.timeout)
            
            self.socket = self.client_connection
            self.connected = True
            
            print(f"LAN client connected from {client_address}")
            
        except socket.timeout:
            print("No client connected within timeout")
        except Exception as e:
            print(f"Error accepting client: {e}")
            if self.on_error:
                self.on_error(e)
    
    def disconnect(self) -> bool:
        """Close LAN connection"""
        try:
            self.stop_receiving()
            
            if self.socket:
                self.socket.close()
                self.socket = None
            
            if self.client_connection:
                self.client_connection.close()
                self.client_connection = None
            
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            
            self.connected = False
            print(f"LAN disconnected from {self.host}:{self.port}")
            
            if self.on_connection_lost:
                self.on_connection_lost()
            
            return True
            
        except Exception as e:
            print(f"LAN disconnect error: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    def send(self, data: bytes) -> bool:
        """
        Send data over LAN
        Args:
            data: Bytes to send
        Returns: True if successful
        """
        if not self.connected or not self.socket:
            print("LAN not connected")
            return False
        
        try:
            self.socket.sendall(data)
            print(f"LAN sent {len(data)} bytes")
            return True
            
        except socket.timeout:
            print("LAN send timeout")
            return False
        except socket.error as e:
            print(f"LAN send error: {e}")
            if self.on_error:
                self.on_error(e)
            # Connection lost
            self.connected = False
            if self.on_connection_lost:
                self.on_connection_lost()
            return False
    
    def receive(self, timeout: float = 5.0, buffer_size: int = 4096) -> Optional[bytes]:
        """
        Receive data from LAN
        Args:
            timeout: Timeout in seconds
            buffer_size: Maximum bytes to receive
        Returns: Received bytes or None
        """
        if not self.connected or not self.socket:
            return None
        
        try:
            # Temporarily set timeout
            original_timeout = self.socket.gettimeout()
            self.socket.settimeout(timeout)
            
            data = self.socket.recv(buffer_size)
            
            # Restore timeout
            self.socket.settimeout(original_timeout)
            
            if data:
                print(f"LAN received {len(data)} bytes")
                return data
            else:
                # Connection closed by remote
                print("LAN connection closed by remote")
                self.connected = False
                if self.on_connection_lost:
                    self.on_connection_lost()
                return None
            
        except socket.timeout:
            return None
        except socket.error as e:
            print(f"LAN receive error: {e}")
            if self.on_error:
                self.on_error(e)
            self.connected = False
            if self.on_connection_lost:
                self.on_connection_lost()
            return None
    
    def send_string(self, message: str, encoding: str = 'utf-8') -> bool:
        """
        Send string message
        Args:
            message: String to send
            encoding: Text encoding
        Returns: True if successful
        """
        return self.send(message.encode(encoding))
    
    def receive_string(self, timeout: float = 5.0, encoding: str = 'utf-8') -> Optional[str]:
        """
        Receive string message
        Args:
            timeout: Timeout in seconds
            encoding: Text encoding
        Returns: Decoded string or None
        """
        data = self.receive(timeout)
        if data:
            return data.decode(encoding, errors='ignore')
        return None
    
    def get_status(self) -> Dict:
        """Get current connection status"""
        return {
            'connected': self.connected,
            'host': self.host,
            'port': self.port,
            'timeout': self.timeout,
            'mode': self.mode
        }
    
    @staticmethod
    def scan_network(port: int, timeout: float = 1.0, start_ip: str = "192.168.1.1", end_ip: str = "192.168.1.254") -> list:
        """
        Scan network for devices listening on specified port
        Args:
            port: Port to scan
            timeout: Timeout per host
            start_ip: Starting IP address
            end_ip: Ending IP address
        Returns: List of responsive IP addresses
        """
        responsive_hosts = []
        
        # Simple scan implementation
        import ipaddress
        start = ipaddress.IPv4Address(start_ip)
        end = ipaddress.IPv4Address(end_ip)
        
        for ip_int in range(int(start), int(end) + 1):
            ip = str(ipaddress.IPv4Address(ip_int))
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    responsive_hosts.append(ip)
                    print(f"Found device at {ip}:{port}")
            except:
                pass
        
        return responsive_hosts
