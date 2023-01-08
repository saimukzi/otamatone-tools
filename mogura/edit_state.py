import common
import math
import pygame
import note_state
from PIL import Image, ImageDraw

PITCH_A4 = 69

class EditState(note_state.NoteState):

    def __init__(self,runtime):
        super().__init__(runtime)
        self.id = 'EDIT'

    def screen_tick(self, screen, sec):
        super().screen_tick(screen, sec)

    def event_tick(self, event, sec):
        pass
