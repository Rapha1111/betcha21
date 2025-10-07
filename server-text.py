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
        for tour in range(5):
            broadcast_msg(f"\n\n=====TOUR {tour}/4====")
            stand=0
            for auj in range(len(gamers)):
                if joueurs[auj]==[] or not gamers[auj][2]:
                    joueurs[auj]=[]
                    stand+=1
                    continue
                broadcast_msg(f'\n===========JOUEUR {auj+1}/{len(joueurs)}===========')
                send_msg(f"Cartes : {", ".join(joueurs[auj])} -> Score : {betcha21.score(joueurs[auj])}", gamers[auj][1])
                broadcast_msg(f"\nMise : {mise}, Pot : {pot}, Argent : {gamers[auj][0]}")
                if tour>0: #on tire pas au premier tour
                    send_msg("\nActions :\n1. Hit\n2. Stand", gamers[auj][1])
                    time.sleep(0.1)
                    act=ask("-> ", gamers[auj][1])
                    if act=="1":
                        broadcast_msg(f"==> Joueur {auj+1} hit")
                        joueurs[auj].append(pick_card())
                        send_msg(f"\nPioché : {joueurs[auj][-1]}\nCartes : {", ".join(joueurs[auj])} -> Score : {betcha21.score(joueurs[auj])}\nMise : {mise}, Pot : {pot}\n", gamers[auj][1])
                    else:
                        broadcast_msg(f"==> Joueur {auj+1} stand")
                        stand+=1
                send_msg(f"\nActions :\n1. Suivre la mise ({mise})\n2. Augmenter la mise\n3. Se coucher", gamers[auj][1])
                time.sleep(0.1)
                act=ask("-> ", gamers[auj][1])
                if act=="1":
                    broadcast_msg(f"==> Joueur {auj+1} suit la mise")
                    pot+=mise
                    gamers[auj][0]-=mise
                elif act=="2":
                    mise=int(ask("Nouvelle mise : ", gamers[auj][1]))
                    pot+=mise
                    gamers[auj][0]-=mise
                    broadcast_msg(f"==> Joueur {auj+1} a mis la mise a {mise}")
                else:
                    joueurs[auj]=[]
                    broadcast_msg(f"==> Joueur {auj+1} se couche")
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
                gagnants=[str(i+1)]
                score=s
            elif score==s:
                gagnants.append(str(i+1))
        if len(gagnants)==1:
            broadcast_msg(f"Le gagnant est : {gagnants[0]}")
            gamers[int(gagnants[0])-1][0]+=pot
            pot=0
        elif len(gagnants)==0:
            broadcast_msg(f"Pas de gagnants a cette partie, le pot est gardé")
        else:
            broadcast_msg(f"Les gagnants sont : {", ".join(gagnants)}")
            for i in gagnants:
                gamers[int(i)-1][0]+=pot//len(gagnants)
            pot%=len(gagnants)
        time.sleep(3)
        clear()

def handle_client(client_socket, id):
    client_socket.send("En attente de la fin de la partie...".encode())
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
        i[1].send(message.encode())

def send_msg(msg, to):
    to.send(msg.encode())

def ask(msg, to):
    send_msg("ask:"+msg, to)
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
