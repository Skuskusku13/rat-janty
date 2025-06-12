"""
Command execution functionality.
"""

import subprocess
from typing import Optional
from src.utils.logger import Logger

class CommandExecutor:
    """Handles command execution and processing."""
    
    def __init__(self):
        """Initialize the command executor."""
        self.logger = Logger("CommandExecutor")
    
    def execute_command(self, command: str) -> str:
        """
        Execute a system command.
        
        Args:
            command: Command to execute
            
        Returns:
            Command output
        """
        try:
            self.logger.info(f"Executing command: {command}")
            result = subprocess.getoutput(command)
            if not result:
                return "[*] Commande exécutée sans sortie."
            return result
        except Exception as e:
            error_msg = f"[!] Erreur d'exécution : {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def execute_safe_command(self, command: str) -> Optional[str]:
        """
        Execute a command with safety checks.
        
        Args:
            command: Command to execute
            
        Returns:
            Command output if safe, None otherwise
        """
        # Add safety checks here
        if self._is_safe_command(command):
            return self.execute_command(command)
        return None
    
    def _is_safe_command(self, command: str) -> bool:
        """
        Check if a command is safe to execute.
        
        Args:
            command: Command to check
            
        Returns:
            True if command is safe, False otherwise
        """
        # Add command safety checks here
        # For example, check for dangerous commands
        dangerous_commands = [
            "rm -rf",
            "format",
            "mkfs",
            "dd",
            ":(){ :|:& };:"
        ]
        
        return not any(dc in command.lower() for dc in dangerous_commands) 