import copy
import math
import time
import rtmidi

VOLUME_MIN = 0
VOLUME_MAX = 0x7f

class MidiPlayer:

    def _set_none(self):
        self.main_start_sec = None
        self.beat_start_sec = None
        self.noteev_list = None
        self.noteev_done = None
        self.ticks_per_beat = None
        self.loop_sec6tpb = None
        
        self.cache_next_sec = None

        self.midiout = None

        self.loop_cnt = None

    
    def __init__(self):
        self._set_none()
        
        self.channel_to_volume_dict = {0:0x7f, 15:0x7f}


    def play(self,noteev_list,loop_sec6tpb,ticks_per_beat,main_start_sec,beat_start_sec):
        assert(beat_start_sec<=main_start_sec)
    
        self.main_start_sec = main_start_sec
        self.beat_start_sec = beat_start_sec
        self.noteev_list = copy.deepcopy(noteev_list)
        self.noteev_done = 0
        self.ticks_per_beat = ticks_per_beat
        self.loop_sec6tpb = loop_sec6tpb
        
        self._midiout_open()
        self.midiout.send_message([0xc0, 40])
        self.midiout.send_message([0xcf, 115])
        
        tmp1 = beat_start_sec-main_start_sec
        tmp1 = math.ceil(tmp1*1000000*ticks_per_beat)
        tmp0 = round(tmp1//loop_sec6tpb)
        tmp1 %= loop_sec6tpb
        tmp1 = get_ceil_note_idx(tmp1,noteev_list)
        if tmp1 == None:
            tmp0 += 1
            tmp1 = 0
        #print(f'tmp0={tmp0},tmp1={tmp1}')
        self.loop_cnt = tmp0
        self.noteev_done = tmp1

        self.update_next_sec(None)


    def stop(self):
        self._midiout_close()
        self._set_none()


    def next_sec(self):
        return self.cache_next_sec


    def update_next_sec(self, _):
        if self.midiout is None:
            self.cache_next_sec = None
            return
        if self.noteev_done >= len(self.noteev_list):
            self.cache_next_sec = None
            return
        ret = self.noteev_list[self.noteev_done]['sec6tpb']
        ret += self.loop_cnt * self.loop_sec6tpb
        ret /= 1000000
        ret /= self.ticks_per_beat
        ret += self.main_start_sec
        ret = max(ret,0)
        self.cache_next_sec = ret


    def run(self, sec):
        if self.midiout is None:
            return
        if sec < self.beat_start_sec: return
        c15_only = sec < self.main_start_sec
        sec6tpb = sec
        sec6tpb -= self.main_start_sec
        sec6tpb *= self.ticks_per_beat
        sec6tpb *= 1000000
        sec6tpb -= self.loop_cnt * self.loop_sec6tpb
        #print(f'sec6tpb = {sec6tpb}')
        #print(f'noteev_done = {self.noteev_done}')
        while True:
            #print(f'self.noteev_done={self.noteev_done}')
            #if self.noteev_done >= len(self.noteev_list): break
            noteev = self.noteev_list[self.noteev_done]
            #print(noteev)
            if sec6tpb < noteev['sec6tpb']: break
            #print(noteev)
            if noteev['type'] == 'on':
                channel = noteev['channel']
                volume = self.channel_to_volume_dict[channel]
                if (not c15_only) or (channel==15):
                    #print(noteev)
                    self.midiout.send_message([0x90+channel, noteev['pitch'] , volume])
            if noteev['type'] == 'off':
                channel = noteev['channel']
                #print(noteev)
                self.midiout.send_message([0x80+channel, noteev['pitch'] , 0])
            self.noteev_done += 1
            if self.noteev_done >= len(self.noteev_list):
                self.noteev_done -= len(self.noteev_list)
                sec6tpb -= self.loop_sec6tpb
                self.loop_cnt += 1

    def _midiout_open(self):
        if self.midiout is not None:
            self._midiout_close()
        self.midiout = rtmidi.MidiOut()
        available_ports = self.midiout.get_ports()
        if available_ports:
            self.midiout.open_port(0)
        else:
            self.midiout.open_virtual_port("My virtual output")


    def _midiout_close(self):
        if self.midiout is None: return
        self.midiout.close_port()
        self.midiout = None


def get_ceil_note_idx(sec6tpb, noteev_list):
    for i in range(len(noteev_list)):
        noteev = noteev_list[i]
        if sec6tpb < noteev['sec6tpb']:
            return i
    return None
