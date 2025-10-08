import pygame
import socket, os,json
def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
clear()
pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()

clock = pygame.time.Clock()
clear()
print("Loading textures...")
t=[str(i) for i in range(2,11)]+["A","V","D","R","call","dos","fold","folded","hit","last_raiser","more","stand","turn","you", "pot"]
textures={i:pygame.image.load("img/"+i+".png").convert_alpha() for i in t}
pygame.display.set_caption("Betcha21")
pygame.display.set_icon(textures["dos"])
print("Textures Loaded !")

def score(a):
  _as=0
  s=0
  for i in a:
    try:
      n=int(i)
      s+=n
    except:
      if i=="A":
        s+=1
        _as+=1
      else:
        s+=10
  while s<12 and _as>0:
    s+=10
    _as-=1
  return s


def input_box(prompt=">", x=400, y=300, numeric=True):
    font = pygame.font.Font(None, 50)
    box = pygame.Rect(x*1.5, y*1.5, 300, 50)
    color_inactive = pygame.Color('gray')
    color_active = pygame.Color('white')
    color = color_active
    text = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return ""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif not numeric or event.unicode.isdigit() or event.unicode == '.':
                    text += event.unicode

        screen.fill((0,150,0))
        draw_string(prompt, x-250, y+10, "white")
        pygame.draw.rect(screen, color, box, 2)
        txt = font.render(text, True, color)
        screen.blit(txt, ((box.x+10), (box.y+5)))
        pygame.display.flip()





font = pygame.font.Font(None, 50)
def draw_string(t,x,y,c="black"):
    text_surface = font.render(t, True, c)
    screen.blit(text_surface, (x*width/1000, y*height/558))
def draw_img(img, x, y, w, h):
    image = pygame.transform.scale(textures[img], (w*width/1000, h*height/558))
    screen.blit(image, (x*width/1000, y*height/558))    
def keydown(k):
  keys = pygame.key.get_pressed()
  if keys[k]:
    return True
  return False
def update_screen(player_nbr, my_cards, my_score, my_money, cards, player_turn, last_act, last_raiser, pot, mise, max_player, tour, act, pseudos):
    screen.fill((0,150,0))
    draw_string("Tour : "+str(tour)+"/4", 10, 438)
    draw_string("Argent : "+str(my_money), 10, 478)
    draw_string("Mise : "+str(mise), 10, 518)
    draw_img("dos", 400, 250, 60, 100)
    draw_img("pot", 500, 250, 100, 75)
    draw_string(str(pot), 530, 275, "white") 
    for i in range(4):
        if i >= max_player:
            break
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
        elif i==last_raiser:
            draw_img("last_raiser", sx+80-a, sy, 100, 40)
        if last_act[i]>0:
            la=["#", "hit", "stand", "folded"]
            draw_img(la[last_act[i]], sx+80-a, sy+45, 100, 40)
        if i == player_nbr:
            draw_img("you", sx-50, sy-45, 100, 40)
            for l in range(len(my_cards)):
                draw_img(my_cards[l], sx-75+l*90/len(my_cards), sy, 60, 100)
            draw_string("Score : "+str(my_score), sx-70, sy+105)
        else:
            draw_string(pseudos[i], sx-50,sy-45)
            if type(cards[0])==type([]):
                for l in range(len(cards[i])):
                    draw_img(cards[i][l], sx-75+l*90/len(cards[i]), sy, 60, 100)
                draw_string("Score : "+str(score(cards[i])), sx-70, sy+105)
            else:
                for l in range(cards[i]):
                    draw_img("dos", sx-75+l*90/cards[i], sy, 60, 100)
    if act=="hit/stand":
        draw_string("Action : (H)it/(S)tand", 350, 370, "white")
    elif act=="call/fold":
        draw_string("Action : (C)all/(R)aise/(F)old", 300, 370, "white")
    elif act[0]=="W":
        draw_string(act, 300, 370, "white")
    pygame.display.flip()


# connexion
HOST = input_box("ip : ", y=200,numeric=False)
if HOST[0:2]=="n:":
    HOST=HOST[2]+".tcp.ngrok.io"
    PORT = int(input_box("port : ", y=200))
elif HOST=="":
    HOST="localhost"
    PORT=5000
else:
    PORT = int(input_box("port : ", y=500))
pseudo=input_box("pseudo", numeric=False)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.setblocking(False)
print(f"[+] Connecté à {HOST}:{PORT}")
player_nbr, my_cards, my_score, my_money, cards, player_turn, last_act, last_raiser, pot, mise, max_player,tour, act, pseudos=0,[],0,10000,[2,2,2,2],0,[0,0,0,0],-1,0,0,0,0,"#",[]
client.send(pseudo.encode())
running=True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
    try:
        data = client.recv(1024)
        if not data:
            print("[-] Déconnecté du serveur")
            break
        message = json.loads("["+data.decode().replace("}{","},{")+"]")
        for msg in message:
            if msg["msg"]=="place":
                player_nbr, my_cards, my_score, my_money, cards, player_turn, last_act, last_raiser, pot, mise, max_player, tour, act, pseudos=msg["nbr"],msg["cards"],msg["score"],msg["argent"],[2,2,2,2],0,[0,0,0,0],-1,msg["pot"],10,msg["max"],0,"#",msg["names"]
                print("\n\nNouelle manche")
                print('Participants : '+", ".join(pseudos))
            elif msg["msg"]=="player_turn":
                player_turn=msg["player"]
                print(f"====Tour de Player {msg["player"]}====")
            elif msg["msg"]=="your_turn":
                my_cards=msg["cards"]
                my_score=msg["score"]
            elif msg["msg"]=="hit":
                cards[msg["player"]]+=1
                last_act[msg["player"]]=1
                print(f"==> Player {msg["player"]} hit")
            elif msg["msg"]=="stand":
                last_act[msg["player"]]=2
                print(f"==> Player {msg["player"]} stand")
            elif msg["msg"]=="fold":
                last_act[msg["player"]]=3
                print(f"==> Player {msg["player"]} fold")
            elif msg["msg"]=="more":
                last_raiser=msg["player"]
                print(f"==> Player {msg["player"]} raise up")
            elif msg["msg"]=="update_details":
                mise=msg["mise"]
                pot=msg["pot"]
                cards[msg["player"]]=msg["nbr_card"]
                print(f"Pot : {msg["pot"]}")
            elif msg["msg"]=="action":
                act=msg["ask"]
            elif msg["msg"]=="winner":
                act="Winner : "+", ".join([str(int(i)+1) for i in msg["players"]])
                cards=msg["cards"]
            elif msg["msg"]=="waitfor":
                act="Waiting for the next game..."
            elif msg["msg"]=="new_turn":
                tour=msg["turn"]
            elif msg["msg"]=="setmoney":
                my_money=msg["money"]
            
    except BlockingIOError:
        pass  # aucun message dispo, on continue
    if act=="hit/stand":
        if keydown(pygame.K_h):
            client.send("1".encode())
            act="#"
        elif keydown(pygame.K_s):
            client.send("2".encode())
            act="#"
    elif act=="call/fold":
        if keydown(pygame.K_c):
            client.send("call".encode())
            act="#"
        elif keydown(pygame.K_r):
            many=(input_box("Mise : "))
            client.send(("more"+many).encode())
            act="#"
        elif keydown(pygame.K_f):
            client.send("fold".encode())
            act="#"
        
    update_screen(player_nbr, my_cards, my_score, my_money, cards, player_turn, last_act, last_raiser, pot, mise, max_player, tour, act, pseudos)
    clock.tick(60)
client.close()