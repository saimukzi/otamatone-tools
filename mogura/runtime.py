import audio_input
import audio_output
import concurrent
import concurrent.futures
import config_audio_input_device_state
import config_audio_input_samplerate_state
import config_audio_input_state
import config_audio_output_device_state
import config_audio_output_state
import config_state
import edit_state
import edit_state
import freq_timer
import math
import midi_data
import midi_player
import null_state
import os
import play_state
import pygame
import state_pool
import text_draw
import threading
import time
import timer_pool
import user_data
import mgr_enum

FPS = 120
EPS = FPS * 10

class Runtime:

    def __init__(self, **kargs):
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(min(32, os.cpu_count()+4))
        self.lock = threading.Condition()

        self.running = None
        self.timer_pool = timer_pool.TimerPool()
        self.state_pool = state_pool.StatePool()
        self.audio_input = audio_input.AudioInput(self)
        self.screen_size = None

        self.ui_zoom_level = 12
        
        self.play_beat_list = [0]*4
        # self.time_multiplier = 2 # >1: slower, <1: faster

        self.init_kargs = kargs
        
        self.config = user_data.load_user_data()
        if self.config is None:
            self.config = {}
        
        DEFAULT_CONFIG = {
            'audio_input_enabled': False,
            'audio_input_device_info': None,
            'audio_input_sample_rate': 44100,
            'audio_output_enabled': False,
            'audio_output_device_info': None,
            'audio_output_sample_rate': 44100,
            'ui_time_direction': mgr_enum.RIGHT,
            'ui_pitch_direction': mgr_enum.DOWN,
        }
        for key in DEFAULT_CONFIG:
            if key not in self.config:
                self.config[key] = DEFAULT_CONFIG[key]

        self.speed_level = self.init_kargs['speed']
        self.beat_vol = 127
        self.main_vol = 127
        self.dpitch = 0
        self.music_vol = 127

        self.exit_done = False

    def run(self):
        try:
            pygame.init()
        
            self.screen = pygame.display.set_mode((1280,720),flags=pygame.RESIZABLE)
            
            self.midi_player = midi_player.MidiPlayer()
            self.audio_output = audio_output.AudioOutput(self)
            
            t0 = time.time()
            self.timer_pool.add_timer(self.midi_player)
            self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0, FPS, lambda sec: self.screen_tick(sec)))
            self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0+1/2/EPS, EPS, lambda sec: self.event_tick(sec)))

            self.state_pool.add_state(config_audio_input_device_state.ConfigAudioInputDeviceState(self))
            self.state_pool.add_state(config_audio_input_samplerate_state.ConfigAudioInputSampleRateState(self))
            self.state_pool.add_state(config_audio_input_state.ConfigAudioInputState(self))
            self.state_pool.add_state(config_audio_output_device_state.ConfigAudioOutputDeviceState(self))
            self.state_pool.add_state(config_audio_output_state.ConfigAudioOutputState(self))
            self.state_pool.add_state(config_state.ConfigState(self))
            self.state_pool.add_state(edit_state.EditState(self))
            self.state_pool.add_state(null_state.NullState(self))
            self.state_pool.add_state(play_state.PlayState(self))
            self.state_pool.set_active('NULL')

            if self.init_kargs['filename'] is not None:
                self.open_file(self.init_kargs['filename'])

            self.text_draw = text_draw.TextDraw()

            self.timer_pool.run()

            self.exit_done = True
        except:
            self.exit_done = True
            raise
        finally:
            self.exit_done = True

    def screen_tick(self, sec):
        # print('screen_tick')
        screen_size = pygame.display.get_window_size()
        if self.screen_size != screen_size:
            self.state_pool.on_screen_change(screen_size)
            self.screen_size = screen_size
        self.text_draw.on_tick_start()
        self.state_pool.screen_tick(screen=self.screen, text_draw=self.text_draw, sec=sec)
        pygame.display.flip()
        # pygame.display.update()


    def event_tick(self, sec):
        # print('event_tick')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.timer_pool.stop()
            if event.type == pygame.DROPFILE:
                self.open_file(event.file)
            self.state_pool.event_tick(event, sec)

    def open_file(self, file_path):
        self.dpitch = 0
        self.midi_data = midi_data.path_to_data(file_path)

        tpb = self.midi_data['track_list'][0]['ticks_per_beat']
        time_signature_list = self.midi_data['track_list'][0]['time_signature_list']

        tick = self.midi_data['track_list'][0]['notetick0']
        for tsi in range(len(time_signature_list)):
            ts = time_signature_list[tsi]
            if ts['tick1'] >= tick: # use gte
                break
        bar_tick = midi_data.get_bar_tick(ts, tpb)
        tick -= ts['tick_anchor']
        tick = math.floor(tick/bar_tick)*bar_tick
        tick += ts['tick_anchor']
        beat0 = tick // tpb
        beat0 -= 4*ts['numerator']//ts['denominator']

        tick = self.midi_data['track_list'][0]['notetick1']
        for tsi in range(len(time_signature_list)):
            ts = time_signature_list[tsi]
            if ts['tick1'] > tick: # use gt
                break
        bar_tick = midi_data.get_bar_tick(ts, tpb)
        tick -= ts['tick_anchor']
        tick = math.ceil(tick/bar_tick)*bar_tick
        tick += ts['tick_anchor']
        beat1 = tick // tpb
        beat1 += 4*ts['numerator']//ts['denominator']

        self.play_beat_list[0] = beat0
        self.play_beat_list[1] = beat0
        # self.play_beat_list[2] = self.midi_data['track_list'][0]['tick1'] // self.midi_data['ticks_per_beat']
        # self.play_beat_list[3] = self.play_beat_list[2]
        self.play_beat_list[2] = beat1
        self.play_beat_list[3] = beat1
        self.state_pool.set_active('EDIT')
        midi_data.track_data_cal_ppitch(self.midi_data['track_list'][0], self.dpitch)
        self.state_pool.on_midi_update()

    def time_multiplier(self):
        return 2**(-self.speed_level/12)

instance = None

def run(**kargs):
    global instance
    instance = Runtime(**kargs)
    instance.run()
