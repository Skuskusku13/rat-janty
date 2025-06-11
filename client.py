from clientThread import ClientThread

def main():
    HOST = '127.0.0.1'  # IP du serveur
    PORT = 9999         # Port du serveur

    client = ClientThread(HOST, PORT)
    client.start()
    client.join()

if __name__ == "__main__":
    main()
