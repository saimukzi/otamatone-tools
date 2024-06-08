import json
import os

PHI = (1+5**0.5)/2 
A4_FREQ = 440
A4_PITCH = 69
EPSILON = 1e-6
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

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

def json_path_to_data(path):
    with open(path, encoding='utf8') as f:
        return json.load(f)
