import copy
import time
import rtmidi

VOLUME_MIN = 0
VOLUME_MAX = 0x7f

class MidiPlayer:

    def _set_none(self):
        self.start_sec = None
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


    def play(self,noteev_list,loop_sec6tpb,ticks_per_beat,start_sec):
        self.start_sec = start_sec
        self.noteev_list = copy.deepcopy(noteev_list)
        self.noteev_done = 0
        self.ticks_per_beat = ticks_per_beat
        self.loop_sec6tpb = loop_sec6tpb
        
        self._midiout_open()
        self.midiout.send_message([0xc0, 40])
        self.midiout.send_message([0xcf, 115])
        
        self.loop_cnt = 0

        self.update_next_sec(start_sec)


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
        ret += self.start_sec
        ret = max(ret,0)
        self.cache_next_sec = ret


    def run(self, sec):
        if self.midiout is None:
            return
        if sec < self.start_sec: return
        sec6tpb = sec
        sec6tpb -= self.start_sec
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
                self.midiout.send_message([0x90+channel, noteev['pitch'] , volume])
            if noteev['type'] == 'off':
                channel = noteev['channel']
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

