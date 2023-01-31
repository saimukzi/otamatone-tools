import common
import pygame

# ek: element key
# em: element

class Gui:

    def __init__(self):
        self.ek_to_em_dict = {}
        self.layer_to_ek_set_dict = {}
        self.active_ek_set = set()

    def add_button(self, ek, img, xy, anchor, layer):
        if ek in self.ek_to_em_dict:
            em = self.ek_to_em_dict[ek]
            _layer = em['layer']
            del self.ek_to_em_dict[ek]
            self.layer_to_ek_set_dict[_layer].remove(ek)

        blit_xy = common.anchor(xy, img.get_size(), anchor)
        em = {
            'type':'button',
            'blit':{
                'source': img,
                'dest': blit_xy,
            },
            'rect':blit_xy+img.get_size(),
            'layer':layer,
            'ek':ek,
        }
        self.ek_to_em_dict[ek] = em
        if layer not in self.layer_to_ek_set_dict:
            self.layer_to_ek_set_dict[layer] = set()
        self.layer_to_ek_set_dict[layer].add(ek)

    def draw_layer(self, surface, layer):
        if layer not in self.layer_to_ek_set_dict: pass
        em_list = self.layer_to_ek_set_dict[layer]
        em_list = map(self.ek_to_em_dict.get, em_list)
        for em in em_list:
            surface.blit(**em['blit'])

    def on_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            ek_list = self.ek_to_em_dict.values()
            ek_list = filter(lambda i:i['type']=='button', ek_list)
            ek_list = filter(in_rect_func(event.pos), ek_list)
            ek_list = map(lambda i:i['ek'], ek_list)
            ek_list = set(ek_list)
            self.active_ek_set |= ek_list

    def is_btn_active(self, ek):
        if ek in self.active_ek_set:
            self.active_ek_set.remove(ek)
            return True
        return False

def in_rect_func(xy):
    def ret_f(em):
        rect = em['rect']
        if xy[0] < rect[0]: return False
        if xy[1] < rect[1]: return False
        if xy[0] >= rect[0]+rect[2]: return False
        if xy[1] >= rect[1]+rect[3]: return False
        return True
    return ret_f
