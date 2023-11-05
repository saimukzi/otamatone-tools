import gui
import null_state
import pygame

SAMPLE_RATE_LIST = [44100, 48000]

class ConfigAudioInputSampleRateState(null_state.NullState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'CONFIG_AUDIO_INPUT_SAMPLERATE'

    def screen_tick(self, screen, text_draw, sec, **kwargs):
        super().screen_tick(screen=screen, sec=sec, text_draw=text_draw, **kwargs)
        self.gui.draw_layer('options', screen, text_draw)
        self.gui.draw_layer('back', screen, text_draw)

    def event_tick(self, event, sec):
        self.gui.on_event(event)
        if self.gui.is_btn_active('back.click'):
            self.runtime.state_pool.set_active('CONFIG_AUDIO_INPUT')

    def on_active(self):
        self.update_ui_matrice()

    def on_inactive(self):
        self.gui = None

    def on_screen_change(self, screen_size):
        self.update_ui_matrice()

    def update_ui_matrice(self):
        width,height = pygame.display.get_window_size()

        self.gui = gui.Gui()

        x = 10
        y = 10
        # self.gui.add_label('audio_input_device.text','',40,(127,127,127), (x,y), 7,'options')
        # self.gui.add_click('audio_input_device.click', (x,y), (240,40), 7, 'options')
        # y += 40

        x = width-10
        y = height-10
        self.gui.add_label('back.text','Back',40,(127,127,127), (x,y), 3,'back')
        self.gui.add_click('back.click', (x,y), (240,40), 3, 'back')
