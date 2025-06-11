import socket

# Configuration du serveur
HOST = '0.0.0.0'  # Accepte les connexions entrantes sur toutes les interfaces réseau
PORT = 9999       # Port d'écoute (peut être modifié si déjà utilisé)

def main():
    # Création de la socket TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)  # Une seule connexion simultanée (pour commencer simple)
    print(f"[*] En attente de connexion sur {HOST}:{PORT}...")

    client_socket, client_address = server.accept()
    print(f"[+] Connexion établie avec {client_address[0]}:{client_address[1]}")

    try:
        while True:
            # Demande une commande à l'utilisateur (opérateur)
            command = input(">> ")

            if command.strip() == "":
                continue  # Ne rien faire si commande vide

            client_socket.send(command.encode())  # Envoie la commande au client

            if command.lower() == "exit":
                print("[*] Déconnexion du client.")
                break

            # Réception du résultat de la commande
            result = client_socket.recv(4096).decode(errors='ignore')
            print(result)
    except KeyboardInterrupt:
        print("\n[!] Interruption par l'utilisateur.")
    finally:
        client_socket.close()
        server.close()
        print("[*] Serveur arrêté.")

if __name__ == "__main__":
    main()
