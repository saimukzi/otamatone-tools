import common
import pygame

TEXT_LIFE_TICK = 300

# tsc = text,size,color

class TextDraw:

    def __init__(self):
        # once init, do not free
        self.size_to_font_data_dict = {}

        # free in TEXT_LIFE_TICK
        self.tsc_to_surface_data_dict = {}

        self.tick = 0

    def on_tick_start(self):
        self.tick += 1

        rm_keys = self.tsc_to_surface_data_dict.items()
        rm_keys = filter(lambda kv:kv[1]['timeout_tick']<=self.tick, rm_keys)
        rm_keys = map(lambda kv:kv[0], rm_keys)
        rm_keys = list(rm_keys)
        for k in rm_keys:
            del self.tsc_to_surface_data_dict[k]

    def draw(self, surface, text, size, color, xy, anchor):
        text_surface = self._get_surface(text, size, color)
        xy = common.anchor(xy, text_surface.get_size(), anchor)
        surface.blit(text_surface,xy)
    
    def _get_surface(self, text, size, color):
        tsc = (text, size, color)
        if tsc not in self.tsc_to_surface_data_dict:
            font = self._get_font(size)
            surface = font.render(text, True, color)
            data = {
                'surface': surface,
            }
            self.tsc_to_surface_data_dict[tsc] = data
        ret = self.tsc_to_surface_data_dict[tsc]
        ret['timeout_tick'] = self.tick+TEXT_LIFE_TICK
        return self.tsc_to_surface_data_dict[tsc]['surface']

    def _get_font(self, size):
        if size not in self.size_to_font_data_dict:
            font = pygame.font.SysFont(None, size)
            data = {
                'font': font,
            }
            self.size_to_font_data_dict[size] = data
        return self.size_to_font_data_dict[size]['font']
