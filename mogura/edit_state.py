import common
import math
import pygame
import note_state
from PIL import Image, ImageDraw

PITCH_A4 = 69

class EditState(note_state.NoteState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'EDIT'
        self.rctrl_down = False
        self.lctrl_down = False

    def screen_tick(self, screen, sec):
        super().screen_tick(screen, sec)

    def event_tick(self, event, sec):
        # print(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RCTRL:
            self.rctrl_down = True
        if event.type == pygame.KEYUP and event.key == pygame.K_RCTRL:
            self.rctrl_down = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL:
            self.lctrl_down = True
        if event.type == pygame.KEYUP and event.key == pygame.K_LCTRL:
            self.lctrl_down = False
        if event.type == pygame.MOUSEWHEEL and not self.is_ctrl_down():
            self.vision_offset_y -= event.y * 60
        if event.type == pygame.MOUSEWHEEL and self.is_ctrl_down():
            mouse_screen_y = pygame.mouse.get_pos()[1]
            mouse_tick = self.y_to_tick(mouse_screen_y)
        
            self.runtime.ui_zoom_level += event.y
            self.runtime.ui_zoom_level = max(self.runtime.ui_zoom_level,4)
            self.runtime.ui_zoom_level = min(self.runtime.ui_zoom_level,16)

            self.update_ui_matrice()

            vision_offset_y = mouse_tick
            vision_offset_y /= self.matric_ticks_per_beat
            vision_offset_y *= self.matric_cell_width
            vision_offset_y -= mouse_screen_y
            vision_offset_y += self.matric_y0
            self.vision_offset_y = vision_offset_y

    def is_ctrl_down(self):
        return self.rctrl_down or self.lctrl_down

    def on_midi_update(self):
        super().on_midi_update()
        self.vision_offset_y = 0
