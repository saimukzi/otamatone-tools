import edit_state
import edit_state
import freq_timer
import midi_data
import midi_player
import null_state
import play_state
import pygame
import state_pool
import text_draw
import time
import timer_pool

FPS = 60
EPS = FPS * 10

class Runtime:

    def __init__(self, **kargs):
        self.running = None
        self.timer_pool = timer_pool.TimerPool()
        self.state_pool = state_pool.StatePool()
        self.screen_size = None

        self.ui_zoom_level = 12
        
        self.play_beat_list = [0]*4
        # self.time_multiplier = 2 # >1: slower, <1: faster

        self.init_kargs = kargs
        
        self.speed_level = self.init_kargs['speed']
        self.beat_vol = 127
        self.main_vol = 127

    def run(self):
        pygame.init()
    
        self.screen = pygame.display.set_mode((1280,720),flags=pygame.RESIZABLE)
        
        self.midi_player = midi_player.MidiPlayer()
        
        t0 = time.time()
        self.timer_pool.add_timer(self.midi_player)
        self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0, FPS, lambda sec: self.screen_tick(sec)))
        self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0+1/2/EPS, EPS, lambda sec: self.event_tick(sec)))

        self.state_pool.add_state(null_state.NullState(self))
        self.state_pool.add_state(edit_state.EditState(self))
        self.state_pool.add_state(play_state.PlayState(self))
        self.state_pool.set_active('NULL')

        if self.init_kargs['filename'] is not None:
            self.open_file(self.init_kargs['filename'])

        self.text_draw = text_draw.TextDraw()

        self.timer_pool.run()

    def screen_tick(self, sec):
        # print('screen_tick')
        screen_size = pygame.display.get_window_size()
        if self.screen_size != screen_size:
            self.state_pool.on_screen_change(screen_size)
            self.screen_size = screen_size
        self.text_draw.on_tick_start()
        self.state_pool.screen_tick(screen=self.screen, text_draw=self.text_draw, sec=sec)
        pygame.display.flip()


    def event_tick(self, sec):
        # print('event_tick')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.timer_pool.stop()
            if event.type == pygame.DROPFILE:
                # file_path = event.file
                # self.midi_data = midi_data.path_to_data(file_path)
                # self.play_beat_list[0] = 0
                # self.play_beat_list[1] = 0
                # self.play_beat_list[2] = self.midi_data['track_list'][0]['bar_list'][-1] // self.midi_data['ticks_per_beat']
                # self.play_beat_list[3] = self.play_beat_list[2]
                # self.state_pool.set_active('EDIT')
                # self.state_pool.on_midi_update()
                self.open_file(event.file)
            self.state_pool.event_tick(event, sec)

    def open_file(self, file_path):
        self.midi_data = midi_data.path_to_data(file_path)
        self.play_beat_list[0] = 0
        self.play_beat_list[1] = 0
        self.play_beat_list[2] = self.midi_data['track_list'][0]['tick1'] // self.midi_data['ticks_per_beat']
        self.play_beat_list[3] = self.play_beat_list[2]
        self.state_pool.set_active('EDIT')
        self.state_pool.on_midi_update()

    def time_multiplier(self):
        return 2**(-self.speed_level/12)

instance = None

def run(**kargs):
    global instance
    instance = Runtime(**kargs)
    instance.run()
