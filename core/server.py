"""
Main server implementation.
"""

import tkinter as tk
import threading
import signal
from typing import Dict, Optional, Tuple
from network.socket_manager import SocketManager
from network.message_handler import MessageHandler
from gui.server_gui import ServerGUI
from utils.constants import DEFAULT_HOST, DEFAULT_PORT
from utils.logger import Logger

class Server:
    """Main server class."""
    
    def __init__(self):
        """Initialize the server."""
        self.logger = Logger("Server")
        self.socket_manager = SocketManager(DEFAULT_HOST, DEFAULT_PORT)
        self.message_handler = MessageHandler()
        
        self.clients: Dict[int, Tuple[SocketManager, threading.Thread]] = {}
        self.next_client_id = 0
        self.running = True
        
        self.setup_gui()
        self.setup_message_handlers()
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
    
    def handle_signal(self, signum, frame) -> None:
        """
        Handle system signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.logger.info("Signal reçu, arrêt du serveur...")
        self.running = False
        self.cleanup()
        self.root.quit()
    
    def setup_gui(self) -> None:
        """Set up the server GUI."""
        self.root = tk.Tk()
        self.gui = ServerGUI(self.root)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_message_handlers(self) -> None:
        """Set up message handlers."""
        self.message_handler.register_handler(
            "command",
            lambda client_id, data: self.handle_command(client_id, data)
        )
        self.message_handler.register_handler(
            "chat",
            lambda client_id, data: self.handle_chat(client_id, data)
        )
        self.message_handler.register_handler(
            "response",
            lambda client_id, data: self.handle_response(client_id, data)
        )
        self.message_handler.register_handler(
            "exit",
            lambda client_id, data: self.handle_exit(client_id)
        )
    
    def start(self) -> None:
        """Start the server."""
        try:
            self.socket_manager.create_server_socket()
            self.logger.info(f"Serveur démarré sur {DEFAULT_HOST}:{DEFAULT_PORT}")
            
            # Start accepting connections in a separate thread
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            # Start GUI main loop
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage du serveur: {e}")
            self.cleanup()
    
    def accept_connections(self) -> None:
        """Accept incoming connections."""
        while self.running:
            try:
                client_socket, address = self.socket_manager.accept_connection()
                client_id = self.next_client_id
                self.next_client_id += 1
                
                # Create client socket manager
                client_socket_manager = SocketManager(socket=client_socket)
                
                # Start client thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_id, client_socket_manager, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
                # Store client info
                self.clients[client_id] = (client_socket_manager, client_thread)
                self.gui.add_client(client_id, address)
                
                self.logger.info(f"Nouveau client connecté: {address}")
                
            except Exception as e:
                if self.running:  # Only log if we're still running
                    self.logger.error(f"Erreur lors de l'acceptation d'une connexion: {e}")
                break
    
    def handle_client(self, client_id: int, 
                     socket_manager: SocketManager,
                     address: Tuple[str, int]) -> None:
        """
        Handle client communication.
        
        Args:
            client_id: Client ID
            socket_manager: Client socket manager
            address: Client address
        """
        try:
            while self.running:
                data = socket_manager.receive_data()
                if not data:
                    break
                
                self.message_handler.process_message(client_id, data)
                
        except Exception as e:
            if self.running:  # Only log if we're still running
                self.logger.error(f"Erreur avec le client {client_id}: {e}")
        finally:
            self.handle_exit(client_id)
    
    def handle_command(self, client_id: int, command: str) -> None:
        """
        Handle command message.
        
        Args:
            client_id: Client ID
            command: Command to execute
        """
        self.gui.log_message(f"[Client {client_id}] Commande: {command}")
    
    def handle_chat(self, client_id: int, message: str) -> None:
        """
        Handle chat message.
        
        Args:
            client_id: Client ID
            message: Chat message
        """
        self.gui.log_chat(f"Client {client_id}", message)
    
    def handle_response(self, client_id: int, response: str) -> None:
        """
        Handle response message.
        
        Args:
            client_id: Client ID
            response: Response message
        """
        self.gui.log_message(f"[Client {client_id}] Réponse: {response}")
    
    def handle_exit(self, client_id: int) -> None:
        """
        Handle client exit.
        
        Args:
            client_id: Client ID
        """
        if client_id in self.clients:
            socket_manager, _ = self.clients[client_id]
            try:
                socket_manager.send_data("exit:")  # Notify client to exit
            except:
                pass
            finally:
                socket_manager.close()
                del self.clients[client_id]
                self.gui.remove_client(client_id)
                self.logger.info(f"Client {client_id} déconnecté")
    
    def send_command(self, client_id: int, command: str) -> None:
        """
        Send command to client.
        
        Args:
            client_id: Client ID
            command: Command to send
        """
        if client_id in self.clients:
            socket_manager, _ = self.clients[client_id]
            try:
                socket_manager.send_data(f"command:{command}")
            except Exception as e:
                self.logger.error(f"Erreur lors de l'envoi de la commande: {e}")
    
    def send_chat(self, client_id: int, message: str) -> None:
        """
        Send chat message to client.
        
        Args:
            client_id: Client ID
            message: Message to send
        """
        if client_id in self.clients:
            socket_manager, _ = self.clients[client_id]
            try:
                socket_manager.send_data(f"chat:{message}")
            except Exception as e:
                self.logger.error(f"Erreur lors de l'envoi du message: {e}")
    
    def on_close(self) -> None:
        """Handle window close event."""
        if tk.messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter ?"):
            self.running = False
            self.cleanup()
            self.root.destroy()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.running = False
        
        # Close all client connections
        for client_id in list(self.clients.keys()):
            self.handle_exit(client_id)
        
        # Close server socket
        self.socket_manager.close()

if __name__ == "__main__":
    server = Server()
    server.start() 