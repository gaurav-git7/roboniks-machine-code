"""
Base Interface Handler
Abstract base class for all communication interfaces
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
import threading
import time


class BaseInterface(ABC):
    """Abstract base class for communication interfaces"""
    
    def __init__(self):
        self.connected = False
        self.receiving = False
        self.receive_thread = None
        self.on_message_received: Optional[Callable[[bytes], None]] = None
        self.on_connection_lost: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
    
    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        Establish connection
        Returns: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Close connection
        Returns: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def send(self, data: bytes) -> bool:
        """
        Send data through the interface
        Args:
            data: Bytes to send
        Returns: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def receive(self, timeout: float = 5.0) -> Optional[bytes]:
        """
        Receive data from the interface
        Args:
            timeout: Timeout in seconds
        Returns: Received bytes or None
        """
        pass
    
    def is_connected(self) -> bool:
        """Check if interface is connected"""
        return self.connected
    
    def start_receiving(self, callback: Callable[[bytes], None]):
        """
        Start continuous receiving in background thread
        Args:
            callback: Function to call when data is received
        """
        self.on_message_received = callback
        self.receiving = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
    
    def stop_receiving(self):
        """Stop background receiving"""
        self.receiving = False
        if self.receive_thread:
            self.receive_thread.join(timeout=2.0)
    
    def _receive_loop(self):
        """Background thread for continuous receiving"""
        while self.receiving and self.connected:
            try:
                data = self.receive(timeout=1.0)
                if data and self.on_message_received:
                    self.on_message_received(data)
            except Exception as e:
                if self.on_error:
                    self.on_error(e)
                time.sleep(0.1)
    
    def set_callbacks(
        self,
        on_message: Optional[Callable[[bytes], None]] = None,
        on_disconnect: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """Set callback functions for events"""
        if on_message:
            self.on_message_received = on_message
        if on_disconnect:
            self.on_connection_lost = on_disconnect
        if on_error:
            self.on_error = on_error
