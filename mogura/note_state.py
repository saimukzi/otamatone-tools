import common
import copy
import math
import midi_data
import pygame
import null_state
from PIL import Image, ImageDraw

PITCH_C4 = 72

class NoteState(null_state.NullState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'NOTE'

        #self.vision_offset_y = 0


    def draw_note_rail(self, screen, vision_offset_y):
        draw_session = self.get_draw_session(screen, vision_offset_y)
        self.draw_color_note_rail_bg(draw_session)
        self.draw_note_length(draw_session)
        self.draw_time_horizontal_line_thin(draw_session)
        self.draw_note_rail_ppitch_line(draw_session)
        self.draw_time_horizontal_line_thick(draw_session)
        self.draw_note_signal(draw_session)

    def get_draw_session(self, screen, vision_offset_y):
        track_data = self.matric_track_data
        ticks_per_beat = self.matric_ticks_per_beat
        min_tick = math.floor(self.y_to_tick(-self.matric_cell_width,vision_offset_y))
        max_tick = math.ceil(self.y_to_tick(self.matric_screen_size[1]+self.matric_cell_width,vision_offset_y))

        draw_session = {
            'screen': screen,
            'track_data': track_data,
            'ticks_per_beat': ticks_per_beat,
            'vision_offset_y': vision_offset_y,
            'min_tick': min_tick,
            'max_tick': max_tick,
        }

        return draw_session

    def draw_color_note_rail_bg(self, draw_session):
        screen = draw_session['screen']
        for matric_note_rail_bg_rect_data in self.matric_note_rail_bg_rect_data_list:
            #pygame.draw.rect(screen, matric_note_rail_bg_rect_data['color'], matric_note_rail_bg_rect_data['rect'])
            screen.fill(**matric_note_rail_bg_rect_data)

    def draw_note_length(self, draw_session):
        screen = draw_session['screen']
        track_data = draw_session['track_data']
        vision_offset_y = draw_session['vision_offset_y']
        min_tick = draw_session['min_tick']
        max_tick = draw_session['max_tick']

        noteev_list = track_data['noteev_list']
        noteev_list = filter(lambda i:i['type']=='on',noteev_list)
        noteev_list = filter(lambda i:i['tick1']>min_tick,noteev_list)
        noteev_list = filter(lambda i:i['tick0']<max_tick,noteev_list)
        noteev_list = list(noteev_list)
        c,e = 0xcc, 0xdd
        d = (c+e)//2
        CC = [
            (e,c,c,e),
            (e,d,c,e),
            (e,e,c,e),
            (d,e,c,e),
            (c,e,c,e),
            (c,e,d,e),
            (c,e,e,e),
            (c,d,e,e),
            (c,c,e,e),
            (d,c,e,e),
            (e,c,e,e),
            (e,c,d,e),
        ]
        for noteev in noteev_list:
            ppitch = noteev['ppitch']
            x = self.ppitch_to_x(noteev['ppitch'])
            x0 = x-self.matric_cell_width//8
            x1 = x+self.matric_cell_width//8
            y0 = round(noteev['y0']-vision_offset_y+self.matric_y0)
            y0 = max(y0,0)
            y1 = round(noteev['y1']-vision_offset_y+self.matric_y0)
            cc = (ppitch+4+300-PITCH_C4)%12
            cc = CC[cc]
            screen.fill(
                rect=(x0,y0,x1-x0,y1-y0),
                color=cc,
            )

    def draw_time_horizontal_line_thin(self, draw_session):
        screen = draw_session['screen']
        vision_offset_y = draw_session['vision_offset_y']
        min_tick = draw_session['min_tick']
        max_tick = draw_session['max_tick']
        ticks_per_beat = draw_session['ticks_per_beat']

        y0 = -self.matric_line0_width//2
        y1 = -self.matric_line1_width//2
        w = self.matric_note_rail_x1-self.matric_note_rail_x0
        for tick in midi_data.get_beat_itr(min_tick, ticks_per_beat):
            if tick > max_tick: break
            #print(f'beat tick={tick}')
            y = round(self.tick_to_y(tick,vision_offset_y))
            screen.fill(
                rect=(self.matric_note_rail_x0,y+y0,w,self.matric_line0_width),
                color=(255,255,255,255),
            )

    def draw_note_rail_ppitch_line(self, draw_session):
        screen = draw_session['screen']
        for matric_note_rail_ppitch_line_data in self.matric_note_rail_ppitch_line_data_list:
            screen.fill(**matric_note_rail_ppitch_line_data)

    def draw_time_horizontal_line_thick(self, draw_session):
        screen = draw_session['screen']
        track_data = draw_session['track_data']
        vision_offset_y = draw_session['vision_offset_y']
        min_tick = draw_session['min_tick']
        max_tick = draw_session['max_tick']

        y0 = -self.matric_line0_width//2
        y1 = -self.matric_line1_width//2
        w = self.matric_note_rail_x1-self.matric_note_rail_x0
        #print(f'bar min_tick={min_tick}')
        for tick in midi_data.get_bar_itr(min_tick, track_data):
            if tick >= max_tick: break
            #print(f'bar min_tick={min_tick} tick={tick}')
            y = round(self.tick_to_y(tick,vision_offset_y))
            screen.fill(
                rect=(self.matric_note_rail_x0,y+y1,w,self.matric_line1_width),
                color=(128,128,128,255),
            )

    def draw_note_signal(self, draw_session):
        screen = draw_session['screen']
        track_data = draw_session['track_data']
        vision_offset_y = draw_session['vision_offset_y']
        min_tick = draw_session['min_tick']
        max_tick = draw_session['max_tick']

        noteev_list = track_data['noteev_list']
        noteev_list = filter(lambda i:i['type']=='on',noteev_list)
        noteev_list = filter(lambda i:i['tick1']>min_tick,noteev_list)
        noteev_list = filter(lambda i:i['tick0']<max_tick,noteev_list)
        noteev_list = list(noteev_list)
        for noteev in noteev_list:
            ppitch = noteev['ppitch']
            x = self.ppitch_to_x(noteev['ppitch'])
            y0 = round(noteev['y0']-vision_offset_y+self.matric_y0)
            p = (ppitch + 300 - PITCH_C4) % 4
            if p in self.matric_note_img_data_dict:
                matric_note_img_data = self.matric_note_img_data_dict[p]
                screen.blit(
                    source=matric_note_img_data['surface'],
                    dest=(x+matric_note_img_data['offset_x'],y0+matric_note_img_data['offset_y']),
                )

    def event_tick(self, event, sec):
        pass

    def on_active(self):
        self.update_ui_matrice()

    def on_screen_change(self, screen_size):
        self.update_ui_matrice()

    def on_midi_update(self):
        self.update_ui_matrice()

    def on_pitch_update(self):
        self.update_ui_matrice()

    def update_ui_matrice(self):
        screen_size = pygame.display.get_window_size()
        midi_data = self.runtime.midi_data
        #track_data = midi_data['track_list'][0]
        track_data = copy.deepcopy(self.track_data)
        self.matric_track_data = track_data

        self.matric_cell_width = max(round(2 ** (self.runtime.ui_zoom_level/2)),1)
        self.matric_line0_width = max(self.matric_cell_width//32,1)
        self.matric_line1_width = max(self.matric_cell_width//16,1)

        self.matric_screen_size = screen_size
        self.matric_cell_width_phii = self.matric_cell_width / common.PHI

        self.matric_ticks_per_beat = self.runtime.midi_data['ticks_per_beat']

        self.matric_ppitch1 = track_data['ppitch1'] + 2
        self.matric_ppitch0 = track_data['ppitch0'] - 2
        ppitch_diff = self.matric_ppitch1 - self.matric_ppitch0
        self.matric_note_rail_x0 = (screen_size[0]-ppitch_diff*self.matric_cell_width//4)//2
        self.matric_note_rail_x1 = self.matric_note_rail_x0+ppitch_diff*self.matric_cell_width//4

        self.matric_note_rail_bg_rect_data_list = []
        ppitch = self.matric_ppitch0
        while ppitch < self.matric_ppitch1:
            ppitch1 = ppitch
            ppitch1 += 300
            ppitch1 -= PITCH_C4
            ppitch1 //= 4
            ppitch1 += 1
            ppitch1 *= 4
            ppitch1 += PITCH_C4
            ppitch1 -= 300
            ppitch1 = min(ppitch1,self.matric_ppitch1)
            x1 = self.matric_note_rail_x0 + (self.matric_ppitch1-ppitch )*self.matric_cell_width // 4
            x0 = self.matric_note_rail_x0 + (self.matric_ppitch1-ppitch1)*self.matric_cell_width // 4
            c = ppitch
            c += 300
            c -= PITCH_C4
            c %= 12
            c //= 4
            c = (255,246,246) if c == 0 else \
                    (246,255,246) if c == 1 else \
                    (246,246,255)
            self.matric_note_rail_bg_rect_data_list.append({
                'rect':(x0,0,x1-x0,screen_size[1]),
                'color':c,
            })
            ppitch = ppitch1

        self.matric_note_rail_ppitch_line_data_list = []
        ppitch = self.matric_ppitch0
        ppitch += 300
        ppitch -= PITCH_C4
        ppitch /= 4
        ppitch = math.ceil(ppitch)
        ppitch *= 4
        ppitch += PITCH_C4
        ppitch -= 300
        while ppitch <= self.matric_ppitch1:
            p = ppitch
            p += 300
            p -= PITCH_C4
            p %= 12
            c,w = (128,self.matric_line1_width) if p == 0 else (192,self.matric_line0_width)
            x = self.ppitch_to_x(ppitch)
            # self.matric_note_rail_ppitch_line_data_list.append({
            #     'start_pos': (x, 0),
            #     'end_pos':   (x, screen_size[1]),
            #     'color':     (c,c,c),
            #     'width':     w,
            # })
            self.matric_note_rail_ppitch_line_data_list.append({
                'rect':  (x-w//2,0,w,screen_size[1]),
                'color': (c,c,c),
            })
            ppitch += 4

        self.matric_y0 = math.floor(self.matric_cell_width*common.PHI)

        self.matric_note_img_data_dict = {}

        self.matric_note_img_data_dict[0] = {}
        with Image.new('RGBA', (self.matric_cell_width*4,self.matric_cell_width*4), (255,255,255,0)) as pil_img4:
            pil_draw = ImageDraw.Draw(pil_img4)
            xy0 = math.floor((self.matric_cell_width-self.matric_cell_width_phii)*2)
            xy1 = math.ceil((self.matric_cell_width+self.matric_cell_width_phii)*2)
            pil_draw.line((xy0,xy0,xy1,xy1),fill=(0,0,0,255),width=self.matric_line1_width*4)
            pil_draw.line((xy0,xy1,xy1,xy0),fill=(0,0,0,255),width=self.matric_line1_width*4)
            with pil_img4.resize((self.matric_cell_width,self.matric_cell_width)) as pil_img:
                img_data = pil_img.tobytes()
                pyg_img = pygame.image.fromstring(img_data, (self.matric_cell_width,self.matric_cell_width), pil_img.mode)
        self.matric_note_img_data_dict[0]['surface'] = pyg_img
        self.matric_note_img_data_dict[0]['offset_x'] = -self.matric_cell_width//2
        self.matric_note_img_data_dict[0]['offset_y'] = -self.matric_cell_width//2

        self.matric_note_img_data_dict[1] = {}
        x1 = self.matric_cell_width * 7 // 8
        with Image.new('RGBA', (self.matric_cell_width*4,self.matric_cell_width*4), (255,255,255,0)) as pil_img4:
            pil_draw = ImageDraw.Draw(pil_img4)
            x41 = x1 * 4
            x40 = math.floor((x1-self.matric_cell_width_phii)*4)
            y40 = math.floor((self.matric_cell_width-self.matric_cell_width_phii)*2)
            y41 = math.floor(self.matric_cell_width*2)
            y42 = math.ceil((self.matric_cell_width+self.matric_cell_width_phii)*2)
            p40,p41,p42 = (x40,y40),(x41,y41),(x40,y42)
            pil_draw.line((p40,p41,p42,p40),fill=(0,0,0,255),width=self.matric_line1_width*4)
            with pil_img4.resize((self.matric_cell_width,self.matric_cell_width)) as pil_img:
                img_data = pil_img.tobytes()
                pyg_img = pygame.image.fromstring(img_data, (self.matric_cell_width,self.matric_cell_width), pil_img.mode)
        self.matric_note_img_data_dict[1]['surface'] = pyg_img
        self.matric_note_img_data_dict[1]['offset_x'] = -x1+self.matric_cell_width//4
        self.matric_note_img_data_dict[1]['offset_y'] = -self.matric_cell_width//2

        self.matric_note_img_data_dict[2] = {}
        with Image.new('RGBA', (self.matric_cell_width*4,self.matric_cell_width*4), (255,255,255,0)) as pil_img4:
            pil_draw = ImageDraw.Draw(pil_img4)
            xy0 = math.floor((self.matric_cell_width-self.matric_cell_width_phii)*2)
            xy1 = math.ceil((self.matric_cell_width+self.matric_cell_width_phii)*2)
            pil_draw.ellipse((xy0,xy0,xy1,xy1),outline=(0,0,0,255),width=self.matric_line1_width*4)
            with pil_img4.resize((self.matric_cell_width,self.matric_cell_width)) as pil_img:
                img_data = pil_img.tobytes()
                pyg_img = pygame.image.fromstring(img_data, (self.matric_cell_width,self.matric_cell_width), pil_img.mode)
        self.matric_note_img_data_dict[2]['surface'] = pyg_img
        self.matric_note_img_data_dict[2]['offset_x'] = -self.matric_cell_width//2
        self.matric_note_img_data_dict[2]['offset_y'] = -self.matric_cell_width//2

        self.matric_note_img_data_dict[3] = {}
        x0 = self.matric_cell_width * 1 // 8
        with Image.new('RGBA', (self.matric_cell_width*4,self.matric_cell_width*4), (255,255,255,0)) as pil_img4:
            pil_draw = ImageDraw.Draw(pil_img4)
            x40 = x0 * 4
            x41 = math.floor((x0+self.matric_cell_width_phii)*4)
            y40 = math.floor((self.matric_cell_width-self.matric_cell_width_phii)*2)
            y41 = math.floor(self.matric_cell_width*2)
            y42 = math.ceil((self.matric_cell_width+self.matric_cell_width_phii)*2)
            p40,p41,p42 = (x41,y40),(x40,y41),(x41,y42)
            pil_draw.line((p40,p41,p42,p40),fill=(0,0,0,255),width=self.matric_line1_width*4)
            with pil_img4.resize((self.matric_cell_width,self.matric_cell_width)) as pil_img:
                img_data = pil_img.tobytes()
                pyg_img = pygame.image.fromstring(img_data, (self.matric_cell_width,self.matric_cell_width), pil_img.mode)
        self.matric_note_img_data_dict[3]['surface'] = pyg_img
        self.matric_note_img_data_dict[3]['offset_x'] = -x0-self.matric_cell_width//4
        self.matric_note_img_data_dict[3]['offset_y'] = -self.matric_cell_width//2

        for noteev in track_data['noteev_list']:
            noteev['y'] = noteev['tick']*self.matric_cell_width/self.matric_ticks_per_beat
            if 'tick0' in noteev:
                noteev['y0'] = noteev['tick0']*self.matric_cell_width/self.matric_ticks_per_beat
            if 'tick1' in noteev:
                noteev['y1'] = noteev['tick1']*self.matric_cell_width/self.matric_ticks_per_beat


    def ppitch_to_x(self,ppitch):
        return self.matric_note_rail_x0 + (self.matric_ppitch1-ppitch )*self.matric_cell_width // 4

    def tick_to_y(self,tick,vision_offset_y):
        ret = tick
        ret /= self.matric_ticks_per_beat
        ret *= self.matric_cell_width
        ret -= vision_offset_y
        ret += self.matric_y0
        return ret

    def y_to_tick(self,y,vision_offset_y):
        ret = y
        ret -= self.matric_y0
        ret += vision_offset_y
        ret /= self.matric_cell_width
        ret *= self.matric_ticks_per_beat
        return ret
