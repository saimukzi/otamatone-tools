import audio_output
import const
import dft
import gui
import null_state
import pygame

class ConfigAudioOutputState(null_state.NullState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'CONFIG_AUDIO_OUTPUT'
        self.audio_output = audio_output.AudioOutput(self.runtime)
        self.dft = dft.Dft(self.runtime)
        self.session = None

        degree = 8*12
        freq_cnt = degree*4
        freq_list = range(freq_cnt)
        freq_list = map(lambda i: i-(freq_cnt//2), freq_list)
        freq_list = map(lambda i: 440*2**(i/degree), freq_list)
        self.freq_list = list(freq_list)

    def screen_tick(self, screen, text_draw, sec, **kwargs):
        super().screen_tick(screen=screen, sec=sec, text_draw=text_draw, **kwargs)

        if self.session['test']:
            level_np = self.dft.get_level_np()
            if level_np is not None:
                x = 0
                # print(level_np.shape)
                for i in range(level_np.shape[0]):
                    v = level_np[i]
                    v = v+10
                    v = max(v,0)
                    v *= 50
                    screen.fill(
                        rect=(x,0,5,v),
                        color=(0,0,0,255),
                    )
                    x += 5

        self.gui.draw_layer('options', screen, text_draw)
        self.gui.draw_layer('back', screen, text_draw)

    def event_tick(self, event, sec):
        self.gui.on_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.runtime.state_pool.set_active('CONFIG')
        if self.gui.is_btn_active('back.click'):
            self.runtime.state_pool.set_active('CONFIG')

        if self.gui.is_btn_active('audio_output_device.click'):
            self.runtime.state_pool.set_active('CONFIG_AUDIO_OUTPUT_DEVICE')
        if self.gui.is_btn_active('audio_output_enable.click'):
            self.runtime.config['audio_output_enabled'] = not self.runtime.config['audio_output_enabled']
            self.update_label_txt()
        if self.gui.is_btn_active('audio_output_test.click'):
            if not self.session['test']:
                self.dft.start(self.runtime.config['audio_output_sample_rate'], self.runtime.config['audio_output_sample_rate']//10, self.freq_list)
                self.audio_output.start()
                self.session['test'] = True
            else:
                self.dft.stop()
                self.audio_output.stop()
                self.session['test'] = False


    def on_active(self):
        self.update_ui_matrice()
        self.session = {
            'test': False
        }

    def on_inactive(self):
        self.gui = None
        self.dft.stop()
        self.audio_output.stop()
        self.session = False

    def on_screen_change(self, screen_size):
        self.update_ui_matrice()

    def update_ui_matrice(self):
        width,height = pygame.display.get_window_size()

        self.gui = gui.Gui()

        x = 10
        y = 10
        self.gui.add_label('audio_output_device.text','',const.FONT_SIZE,(127,127,127), (x,y), 7,'options')
        self.gui.add_click('audio_output_device.click', (x,y), (240,40), 7, 'options')

        y += 40
        self.gui.add_label('audio_output_test.text','Test',const.FONT_SIZE,(127,127,127), (x,y), 7,'options')
        self.gui.add_click('audio_output_test.click', (x,y), (240,40), 7, 'options')

        y += 40
        self.gui.add_label('audio_output_enable.text','',const.FONT_SIZE,(127,127,127), (x,y), 7,'options')
        self.gui.add_click('audio_output_enable.click', (x,y), (240,40), 7, 'options')

        x = width-10
        y = height-10
        self.gui.add_label('back.text','Back',const.FONT_SIZE,(127,127,127), (x,y), 3,'back')
        self.gui.add_click('back.click', (x,y), (240,40), 3, 'back')

        self.update_label_txt()

    def update_label_txt(self):
        txt = 'None' if self.runtime.config['audio_output_device_info'] is None else \
              self.runtime.config['audio_output_device_info']['name_utf8']
        self.gui.set_label_text('audio_output_device.text', txt)

        txt = 'On' if self.runtime.config['audio_output_enabled'] else 'Off'
        self.gui.set_label_text('audio_output_enable.text', txt)
