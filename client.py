from clientThread import ClientThread

def main():
    HOST = '127.0.0.1'  # Adresse IP du serveur
    PORT = 9999         # Port utilisé par le serveur

    client = ClientThread(HOST, PORT)
    client.start()
    client.join()  # Attend que le thread se termine

if __name__ == "__main__":
    main()
