import audio_output
import common
import const
import gui
import pygame
import null_state

class ConfigAudioOutputDeviceState(null_state.NullState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'CONFIG_AUDIO_OUTPUT_DEVICE'
        self.device_list_scroll_y = 0

    def screen_tick(self, screen, text_draw, sec, **kwargs):
        super().screen_tick(screen=screen, sec=sec, text_draw=text_draw, **kwargs)
        self.gui.draw_layer('options', screen, text_draw)
        self.gui.draw_layer('back', screen, text_draw)

    def event_tick(self, event, sec):
        self.gui.on_event(event)

        if event.type == pygame.MOUSEWHEEL:
            self.device_list_scroll_y += event.y * 60
            self.update_device_list_pos()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.runtime.state_pool.set_active('CONFIG_AUDIO_OUTPUT')
        if self.gui.is_btn_active('back.click'):
            self.runtime.state_pool.set_active('CONFIG_AUDIO_OUTPUT')

        for audio_output_device in self.audio_output_device_list:
            hash = audio_output_device['hash']
            if self.gui.is_btn_active(f'audio_output_device.{hash}.click'):
                self.runtime.config['audio_output_device_info'] = audio_output_device
                self.runtime.state_pool.set_active('CONFIG_AUDIO_OUTPUT')
                break

    def on_active(self):
        self.refresh_audio_output_device_list()
        self.update_ui_matrice()

    def on_inactive(self):
        self.gui = None
        self.audio_output_device_list = None

    def on_screen_change(self, screen_size):
        self.update_ui_matrice()

    def update_ui_matrice(self):
        width,height = pygame.display.get_window_size()

        self.gui = gui.Gui()

        x = 10
        y = 10
        for audio_output_device in self.audio_output_device_list:
            hash = audio_output_device['hash']
            name_utf8 = audio_output_device['name_utf8']
            host_api = audio_output_device['hostApi']
            default_sample_rate = int(audio_output_device['defaultSampleRate'])
            low_output_latency = audio_output_device['defaultLowOutputLatency']
            high_output_latency = audio_output_device['defaultHighOutputLatency']
            name = f'{name_utf8} {host_api} {default_sample_rate} {low_output_latency}-{high_output_latency}'
            self.gui.add_label(f'audio_output_device.{hash}.text',name,const.FONT_SIZE,(127,127,127), (x,y), 7,'options')
            self.gui.add_click(f'audio_output_device.{hash}.click', (0,y), (width-300,40), 7, 'options')
            y += 40
        self.update_device_list_pos()

        x = width-10
        y = height-10
        self.gui.add_label('back.text','Back',const.FONT_SIZE,(127,127,127), (x,y), 3,'back')
        self.gui.add_click('back.click', (x,y), (240,40), 3, 'back')

    def update_device_list_pos(self):
        width,height = pygame.display.get_window_size()
        x = 10
        y = 10 + self.device_list_scroll_y
        for audio_output_device in self.audio_output_device_list:
            hash = audio_output_device['hash']
            click_rect = common.anchor((x,y), (width-300,40), 7) + (width-300,40)
            self.gui.get(f'audio_output_device.{hash}.text')['draw_kargs']['xy'] = (x,y)
            self.gui.get(f'audio_output_device.{hash}.click')['rect'] = click_rect
            y += 40

    def refresh_audio_output_device_list(self):
        self.audio_output_device_list = audio_output.get_audio_output_device_list(44100)
        for audio_output_device in self.audio_output_device_list:
            print(audio_output_device)
