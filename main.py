import pygame
import socket, os,json
def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
pygame.init()
screen = pygame.display.set_mode((1000,558))

clear()
print("Loading textures...")
t=[str(i) for i in range(2,11)]+["A","V","D","R","call","dos","fold","folded","hit","last_raiser","more","stand","turn","you"]
textures={i:pygame.image.load("img/"+i+".png").convert_alpha() for i in t}
print("Textures Loaded !")
#HOST = input("ip : ")
#PORT = int(input("port : "))

font = pygame.font.Font(None, 50)
def draw_string(t,x,y,c="black",cf=""):
    text_surface = font.render(t, True, c)
    screen.blit(text_surface, (x, y))
def draw_img(img, x, y, w, h):
    image = pygame.transform.scale(textures[img], (w, h))
    screen.blit(image, (x, y))    

def update_screen(player_nbr, my_cards, my_score, my_money, cards, player_turn, last_act):
    screen.fill((0,150,0))
    draw_string("Argent : "+str(my_money), 10, 508)
    for i in range(4):
        a=0
        if i==0:
            sx,sy=100,250
        elif i==1:
            sx,sy=500,100
        elif i==2:
            sx,sy=900,250
            a=280
        else:
            sx,sy=500,400
        if i == player_turn:
            draw_img("turn", sx+80-a, sy, 100, 40)
        if last_act[i]>0:
            la=["#", "hit", "stand", "folded"]
            draw_img(la[last_act[i]], sx+80-a, sy+45, 100, 40)
        if i == player_nbr:
            draw_img("you", sx-50, sy-45, 100, 40)
            for l in range(len(my_cards)):
                draw_img(my_cards[l], sx-75+l*90/len(my_cards), sy, 60, 100)
            draw_string("Score : "+str(my_score), sx-70, sy+105)
        else:
            for l in range(cards[i]):
                draw_img("dos", sx-75+l*90/cards[i], sy, 60, 100)

    pygame.display.flip()

#LASTACT : 0 = None, 1 = HIT, 2 = STAND, 3 = FOLD

update_screen(0, ["10","A", "2", "3", "6"], 18, 100, [2,2,3,2], 2, [1, 2, 3, 1])
input()
"""
# connexion
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print(f"[+] Connecté à {HOST}:{PORT}")


try:
    while True:
        data = client.recv(1024)
        if not data:
            print("[-] Déconnecté du serveur")
            break
        
        message = data.decode("utf-8").strip()
        
        # si le message commence par ask:, on demande une réponse à l'utilisateur
        if "ask:" in message:
            question = message.replace("ask:","")
            answer = input(question)
            client.send(answer.encode("utf-8"))
            clear()
        else:
            print(message)

except KeyboardInterrupt:
    print("\n[!] Fermeture du client.")

finally:
    client.close()
"""