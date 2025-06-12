"""
Constants used throughout the application.
"""

# Network settings
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 9999
SERVER_HOST = '127.0.0.1'  # localhost
SERVER_PORT = 9999
BUFFER_SIZE = 4096

# Message types
MSG_TYPE_COMMAND = "command"
MSG_TYPE_CHAT = "chat"
MSG_TYPE_RESPONSE = "response"
MSG_TYPE_EXIT = "exit"

# GUI settings
SERVER_WINDOW_SIZE = "800x600"
CLIENT_WINDOW_SIZE = "400x300"
SERVER_TITLE = "RAT Server"
CLIENT_TITLE = "RAT Client"

# Message prefixes
RESPONSE_PREFIX = "[RESPONSE]"
CHAT_PREFIX = "[CHAT]"
ERROR_PREFIX = "[ERROR]"
INFO_PREFIX = "[INFO]" 