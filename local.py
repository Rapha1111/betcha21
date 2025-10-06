import betcha21, os
from random import randint
PLAYERS=4

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

while 1:
    cards=betcha21.cards()
    joueurs=[]
    mise=0
    pot=PLAYERS
    for i in range(PLAYERS):
        joueurs.append([pick_card()])
    for i in range(PLAYERS):
        joueurs[i].append(pick_card())
    for tour in range(5):
        print(f"====TOUR {tour}====")
        stand=0
        for auj in range(PLAYERS):
            if joueurs[auj]==[]:
                stand+=1
                continue
            print(f'===========JOUEUR {auj}===========')
            print(f"Cartes : {", ".join(joueurs[auj])} -> Score : {betcha21.score(joueurs[auj])}")
            print(f"Mise : {mise}, Pot : {pot}")
            if tour>0: #on tire pas au premier tour
                print("\nActions :\n1. Hit\n2. Stand")
                act=input("-> ")
                if act=="1":
                    joueurs[auj].append(pick_card())
                    print(f"\nPioché : {joueurs[auj][-1]}\n")
                    print(f"Cartes : {", ".join(joueurs[auj])} : {betcha21.score(joueurs[auj])}")
                    print(f"Mise : {mise}, Pot : {pot}")
                else:
                    stand+=1
            print(f"\nActions :\n1. Suivre la mise ({mise})\n2. Augmenter la mise\n3. Se coucher")
            act=input("-> ")
            if act=="1":
                pot+=mise
            elif act=="2":
                mise=int(input("Nouvelle mise : "))
                pot+=mise
            else:
                joueurs[auj]=[]
            clear()
        if stand==PLAYERS:
            break
        jg=-1
        for i in range(PLAYERS):
            if joueurs[i]!=[]:
                if jg==-1:
                    jg=i
                else:
                    jg=-1
                    break
        if jg!=-1:
            break
    gagnants=[]
    score=0
    for i in range(PLAYERS):
        s=betcha21.score(joueurs[i])
        if s>21:
            continue
        if s>score:
            gagnants=[str(i)]
            score=s
        elif score==s:
            gagnants.append(str(i))
    if len(gagnants)==1:
        print(f"Le gagnant est : {gagnants[0]}")
    elif len(gagnants)==0:
        print(f"Pas de gagnants a cette partie, le pot est gardé")
    else:
        print(f"Les gagnants sont : {", ".join(gagnants)}")
    input("<enter> pour la prochaine partie")
    clear()
        