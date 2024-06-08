import common
import pygame
import os
from PIL import Image, ImageDraw

# def plus_btn_img():
#     SIZE,M = 32,4
#     SIZEM = SIZE*M
#     with Image.new('RGBA', (SIZEM,SIZEM), (0,0,0,0)) as pil_img4:
#         pil_draw = ImageDraw.Draw(pil_img4)
#         xy0 = 1*M
#         xy1 = SIZEM-xy0-1
#         w4 = 4*M
#         pil_draw.ellipse((xy0,xy0,xy1,xy1),outline=(0,0,0,255),width=w4)
#         x0 = 7*M
#         x1 = SIZEM-x0-1
#         y0 = (SIZEM//2)-2*M
#         y1 = (SIZEM//2)+2*M-1
#         pil_draw.rectangle((x0,y0,x1,y1),fill=(0,0,0,255))
#         pil_draw.rectangle((y0,x0,y1,x1),fill=(0,0,0,255))
#         with pil_img4.resize((SIZE,SIZE)) as pil_img:
#             img_data = pil_img.tobytes()
#             return pygame.image.fromstring(img_data, (SIZE,SIZE), pil_img.mode)

def load_img(fn):
    ret = pygame.image.load(os.path.join(common.PROJECT_PATH, 'img', fn))
    ret = pygame.Surface.convert_alpha(ret)
    return ret

def plus_btn_img():
    return load_img('plus_btn.svg')
    # return pygame.image.load(os.path.join(common.PROJECT_PATH, 'img', 'plus_btn.svg'))

# def minus_btn_img():
#     SIZE,M = 32,4
#     SIZEM = SIZE*M
#     with Image.new('RGBA', (SIZEM,SIZEM), (0,0,0,0)) as pil_img4:
#         pil_draw = ImageDraw.Draw(pil_img4)
#         xy0 = 1*M
#         xy1 = SIZEM-xy0-1
#         w4 = 4*M
#         pil_draw.ellipse((xy0,xy0,xy1,xy1),outline=(0,0,0,255),width=w4)
#         x0 = 7*M
#         x1 = SIZEM-x0-1
#         y0 = (SIZEM//2)-2*M
#         y1 = (SIZEM//2)+2*M-1
#         pil_draw.rectangle((x0,y0,x1,y1),fill=(0,0,0,255))
#         with pil_img4.resize((SIZE,SIZE)) as pil_img:
#             img_data = pil_img.tobytes()
#             return pygame.image.fromstring(img_data, (SIZE,SIZE), pil_img.mode)

def minus_btn_img():
    return load_img('minus_btn.svg')
    # return pygame.image.load(os.path.join(common.PROJECT_PATH, 'img', 'minus_btn.svg'))

# def zero_btn_img():
#     SIZE,M = 32,4
#     SIZEM = SIZE*M
#     with Image.new('RGBA', (SIZEM,SIZEM), (0,0,0,0)) as pil_img4:
#         pil_draw = ImageDraw.Draw(pil_img4)
#         xy0 = 1*M
#         xy1 = SIZEM-xy0-1
#         w4 = 4*M
#         pil_draw.ellipse((xy0,xy0,xy1,xy1),outline=(0,0,0,255),width=w4)

#         xy0 = 8*M
#         xy1 = SIZEM-xy0-1
#         w4 = 4*M
#         pil_draw.ellipse((xy0,xy0,xy1,xy1),outline=(0,0,0,255),width=w4)

#         with pil_img4.resize((SIZE,SIZE)) as pil_img:
#             img_data = pil_img.tobytes()
#             return pygame.image.fromstring(img_data, (SIZE,SIZE), pil_img.mode)

def zero_btn_img():
    return load_img('zero_btn.svg')
    # return pygame.image.load(os.path.join(common.PROJECT_PATH, 'img', 'zero_btn.svg'))

def max_btn_img():
    return load_img('max_btn.svg')
    # return pygame.image.load(os.path.join(common.PROJECT_PATH, 'img', 'max_btn.svg'))
