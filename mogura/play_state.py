import audio_input
import common
import const
import copy
import dft
import midi_data
import note_state
import pygame
import time

class PlayState(note_state.NoteState):

    def __init__(self,runtime):
        super().__init__(runtime)

        self.id = 'PLAY'

        self.audio_input = audio_input.AudioInput(self.runtime)
        self.dft = dft.Dft(self.runtime)
        self.audio_input.add_stream_callback(self.dft.stream_callback)

        self.rctrl_down = False
        self.lctrl_down = False
        
        self.start_sec = None
        #self.track_list = None
        self.loop_sec6tpb = None

        self.freq_list = None

    def screen_tick(self, screen, sec, **kwargs):
        super().screen_tick(screen=screen, sec=sec, **kwargs)

        vision_offset_tt = time.time()
        vision_offset_tt -= self.start_sec
        vision_offset_tt *= 1000000
        vision_offset_tt *= self.matric_ticks_per_beat
        # vision_offset_tt %= self.track_data['sec6tpb']
        vision_offset_tt %= self.loop_sec6tpb
        # print(f'sec6tpb={vision_offset_tt}')
        vision_offset_tt = midi_data.sec6tpb_to_tick(vision_offset_tt, self.track_data['tempo_list'], self.track_data['time_multiplier'])
        # print(f'tick={vision_offset_tt}')
        vision_offset_tt /= self.matric_ticks_per_beat
        vision_offset_tt *= self.matric_cell_z
        vision_offset_tt *= note_state.NOTE_SPEED
        # self.draw_note_rail(screen, vision_offset_tt)

        draw_session = self.get_draw_session(screen, vision_offset_tt)

        self.draw_color_note_rail_bg(draw_session)
        self.draw_note_length(draw_session)

        if self.freq_list is not None:
            level_np = self.dft.get_level_np()
            if level_np is not None:
                # print(level_np.shape)
                for i in range(level_np.shape[0]):
                    v = level_np[i]
                    v = v+5
                    v = max(v,0)
                    v *= 50
                    screen.fill(
                        # rect=(self.freq_pp0_list[i],self.matric_aim_tt,self.freq_pp1_list[i],v),
                        ret = self.ppttrect_to_xyrect(self.freq_pp0_list[i],self.matric_aim_tt,self.freq_pp1_list[i],self.matric_aim_tt+v),
                        color=(63,63,63,255),
                    )

        self.draw_time_line_thin(draw_session)
        self.draw_note_rail_ppitch_line(draw_session)
        self.draw_time_line_thick(draw_session)
        self.draw_note_signal(draw_session)

        screen.fill(
            # rect=(0,self.matric_aim_tt,self.matric_screen_size[0],1),
            rect=self.ppttrect_to_xyrect((0,self.matric_aim_tt,self.matric_screen_pp_max,self.matric_aim_tt+1)),
            color=(0,0,0),
        )

    def on_active(self):
#        src_track_data = self.runtime.midi_data['track_list'][0]
#        
#        play_tick_list    = list(map(lambda i:i*self.runtime.midi_data['ticks_per_beat'],self.runtime.play_beat_list))
#        play_sec6tpb_list = list(map(lambda i:midi_data.tick_to_sec6tpb(i,src_track_data['tempo_list']),play_tick_list))
#
#        self.track_data = {}
#
#        noteev_list = src_track_data['noteev_list']
#        noteev_list = filter(lambda i:i['type']=='on', noteev_list)
#        noteev_list = filter(lambda i:i['tick1']>=play_tick_list[1],noteev_list)
#        noteev_list = filter(lambda i:i['tick0']<play_tick_list[2],noteev_list)
#        noteev_list = list(noteev_list)
#        noteev_list = copy.deepcopy(noteev_list)
#        for noteev in noteev_list:
#            noteev['tick']  -= play_tick_list[0]
#            if 'tick0' in noteev: noteev['tick0'] -= play_tick_list[0]
#            if 'tick1' in noteev: noteev['tick1'] -= play_tick_list[0]
#            noteev['sec6tpb']  -= play_sec6tpb_list[0]
#            if 'sec6tpb0' in noteev: noteev['sec6tpb0'] -= play_sec6tpb_list[0]
#            if 'sec6tpb1' in noteev: noteev['sec6tpb1'] -= play_sec6tpb_list[0]
#
#        play_noteev_list = copy.deepcopy(noteev_list)
#
#        noteev_list0 = copy.deepcopy(noteev_list)
#        for noteev in noteev_list0:
#            noteev['tick']  -= play_tick_list[3]-play_tick_list[0]
#            if 'tick0' in noteev: noteev['tick0'] -= play_tick_list[3]-play_tick_list[0]
#            if 'tick1' in noteev: noteev['tick1'] -= play_tick_list[3]-play_tick_list[0]
#            noteev['sec6tpb']  -= play_sec6tpb_list[3]-play_sec6tpb_list[0]
#            if 'sec6tpb0' in noteev: noteev['sec6tpb0'] -= play_sec6tpb_list[3]-play_sec6tpb_list[0]
#            if 'sec6tpb1' in noteev: noteev['sec6tpb1'] -= play_sec6tpb_list[3]-play_sec6tpb_list[0]
#
#        noteev_list1 = copy.deepcopy(noteev_list)
#        for noteev in noteev_list1:
#            noteev['tick']  += play_tick_list[3]-play_tick_list[0]
#            if 'tick0' in noteev: noteev['tick0'] += play_tick_list[3]-play_tick_list[0]
#            if 'tick1' in noteev: noteev['tick1'] += play_tick_list[3]-play_tick_list[0]
#            noteev['sec6tpb']  += play_sec6tpb_list[3]-play_sec6tpb_list[0]
#            if 'sec6tpb0' in noteev: noteev['sec6tpb0'] += play_sec6tpb_list[3]-play_sec6tpb_list[0]
#            if 'sec6tpb1' in noteev: noteev['sec6tpb1'] += play_sec6tpb_list[3]-play_sec6tpb_list[0]
#
#        noteev_list = noteev_list0+noteev_list+noteev_list1
#
#        self.track_data['noteev_list'] = noteev_list
#        
#        bar_list = src_track_data['bar_list']
#        bar_list = filter(lambda i:i>=play_tick_list[0],bar_list)
#        bar_list = filter(lambda i:i<=play_tick_list[3],bar_list)
#        bar_list = map(lambda i:i-play_tick_list[0],bar_list)
#        bar_list = list(bar_list)
#
#        bar_list0 = list(map(lambda i:i-play_tick_list[3]+play_tick_list[0],bar_list))
#        bar_list1 = list(map(lambda i:i+play_tick_list[3]-play_tick_list[0],bar_list))
#        bar_list = bar_list0 + bar_list + bar_list1
#
#        bar_set = set(bar_list)
#        bar_list = sorted(bar_set)
#        self.track_data['bar_list'] = bar_list
#        self.track_data['bar_set'] = bar_set
#        
#        tempo_list = src_track_data['tempo_list']
#        tempo_list = filter(lambda i:i['tick1']>play_tick_list[0],tempo_list)
#        tempo_list = filter(lambda i:i['tick0']<=play_tick_list[3],tempo_list)
#        tempo_list = list(tempo_list)
#        for tempo in tempo_list:
#            tempo['tick0'] -= play_tick_list[0]
#            tempo['tick1'] -= play_tick_list[0]
#            tempo['sec6tpb0'] -= play_sec6tpb_list[0]
#            tempo['sec6tpb1'] -= play_sec6tpb_list[0]
#        tempo_list[0]['tick0']    = 0
#        tempo_list[0]['tick1']    = play_tick_list[3] - play_tick_list[0]
#        tempo_list[0]['sec6tpb0'] = 0
#        tempo_list[0]['sec6tpb1'] = play_sec6tpb_list[3] - play_sec6tpb_list[0]
#        self.track_data['tempo_list'] = tempo_list
#
#        self.track_data['pitch1'] = src_track_data['pitch1']
#        self.track_data['pitch0'] = src_track_data['pitch0']
#        
#        self.track_data['sec6tpb'] = play_sec6tpb_list[3]-play_sec6tpb_list[0]
#
#        min_sec6tpb = play_sec6tpb_list[1]-play_sec6tpb_list[0]
#        max_sec6tpb = play_sec6tpb_list[2]-play_sec6tpb_list[0]
#        sec6tpb_30 = play_sec6tpb_list[3]-play_sec6tpb_list[0]
#        play_noteev_list = filter(lambda i:i['type']=='on',play_noteev_list)
#        play_noteev_list = list(play_noteev_list)
#        for noteev in play_noteev_list:
#            noteev['sec6tpb0'] = max(noteev['sec6tpb0'],min_sec6tpb)
#            noteev['sec6tpb1'] = min(noteev['sec6tpb1'],max_sec6tpb)
#            noteev['sec6tpb']  = noteev['sec6tpb0']
#            noteev['sort_key'] = (noteev['sec6tpb'],1,noteev['pitch'])
#        play_noteev_off_list = copy.deepcopy(play_noteev_list)
#        for noteev in play_noteev_off_list:
#            noteev['type'] = 'off'
#            noteev['sec6tpb']  = noteev['sec6tpb1']
#            noteev['sort_key'] = (noteev['sec6tpb'],0,noteev['pitch'])
#        play_noteev_list = play_noteev_list + play_noteev_off_list
#        play_noteev_list = sorted(play_noteev_list, key=lambda i:i['sort_key'])

        #print(self.runtime.play_beat_list)
        play_track_data = copy.deepcopy(self.runtime.midi_data['track_list'][0])
        play_tick_list    = list(map(lambda i:i*play_track_data['ticks_per_beat'],self.runtime.play_beat_list))
        # play_sec6tpb_list = list(map(lambda i:midi_data.tick_to_sec6tpb(i,play_track_data['tempo_list']),play_tick_list))
        play_track_data = midi_data.track_data_chop_tick(play_track_data, *play_tick_list)
        play_track_data = midi_data.track_data_move_tick(play_track_data, -play_tick_list[0])
        # play_track_data = midi_data.track_data_move_sec6tpb(play_track_data, -play_sec6tpb_list[0])
        
        tick_30    = play_tick_list[3]-play_tick_list[0]
        # sec6tpb_30 = play_sec6tpb_list[3]-play_sec6tpb_list[0]
        #print(f'YDXUFZLYQK tick_30={tick_30}, sec6tpb_30={sec6tpb_30}, play_tick_list={play_tick_list}, play_sec6tpb_list={play_sec6tpb_list}')
        display_track_data = copy.deepcopy(play_track_data)
        display_track_data0 = copy.deepcopy(display_track_data)
        display_track_data0 = midi_data.track_data_move_tick(display_track_data0, -tick_30)
        # display_track_data0 = midi_data.track_data_move_sec6tpb(display_track_data0, -sec6tpb_30)
        display_track_data1 = copy.deepcopy(display_track_data)
        display_track_data1 = midi_data.track_data_move_tick(display_track_data1, tick_30)
        # display_track_data1 = midi_data.track_data_move_sec6tpb(display_track_data1, sec6tpb_30)
        # for dm in display_track_data0['noteev_list']: dm['src']='0'
        # for dm in display_track_data['noteev_list']:  dm['src']='1'
        # for dm in display_track_data1['noteev_list']: dm['src']='2'
        display_track_data = midi_data.merge_track_data([display_track_data0,display_track_data,display_track_data1],[0,tick_30])

        play_track_data = midi_data.track_data_add_woodblock(play_track_data, 0, tick_30)
        
        time_multiplier = self.runtime.time_multiplier()
        # play_track_data = midi_data.track_data_time_multiply(play_track_data, time_multiplier)
        # display_track_data = midi_data.track_data_time_multiply(display_track_data, time_multiplier)
        midi_data.fill_sec6tpb(play_track_data, time_multiplier)
        midi_data.fill_sec6tpb(display_track_data, time_multiplier)
        self.track_data = display_track_data
        # self.loop_sec6tpb = midi_data.tick_to_sec6tpb(tick_30, play_track_data['tempo_list'], time_multiplier)
        self.loop_sec6tpb =   midi_data.tick_to_sec6tpb(play_tick_list[3], play_track_data['tempo_list'], time_multiplier) \
                            - midi_data.tick_to_sec6tpb(play_tick_list[0], play_track_data['tempo_list'], time_multiplier)

        self.start_sec = time.time() + 3
        self.runtime.midi_player.channel_to_volume_dict[0]  = self.runtime.main_vol
        self.runtime.midi_player.channel_to_volume_dict[15] = self.runtime.beat_vol
        self.runtime.midi_player.play(play_track_data['noteev_list'],self.loop_sec6tpb,play_track_data['ticks_per_beat'],self.start_sec,self.start_sec-2)

        self.audio_input_enabled = self.runtime.config['audio_input_enabled']
        if self.audio_input_enabled:
            ppitch0x = (self.track_data['ppitch0']-2) * const.DFT_PITCH_SAMPLE_COUNT
            ppitch1x = (self.track_data['ppitch1']+2) * const.DFT_PITCH_SAMPLE_COUNT
            freq_list = range(ppitch0x, ppitch1x+1)
            if not note_state.PITCH_POS:
                freq_list = reversed(freq_list)
            freq_list = map(lambda i: i/const.DFT_PITCH_SAMPLE_COUNT, freq_list)
            freq_list = map(lambda i: i-common.A4_PITCH, freq_list)
            freq_list = map(lambda i: common.A4_FREQ*2**(i/12), freq_list)
            freq_list = list(freq_list)
            self.dft.start(self.runtime.config['audio_input_sample_rate'], self.runtime.config['audio_input_sample_rate']//10, freq_list)
            self.audio_input.start()

            self.ppitch0x = ppitch0x
            self.ppitch1x = ppitch1x
            self.freq_list = freq_list
        else:
            self.freq_list = None

        super().on_active()

    def on_inactive(self):
        self.runtime.midi_player.stop()
        self.dft.stop()
        self.audio_input.stop()
        super().on_inactive()

    def update_ui_matrice(self):
        super().update_ui_matrice()
        if self.freq_list is not None:
            self.freq_pp0_list = []
            self.freq_pp1_list = []
            pppp0 = self.matric_note_rail_pp_min
            pppp1 = self.matric_note_rail_pp_max
            for f in range(len(self.freq_list)):
                ppp0 = pppp0 + (pppp1-pppp0)*(f-1)/len(self.freq_list)
                ppp1 = pppp0 + (pppp1-pppp0)*(f  )/len(self.freq_list)
                ppp2 = pppp0 + (pppp1-pppp0)*(f+1)/len(self.freq_list)
                pp0 = int((ppp0+ppp1)/2)
                pp1 = int((ppp1+ppp2)/2)
                if pp1 == pp0: pp1=pp0+1
                self.freq_pp0_list.append(pp0)
                self.freq_pp1_list.append(pp1)
        else:
            self.freq_pp0_list = None
            self.freq_pp1_list = None

    def event_tick(self, event, sec):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.runtime.state_pool.set_active('EDIT')
