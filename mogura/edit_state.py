import common
import math
import pygame
import null_state

PITCH_A4 = 69

class EditState(null_state.NullState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'EDIT'

        self.ui_cell_width = 64
        self.ui_line0_width = 2
        self.ui_line1_width = 4

    def screen_tick(self, screen, sec):
        screen.fill((255,255,255))
        
        for matric_note_bar_bg_rect_data in self.matric_note_bar_bg_rect_data_list:
            pygame.draw.rect(screen, matric_note_bar_bg_rect_data['color'], matric_note_bar_bg_rect_data['rect'])

        for matric_note_bar_pitch_line_data in self.matric_note_bar_pitch_line_data_list:
            pygame.draw.line(screen, **matric_note_bar_pitch_line_data)
        
        pygame.display.flip()

    def event_tick(self, event, sec):
        pass

    def on_active(self):
        self.update_ui_matrice()

    def on_screen_change(self, screen_size):
        self.update_ui_matrice()

    def update_ui_matrice(self):
        screen_size = pygame.display.get_window_size()
        midi_data = self.runtime.midi_data
        track_data = midi_data['track_list'][0]

        self.matric_screen_size = screen_size
        self.matric_cell_width_phii = self.ui_cell_width // common.PHI

        self.matric_max_pitch = track_data['max_pitch'] + 2
        self.matric_min_pitch = track_data['min_pitch'] - 2
        pitch_diff = self.matric_max_pitch - self.matric_min_pitch
        self.matric_note_bar_x0 = (screen_size[0]-pitch_diff*self.ui_cell_width//4)//2

        self.matric_note_bar_bg_rect_data_list = []
        pitch = self.matric_min_pitch
        while pitch < self.matric_max_pitch:
            pitch1 = pitch
            pitch1 += 300
            pitch1 -= PITCH_A4
            pitch1 //= 4
            pitch1 += 1
            pitch1 *= 4
            pitch1 += PITCH_A4
            pitch1 -= 300
            pitch1 = min(pitch1,self.matric_max_pitch)
            x1 = self.matric_note_bar_x0 + (self.matric_max_pitch-pitch )*self.ui_cell_width // 4
            x0 = self.matric_note_bar_x0 + (self.matric_max_pitch-pitch1)*self.ui_cell_width // 4
            c = pitch
            c += 300
            c -= PITCH_A4
            c %= 12
            c //= 4
            c = (255,246,246) if c == 0 else \
                    (246,255,246) if c == 1 else \
                    (246,246,255)
            self.matric_note_bar_bg_rect_data_list.append({
                'rect':(x0,0,x1-x0,screen_size[1]),
                'color':c,
            })
            pitch = pitch1

        self.matric_note_bar_pitch_line_data_list = []
        pitch = self.matric_min_pitch
        pitch += 300
        pitch -= PITCH_A4
        pitch /= 4
        pitch = math.ceil(pitch)
        pitch *= 4
        pitch += PITCH_A4
        pitch -= 300
        while pitch <= self.matric_max_pitch:
            p = pitch
            p += 300
            p -= PITCH_A4
            p %= 12
            c,w = (128,self.ui_line1_width) if p == 0 else (192,self.ui_line0_width)
            x = self.pitch_to_x(pitch)
            self.matric_note_bar_pitch_line_data_list.append({
                'start_pos': (x, 0),
                'end_pos':   (x, screen_size[1]),
                'color':     (c,c,c),
                'width':     w,
            })
            pitch += 4

    def pitch_to_x(self,pitch):
        return self.matric_note_bar_x0 + (self.matric_max_pitch-pitch )*self.ui_cell_width // 4
