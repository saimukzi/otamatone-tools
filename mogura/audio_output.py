import copy
import hashlib
import json
import pyaudio
import pyaudio_hack
import midi_data
import time

BUF_LEN = 512

# EMPTY_BUF = b'\x00' * BUF_LEN * 2 * 2

class AudioOutput(object):

    def __init__(self, runtime):
        self.runtime = runtime

        self._audio_interface = None
        self._audio_stream = None
        self.stream_callback_list = []

        self.audio_data = None
        self.loop_sec = None
        self.start_sec = None

        self.frame0 = None
        self.frame1 = None
        self.frame_diff = None
        self.frame_done = None

    def play(self, audio_data, loop_sec, start_sec):
        print('Starting audio output...')
        assert(self._audio_stream is None)
        assert(self._audio_interface is None)

        if audio_data is None:
            print('No audio data found')
            return False

        if self.runtime.config['audio_output_device_info'] is None:
            print('No audio output device configured')
            return False
        
        self.audio_data = audio_data
        self.loop_sec = loop_sec
        self.start_sec = start_sec

        sec0 = midi_data.audio_tick_to_sec(0, self.audio_data)
        sec1 = sec0 + loop_sec
        self.frame0 = round(sec0*self.audio_data['SAMPLE_RATE'])
        self.frame1 = round(sec1*self.audio_data['SAMPLE_RATE'])
        self.frame_diff = self.frame1 - self.frame0
        self.frame_done = None

        print(f'self.frame0 = {self.frame0}')

        audio_output_device_list = get_audio_output_device_list(self.audio_data['SAMPLE_RATE'])
        # print(audio_output_device_list)
        audio_output_device_list = filter(lambda info: info['hash']==self.runtime.config['audio_output_device_info']['hash'], audio_output_device_list)
        audio_output_device_list = list(audio_output_device_list)

        if len(audio_output_device_list) <= 0:
            print('No audio output device found')
            return False
        
        self._audio_interface = pyaudio_hack.PyAudioHack()

        info = audio_output_device_list[0]
        print(info)

        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=audio_data['SAMPLE_RATE'],
            output=True,
            output_device_index = info['index'],
            frames_per_buffer=BUF_LEN,
            stream_callback=self._stream_callback,
        )

        print('Audio output started')

    def stop(self):
        print('Stopping audio output...')
        if self._audio_stream is not None:
            self._audio_stream.stop_stream()
            self._audio_stream.close()
            self._audio_stream = None
            self._audio_interface.terminate()
            self._audio_interface = None

        self.audio_data = None
        self.loop_sec = None
        self.start_sec = None

        self.frame0 = None
        self.frame1 = None
        self.frame_diff = None
        self.frame_done = None
        print('Audio output stopped')

    def _stream_callback(self, in_data, frame_count, time_info, status_flags):
        if self.audio_data is None:
            return (None, pyaudio.paComplete)
        # if self.loop_sec is not None and time_info['current_time'] - self.start_sec > self.loop_sec:
        #     return (None, pyaudio.paComplete)
        # if self.stream_callback_list:
        #     for callback in self.stream_callback_list:
        #         callback()
        # return (self.audio_data['data'], pyaudio.paContinue)
        if self.frame_done is None:
            sec_diff = time.time() - self.start_sec
            # print(f'sec_diff = {sec_diff}')
            frame_diff = int(sec_diff * self.audio_data['SAMPLE_RATE'])
            # sample_rate = self.audio_data['SAMPLE_RATE']
            # print(f'sample_rate = {sample_rate}')
            self.frame_done = frame_diff + self.frame0
            print(f'self.frame_done = {self.frame_done}')

        # print('0')
        # print(f'self.frame0 = {self.frame0}')
        # print(f'self.frame_done = {self.frame_done}')

        while self.frame_done + frame_count >= self.frame1:
            self.frame_done -= self.frame_diff

        # print('1')

        if self.frame_done < 0:
            self.frame_done += frame_count
            return (b'\x00'*frame_count*2*2, pyaudio.paContinue)

        # print('2')

        if (self.frame_done + frame_count)*2*2 >= len(self.audio_data['data']):
            self.frame_done += frame_count
            return (b'\x00'*frame_count*2*2, pyaudio.paContinue)

        # print('3')

        ret = self.audio_data['data'][self.frame_done*2*2:(self.frame_done+frame_count)*2*2]
        self.frame_done += frame_count

        # print('AudioOutput._stream_callback END')

        return (ret, pyaudio.paContinue)

def get_audio_output_device_list(sample_rate):
    audio_interface = pyaudio_hack.PyAudioHack()
    ret = _get_audio_output_device_list(audio_interface, sample_rate)
    audio_interface.terminate()
    return ret

def _get_audio_output_device_list(audio_interface, sample_rate):
    device_list = []
    for i in range(audio_interface.get_device_count()):
        info = audio_interface.get_device_info_by_index_hack(i)
        if info['maxOutputChannels'] <= 0: continue
        try:
            if not audio_interface.is_format_supported(
                rate=sample_rate,
                output_device=info['index'],
                output_channels=2,
                output_format=pyaudio.paInt16,
            ):
                continue
        except:
            continue

        info0 = copy.deepcopy(info)
        del info0['index']
        info0_json = json.dumps(info0, sort_keys=True)
        info0_json_hash = hashlib.md5(info0_json.encode('utf-8')).hexdigest()

        info1 = copy.deepcopy(info)
        info1['hash'] = info0_json_hash
        device_list.append(info1)

    return device_list
