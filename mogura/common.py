PHI = (1+5**0.5)/2 

def anchor(xy, size, anc):
    x,y = xy
    width,height = size
    dx = anc % 3
    dx = (-width)    if dx==0 else \
         (-width//2) if dx==2 else \
         0
    dy = (anc-1)//3
    dy = (-height)    if dy==0 else \
         (-height//2) if dy==1 else \
         0
    return (x+dx,y+dy)
