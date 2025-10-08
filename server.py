import socket, threading, json, time
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
            gamers[i][0]-=10
            if gamers[i][0]<0:
                gamers[i][0]=0
            else:
                pot+=10
        cards=betcha21.cards()
        joueurs=[]
        mise=10
        noms=[]
        for i in range(len(gamers)):
            joueurs.append([pick_card()])
            noms.append(gamers[i][5])
        for i in range(len(gamers)):
            joueurs[i].append(pick_card())
            send_msg({"msg":"place","nbr":i, "max":len(gamers), "cards":joueurs[i], "score":betcha21.score(joueurs[i]), "argent":gamers[i][0], "pot":pot, "names":noms},gamers[i][1])
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
                if act[0:4]=="more":
                    nmise=int(act[4:])
                    if nmise<mise:
                        act="call"
                    else:
                        if nmise>gamers[auj][0]:
                            act="call"
                        else:    
                            pot+=nmise
                            mise=nmise
                            gamers[auj][0]-=mise
                            broadcast_msg({"msg":"more", "player":auj})
                if act=="call":
                    if mise>gamers[auj][0]:
                        gamers[auj][4]+=mise-gamers[auj][0]
                        pot+=gamers[auj][0]
                        gamers[auj][0]=0
                    else:
                        pot+=mise
                        gamers[auj][0]-=mise
                    
                elif act[0:4]!="more":
                    joueurs[auj]=[]
                    broadcast_msg({"msg":"fold","player":auj})
                send_msg({"msg":"setmoney", "money":gamers[auj][0]}, gamers[auj][1])
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
        gp=[]
        dnr=False
        score=1
        for i in range(len(gamers)):
            s=betcha21.score(joueurs[i])
            if s>21:
                continue
            else:
                gp.append(str(i))
            if s>score:
                gagnants=[str(i)]
                score=s
            elif score==s:
                gagnants.append(str(i))
        if len(gagnants)==0:
            if len(gp)==1:
                gagnants=gp.copy()
                dnr=True
        
        if len(gagnants)==1:
            if gamers[int(gagnants[0])][4]*2>pot:
                gamers[int(gagnants[0])][4]-=pot
            else:
                recup=pot-gamers[int(gagnants[0])][4]*2
                pot-=recup
                gamers[int(gagnants[0])][0]+=recup
                gamers[int(gagnants[0])][4]=0
                
                
        elif len(gagnants)==0:
            pass
        else:
            gain=pot//len(gagnants)
            pot%=len(gagnants)
            for i in gagnants:
                if gamers[int(i)][4]*2>gain:
                    gamers[int(i)][4]-=gain
                else:
                    recup=gamers[int(i)][4]*2
                    pot+=recup
                    gamers[int(gagnants[0])][0]+=gain-recup
                    gamers[int(gagnants[0])][4]=0
                #gamers[int(i)][0]+=pot//len(gagnants)
        if dnr:
            c=[]
            for i in range(len(joueurs)):
                if i in gagnants:
                    c.append(len(joueurs[auj]))
                else:
                    c.append(0)
            broadcast_msg({"msg":"winner","players":gagnants, "cards":c})
        else:
            broadcast_msg({"msg":"winner","players":gagnants, "cards":joueurs})
        time.sleep(5)

def handle_client(client_socket, id):
    pseudo=client_socket.recv(1024).decode()
    send_msg({"msg":"waitfor"},client_socket)
    waiters.append([10000, client_socket, True, id, 0, pseudo])
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
