import socket, threading, json, cmd,time
from random import randint

global clients
ingame=False
nextgame=0
turnof=0
gamers=[]
pot=0
def handle_client(client_socket, id):
    if ingame:
        client_socket.send(json.dumps({"etat":"ingame"}).encode())
    while ingame:
        try:
            pass
        except:
            return
    nextgame=time.time()+90
    pot=0
    running=True
    gamers.append((id, client_socket, []))
    while running:
        while nextgame>0:
            try:
                client_socket.send(json.dumps({"etat":"waiting","time":int(time.time()-nextgame), "players":len(gamers)}).encode())
            except:
                running=False
        
        ingame=True
        running=True
        client_socket.send(json.dumps({"etat":"playing","players":len(gamers)}).encode())
            
        while ingame:
            try:
                if gamers[turnof][0]==id:
                    client_socket.send(json.dumps({"etat":"waiting","time":int(time.time()-nextgame), "players":len(gamers)}).encode())
            except:
                running=False
        for i in range(len(gamers)):
            if gamers[i][0]==id:
                del gamers[i]
                break
    client_socket.close()

def broadcast_msg(message):
    print(message)
    for i in gamers:
        clients[i]["socket"].send(message.encode())

def server_cmd():
    while 1:
        cm=input()
        cmd.exe_cmd("-1", "/"+cm, clients)

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen()
    print(f"Serveur en écoute sur le port {port}...")
    prompt_cmd = threading.Thread(target=server_cmd)
    prompt_cmd.start()
    id=0
    while True:
        client_socket, addr = server.accept()
        print(f"Connexion de {addr}...")

        client_handler = threading.Thread(target=handle_client, args=(client_socket,id))
        client_handler.start()

if __name__ == "__main__":
    port=input("Sur quel port lancer le serveur (12345 par défaut) : ")
    if port=="":
        port=12345
    else:
        port=int(port)
    start_server(port)
