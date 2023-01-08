import common
import math
import pygame
import null_state
from PIL import Image, ImageDraw

PITCH_A4 = 69

class EditState(null_state.NullState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'EDIT'

        self.ui_cell_width = 64
        self.ui_line0_width = 2
        self.ui_line1_width = 4

        self.vision_offset_y = 0

    def screen_tick(self, screen, sec):
        screen.fill((255,255,255))
        
        for matric_note_rail_bg_rect_data in self.matric_note_rail_bg_rect_data_list:
            #pygame.draw.rect(screen, matric_note_rail_bg_rect_data['color'], matric_note_rail_bg_rect_data['rect'])
            screen.fill(**matric_note_rail_bg_rect_data)

        for matric_note_rail_pitch_line_data in self.matric_note_rail_pitch_line_data_list:
            screen.fill(**matric_note_rail_pitch_line_data)

        min_tick = self.y_to_tick(-self.ui_cell_width)
        max_tick = self.y_to_tick(self.matric_screen_size[1]+self.ui_cell_width)
        track_data = self.runtime.midi_data['track_list'][0]
        noteev_list = track_data['noteev_list']
        noteev_list = filter(lambda i:i['type']=='on',noteev_list)
        noteev_list = filter(lambda i:i['tick1']>min_tick,noteev_list)
        noteev_list = filter(lambda i:i['tick0']<max_tick,noteev_list)
        noteev_list = list(noteev_list)
        for noteev in noteev_list:
            pitch = noteev['pitch']
            x = self.pitch_to_x(noteev['pitch'])
            y = self.tick_to_y(noteev['tick0'])
            p = (pitch + 300 - PITCH_A4) % 4
            if p in self.matric_note_img_data_dict:
                matric_note_img_data = self.matric_note_img_data_dict[p]
                screen.blit(
                    source=matric_note_img_data['surface'],
                    dest=(x+matric_note_img_data['offset_x'],y+matric_note_img_data['offset_y']),
                )

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
        self.matric_cell_width_phii = self.ui_cell_width / common.PHI

        self.matric_max_pitch = track_data['max_pitch'] + 2
        self.matric_min_pitch = track_data['min_pitch'] - 2
        pitch_diff = self.matric_max_pitch - self.matric_min_pitch
        self.matric_note_rail_x0 = (screen_size[0]-pitch_diff*self.ui_cell_width//4)//2

        self.matric_note_rail_bg_rect_data_list = []
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
            x1 = self.matric_note_rail_x0 + (self.matric_max_pitch-pitch )*self.ui_cell_width // 4
            x0 = self.matric_note_rail_x0 + (self.matric_max_pitch-pitch1)*self.ui_cell_width // 4
            c = pitch
            c += 300
            c -= PITCH_A4
            c %= 12
            c //= 4
            c = (255,246,246) if c == 0 else \
                    (246,255,246) if c == 1 else \
                    (246,246,255)
            self.matric_note_rail_bg_rect_data_list.append({
                'rect':(x0,0,x1-x0,screen_size[1]),
                'color':c,
            })
            pitch = pitch1

        self.matric_note_rail_pitch_line_data_list = []
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
            # self.matric_note_rail_pitch_line_data_list.append({
            #     'start_pos': (x, 0),
            #     'end_pos':   (x, screen_size[1]),
            #     'color':     (c,c,c),
            #     'width':     w,
            # })
            self.matric_note_rail_pitch_line_data_list.append({
                'rect':  (x-w//2,0,w,screen_size[1]),
                'color': (c,c,c),
            })
            pitch += 4

        self.matric_y0 = math.floor(self.ui_cell_width*common.PHI)

        self.matric_note_img_data_dict = {}

        self.matric_note_img_data_dict[0] = {}
        with Image.new('RGBA', (self.ui_cell_width*4,self.ui_cell_width*4), (255,255,255,0)) as pil_img4:
            pil_draw = ImageDraw.Draw(pil_img4)
            xy0 = math.floor((self.ui_cell_width-self.matric_cell_width_phii)*2)
            xy1 = math.ceil((self.ui_cell_width+self.matric_cell_width_phii)*2)
            pil_draw.line((xy0,xy0,xy1,xy1),fill=(0,0,0,255),width=self.ui_line1_width*4)
            pil_draw.line((xy0,xy1,xy1,xy0),fill=(0,0,0,255),width=self.ui_line1_width*4)
            with pil_img4.resize((self.ui_cell_width,self.ui_cell_width)) as pil_img:
                img_data = pil_img.tobytes()
                pyg_img = pygame.image.fromstring(img_data, (self.ui_cell_width,self.ui_cell_width), pil_img.mode)
        self.matric_note_img_data_dict[0]['surface'] = pyg_img
        self.matric_note_img_data_dict[0]['offset_x'] = -self.ui_cell_width//2
        self.matric_note_img_data_dict[0]['offset_y'] = -self.ui_cell_width//2

        self.matric_note_img_data_dict[1] = {}
        x1 = self.ui_cell_width * 7 // 8
        with Image.new('RGBA', (self.ui_cell_width*4,self.ui_cell_width*4), (255,255,255,0)) as pil_img4:
            pil_draw = ImageDraw.Draw(pil_img4)
            x41 = x1 * 4
            x40 = math.floor((x1-self.matric_cell_width_phii)*4)
            y40 = math.floor((self.ui_cell_width-self.matric_cell_width_phii)*2)
            y41 = math.floor(self.ui_cell_width*2)
            y42 = math.ceil((self.ui_cell_width+self.matric_cell_width_phii)*2)
            p40,p41,p42 = (x40,y40),(x41,y41),(x40,y42)
            pil_draw.line((p40,p41,p42,p40),fill=(0,0,0,255),width=self.ui_line1_width*4)
            with pil_img4.resize((self.ui_cell_width,self.ui_cell_width)) as pil_img:
                img_data = pil_img.tobytes()
                pyg_img = pygame.image.fromstring(img_data, (self.ui_cell_width,self.ui_cell_width), pil_img.mode)
        self.matric_note_img_data_dict[1]['surface'] = pyg_img
        self.matric_note_img_data_dict[1]['offset_x'] = -x1+self.ui_cell_width//4
        self.matric_note_img_data_dict[1]['offset_y'] = -self.ui_cell_width//2

        self.matric_note_img_data_dict[2] = {}
        with Image.new('RGBA', (self.ui_cell_width*4,self.ui_cell_width*4), (255,255,255,0)) as pil_img4:
            pil_draw = ImageDraw.Draw(pil_img4)
            xy0 = math.floor((self.ui_cell_width-self.matric_cell_width_phii)*2)
            xy1 = math.ceil((self.ui_cell_width+self.matric_cell_width_phii)*2)
            pil_draw.ellipse((xy0,xy0,xy1,xy1),outline=(0,0,0,255),width=self.ui_line1_width*4)
            with pil_img4.resize((self.ui_cell_width,self.ui_cell_width)) as pil_img:
                img_data = pil_img.tobytes()
                pyg_img = pygame.image.fromstring(img_data, (self.ui_cell_width,self.ui_cell_width), pil_img.mode)
        self.matric_note_img_data_dict[2]['surface'] = pyg_img
        self.matric_note_img_data_dict[2]['offset_x'] = -self.ui_cell_width//2
        self.matric_note_img_data_dict[2]['offset_y'] = -self.ui_cell_width//2

        self.matric_note_img_data_dict[3] = {}
        x0 = self.ui_cell_width * 1 // 8
        with Image.new('RGBA', (self.ui_cell_width*4,self.ui_cell_width*4), (255,255,255,0)) as pil_img4:
            pil_draw = ImageDraw.Draw(pil_img4)
            x40 = x0 * 4
            x41 = math.floor((x0+self.matric_cell_width_phii)*4)
            y40 = math.floor((self.ui_cell_width-self.matric_cell_width_phii)*2)
            y41 = math.floor(self.ui_cell_width*2)
            y42 = math.ceil((self.ui_cell_width+self.matric_cell_width_phii)*2)
            p40,p41,p42 = (x41,y40),(x40,y41),(x41,y42)
            pil_draw.line((p40,p41,p42,p40),fill=(0,0,0,255),width=self.ui_line1_width*4)
            with pil_img4.resize((self.ui_cell_width,self.ui_cell_width)) as pil_img:
                img_data = pil_img.tobytes()
                pyg_img = pygame.image.fromstring(img_data, (self.ui_cell_width,self.ui_cell_width), pil_img.mode)
        self.matric_note_img_data_dict[3]['surface'] = pyg_img
        self.matric_note_img_data_dict[3]['offset_x'] = -x0-self.ui_cell_width//4
        self.matric_note_img_data_dict[3]['offset_y'] = -self.ui_cell_width//2

    def pitch_to_x(self,pitch):
        return self.matric_note_rail_x0 + (self.matric_max_pitch-pitch )*self.ui_cell_width // 4

    def tick_to_y(self,tick):
        ret = tick
        ret /= self.runtime.midi_data['ticks_per_beat']
        ret *= self.ui_cell_width
        ret -= self.vision_offset_y
        ret += self.matric_y0
        return ret

    def y_to_tick(self,y):
        ret = y
        ret -= self.matric_y0
        ret += self.vision_offset_y
        ret /= self.ui_cell_width
        ret *= self.runtime.midi_data['ticks_per_beat']
        return ret
