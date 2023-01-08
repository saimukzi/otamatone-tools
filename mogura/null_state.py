import pygame

class NullState:

    def __init__(self,runtime):
        self.id = 'NULL'
        self.runtime = runtime

    def screen_tick(self, screen, sec):
        screen.fill((255,255,255))
        pygame.display.flip()

    def event_tick(self, event, sec):
        pass

    def on_active(self):
        pass

    def on_inactive(self):
        pass

    def on_screen_change(self, screen_size):
        pass

    def on_midi_update(self):
        pass
