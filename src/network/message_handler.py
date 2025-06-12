"""
Message handler for processing different types of messages.
"""

import json
from src.utils.logger import Logger

class MessageHandler:
    def __init__(self, client):
        """
        Initialize the message handler.
        
        Args:
            client: Client instance
        """
        self.client = client
        self.logger = Logger("MessageHandler")
        self.handlers = {}
        self.register_default_handlers()
    
    def register_default_handlers(self):
        """Register default message handlers."""
        self.register_handler("command", self.handle_command)
        self.register_handler("chat", self.handle_chat)
        self.register_handler("response", self.handle_response)
        self.register_handler("screenshot", self.handle_screenshot)
        self.register_handler("exit", self.handle_exit)
    
    def register_handler(self, message_type, handler):
        """
        Register a message handler.
        
        Args:
            message_type: Type of message to handle
            handler: Handler function
        """
        self.handlers[message_type] = handler
    
    def handle_message(self, message):
        """
        Handle an incoming message.
        
        Args:
            message: Message to handle
        """
        try:
            if isinstance(message, str):
                message = json.loads(message)
            
            message_type = message.get("type")
            if message_type in self.handlers:
                self.handlers[message_type](message.get("content"))
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
    
    def handle_command(self, command):
        """
        Handle command messages.
        
        Args:
            command: Command to execute
        """
        self.client.handle_command(command)
    
    def handle_chat(self, message):
        """
        Handle chat messages.
        
        Args:
            message: Chat message
        """
        self.client.gui.log_chat("Server", message)
    
    def handle_response(self, response):
        """
        Handle response messages.
        
        Args:
            response: Response message
        """
        self.client.gui.log_message(response)
    
    def handle_screenshot(self, image_data):
        """
        Handle screenshot messages.
        
        Args:
            image_data: Base64 encoded image data
        """
        self.client.gui.display_screenshot(image_data)
    
    def handle_exit(self, _):
        """Handle exit messages."""
        self.client.gui.root.quit() 