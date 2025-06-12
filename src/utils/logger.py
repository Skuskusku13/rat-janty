"""
Logging utilities for the application.
"""

import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """Custom logger for the application."""
    
    def __init__(self, name: str):
        """
        Initialize the logger.
        
        Args:
            name: Name of the logger
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # Create file handler
        log_file = f"logs/{name.lower()}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def info(self, message: str) -> None:
        """
        Log an info message.
        
        Args:
            message: Message to log
        """
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: Message to log
        """
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: Message to log
        """
        self.logger.warning(message)
    
    def debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: Message to log
        """
        self.logger.debug(message)

class ChatLogger:
    """Logger specifically for chat messages."""
    
    def __init__(self, text_widget):
        """
        Initialize the chat logger.
        
        Args:
            text_widget: Tkinter text widget to display messages
        """
        self.text_widget = text_widget
    
    def log_message(self, sender: str, message: str) -> None:
        """
        Log a chat message.
        
        Args:
            sender: Name of the message sender
            message: Message content
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {sender}: {message}\n"
        
        self.text_widget.config(state='normal')
        self.text_widget.insert('end', formatted_message)
        self.text_widget.see('end')
        self.text_widget.config(state='disabled') 