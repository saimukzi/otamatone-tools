import freq_timer
import pygame
import time
import timer_pool

FPS = 60
EPS = FPS * 10

class Runtime:

    def __init__(self):
        self.running = None
        self.timer_pool = timer_pool.TimerPool()

    def run(self):
        pygame.init()
    
        screen = pygame.display.set_mode((1280,720))
        
        t0 = time.time()
        self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0, FPS, lambda sec: self.screen_tick()))
        self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0+1/2/EPS, EPS, lambda sec: self.event_tick()))
        
        self.timer_pool.run()

    def screen_tick(self):
        #print('screen_tick')
        pass


    def event_tick(self):
        #print('event_tick')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.timer_pool.stop()


instance = None

def run():
    global instance
    instance = Runtime()
    instance.run()
