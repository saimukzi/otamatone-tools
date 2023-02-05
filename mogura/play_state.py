import copy
import midi_data
import note_state
import pygame
import time

class PlayState(note_state.NoteState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'PLAY'
        self.rctrl_down = False
        self.lctrl_down = False
        
        self.start_sec = None
        #self.track_list = None
        self.loop_sec6tpb = None

    def screen_tick(self, screen, sec, **kwargs):
        super().screen_tick(screen=screen, sec=sec, **kwargs)

        vision_offset_y = time.time()
        vision_offset_y -= self.start_sec
        vision_offset_y *= 1000000
        vision_offset_y *= self.matric_ticks_per_beat
        # vision_offset_y %= self.track_data['sec6tpb']
        vision_offset_y %= self.loop_sec6tpb
        vision_offset_y = midi_data.sec6tpb_to_tick(vision_offset_y, self.track_data['tempo_list'], self.track_data['time_multiplier'])
        vision_offset_y /= self.matric_ticks_per_beat
        vision_offset_y *= self.matric_cell_width
        self.draw_note_rail(screen, vision_offset_y)

        screen.fill(
            rect=(0,self.matric_y0,self.matric_screen_size[0],1),
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
#        self.track_data['max_pitch'] = src_track_data['max_pitch']
#        self.track_data['min_pitch'] = src_track_data['min_pitch']
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
        self.loop_sec6tpb = midi_data.tick_to_sec6tpb(tick_30, play_track_data['tempo_list'], time_multiplier)

        self.start_sec = time.time() + 2
        self.runtime.midi_player.channel_to_volume_dict[0]  = self.runtime.main_vol
        self.runtime.midi_player.channel_to_volume_dict[15] = self.runtime.beat_vol
        self.runtime.midi_player.play(play_track_data['noteev_list'],self.loop_sec6tpb,play_track_data['ticks_per_beat'],self.start_sec-0.15)

        super().on_active()

    def on_inactive(self):
        self.runtime.midi_player.stop()
        super().on_active()

    def event_tick(self, event, sec):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.runtime.state_pool.set_active('EDIT')
