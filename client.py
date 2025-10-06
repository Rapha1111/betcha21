import socket, os

HOST = "127.0.0.1"  # adresse du serveur
PORT = 5000         # port du serveur

# connexion
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print(f"[+] Connecté à {HOST}:{PORT}")

def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

try:
    while True:
        data = client.recv(1024)
        if not data:
            print("[-] Déconnecté du serveur")
            break

        message = data.decode("utf-8").strip()
        
        # si le message commence par ask:, on demande une réponse à l'utilisateur
        if message.startswith("ask:"):
            question = message[4:]
            answer = input(question)
            client.send(answer.encode("utf-8"))
            clear()
        else:
            print(message)

except KeyboardInterrupt:
    print("\n[!] Fermeture du client.")

finally:
    client.close()
