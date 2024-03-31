import common
import common_pil
import copy
import math
import midi_data
import mgr_enum
import pygame
import null_state
from PIL import Image, ImageDraw

PITCH_C4 = 72
# TIME_DIRECTION = mgr_enum.DOWN
# PITCH_DIRECTION = mgr_enum.LEFT

# TIME_DIRECTION = mgr_enum.DOWN
# PITCH_DIRECTION = mgr_enum.RIGHT

# TIME_DIRECTION = mgr_enum.UP
# PITCH_DIRECTION = mgr_enum.LEFT

TIME_DIRECTION = mgr_enum.RIGHT
PITCH_DIRECTION = mgr_enum.DOWN

# TIME_HORI = TIME_DIRECTION & mgr_enum.HORI_MASK
PITCH_HORI = PITCH_DIRECTION & mgr_enum.HORI_MASK
TIME_POS = TIME_DIRECTION & mgr_enum.POS_MASK
PITCH_POS = PITCH_DIRECTION & mgr_enum.POS_MASK

NOTE_SPEED = 2

# pp: pitch axis
# tt: time axis
# z: general axis

class NoteState(null_state.NullState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'NOTE'

        #self.vision_offset_tt = 0


    def draw_note_rail(self, screen, vision_offset_tt):
        draw_session = self.get_draw_session(screen, vision_offset_tt)
        self.draw_color_note_rail_bg(draw_session)
        self.draw_note_length(draw_session)
        self.draw_time_line_thin(draw_session)
        self.draw_note_rail_ppitch_line(draw_session)
        self.draw_time_line_thick(draw_session)
        self.draw_key_signature(draw_session)
        self.draw_note_signal(draw_session)

    def get_draw_session(self, screen, vision_offset_tt):
        track_data = self.matric_track_data
        ticks_per_beat = self.matric_ticks_per_beat
        min_tick = math.floor(self.tt_to_tick(-self.matric_cell_z,vision_offset_tt))
        max_tick = math.ceil(self.tt_to_tick(self.matric_screen_tt_max+self.matric_cell_z,vision_offset_tt))

        draw_session = {
            'screen': screen,
            'track_data': track_data,
            'ticks_per_beat': ticks_per_beat,
            'vision_offset_tt': vision_offset_tt,
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
        vision_offset_tt = draw_session['vision_offset_tt']
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
            pp = self.ppitch_to_pp(noteev['ppitch'])
            pp0 = pp-self.matric_cell_z//8
            pp1 = pp+self.matric_cell_z//8
            tt0 = round(noteev['tt0']-vision_offset_tt+self.matric_aim_tt)
            tt0 = min(max(tt0,0),self.matric_screen_tt_max)
            tt1 = round(noteev['tt1']-vision_offset_tt+self.matric_aim_tt)
            tt1 = min(max(tt1,0),self.matric_screen_tt_max)
            cc = (ppitch+4+300-PITCH_C4)%12
            cc = CC[cc]
            screen.fill(
                rect=self.ppttrect_to_xyrect((pp0,tt0,pp1,tt1)),
                color=cc,
            )

    def draw_time_line_thin(self, draw_session):
        screen = draw_session['screen']
        vision_offset_tt = draw_session['vision_offset_tt']
        min_tick = draw_session['min_tick']
        max_tick = draw_session['max_tick']
        ticks_per_beat = draw_session['ticks_per_beat']

        pp0 = self.matric_note_rail_pp_min
        pp1 = self.matric_note_rail_pp_max
        matric_line0_z_2 = self.matric_line0_z//2
        # w = self.matric_note_rail_pp_max-self.matric_note_rail_pp_min
        for tick in midi_data.get_beat_itr(min_tick, ticks_per_beat):
            if tick > max_tick: break
            #print(f'beat tick={tick}')
            tt = round(self.tick_to_tt(tick,vision_offset_tt))
            tt0 = tt-matric_line0_z_2
            tt1 = tt0+self.matric_line0_z
            screen.fill(
                # rect=(self.matric_note_rail_pp_min,y+y0,w,self.matric_line0_z),
                rect=self.ppttrect_to_xyrect((pp0,tt0,pp1,tt1)),
                color=(255,255,255,255),
            )

    def draw_note_rail_ppitch_line(self, draw_session):
        screen = draw_session['screen']
        for matric_note_rail_ppitch_line_data in self.matric_note_rail_ppitch_line_data_list:
            screen.fill(**matric_note_rail_ppitch_line_data)

    def draw_time_line_thick(self, draw_session):
        screen = draw_session['screen']
        track_data = draw_session['track_data']
        vision_offset_tt = draw_session['vision_offset_tt']
        min_tick = draw_session['min_tick']
        max_tick = draw_session['max_tick']

        pp0 = self.matric_note_rail_pp_min
        pp1 = self.matric_note_rail_pp_max
        matric_line1_z_2 = self.matric_line1_z//2

        # y0 = -self.matric_line0_z//2
        # y1 = -self.matric_line1_z//2
        # w = self.matric_note_rail_pp_max-self.matric_note_rail_pp_min
        #print(f'bar min_tick={min_tick}')
        for tick in midi_data.get_bar_itr(min_tick, track_data):
            if tick >= max_tick: break
            #print(f'bar min_tick={min_tick} tick={tick}')
            # y = round(self.tick_to_tt(tick,vision_offset_tt))
            tt = round(self.tick_to_tt(tick,vision_offset_tt))
            tt0 = tt-matric_line1_z_2
            tt1 = tt0+self.matric_line1_z
            screen.fill(
                rect=self.ppttrect_to_xyrect((pp0,tt0,pp1,tt1)),
                color=(128,128,128,255),
            )

    def draw_key_signature(self, draw_session):
        screen = draw_session['screen']
        track_data = draw_session['track_data']
        vision_offset_tt = draw_session['vision_offset_tt']
        min_tick = draw_session['min_tick']
        max_tick = draw_session['max_tick']

        key_signature_list = track_data['key_signature_list']
        key_signature_list = filter(lambda i:i['tick0']>min_tick,key_signature_list)
        key_signature_list = filter(lambda i:i['tick0']<max_tick,key_signature_list)
        key_signature_list = list(key_signature_list)
        for key_signature in key_signature_list:
            key = key_signature['key']
            if key is None: continue
            tick = key_signature['tick0']
            # y = round(self.tick_to_tt(tick,vision_offset_tt))
            tt = round(self.tick_to_tt(tick,vision_offset_tt))
            tt0 = tt-self.matric_cell_z//16
            tt1 = tt0+self.matric_cell_z//8
            for p in range(self.matric_ppitch0, self.matric_ppitch1+1, 1):
                px = (p-key)%12
                if px not in midi_data.MAIN_PITCH_SET: continue
                pp = self.ppitch_to_pp(p)
                pp0 = pp-self.matric_line0_z//2
                pp1 = pp0+self.matric_line0_z
                screen.fill(
                    rect=self.ppttrect_to_xyrect((pp0,tt0,pp1,tt1)),
                    color=(0,0,0,255),
                )
            # pp0 = self.matric_note_rail_pp_min
            # pp1 = self.matric_note_rail_pp_max
            # screen.fill(
            #     rect=self.ppttrect_to_xyrect((pp0,tt0,pp1,tt1)),
            #     color=(255,255,255,255),
            # )

    def draw_note_signal(self, draw_session):
        screen = draw_session['screen']
        track_data = draw_session['track_data']
        vision_offset_tt = draw_session['vision_offset_tt']
        min_tick = draw_session['min_tick']
        max_tick = draw_session['max_tick']

        noteev_list = track_data['noteev_list']
        noteev_list = filter(lambda i:i['type']=='on',noteev_list)
        noteev_list = filter(lambda i:i['tick1']>min_tick,noteev_list)
        noteev_list = filter(lambda i:i['tick0']<max_tick,noteev_list)
        noteev_list = list(noteev_list)
        for noteev in noteev_list:
            ppitch = noteev['ppitch']
            pp = self.ppitch_to_pp(noteev['ppitch'])
            tt = round(noteev['tt0']-vision_offset_tt+self.matric_aim_tt)
            x, y = self.pptt_to_xy((pp,tt))
            p = (ppitch + 300 - PITCH_C4) % 4
            matric_note_img_data = self.matric_note_img_data_dict[p]
            screen.blit(
                source=matric_note_img_data['surface'],
                dest=(x+matric_note_img_data['offset_x'],y+matric_note_img_data['offset_y']),
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
        screen_tt_max = screen_size[0] if TIME_DIRECTION & mgr_enum.HORI_MASK else screen_size[1]
        screen_pp_max = screen_size[0] if PITCH_DIRECTION & mgr_enum.HORI_MASK else screen_size[1]
        # self.matric_tt_dir = 1 if TIME_DIRECTION & mgr_enum.POS_MASK else -1
        # self.matric_pp_dir = 1 if PITCH_DIRECTION & mgr_enum.POS_MASK else -1

        # midi_data = self.runtime.midi_data
        # track_data = midi_data['track_list'][0]
        track_data = copy.deepcopy(self.track_data)
        self.matric_track_data = track_data

        self.matric_cell_z = max(round(2 ** (self.runtime.ui_zoom_level/2)),1)
        self.matric_line0_z = max(self.matric_cell_z//32,1)
        self.matric_line1_z = max(self.matric_cell_z//16,1)

        self.matric_screen_size = screen_size
        self.matric_screen_tt_max = screen_tt_max
        self.matric_screen_pp_max = screen_pp_max
        self.matric_cell_z_phii = self.matric_cell_z / common.PHI

        self.matric_ticks_per_beat = self.runtime.midi_data['ticks_per_beat']

        self.matric_ppitch1 = track_data['ppitch1'] + 2
        self.matric_ppitch0 = track_data['ppitch0'] - 2
        ppitch_diff = self.matric_ppitch1 - self.matric_ppitch0
        self.matric_note_rail_pp_min = (screen_pp_max-ppitch_diff*self.matric_cell_z//4)//2
        self.matric_note_rail_pp_max = self.matric_note_rail_pp_min+ppitch_diff*self.matric_cell_z//4

        # RGB rail
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
            # x1 = self.matric_note_rail_pp_min + (self.matric_ppitch1-ppitch )*self.matric_cell_z // 4
            # x0 = self.matric_note_rail_pp_min + (self.matric_ppitch1-ppitch1)*self.matric_cell_z // 4
            pp0 = self.ppitch_to_pp(ppitch)
            pp1 = self.ppitch_to_pp(ppitch1)
            c = ppitch
            c += 300
            c -= PITCH_C4
            c %= 12
            c //= 4
            c = (255,246,246) if c == 0 else \
                    (246,255,246) if c == 1 else \
                    (246,246,255)
            self.matric_note_rail_bg_rect_data_list.append({
                'rect':self.ppttrect_to_xyrect((pp0,0,pp1,self.matric_screen_tt_max)),
                'color':c,
            })
            ppitch = ppitch1

        # ppitch line
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
            c,w = (128,self.matric_line1_z) if p == 0 else (192,self.matric_line0_z)
            pp = self.ppitch_to_pp(ppitch)
            pp0 = pp - w//2
            pp1 = pp0 + w
            # self.matric_note_rail_ppitch_line_data_list.append({
            #     'start_pos': (x, 0),
            #     'end_pos':   (x, screen_size[1]),
            #     'color':     (c,c,c),
            #     'width':     w,
            # })
            self.matric_note_rail_ppitch_line_data_list.append({
                'rect':  self.ppttrect_to_xyrect((pp0,0,pp1,self.matric_screen_tt_max)),
                'color': (c,c,c),
            })
            ppitch += 4

        self.matric_aim_tt = math.floor(self.matric_cell_z*common.PHI)

        # note img
        self.matric_note_img_data_dict = {}

        self.matric_note_img_data_dict[0] = {}
        pil_img = Image.new('RGBA', (self.matric_cell_z*4,self.matric_cell_z*4), (255,255,255,0))
        pil_draw = ImageDraw.Draw(pil_img)
        pptt0 = math.floor((self.matric_cell_z-self.matric_cell_z_phii)*2)
        pptt1 = math.ceil((self.matric_cell_z+self.matric_cell_z_phii)*2)
        pil_draw.line((pptt0,pptt0,pptt1,pptt1),fill=(0,0,0,255),width=self.matric_line1_z*4)
        pil_draw.line((pptt0,pptt1,pptt1,pptt0),fill=(0,0,0,255),width=self.matric_line1_z*4)
        pil_img = common_pil.resize_free(pil_img, (self.matric_cell_z,self.matric_cell_z))
        img_data = pil_img.tobytes()
        pyg_img = pygame.image.fromstring(img_data, (self.matric_cell_z,self.matric_cell_z), pil_img.mode)
        pil_img.close()
        self.matric_note_img_data_dict[0]['surface'] = pyg_img
        self.matric_note_img_data_dict[0]['offset_pp'] = -self.matric_cell_z//2
        self.matric_note_img_data_dict[0]['offset_tt'] = -self.matric_cell_z//2

        self.matric_note_img_data_dict[1] = {}
        pil_img = Image.new('RGBA', (self.matric_cell_z*4,self.matric_cell_z*4), (255,255,255,0))
        pil_draw = ImageDraw.Draw(pil_img)
        pp0 = self.matric_cell_z * 1 // 8
        pp40 = pp0 * 4
        pp41 = math.floor((pp0+self.matric_cell_z_phii)*4)
        tt40 = math.floor((self.matric_cell_z-self.matric_cell_z_phii)*2)
        tt41 = math.floor(self.matric_cell_z*2)
        tt42 = math.ceil((self.matric_cell_z+self.matric_cell_z_phii)*2)
        p40,p41,p42 = (pp41,tt40),(pp40,tt41),(pp41,tt42)
        pil_draw.line((p40,p41,p42,p40),fill=(0,0,0,255),width=self.matric_line1_z*4)
        pil_img = common_pil.resize_free(pil_img, (self.matric_cell_z,self.matric_cell_z))
        if PITCH_DIRECTION == mgr_enum.LEFT:
            pil_img = common_pil.hflip_free(pil_img)
        elif PITCH_DIRECTION == mgr_enum.UP:
            pil_img = common_pil.ccw_rotate_free(pil_img)
        elif PITCH_DIRECTION == mgr_enum.DOWN:
            pil_img = common_pil.cw_rotate_free(pil_img)
        img_data = pil_img.tobytes()
        pyg_img = pygame.image.fromstring(img_data, (self.matric_cell_z,self.matric_cell_z), pil_img.mode)
        pil_img.close()
        self.matric_note_img_data_dict[1]['surface'] = pyg_img
        self.matric_note_img_data_dict[1]['offset_pp'] = -pp0-self.matric_cell_z//4
        self.matric_note_img_data_dict[1]['offset_tt'] = -self.matric_cell_z//2

        self.matric_note_img_data_dict[2] = {}
        pil_img = Image.new('RGBA', (self.matric_cell_z*4,self.matric_cell_z*4), (255,255,255,0))
        pil_draw = ImageDraw.Draw(pil_img)
        pptt0 = math.floor((self.matric_cell_z-self.matric_cell_z_phii)*2)
        pptt1 = math.ceil((self.matric_cell_z+self.matric_cell_z_phii)*2)
        pil_draw.ellipse((pptt0,pptt0,pptt1,pptt1),outline=(0,0,0,255),width=self.matric_line1_z*4)
        pil_img = common_pil.resize_free(pil_img, (self.matric_cell_z,self.matric_cell_z))
        img_data = pil_img.tobytes()
        pyg_img = pygame.image.fromstring(img_data, (self.matric_cell_z,self.matric_cell_z), pil_img.mode)
        pil_img.close()
        self.matric_note_img_data_dict[2]['surface'] = pyg_img
        self.matric_note_img_data_dict[2]['offset_pp'] = -self.matric_cell_z//2
        self.matric_note_img_data_dict[2]['offset_tt'] = -self.matric_cell_z//2

        self.matric_note_img_data_dict[3] = {}
        pil_img = Image.new('RGBA', (self.matric_cell_z*4,self.matric_cell_z*4), (255,255,255,0))
        pil_draw = ImageDraw.Draw(pil_img)
        pp1 = self.matric_cell_z * 7 // 8
        pp41 = pp1 * 4
        pp40 = math.floor((pp1-self.matric_cell_z_phii)*4)
        tt40 = math.floor((self.matric_cell_z-self.matric_cell_z_phii)*2)
        tt41 = math.floor(self.matric_cell_z*2)
        tt42 = math.ceil((self.matric_cell_z+self.matric_cell_z_phii)*2)
        p40,p41,p42 = (pp40,tt40),(pp41,tt41),(pp40,tt42)
        pil_draw.line((p40,p41,p42,p40),fill=(0,0,0,255),width=self.matric_line1_z*4)
        pil_img = common_pil.resize_free(pil_img, (self.matric_cell_z,self.matric_cell_z))
        if PITCH_DIRECTION == mgr_enum.LEFT:
            pil_img = common_pil.hflip_free(pil_img)
        elif PITCH_DIRECTION == mgr_enum.UP:
            pil_img = common_pil.ccw_rotate_free(pil_img)
        elif PITCH_DIRECTION == mgr_enum.DOWN:
            pil_img = common_pil.cw_rotate_free(pil_img)
        img_data = pil_img.tobytes()
        pyg_img = pygame.image.fromstring(img_data, (self.matric_cell_z,self.matric_cell_z), pil_img.mode)
        pil_img.close()
        self.matric_note_img_data_dict[3]['surface'] = pyg_img
        self.matric_note_img_data_dict[3]['offset_pp'] = -pp1+self.matric_cell_z//4
        self.matric_note_img_data_dict[3]['offset_tt'] = -self.matric_cell_z//2

        for _k, matric_note_img_data in self.matric_note_img_data_dict.items():
            matric_note_img_data['offset_x'] = matric_note_img_data['offset_pp'] if PITCH_DIRECTION == mgr_enum.RIGHT else \
                                               -self.matric_cell_z-matric_note_img_data['offset_pp'] if PITCH_DIRECTION == mgr_enum.LEFT else \
                                               matric_note_img_data['offset_tt'] if TIME_DIRECTION == mgr_enum.RIGHT else \
                                               -self.matric_cell_z-matric_note_img_data['offset_tt'] if TIME_DIRECTION == mgr_enum.LEFT else \
                                               float("nan")
            matric_note_img_data['offset_y'] = matric_note_img_data['offset_pp'] if PITCH_DIRECTION == mgr_enum.DOWN else \
                                               -self.matric_cell_z-matric_note_img_data['offset_pp'] if PITCH_DIRECTION == mgr_enum.UP else \
                                               matric_note_img_data['offset_tt'] if TIME_DIRECTION == mgr_enum.DOWN else \
                                               -self.matric_cell_z-matric_note_img_data['offset_tt'] if TIME_DIRECTION == mgr_enum.UP else \
                                               float("nan")


        for noteev in track_data['noteev_list']:
            noteev['tt'] = noteev['tick']*self.matric_cell_z*NOTE_SPEED/self.matric_ticks_per_beat
            if 'tick0' in noteev:
                noteev['tt0'] = noteev['tick0']*self.matric_cell_z*NOTE_SPEED/self.matric_ticks_per_beat
            if 'tick1' in noteev:
                noteev['tt1'] = noteev['tick1']*self.matric_cell_z*NOTE_SPEED/self.matric_ticks_per_beat


    def ppitch_to_pp(self,ppitch):
        return self.matric_note_rail_pp_min + (ppitch-self.matric_ppitch0)*self.matric_cell_z // 4

    def tick_to_tt(self,tick,vision_offset_tt):
        ret = tick
        ret /= self.matric_ticks_per_beat
        ret *= self.matric_cell_z
        ret *= NOTE_SPEED
        ret -= vision_offset_tt
        ret += self.matric_aim_tt
        return ret

    def tt_to_tick(self,tt,vision_offset_tt):
        ret = tt
        ret -= self.matric_aim_tt
        ret += vision_offset_tt
        ret /= NOTE_SPEED
        ret /= self.matric_cell_z
        ret *= self.matric_ticks_per_beat
        return ret
    
    def pptt_to_xy(self, pptt):
        pp,tt = pptt
        x = pp if PITCH_DIRECTION == mgr_enum.RIGHT else \
            self.matric_screen_pp_max-pp if PITCH_DIRECTION == mgr_enum.LEFT else \
            tt if TIME_DIRECTION == mgr_enum.RIGHT else \
            self.matric_screen_tt_max-tt if TIME_DIRECTION == mgr_enum.LEFT else \
            float("nan")
        y = pp if PITCH_DIRECTION == mgr_enum.DOWN else \
            self.matric_screen_pp_max-pp if PITCH_DIRECTION == mgr_enum.UP else \
            tt if TIME_DIRECTION == mgr_enum.DOWN else \
            self.matric_screen_tt_max-tt if TIME_DIRECTION == mgr_enum.UP else \
            float("nan")
        return (x,y)

    def xy_to_pptt(self, xy):
        x,y = xy
        pp = x if PITCH_DIRECTION == mgr_enum.RIGHT else \
             self.matric_screen_size[0]-x if PITCH_DIRECTION == mgr_enum.LEFT else \
             y if PITCH_DIRECTION == mgr_enum.DOWN else \
             self.matric_screen_size[1]-y if PITCH_DIRECTION == mgr_enum.UP else \
             float("nan")
        tt = x if TIME_DIRECTION == mgr_enum.RIGHT else \
             self.matric_screen_size[0]-x if TIME_DIRECTION == mgr_enum.LEFT else \
             y if TIME_DIRECTION == mgr_enum.DOWN else \
             self.matric_screen_size[1]-y if TIME_DIRECTION == mgr_enum.UP else \
             float("nan")
        return (pp,tt)

    def ppttrect_to_xyrect(self, ppttrect):
        pp0,tt0,pp1,tt1 = ppttrect
        x0,y0 = self.pptt_to_xy((pp0,tt0))
        x1,y1 = self.pptt_to_xy((pp1,tt1))
        x0,x1 = min(x0,x1),max(x0,x1)
        y0,y1 = min(y0,y1),max(y0,y1)
        x0 = max(x0,0)
        y0 = max(y0,0)
        x1 = min(x1,self.matric_screen_size[0])
        y1 = min(y1,self.matric_screen_size[1])
        return (x0,y0,x1-x0,y1-y0)
