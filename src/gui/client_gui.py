"""
Client GUI implementation.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional
from src.utils.logger import Logger, ChatLogger
from src.utils.constants import CLIENT_TITLE, CLIENT_WINDOW_SIZE, ICON_PATH
from datetime import datetime
import base64
from PIL import Image, ImageTk
import io

class ClientGUI:
    """Client graphical user interface."""
    
    def __init__(self, root, client):
        """
        Initialize the client GUI.
        
        Args:
            root: Tkinter root window
            client: Client instance
        """
        self.root = root
        self.client = client

        self.root.iconbitmap(ICON_PATH)
        self.root.title(CLIENT_TITLE)
        self.root.geometry(CLIENT_WINDOW_SIZE)
        
        self.logger = Logger("ClientGUI")
        self.chat_logger = None  # Will be initialized after creating chat_text
        
        self.setup_gui()
    
    def setup_gui(self) -> None:
        """Set up the GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chat area
        chat_frame = ttk.LabelFrame(main_frame, text="Chat")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_text = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD)
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_text.config(state=tk.DISABLED)
        
        # Initialize chat logger
        self.chat_logger = ChatLogger(self.chat_text)
        
        # Input area
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Répondre :").pack(side=tk.LEFT, padx=(0, 5))
        
        self.chat_entry = ttk.Entry(input_frame)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_entry.bind('<Return>', self.send_chat_message)
        
        ttk.Button(input_frame, text="Envoyer", command=self.send_chat_message).pack(side=tk.RIGHT)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log")
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=5)
        self.log_text.pack(fill=tk.X, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def send_chat_message(self, event=None) -> Optional[str]:
        """
        Handle chat message sending.
        
        Args:
            event: Optional event
            
        Returns:
            Optional[str]: Message to send, or None if empty
        """
        message = self.chat_entry.get()
        if not message:
            return None
        
        self.client.send_chat(message)
        self.chat_entry.delete(0, tk.END)
        
        return message
    
    def log_chat(self, sender: str, message: str) -> None:
        """
        Log a chat message.
        
        Args:
            sender: Message sender
            message: Message content
        """
        if self.chat_logger:
            self.chat_logger.log_message(sender, message)
            self.root.lift()  # Bring window to front
            self.chat_entry.focus_set()  # Focus on input field
    
    def log_message(self, message: str) -> None:
        """Log a system message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def show_dialog(self, title: str, message: str) -> None:
        """
        Show a dialog box.
        
        Args:
            title: Dialog title
            message: Dialog message
        """
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Message
        ttk.Label(dialog, text=message, wraplength=350).pack(
            fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # OK button
        ttk.Button(dialog, text="OK", command=dialog.destroy).pack(pady=10)
        
        # Bring dialog to front
        dialog.lift()
        dialog.focus_set()
    
    def on_close(self):
        """Handle window close event."""
        self.client.on_close()
    
    def display_screenshot(self, image_data):
        """Display a screenshot."""
        try:
            # Convertir les données base64 en image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Redimensionner l'image pour l'adapter à la fenêtre
            width = min(image.width, 800)
            height = int(width * image.height / image.width)
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convertir en PhotoImage pour Tkinter
            photo = ImageTk.PhotoImage(image)
            
            # Créer une nouvelle fenêtre pour afficher l'image
            window = tk.Toplevel(self.root)
            window.title("Screenshot")
            
            # Afficher l'image
            label = ttk.Label(window, image=photo)
            label.image = photo  # Garder une référence
            label.pack()
            
        except Exception as e:
            self.show_dialog("Erreur", f"Erreur lors de l'affichage du screenshot: {str(e)}") 