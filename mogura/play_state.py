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
        self.track_list = None

    def screen_tick(self, screen, sec):
        super().screen_tick(screen, sec)

        vision_offset_y = time.time()
        vision_offset_y -= self.start_sec
        vision_offset_y *= 1000000
        vision_offset_y *= self.matric_ticks_per_beat
        vision_offset_y %= self.track_data['sec6tpb']
        vision_offset_y = midi_data.sec6tpb_to_tick(vision_offset_y, self.track_data['tempo_list'])
        vision_offset_y /= self.matric_ticks_per_beat
        vision_offset_y *= self.matric_cell_width
        self.draw_note_rail(screen, vision_offset_y)

        screen.fill(
            rect=(0,self.matric_y0,self.matric_screen_size[0],1),
            color=(0,0,0),
        )
        
    def on_active(self):
        self.start_sec = time.time()

        src_track_data = self.runtime.midi_data['track_list'][0]
        
        play_tick_list    = list(map(lambda i:i*self.runtime.midi_data['ticks_per_beat'],self.runtime.play_beat_list))
        play_sec6tpb_list = list(map(lambda i:midi_data.tick_to_sec6tpb(i,src_track_data['tempo_list']),play_tick_list))

        self.track_data = {}

        noteev_list = src_track_data['noteev_list']
        noteev_list = filter(lambda i:i['tick']>=play_tick_list[1],noteev_list)
        noteev_list = filter(lambda i:i['tick']<=play_tick_list[2],noteev_list)
        noteev_list = list(noteev_list)
        noteev_list = copy.deepcopy(noteev_list)
        for noteev in noteev_list:
            noteev['tick']  -= play_tick_list[0]
            if 'tick0' in noteev: noteev['tick0'] -= play_tick_list[0]
            if 'tick1' in noteev: noteev['tick1'] -= play_tick_list[0]
            noteev['sec6tpb']  -= play_sec6tpb_list[0]
            if 'sec6tpb0' in noteev: noteev['sec6tpb0'] -= play_sec6tpb_list[0]
            if 'sec6tpb1' in noteev: noteev['sec6tpb1'] -= play_sec6tpb_list[0]

        noteev_list0 = copy.deepcopy(noteev_list)
        for noteev in noteev_list0:
            noteev['tick']  -= play_tick_list[3]-play_tick_list[0]
            if 'tick0' in noteev: noteev['tick0'] -= play_tick_list[3]-play_tick_list[0]
            if 'tick1' in noteev: noteev['tick1'] -= play_tick_list[3]-play_tick_list[0]
            noteev['sec6tpb']  -= play_sec6tpb_list[3]-play_sec6tpb_list[0]
            if 'sec6tpb0' in noteev: noteev['sec6tpb0'] -= play_sec6tpb_list[3]-play_sec6tpb_list[0]
            if 'sec6tpb1' in noteev: noteev['sec6tpb1'] -= play_sec6tpb_list[3]-play_sec6tpb_list[0]

        noteev_list1 = copy.deepcopy(noteev_list)
        for noteev in noteev_list1:
            noteev['tick']  += play_tick_list[3]-play_tick_list[0]
            if 'tick0' in noteev: noteev['tick0'] += play_tick_list[3]-play_tick_list[0]
            if 'tick1' in noteev: noteev['tick1'] += play_tick_list[3]-play_tick_list[0]
            noteev['sec6tpb']  += play_sec6tpb_list[3]-play_sec6tpb_list[0]
            if 'sec6tpb0' in noteev: noteev['sec6tpb0'] += play_sec6tpb_list[3]-play_sec6tpb_list[0]
            if 'sec6tpb1' in noteev: noteev['sec6tpb1'] += play_sec6tpb_list[3]-play_sec6tpb_list[0]

        noteev_list = noteev_list0+noteev_list+noteev_list1

        self.track_data['noteev_list'] = noteev_list
        
        bar_list = src_track_data['bar_list']
        bar_list = filter(lambda i:i>=play_tick_list[0],bar_list)
        bar_list = filter(lambda i:i<=play_tick_list[3],bar_list)
        bar_list = map(lambda i:i-play_tick_list[0],bar_list)
        bar_list = list(bar_list)

        bar_list0 = list(map(lambda i:i-play_tick_list[3]+play_tick_list[0],bar_list))
        bar_list1 = list(map(lambda i:i+play_tick_list[3]-play_tick_list[0],bar_list))
        bar_list = bar_list0 + bar_list + bar_list1

        bar_set = set(bar_list)
        bar_list = sorted(bar_set)
        self.track_data['bar_list'] = bar_list
        self.track_data['bar_set'] = bar_set
        
        tempo_list = src_track_data['tempo_list']
        tempo_list = filter(lambda i:i['tick1']>play_tick_list[0],tempo_list)
        tempo_list = filter(lambda i:i['tick0']<=play_tick_list[3],tempo_list)
        tempo_list = list(tempo_list)
        for tempo in tempo_list:
            tempo['tick0'] -= play_tick_list[0]
            tempo['tick1'] -= play_tick_list[0]
            tempo['sec6tpb0'] -= play_sec6tpb_list[0]
            tempo['sec6tpb1'] -= play_sec6tpb_list[0]
        tempo_list[0]['tick0']    = 0
        tempo_list[0]['tick1']    = play_tick_list[3] - play_tick_list[0]
        tempo_list[0]['sec6tpb0'] = 0
        tempo_list[0]['sec6tpb1'] = play_sec6tpb_list[3] - play_sec6tpb_list[0]
        self.track_data['tempo_list'] = tempo_list

        max_pitch = self.track_data['noteev_list']
        max_pitch = map(lambda i:i['pitch'],max_pitch)
        max_pitch = max(max_pitch)
        self.track_data['max_pitch'] = max_pitch
    
        min_pitch = self.track_data['noteev_list']
        min_pitch = map(lambda i:i['pitch'],min_pitch)
        min_pitch = min(min_pitch)
        self.track_data['min_pitch'] = min_pitch
        
        self.track_data['sec6tpb'] = play_sec6tpb_list[3]-play_sec6tpb_list[0]

        super().on_active()

    def event_tick(self, event, sec):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.runtime.state_pool.set_active('EDIT')
