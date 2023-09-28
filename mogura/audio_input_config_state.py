import audio_input
import null_state

class AudioInputConfigState(null_state.NullState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'AUDIO_INPUT_CONFIG'

    def screen_tick(self, screen, **kwargs):
        screen.fill((255,255,255))

    def event_tick(self, event, sec):
        pass

    def on_active(self):
        self.refresh_audio_input_device_list()

    def on_inactive(self):
        pass

    def on_screen_change(self, screen_size):
        pass

    def on_midi_update(self):
        pass

    def on_pitch_update(self):
        pass

    def refresh_audio_input_device_list(self):
        self.audio_input_device_list = audio_input.get_audio_input_device_list()
        for audio_input_device in self.audio_input_device_list:
            print(audio_input_device)
