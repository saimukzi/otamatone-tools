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
        
        self.vision_offset_y = 0

    def screen_tick(self, screen, sec):
        super().screen_tick(screen, sec)

        self.draw_note_rail(screen, self.vision_offset_y)

        matric_screen_size = self.matric_screen_size
        ticks_per_beat = self.matric_ticks_per_beat
        
        play_tick_itr = map(lambda i:i*ticks_per_beat,self.runtime.play_beat_list)
        play_y0_list  = list(map(lambda i:round(self.tick_to_y(i,self.vision_offset_y)),play_tick_itr))

        x0 = self.matric_note_rail_x0 - self.matric_cell_width
        x1 = self.matric_note_rail_x0 - self.matric_cell_width // 2
        x2 = self.matric_note_rail_x1 + self.matric_cell_width // 2
        x3 = self.matric_note_rail_x1 + self.matric_cell_width
        y0 = - self.matric_line1_width // 2
        
        c00,c01=63,127
        c10,c11=127,191
        screen.fill(
            rect=(x0,play_y0_list[0]+y0,x3-x0,self.matric_line1_width),
            color=(c00,c01,c00),
        )

        screen.fill(
            rect=(x1,play_y0_list[1]+y0,x2-x1,self.matric_line1_width),
            color=(c10,c11,c10),
        )

        screen.fill(
            rect=(x0,play_y0_list[3]+y0,x3-x0,self.matric_line1_width),
            color=(c01,c00,c00),
        )

        screen.fill(
            rect=(x1,play_y0_list[2]+y0,x2-x1,self.matric_line1_width),
            color=(c11,c10,c10),
        )


    def event_tick(self, event, sec):
        # print(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.runtime.state_pool.set_active('PLAY')
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RCTRL:
            self.rctrl_down = True
        if event.type == pygame.KEYUP and event.key == pygame.K_RCTRL:
            self.rctrl_down = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL:
            self.lctrl_down = True
        if event.type == pygame.KEYUP and event.key == pygame.K_LCTRL:
            self.lctrl_down = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            mouse_screen_y = pygame.mouse.get_pos()[1]
            self.runtime.play_beat_list[0] = self.y_to_beat(mouse_screen_y)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            mouse_screen_y = pygame.mouse.get_pos()[1]
            self.runtime.play_beat_list[1] = self.y_to_beat(mouse_screen_y)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_3:
            mouse_screen_y = pygame.mouse.get_pos()[1]
            self.runtime.play_beat_list[2] = self.y_to_beat(mouse_screen_y)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_4:
            mouse_screen_y = pygame.mouse.get_pos()[1]
            self.runtime.play_beat_list[3] = self.y_to_beat(mouse_screen_y)
        if event.type == pygame.MOUSEWHEEL and not self.is_ctrl_down():
            self.vision_offset_y -= event.y * 60
        if event.type == pygame.MOUSEWHEEL and self.is_ctrl_down():
            mouse_screen_y = pygame.mouse.get_pos()[1]
            mouse_tick = self.y_to_tick(mouse_screen_y, self.vision_offset_y)
        
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

    def on_active(self):
        self.track_data = self.runtime.midi_data['track_list'][0]
        super().on_active()

    def on_midi_update(self):
        self.track_data = self.runtime.midi_data['track_list'][0]
        super().on_midi_update()
        self.vision_offset_y = 0

    def y_to_beat(self,y):
        ret = self.y_to_tick(y, self.vision_offset_y)
        ret /= self.matric_ticks_per_beat
        ret = round(ret)
        return ret
