import socket, threading, json, cmd,time
from random import randint
import betcha21, os

global clients
ingame=False
nextgame=0
turnof=0
gamers=[]
waiters=[]
pot=0


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
cards=betcha21.cards()

def pick_card():
    global cards
    c=cards[0]
    del cards[0]
    return c

def game():
    global gamers
    global waiters
    global cards
    pot=0
    while 1:
        while len(gamers)+len(waiters)<2:
            pass
        gamers=gamers+waiters
        waiters=[]
        g=[]
        for i in range(len(gamers)):
            if gamers[i][2]:
                g.append(gamers[i])
        gamers=g.copy()
        for i in range(len(gamers)):
            gamers[i][0]-=1
        cards=betcha21.cards()
        joueurs=[]
        mise=0
        pot+=len(gamers)
        for i in range(len(gamers)):
            joueurs.append([pick_card()])
        for i in range(len(gamers)):
            joueurs[i].append(pick_card())
            send_msg({"msg":"place","nbr":i, "max":len(gamers), "cards":joueurs[i], "score":betcha21.score(joueurs[i]), "argent":gamers[i][0]},gamers[i][1])
        for tour in range(5):
            broadcast_msg({"msg":"new_turn", "turn":tour})
            stand=0
            for auj in range(len(gamers)):
                if joueurs[auj]==[] or not gamers[auj][2]:
                    joueurs[auj]=[]
                    stand+=1
                    continue
                broadcast_msg({"msg":"player_turn", "player":auj})
                send_msg({"msg":"your_turn", "cards":joueurs[auj], "score":betcha21.score(joueurs[auj])}, gamers[auj][1])
                if tour>0: #on tire pas au premier tour
                    send_msg({"msg":"action", "ask":"hit/stand"}, gamers[auj][1])
                    act=ask(gamers[auj][1])
                    if act=="1":
                        broadcast_msg({"msg":"hit", "player":auj})
                        joueurs[auj].append(pick_card())
                        send_msg({"msg":"your_turn", "cards":joueurs[auj], "score":betcha21.score(joueurs[auj])}, gamers[auj][1])        
                    else:
                        broadcast_msg({"msg":"stand", "player":auj})
                        stand+=1
                send_msg({"msg":"action", "ask":"call/fold"}, gamers[auj][1])
                time.sleep(0.1)
                act=ask(gamers[auj][1])
                if act=="call":
                    if mise>gamers[auj][0]:
                        pot+=gamers[auj][0]
                        gamers[auj][0]=0
                    else:
                        pot+=mise
                        gamers[auj][0]-=mise
                    
                elif act[0:4]=="more":
                    nmise=int(act[4:])
                    if nmise<mise:
                        if nmise>gamers[auj][0]:
                            pot+=gamers[auj][0]
                            gamers[auj][0]=0
                        else:
                            pot+=mise
                            gamers[auj][0]-=mise
                    else:
                        if nmise>gamers[auj][0]:
                            pot+=gamers[auj][0]
                            gamers[auj][0]=0
                        else:    
                            pot+=nmise
                            mise=nmise
                            gamers[auj][0]-=mise
                            broadcast_msg({"msg":"more", "player":auj})
                else:
                    joueurs[auj]=[]
                    broadcast_msg({"msg":"fold","player":auj})
                broadcast_msg({"msg":"update_details","player":auj,"mise":mise, "pot":pot, "nbr_card":len(joueurs[auj])})
                
            if stand==len(gamers):
                break
            jg=-1
            for i in range(len(gamers)):
                if joueurs[i]!=[]:
                    if jg==-1:
                        jg=i
                    else:
                        jg=-1
                        break
            if jg!=-1:
                break
        gagnants=[]
        score=1
        for i in range(len(gamers)):
            s=betcha21.score(joueurs[i])
            if s>21:
                continue
            if s>score:
                gagnants=[str(i)]
                score=s
            elif score==s:
                gagnants.append(str(i))
        if len(gagnants)==1:
            gamers[int(gagnants[0])][0]+=pot
            pot=0
        elif len(gagnants)==0:
            pass
        else:
            for i in gagnants:
                gamers[int(i)][0]+=pot//len(gagnants)
            pot%=len(gagnants)
        broadcast_msg({"msg":"winner","players":gagnants, "cards":joueurs})
        time.sleep(5)

def handle_client(client_socket, id):
    send_msg({"msg":"waitfor"},client_socket)
    waiters.append([10000, client_socket, True, id])
    running=True
    while running:
        try:
            pass    
        except:
            running=False
    for i in range(len(gamers)):
        if gamers[i][3]==id:
            gamers[i][2]=False
            break
    client_socket.close()

def broadcast_msg(message):
    print(message)
    for i in gamers:
        i[1].send(json.dumps(message).encode())

def send_msg(msg, to):
    to.send(json.dumps(msg).encode())

def ask(to):
    n=to.recv(1024)
    return n.decode()
        

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', port))
    server.listen()
    print(f"Serveur en écoute sur le port {port}...")
    prompt_cmd = threading.Thread(target=game)
    prompt_cmd.start()
    id=0
    while True:
        client_socket, addr = server.accept()
        print(f"Connexion de {addr}...")

        client_handler = threading.Thread(target=handle_client, args=(client_socket,id))
        client_handler.start()

if __name__ == "__main__":
    """port=input("Sur quel port lancer le serveur (12345 par défaut) : ")
    if port=="":
        port=12345
    else:
        port=int(port)"""
    start_server(5000)
