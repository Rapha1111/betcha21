from random import randint
def cards():
  card=(list("23456789VDRA")+["10"])*4
  pak=[]
  while len(card)>0:
    n=randint(0,len(card)-1)
    pak.append(card[n])
    del card[n]
  return pak

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

