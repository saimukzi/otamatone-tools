import common

# ek: element key
# em: element

class Gui:

    def __init__(self):
        self.ek_to_em_dict = {}
        self.layer_to_ek_set_dict = {}

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
            'rect':xy+img.get_size(),
            'layer':layer,
            'ek':ek,
        }
        self.ek_to_em_dict[ek] = em
        if layer not in self.layer_to_ek_set_dict:
            self.layer_to_ek_set_dict[layer] = Set()
        self.layer_to_ek_set_dict[layer].add(ek)

    def draw_layer(self, surface, layer):
        if layer not in self.layer_to_ek_set_dict: pass
        em_list = self.layer_to_ek_set_dict[layer]
        em_list = map(self.ek_to_em_dict.get, em_list)
        for em in em_list:
            surface.blit(**em['blit'])
