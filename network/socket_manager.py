"""
Socket management for network communications.
"""

import socket
import threading
import json
from typing import Optional, Tuple, Dict, Any
from utils.constants import DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE
from utils.logger import Logger

class SocketManager:
    """Manages socket connections and communications."""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """
        Initialize the socket manager.
        
        Args:
            host: Host address
            port: Port number
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.logger = Logger("SocketManager")
        self.running = True
        self.lock = threading.Lock()
    
    def create_server_socket(self) -> None:
        """Create and configure a server socket."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.logger.info(f"Server listening on {self.host}:{self.port}")
        except Exception as e:
            self.logger.error(f"Failed to create server socket: {e}")
            raise
    
    def create_client_socket(self) -> None:
        """Create and configure a client socket."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logger.info("Client socket created")
        except Exception as e:
            self.logger.error(f"Failed to create client socket: {e}")
            raise
    
    def connect(self, address: Tuple[str, int]) -> None:
        """
        Connect to a server.
        
        Args:
            address: Server address (host, port)
        """
        if not self.socket:
            raise RuntimeError("Client socket not initialized")
        try:
            self.socket.connect(address)
            self.host, self.port = address
            self.logger.info(f"Connected to server {self.host}:{self.port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {e}")
            raise
    
    def accept_connection(self) -> Tuple[socket.socket, Tuple[str, int]]:
        """
        Accept a new connection (server only).
        
        Returns:
            Tuple of (socket, address)
        """
        if not self.socket:
            raise RuntimeError("Server socket not initialized")
        return self.socket.accept()
    
    def send_message(self, message: Dict[str, Any]) -> None:
        """
        Send a message through the socket.
        
        Args:
            message: Message to send (will be converted to JSON)
        """
        if not self.socket:
            raise RuntimeError("Socket not initialized")
        try:
            with self.lock:
                data = json.dumps(message).encode()
                # Send message length first
                length = len(data)
                self.socket.sendall(length.to_bytes(4, byteorder='big'))
                # Then send the message
                self.socket.sendall(data)
                self.logger.debug(f"Sent message: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            raise
    
    def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        Receive a message from the socket.
        
        Returns:
            Received message as dictionary or None if connection closed
        """
        if not self.socket:
            raise RuntimeError("Socket not initialized")
        try:
            # Receive message length first
            length_data = self.socket.recv(4)
            if not length_data:
                return None
            length = int.from_bytes(length_data, byteorder='big')
            
            # Receive the full message
            data = b''
            while len(data) < length:
                chunk = self.socket.recv(min(BUFFER_SIZE, length - len(data)))
                if not chunk:
                    return None
                data += chunk
            
            message = json.loads(data.decode())
            self.logger.debug(f"Received message: {message}")
            return message
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode message: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return None
    
    def close(self) -> None:
        """Close the socket connection."""
        if self.socket:
            try:
                self.socket.close()
                self.logger.info("Socket closed")
            except Exception as e:
                self.logger.error(f"Error closing socket: {e}")
            finally:
                self.socket = None
                self.running = False 