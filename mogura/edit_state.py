import const
import gui
import img
import midi_data
import pygame
import note_state
from PIL import Image, ImageDraw

PITCH_C4 = note_state.PITCH_C4

class EditState(note_state.NoteState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'EDIT'
        
        self.vision_offset_tt = 0
        self.gui = None

    def screen_tick(self, screen, text_draw, sec, **kwargs):
        super().screen_tick(screen=screen, sec=sec, text_draw=text_draw, **kwargs)

        self.draw_note_rail(screen, self.vision_offset_tt)

        matric_screen_size = self.matric_screen_size
        ticks_per_beat = self.matric_ticks_per_beat
        
        play_tick_itr = map(lambda i:i*ticks_per_beat,self.runtime.play_beat_list)
        play_y0_list  = list(map(lambda i:round(self.tick_to_tt(i,self.vision_offset_tt)),play_tick_itr))

        pp0 = self.matric_note_rail_pp_min - self.matric_cell_z
        pp1 = self.matric_note_rail_pp_min - self.matric_cell_z // 2
        pp2 = self.matric_note_rail_pp_max + self.matric_cell_z // 2
        pp3 = self.matric_note_rail_pp_max + self.matric_cell_z
        tt0 = - self.matric_line1_z // 2
        tt1 = tt0 + self.matric_line1_z
        
        c00,c01=63,127
        c10,c11=127,191
        screen.fill(
            # rect=(pp0,play_y0_list[0]+tt0,pp3-pp0,self.matric_line1_z),
            rect = self.ppttrect_to_xyrect((pp0,play_y0_list[0]+tt0,pp3,play_y0_list[0]+tt1)),
            color=(c00,c01,c00),
        )

        screen.fill(
            # rect=(pp1,play_y0_list[1]+tt0,pp2-pp1,self.matric_line1_z),
            rect = self.ppttrect_to_xyrect((pp1,play_y0_list[1]+tt0,pp3,play_y0_list[1]+tt1)),
            color=(c10,c11,c10),
        )

        screen.fill(
            # rect=(pp0,play_y0_list[3]+tt0,pp3-pp0,self.matric_line1_z),
            rect = self.ppttrect_to_xyrect((pp1,play_y0_list[2]+tt0,pp3,play_y0_list[2]+tt1)),
            color=(c01,c00,c00),
        )

        screen.fill(
            # rect=(pp1,play_y0_list[2]+tt0,pp2-pp1,self.matric_line1_z),
            rect = self.ppttrect_to_xyrect((pp0,play_y0_list[3]+tt0,pp3,play_y0_list[3]+tt1)),
            color=(c11,c10,c10),
        )
        
        self.gui.set_label_text('speed.text', f'speed={self.runtime.speed_level}')
        self.gui.set_label_text('beat_vol.text', f'beat={self.runtime.beat_vol}')
        self.gui.set_label_text('main_vol.text', f'main={self.runtime.main_vol}')
        self.gui.set_label_text('dpitch.text', f'pitch={self.runtime.dpitch}')
        self.gui.draw_layer('se_control', screen, text_draw)


    def event_tick(self, event, sec):
        # print(event)
        is_ctrl_down  = (pygame.key.get_mods() & pygame.KMOD_CTRL)
        is_shift_down = (pygame.key.get_mods() & pygame.KMOD_SHIFT)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.runtime.state_pool.set_active('PLAY')
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL:
            self.lctrl_down = True
        if event.type == pygame.KEYUP and event.key == pygame.K_LCTRL:
            self.lctrl_down = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            self.runtime.play_beat_list[0] = self.xy_to_beat(pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
            self.runtime.play_beat_list[1] = self.xy_to_beat(pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN and event.key == pygame.K_3:
            self.runtime.play_beat_list[2] = self.xy_to_beat(pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN and event.key == pygame.K_4:
            self.runtime.play_beat_list[3] = self.xy_to_beat(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEWHEEL and not is_ctrl_down:
            self.vision_offset_tt -= event.y * 60
        if event.type == pygame.MOUSEWHEEL and is_ctrl_down:
            # mouse_screen_y = pygame.mouse.get_pos()[1]
            mouse_screen_xy = pygame.mouse.get_pos()
            mouse_screen_tt = self.xy_to_pptt(mouse_screen_xy)[1]
            mouse_tick = self.tt_to_tick(mouse_screen_tt, self.vision_offset_tt)
        
            self.runtime.ui_zoom_level += event.y
            self.runtime.ui_zoom_level = min(max(4,self.runtime.ui_zoom_level),16)

            self.update_ui_matrice()

            vision_offset_tt = mouse_tick
            vision_offset_tt /= self.matric_ticks_per_beat
            vision_offset_tt *= self.matric_cell_z
            vision_offset_tt *= note_state.NOTE_SPEED
            vision_offset_tt -= mouse_screen_tt
            vision_offset_tt += self.matric_aim_tt
            self.vision_offset_tt = vision_offset_tt
        self.gui.on_event(event)
        if self.gui.is_btn_active('speed.minus'):
            self.runtime.speed_level -= 6 if is_shift_down else 1
        if self.gui.is_btn_active('speed.plus'):
            self.runtime.speed_level += 6 if is_shift_down else 1
        if self.gui.is_btn_active('beat_vol.zero'):
            self.runtime.beat_vol = 0
        if self.gui.is_btn_active('beat_vol.minus'):
            self.runtime.beat_vol -= 16 if is_shift_down else 1
            self.runtime.beat_vol = min(max(0,self.runtime.beat_vol),127)
        if self.gui.is_btn_active('beat_vol.plus'):
            self.runtime.beat_vol += 16 if is_shift_down else 1
            self.runtime.beat_vol = min(max(0,self.runtime.beat_vol),127)
        if self.gui.is_btn_active('beat_vol.max'):
            self.runtime.beat_vol = 127
        if self.gui.is_btn_active('main_vol.zero'):
            self.runtime.main_vol = 0
        if self.gui.is_btn_active('main_vol.minus'):
            self.runtime.main_vol -= 16 if is_shift_down else 1
            self.runtime.main_vol = min(max(0,self.runtime.main_vol),127)
        if self.gui.is_btn_active('main_vol.plus'):
            self.runtime.main_vol += 16 if is_shift_down else 1
            self.runtime.main_vol = min(max(0,self.runtime.main_vol),127)
        if self.gui.is_btn_active('main_vol.max'):
            self.runtime.main_vol = 127
        if self.gui.is_btn_active('dpitch.minus'):
            self.runtime.dpitch -= 4 if is_shift_down else 1
            self.runtime.dpitch = min(max(
                -self.runtime.midi_data['track_list'][0]['opitch0'],
                self.runtime.dpitch),
                127-self.runtime.midi_data['track_list'][0]['opitch1']
            )
            midi_data.track_data_cal_ppitch(self.runtime.midi_data['track_list'][0], self.runtime.dpitch)
            self.runtime.state_pool.on_pitch_update()
        if self.gui.is_btn_active('dpitch.plus'):
            self.runtime.dpitch += 4 if is_shift_down else 1
            self.runtime.dpitch = min(max(
                -self.runtime.midi_data['track_list'][0]['opitch0'],
                self.runtime.dpitch),
                127-self.runtime.midi_data['track_list'][0]['opitch1']
            )
            midi_data.track_data_cal_ppitch(self.runtime.midi_data['track_list'][0], self.runtime.dpitch)
            self.runtime.state_pool.on_pitch_update()
        if self.gui.is_btn_active('config.open_ui'):
            # print('config.open_ui')
            self.runtime.state_pool.set_active('CONFIG')

#    def is_ctrl_down(self, event):
#        return self.rctrl_down or self.lctrl_down
#
#    def is_shift_down(self, event):
#        return self.rshift_down or self.lshift_down

    def on_active(self):
        self.track_data = self.runtime.midi_data['track_list'][0]
        self.img_dict = {}
        self.img_dict['zero']  = img.zero_btn_img()
        self.img_dict['minus'] = img.minus_btn_img()
        self.img_dict['plus']  = img.plus_btn_img()
        self.img_dict['max']   = img.max_btn_img()
        super().on_active()

    def on_inactive(self):
        super().on_inactive()
        self.gui = None
        self.img_dict = None

    def update_ui_matrice(self):
        super().update_ui_matrice()
        width,height = self.matric_screen_size
        x2 = 152
        x1 = x2-80
        x0 = x1-32
        x3 = x2+80
        x4 = x3+32
        y = height-30
        self.gui = gui.Gui()
        self.gui.add_button('speed.minus',self.img_dict['minus'],(x1,y),6,'se_control')
        self.gui.add_label('speed.text','',const.FONT_SIZE,(127,127,127), (x2,y), 5,'se_control')
        self.gui.add_button('speed.plus', self.img_dict['plus'], (x3,y),4,'se_control')
        y -= 40
        self.gui.add_button('beat_vol.zero',self.img_dict['zero'],(x0,y),6,'se_control')
        self.gui.add_button('beat_vol.minus',self.img_dict['minus'],(x1,y),6,'se_control')
        self.gui.add_label('beat_vol.text','',const.FONT_SIZE,(127,127,127), (x2,y), 5,'se_control')
        self.gui.add_button('beat_vol.plus', self.img_dict['plus'], (x3,y),4,'se_control')
        self.gui.add_button('beat_vol.max', self.img_dict['max'], (x4,y),4,'se_control')
        y -= 40
        self.gui.add_button('main_vol.zero',self.img_dict['zero'],(x0,y),6,'se_control')
        self.gui.add_button('main_vol.minus',self.img_dict['minus'],(x1,y),6,'se_control')
        self.gui.add_label('main_vol.text','',const.FONT_SIZE,(127,127,127), (x2,y), 5,'se_control')
        self.gui.add_button('main_vol.plus', self.img_dict['plus'], (x3,y),4,'se_control')
        self.gui.add_button('main_vol.max', self.img_dict['max'], (x4,y),4,'se_control')
        y -= 40
        self.gui.add_button('dpitch.minus',self.img_dict['minus'],(x1,y),6,'se_control')
        self.gui.add_label('dpitch.text','',const.FONT_SIZE,(127,127,127), (x2,y), 5,'se_control')
        self.gui.add_button('dpitch.plus', self.img_dict['plus'], (x3,y),4,'se_control')
        y -= 40
        self.gui.add_label('config.text','Config',const.FONT_SIZE,(127,127,127), (x2,y), 5,'se_control')
        self.gui.add_click('config.open_ui', (x2,y), (240,40), 5,'se_control')

    def on_midi_update(self):
        self.track_data = self.runtime.midi_data['track_list'][0]
        super().on_midi_update()
        self.vision_offset_tt = 0

    def on_pitch_update(self):
        self.track_data = self.runtime.midi_data['track_list'][0]
        super().on_pitch_update()

    def xy_to_beat(self,xy):
        tt = self.xy_to_pptt(xy)[1]
        ret = self.tt_to_tick(tt, self.vision_offset_tt)
        ret /= self.matric_ticks_per_beat
        ret = round(ret)
        return ret
