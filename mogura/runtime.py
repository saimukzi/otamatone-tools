import freq_timer
import pygame
import time

FPS = 60
EPS = FPS * 10

class Runtime:

    def __init__(self):
        self.running = None
        self.timer_list = [] 

    def run(self):
        pygame.init()
    
        screen = pygame.display.set_mode((1280,720))
        
        self.t0 = time.time()
        
        self.screen_timer = freq_timer.FreqTimer(self, self.t0, FPS, lambda sec: self.screen_tick())
        self.timer_list.append(self.screen_timer)

        self.event_timer = freq_timer.FreqTimer(self, self.t0+1/2/EPS, EPS, lambda sec: self.event_tick())
        self.timer_list.append(self.event_timer)
        
        self.running = True
        while self.running:
            now_sec = time.time()
            #print(f'loop now_sec={now_sec}')

            active_timer_sec_idx_timer_list = []
            for i,timer in enumerate(self.timer_list):
                next_sec = timer.next_sec()
                if next_sec > now_sec: continue
                active_timer_sec_idx_timer_list.append((next_sec,i,timer))
            active_timer_sec_idx_timer_list.sort()

            for _,_,timer in active_timer_sec_idx_timer_list:
                timer.run(now_sec)
                timer.update_next_sec(now_sec)

            next_sec = self.timer_list
            next_sec = map(lambda i:i.next_sec(),next_sec)
            next_sec = min(next_sec)

            now_sec = time.time()
            time.sleep(max(next_sec-now_sec,0))

    def screen_tick(self):
        #print('screen_tick')
        pass


    def event_tick(self):
        #print('event_tick')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False


instance = None

def run():
    global instance
    instance = Runtime()
    instance.run()
