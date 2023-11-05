import const
import gui
import null_state
import pygame

class ConfigState(null_state.NullState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'CONFIG'

    def screen_tick(self, screen, text_draw, sec, **kwargs):
        super().screen_tick(screen=screen, sec=sec, text_draw=text_draw, **kwargs)
        self.gui.draw_layer('options', screen, text_draw)
        self.gui.draw_layer('back', screen, text_draw)

    def event_tick(self, event, sec):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.runtime.state_pool.set_active('EDIT')

        self.gui.on_event(event)
        if self.gui.is_btn_active('audio_input.click'):
            self.runtime.state_pool.set_active('CONFIG_AUDIO_INPUT')
        if self.gui.is_btn_active('back.click'):
            self.runtime.state_pool.set_active('EDIT')

    def on_active(self):
        self.update_ui_matrice()

    def on_screen_change(self, screen_size):
        self.update_ui_matrice()

    def on_inactive(self):
        self.gui = None

    def update_ui_matrice(self):
        width,height = pygame.display.get_window_size()

        self.gui = gui.Gui()

        x = 10
        y = 10
        self.gui.add_label('audio_input.text','Audio',const.FONT_SIZE,(127,127,127), (x,y), 7,'options')
        self.gui.add_click('audio_input.click', (x,y), (240,40), 7, 'options')

        self.gui.add_label('back.text','Back',const.FONT_SIZE,(127,127,127), (width-10,height-10), 3,'back')
        self.gui.add_click('back.click', (width-10,height-10), (240,40), 3, 'options')
